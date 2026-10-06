"""Benchmark implementations of KernelModel."""

import numpy as np
import torch
from torch import nn
from .base import conditional_model, mlp
from .posterior import contrast_nll, flat_offset_posterior


class kernel_model(conditional_model):
    """Neural-mean conventional GP, DKT, or ADKF-IFT with nuisance intercept."""

    def __init__(self, c):
        super().__init__()
        self.c = c
        d = c["input_dim"]
        w = c["width"]
        f = c["feature_dim"]
        self.adapter = (
            nn.Identity()
            if c["method"] == "neural_mean_gp"
            else mlp(d, w, f, c["depth"])
        )
        self.mean_net = (
            mlp(d, w, 1, c["depth"]) if c["method"] == "neural_mean_gp" else None
        )
        lower = torch.tensor([0.03, 0.001, 0.0001], dtype=torch.float64)
        upper = torch.tensor([30.0, 20.0, 5.0], dtype=torch.float64)
        initial = torch.tensor([1.0, 1.0, 0.1], dtype=torch.float64)
        raw = torch.logit((initial - lower) / (upper - lower))
        self.register_buffer("lower", lower)
        self.register_buffer("upper", upper)
        self.register_buffer("prior_phi", raw.clone())
        self.phi = nn.Parameter(raw, requires_grad=c["method"] != "adkf_ift")
        self.last_fit = {}

    def embeddings(self, context, query):
        xc = self.adapter(context.x).double()
        xq = self.adapter(query).double()
        mc = (
            torch.zeros(len(xc), dtype=torch.float64)
            if self.mean_net is None
            else self.mean_net(context.x)[:, 0].double()
        )
        mq = (
            torch.zeros(len(xq), dtype=torch.float64)
            if self.mean_net is None
            else self.mean_net(query)[:, 0].double()
        )
        return (xc, xq, mc, mq)

    def hyperparameters(self, phi):
        return self.lower + (self.upper - self.lower) * phi.sigmoid()

    def kernel(self, x, z, phi):
        length, amplitude, _ = self.hyperparameters(phi)
        distance = ((x[:, None] - z[None]) / length).square().mean(-1)
        if self.c["kernel"] == "rbf":
            return amplitude * torch.exp(-distance / 2)
        radius = (5 * distance + 1e-20).sqrt()
        return amplitude * (1 + radius + 5 * distance / 3) * torch.exp(-radius)

    def evidence(self, x, mean, y, phi, regularize=False):
        noise = self.hyperparameters(phi)[2]
        covariance = self.kernel(x, x, phi) + noise * torch.eye(
            len(x), dtype=torch.float64
        )
        loss = contrast_nll(mean, covariance, y)
        if regularize:
            loss = (
                loss
                + self.c["gp_prior_strength"]
                * (phi - self.prior_phi).square().sum()
                / 2
            )
        return loss

    def posterior(self, xc, xq, mc, mq, y, phi):
        _, amp, noise = self.hyperparameters(phi)
        return flat_offset_posterior(
            mc,
            mq,
            self.kernel(xc, xc, phi),
            self.kernel(xq, xc, phi),
            amp.expand(len(xq)),
            noise,
            y,
        )

    def fit_phi(self, xc, mc, y):
        from scipy.optimize import minimize

        xc = xc.detach()
        mc = mc.detach()
        y = y.detach()
        if len(y) == 1:
            self.last_fit = dict(gradient_norm=0.0, iterations=0, one_shot_prior=True)
            return self.prior_phi.detach().clone().requires_grad_(True)

        def objective(raw):
            with torch.enable_grad():
                phi = torch.tensor(raw, dtype=torch.float64, requires_grad=True)
                loss = self.evidence(xc, mc, y, phi, True)
                gradient = torch.autograd.grad(loss, phi)[0]
            return (float(loss.detach()), gradient.detach().numpy())

        result = minimize(
            objective,
            self.prior_phi.detach().numpy(),
            jac=True,
            method="BFGS",
            options=dict(
                maxiter=self.c["gp_inner_maxiter"], gtol=self.c["gp_inner_tolerance"]
            ),
        )
        norm = float(np.linalg.norm(result.jac))
        self.last_fit = dict(
            gradient_norm=norm, iterations=int(result.nit), success=bool(result.success)
        )
        if not np.isfinite(result.fun) or norm > max(
            0.001, 10 * self.c["gp_inner_tolerance"]
        ):
            raise RuntimeError(
                "ADKF inner optimizer failed stationarity: " + str(self.last_fit)
            )
        return torch.tensor(result.x, dtype=torch.float64, requires_grad=True)

    def predict(self, context, query):
        xc, xq, mc, mq = self.embeddings(context, query)
        y = context.y.double()
        phi = self.fit_phi(xc, mc, y) if self.c["method"] == "adkf_ift" else self.phi
        return self.posterior(xc, xq, mc, mq, y, phi)

    def loss(self, episode):
        context = episode.context
        xc, xq, mc, mq = self.embeddings(context, episode.query)
        y = context.y.double()
        if self.c["method"] != "adkf_ift":
            return self.evidence(
                torch.cat([xc, xq]),
                torch.cat([mc, mq]),
                torch.cat([y, episode.target.double()]),
                self.phi,
            )
        phi = self.fit_phi(xc, mc, y)
        outer = (
            -self.posterior(xc, xq, mc, mq, y, phi)
            .log_prob(episode.target.double())
            .mean()
        )
        inner = self.evidence(xc, mc, y, phi, True)
        gradient = torch.autograd.grad(inner, phi, create_graph=True)[0]
        hessian = torch.stack(
            [torch.autograd.grad(g, phi, retain_graph=True)[0] for g in gradient]
        )
        hessian = (hessian + hessian.T) / 2
        eig = torch.linalg.eigvalsh(hessian.detach())
        damping = max(self.c["ift_damping"], float(-eig.min()) + self.c["ift_damping"])
        v = torch.linalg.solve(
            hessian.detach() + damping * torch.eye(3, dtype=torch.float64),
            torch.autograd.grad(outer, phi, retain_graph=True)[0].detach(),
        )
        self.last_fit.update(min_hessian_eigenvalue=float(eig.min()), damping=damping)
        implicit = gradient @ v
        return outer - implicit + implicit.detach()
