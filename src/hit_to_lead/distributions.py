"""Gaussian/Student predictive mixtures and interval computations."""

import math
import numpy as np
from dataclasses import dataclass
import torch


@dataclass
class measured_context:
    x: torch.Tensor
    y: torch.Tensor

    def __post_init__(self):
        if self.x.ndim != 2 or self.y.shape != (len(self.x),) or len(self.x) < 1:
            raise ValueError(
                "Context needs [n, d] features and [n] outcomes, with n >= 1"
            )


@dataclass
class prediction_episode:
    context: measured_context
    query: torch.Tensor
    target: torch.Tensor
    meta: dict


@dataclass
class predictive_distribution:
    loc: torch.Tensor
    scale: torch.Tensor
    df: torch.Tensor | None = None

    def __post_init__(self):
        assert self.loc.ndim == 2 and self.scale.shape == self.loc.shape
        if self.df is not None:
            assert self.df.shape == self.loc.shape

    @classmethod
    def normal(cls, mean, variance):
        return cls(mean[None], variance.clamp_min(1e-10).sqrt()[None])

    def log_prob(self, y):
        normal = torch.distributions.Normal(self.loc, self.scale)
        if self.df is None:
            lp = normal.log_prob(y)
        else:
            finite = torch.isfinite(self.df)
            student = torch.distributions.StudentT(
                torch.where(finite, self.df, 4.0), self.loc, self.scale
            )
            lp = torch.where(finite, student.log_prob(y), normal.log_prob(y))
        return torch.logsumexp(lp, dim=0) - math.log(len(self.loc))

    def moments(self):
        var = self.scale.square()
        if self.df is not None:
            finite = torch.isfinite(self.df)
            df = torch.where(finite, self.df, 4.0)
            var = torch.where(finite, var * df / (df - 2), var)
        mean = self.loc.mean(0)
        return (mean, var.mean(0) + self.loc.var(0, unbiased=False))

    def detached(self):
        return predictive_distribution(
            self.loc.detach(),
            self.scale.detach(),
            None if self.df is None else self.df.detach(),
        )

    def interval(self, mass=0.9):
        from scipy.stats import norm, t

        loc = self.loc.detach().numpy()
        scale = self.scale.detach().numpy()
        df = None if self.df is None else self.df.detach().numpy()

        def cdf(v):
            z = (v - loc) / scale
            return (
                norm.cdf(z)
                if df is None
                else np.where(np.isfinite(df), t.cdf(z, df), norm.cdf(z))
            ).mean(0)

        def quantile(p):
            lo = np.min(loc - 100 * scale, axis=0)
            hi = np.max(loc + 100 * scale, axis=0)
            for _ in range(20):
                width = hi - lo
                lo = np.where(cdf(lo) > p, lo - width, lo)
                hi = np.where(cdf(hi) < p, hi + width, hi)
            for _ in range(60):
                mid = (lo + hi) / 2
                below = cdf(mid) < p
                lo = np.where(below, mid, lo)
                hi = np.where(below, hi, mid)
            return (lo + hi) / 2

        return (quantile((1 - mass) / 2), quantile((1 + mass) / 2))


def mixture(predictions):
    assert len({len(p.loc) for p in predictions}) == 1
    df = None
    if any((p.df is not None for p in predictions)):
        df = torch.cat(
            [
                p.df if p.df is not None else torch.full_like(p.loc, torch.inf)
                for p in predictions
            ]
        )
    return predictive_distribution(
        torch.cat([p.loc for p in predictions]),
        torch.cat([p.scale for p in predictions]),
        df,
    )
