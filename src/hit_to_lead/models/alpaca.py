"""Benchmark implementations of ALPaCA."""

import torch
from torch import nn
from torch.nn import functional
from .base import conditional_model, mlp
from .posterior import flat_offset_posterior, fixed_offset_posterior


class alpaca_model(conditional_model):
    """Learned nonlinear basis and full Gaussian linear-head prior.

    Evaluated in the equivalent function-space covariance algebra; observation
    noise is learned (an extension) and a flat series intercept is marginalized.
    """

    def __init__(self, c):
        super().__init__()
        self.c = c
        d = c["feature_dim"]
        self.basis = mlp(c["input_dim"], c["width"], d, c["depth"])
        self.prior_mean = nn.Parameter(torch.zeros(d))
        self.raw_chol = nn.Parameter(torch.zeros(d, d))
        self.raw_noise = nn.Parameter(torch.tensor(-2.25))

    def prior_chol(self):
        return self.raw_chol.tril(-1) + torch.diag(
            functional.softplus(self.raw_chol.diagonal()) + 0.01
        )

    def predict(self, context, query):
        hc = self.basis(context.x).double()
        hq = self.basis(query).double()
        chol = self.prior_chol().double()
        fc = hc @ chol
        fq = hq @ chol
        return flat_offset_posterior(
            hc @ self.prior_mean.double(),
            hq @ self.prior_mean.double(),
            fc @ fc.T,
            fq @ fc.T,
            fq.square().sum(-1),
            functional.softplus(self.raw_noise.double()) + 0.0001,
            context.y.double(),
        )


class alpaca_no_offset_model(alpaca_model):

    def predict(self, context, query):
        hc = self.basis(context.x).double()
        hq = self.basis(query).double()
        chol = self.prior_chol().double()
        fc, fq = (hc @ chol, hq @ chol)
        return fixed_offset_posterior(
            hc @ self.prior_mean.double(),
            hq @ self.prior_mean.double(),
            fc @ fc.T,
            fq @ fc.T,
            fq.square().sum(-1),
            functional.softplus(self.raw_noise.double()) + 0.0001,
            context.y.double(),
        )
