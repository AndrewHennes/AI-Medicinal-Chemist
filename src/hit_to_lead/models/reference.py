"""Average-anchor baseline, centered residual kernel and learned variance.

The numerical graph and historical parameter names are preserved, but no
experiment-directory imports or runtime inheritance chain remain.
"""

import math
import numpy as np
import torch
from torch import nn
from torch.nn import functional
from .base import conditional_model
from ..distributions import predictive_distribution


def collate(rows):
    batch_count = len(rows)
    query_count = max((len(r["query"]) for r in rows))
    context_capacity = max(1, max((len(r["local"]) for r in rows)))
    d = rows[0]["query"].shape[-1]
    b = dict(
        query=np.zeros((batch_count, query_count, d), np.float32),
        local=np.zeros((batch_count, context_capacity, d), np.float32),
        target=np.zeros((batch_count, query_count), np.float32),
        local_values=np.zeros((batch_count, context_capacity), np.float32),
        query_valid=np.zeros((batch_count, query_count), bool),
        local_valid=np.zeros((batch_count, context_capacity), bool),
    )
    for i, r in enumerate(rows):
        q = len(r["query"])
        c = len(r["local"])
        b["query"][i, :q] = r["query"]
        b["target"][i, :q] = r.get("target", np.zeros(q))
        b["query_valid"][i, :q] = True
        b["local"][i, :c] = r["local"]
        b["local_values"][i, :c] = r["local_values"]
        b["local_valid"][i, :c] = True
    return {k: torch.from_numpy(v) for k, v in b.items()}


def conditional_variance(matrix, cross, diagonal):
    """Latent conditional variance. Padding has identity diagonal and zero cross.

    Double precision factorization reduces cancellation. No inverse is formed.
    Roundoff clipping is applied only after checking for material negativity.
    """
    factor = torch.linalg.cholesky(matrix.double())
    projected = torch.linalg.solve_triangular(
        factor, cross.double().transpose(-1, -2), upper=False
    )
    raw = diagonal.double() - projected.square().sum(-2)
    if not torch.isfinite(raw).all() or (raw.detach() < -1e-05).any():
        raise ArithmeticError("Invalid conditional variance; check kernel PSD.")
    return raw.clamp_min(0).to(cross.dtype)


def centered_geometry(kcc, kqc, valid, ridge):
    """Center latent covariance and iid raw measurement noise in the same basis.

    centering_matrix is the orthogonal projector onto zero-sum measured contrasts. It has a
    one-dimensional null space. gauge_matrix fixes that unused coordinate; it is not extra
    observation noise. Invalid padding receives an identity block. Projected
    residuals and cross covariance are orthogonal to both unused subspaces.
    """
    v = valid.to(kcc.dtype)
    n = v.sum(-1)
    w = v / n[:, None]
    gauge_matrix = v[:, :, None] * v[:, None, :] / n[:, None, None]
    centering_matrix = torch.diag_embed(v) - gauge_matrix
    centered_cc = centering_matrix @ kcc @ centering_matrix
    qbar = (kqc * w[:, None, :]).sum(-1)
    cbar = (kcc * w[:, None, :]).sum(-1)
    grand = (cbar * w).sum(-1)
    centered_qc = (kqc - qbar[..., None] - cbar[:, None, :] + grand[:, None, None]) * v[
        :, None, :
    ]
    diagonal = 1 - 2 * qbar + grand[:, None]
    noise = ridge * centering_matrix
    matrix = centered_cc + noise + gauge_matrix + torch.diag_embed(1 - v)
    return dict(
        matrix=matrix,
        cross=centered_qc,
        diagonal=diagonal,
        projection=centering_matrix,
        centered_covariance=centered_cc,
        noise=noise,
        gauge=gauge_matrix,
        weights=w,
    )


class pair_backbone(nn.Module):
    """Pair/context encoders compatible with the saved checkpoints."""

    def __init__(self, c):
        super().__init__()
        self.c = c
        d = c["input_dim"]
        w = c["width"]
        self.bayes = False

        def linear(a, b):
            return nn.Linear(a, b)

        self.pair = nn.Sequential(linear(2 * d, w), nn.GELU(), linear(w, w), nn.GELU())
        self.context = nn.Sequential(
            linear(2 * d + 1, w), nn.GELU(), linear(w, w), nn.GELU()
        )
        outputs = 4 if c["family"] == "evidential_nig" else 2
        self.decoder = nn.Sequential(
            linear(2 * w + 3, w), nn.GELU(), linear(w, outputs)
        )
        if c["family"] in ["attentive_np", "metric_np"]:
            self.prior = nn.Linear(w, 1)
            self.key = nn.Linear(w, w, bias=False)
            self.value = nn.Sequential(nn.Linear(w + 1, w), nn.GELU(), nn.Linear(w, w))
            self.attn_decode = nn.Sequential(
                nn.Linear(3 * w + 6, w), nn.GELU(), nn.Linear(w, 3)
            )
            self.null_logit = nn.Parameter(torch.tensor(0.0))
            self.log_temperature = nn.Parameter(torch.tensor(0.0))
            if c["family"] == "metric_np":
                self.log_metric_scale = nn.Parameter(torch.zeros(d))
                self.log_temperature.data.fill_(math.log(c.get("temperature", 1.0)))


class centered_kernel_model(nn.Module):
    """Average mean and average-reference covariance with finite residual updates."""

    def __init__(self, c):
        super().__init__()
        self.c = c
        d = c["input_dim"]
        w = c["width"]
        self.d = d
        self.w = w
        base = dict(c, family="metric_np")
        self.base = pair_backbone(base)
        self.log_df = nn.Parameter(torch.tensor(math.log(4.0)))
        if c["family"] == "residual_graph":
            self.log_bandwidth = nn.Parameter(torch.tensor(math.log(1.0)))
            self.log_ridge = nn.Parameter(torch.tensor(math.log(0.15)))
            self.step_logits = nn.Parameter(torch.zeros(c["graph_steps"]))
            self.output = nn.Sequential(
                nn.Linear(2 * w + 8, w), nn.GELU(), nn.Linear(w, 3)
            )
            nn.init.zeros_(self.output[-1].weight)
            nn.init.zeros_(self.output[-1].bias)
        self.output[-1] = nn.Linear(self.w, 4)
        nn.init.zeros_(self.output[-1].weight)
        nn.init.zeros_(self.output[-1].bias)
        with torch.no_grad():
            self.output[-1].bias[3] = math.log(math.expm1(0.05))

    def distance(self, query, measured):
        scale = self.base.log_metric_scale.exp().clamp(0.05, 20)
        return (
            ((query[:, :, None, : self.d] - measured[:, None, :, : self.d]) / scale)
            ** 2
        ).mean(-1)

    def centered_baselines(self, b, anchors, valid):
        v = valid.float()
        n = v.sum(-1)
        if not self.c["average_mean"]:
            query_prior = self.base.prior(self.base.pair(b["query"])).squeeze(-1)
            local = self.base.prior(self.base.pair(b["local"])).squeeze(-1)
            anchor_prior = torch.cat([torch.zeros_like(local[:, :1]), local], -1)
        else:
            batch_count, anchor_count, embedding_width = anchors.shape
            query = b["query"][..., :embedding_width]
            query_count = query.shape[1]
            pairs = torch.cat(
                [
                    query[:, :, None].expand(
                        batch_count, query_count, anchor_count, embedding_width
                    ),
                    anchors[:, None].expand(
                        batch_count, query_count, anchor_count, embedding_width
                    ),
                ],
                -1,
            )
            deltas = self.base.prior(self.base.pair(pairs)).squeeze(-1)
            query_prior = (deltas * v[:, None]).sum(-1) / n[:, None]
            pairs = torch.cat(
                [
                    anchors[:, :, None].expand(
                        batch_count, anchor_count, anchor_count, embedding_width
                    ),
                    anchors[:, None].expand(
                        batch_count, anchor_count, anchor_count, embedding_width
                    ),
                ],
                -1,
            )
            deltas = self.base.prior(self.base.pair(pairs)).squeeze(-1)
            eligible = (
                valid[:, None, :]
                & ~torch.eye(anchor_count, dtype=torch.bool, device=anchors.device)[
                    None
                ]
            )
            anchor_prior = (
                torch.where(eligible, deltas, torch.zeros_like(deltas)).sum(-1)
                / n[:, None]
            )
        mean_prior = (anchor_prior * v).sum(-1) / n
        return (
            query_prior - mean_prior[:, None],
            (anchor_prior - mean_prior[:, None]) * v,
        )

    def forward(self, b, diagnostics=False):
        q = self.base.pair(b["query"])
        mask = b["local_valid"].float()
        n = mask.sum(-1)
        ref = b["query"][:, :1, self.d :]
        local = b["local"][..., : self.d]
        query = b["query"][..., : self.d]
        anchors = torch.cat([ref, local], 1)
        valid = torch.cat(
            [torch.ones_like(b["local_valid"][:, :1]), b["local_valid"]], 1
        )
        anchors = torch.where(valid[..., None], anchors, torch.zeros_like(anchors))
        values = torch.cat(
            [torch.zeros_like(b["local_values"][:, :1]), b["local_values"]], -1
        )
        values = torch.where(valid, values, torch.zeros_like(values))
        observed_mean = values.sum(-1) / (n + 1)
        query_prior, anchor_prior = self.centered_baselines(b, anchors, valid)
        raw_residual = (values - observed_mean[:, None] - anchor_prior) * valid
        scale = self.base.log_metric_scale.exp().clamp(0.05, 20)
        bandwidth = self.log_bandwidth.exp().clamp(0.02, 100)

        def sim(a, b):
            distance = (((a[:, :, None] - b[:, None, :]) / scale) ** 2).mean(
                -1
            ) / bandwidth
            if self.c.get("similarity", "rbf") == "matern":
                radius = (5 * distance.clamp_min(1e-12)).sqrt()
                return (1 + radius + 5 * distance / 3) * torch.exp(-radius)
            return torch.exp(-distance)

        geometry = centered_geometry(
            sim(anchors, anchors),
            sim(query, anchors),
            valid,
            self.log_ridge.exp().clamp(0.001, 5),
        )
        residual = (geometry["projection"] @ raw_residual[..., None]).squeeze(-1)
        matrix, cross = (geometry["matrix"], geometry["cross"])
        bound = matrix.abs().sum(-1).amax(-1).clamp_min(1)
        alpha = torch.zeros_like(residual)
        for step in self.step_logits:
            alpha = alpha + 1.8 * step.sigmoid() / bound[:, None] * (
                residual - (matrix @ alpha[..., None]).squeeze(-1)
            )
        correction = (cross @ alpha[..., None]).squeeze(-1)
        local_residual = residual[:, 1:] * mask
        z = self.base.context(torch.cat([b["local"], b["local_values"][..., None]], -1))
        pooled = (z * mask[..., None]).sum(1) / n.clamp_min(1)[:, None]
        avg = local_residual.sum(-1) / n.clamp_min(1)
        second = local_residual.square().sum(-1) / n.clamp_min(1)
        stats = torch.stack([torch.log1p(n), avg, second], -1)
        distance = self.distance(b["query"], b["local"])
        weights = (-distance / 0.3).masked_fill(
            ~b["local_valid"][:, None, :], -1000000000.0
        )
        weights = torch.cat([torch.zeros_like(weights[..., :1]), weights], -1).softmax(
            -1
        )[..., 1:]
        near = (distance + 1000000.0 * (1 - mask[:, None, :])).amin(-1).clamp(max=100)
        extras = torch.stack(
            [
                correction,
                (weights * local_residual[:, None]).sum(-1),
                weights.sum(-1),
                near,
                cross.square().sum(-1) / (n[:, None] + 1),
            ],
            -1,
        )
        count = q.shape[1]
        features = torch.cat(
            [
                q,
                pooled[:, None].expand(-1, count, -1),
                stats[:, None].expand(-1, count, -1),
                extras,
            ],
            -1,
        )
        v = self.output(features)
        baseline = query_prior + observed_mean[:, None]
        mean = (
            baseline
            + 2 * torch.sigmoid(v[..., 0]) * correction
            + v[..., 1] * (n[:, None] > 0)
        )
        kernel_variance = conditional_variance(matrix, cross, geometry["diagonal"])
        gamma = functional.softplus(v[..., 3]) + 1e-06
        extra_variance = functional.softplus(v[..., 2]) + 0.0001
        df = None
        if self.c["likelihood"] == "student":
            df = (2.1 + functional.softplus(self.log_df)).expand_as(mean)
            extra_variance = extra_variance * df / (df - 2)
        variance = gamma * kernel_variance + extra_variance
        scale_squared = variance if df is None else variance * (df - 2) / df
        out = dict(mu=mean, scale=scale_squared.sqrt())
        if df is not None:
            out["df"] = df
        if diagnostics:
            out.update(
                baseline_mean=baseline,
                kernel_variance=kernel_variance,
                gamma=gamma,
                extra_variance=extra_variance,
                variance=variance,
                correction=correction,
                centered_residual=residual,
                alpha=alpha,
            )
        return out


class reference_model(conditional_model):
    """Current endpoint-specific ensemble member, without a learned actor."""

    def __init__(self, configuration, endpoint):
        super().__init__()
        self.c = configuration
        config = dict(
            family="residual_graph",
            input_dim=32,
            width=64,
            graph_steps=24,
            average_mean=True,
            similarity="rbf",
            temperature=0.3,
            likelihood=(
                "normal"
                if endpoint in ("microsomal_clearance", "in_vivo_clearance")
                else "student"
            ),
        )
        self.model = centered_kernel_model(config)

    def predict(self, context, query):
        reference = context.x[0]
        origin = context.y[0]
        dimension = query.shape[-1]
        row = dict(
            query=torch.cat([query, reference.expand(len(query), dimension)], -1)
            .detach()
            .numpy(),
            local=torch.cat(
                [context.x[1:], reference.expand(len(context.x) - 1, dimension)], -1
            )
            .detach()
            .numpy(),
            local_values=(context.y[1:] - origin).detach().numpy(),
        )
        output = self.model(collate([row]))
        return predictive_distribution(
            output["mu"] + origin, output["scale"], output.get("df")
        )
