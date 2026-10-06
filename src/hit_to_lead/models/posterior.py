"""Contrast likelihood and Gaussian conditioning with an unknown intercept."""

import math
import torch
from ..distributions import predictive_distribution


def helmert(n, dtype=torch.float64, device=None):
    """n x (n-1) orthonormal contrasts. No noisy anchor is treated as fixed truth."""
    h = torch.zeros(n, max(0, n - 1), dtype=dtype, device=device)
    for j in range(n - 1):
        v = math.sqrt((j + 1) * (j + 2))
        h[: j + 1, j] = 1 / v
        h[j + 1, j] = -(j + 1) / v
    return h


def contrast_nll(mean, covariance, y):
    """Restricted Gaussian evidence, integrating an arbitrary constant series offset."""
    n = len(y)
    if n == 1:
        return mean.sum() * 0 + covariance.sum() * 0
    h = helmert(n, mean.dtype, mean.device)
    residual = h.T @ (y - mean)
    matrix = h.T @ covariance @ h
    chol = torch.linalg.cholesky((matrix + matrix.T) / 2)
    return (
        0.5 * (residual @ torch.cholesky_solve(residual[:, None], chol)[:, 0])
        + chol.diagonal().log().sum()
        + 0.5 * (n - 1) * math.log(2 * math.pi)
    ) / (n - 1)


def flat_offset_posterior(mc, mq, kcc, kqc, kqq_diag, noise, y):
    """Universal kriging with a flat nuisance intercept and iid raw observation noise.

    A=Kcc+noise I; b_hat=(1'A^-1(y-mc))/(1'A^-1 1).
    Includes uncertainty in the unknown intercept and in the new observation.
    """
    n = len(y)
    one = torch.ones_like(y)
    a = kcc + noise * torch.eye(n, dtype=y.dtype, device=y.device)
    chol = torch.linalg.cholesky((a + a.T) / 2)
    ai_one = torch.cholesky_solve(one[:, None], chol)[:, 0]
    ai_res = torch.cholesky_solve((y - mc)[:, None], chol)[:, 0]
    precision = one @ ai_one
    offset = one @ ai_res / precision
    mean = mq + offset + kqc @ (ai_res - ai_one * offset)
    solved = torch.cholesky_solve(kqc.T, chol)
    variance = (
        kqq_diag
        + noise
        - (kqc * solved.T).sum(-1)
        + (1 - kqc @ ai_one).square() / precision
    )
    if not torch.isfinite(variance).all() or variance.min().detach() < -1e-07:
        raise FloatingPointError("Invalid predictive variance")
    return predictive_distribution.normal(mean, variance)


def fixed_offset_posterior(mc, mq, kcc, kqc, kqq_diag, noise, y):
    """Ordinary Gaussian conditioning with the additional offset fixed at zero."""
    a = kcc + noise * torch.eye(len(y), dtype=y.dtype, device=y.device)
    chol = torch.linalg.cholesky((a + a.T) / 2)
    alpha = torch.cholesky_solve((y - mc)[:, None], chol)[:, 0]
    mean = mq + kqc @ alpha
    solved = torch.cholesky_solve(kqc.T, chol)
    variance = kqq_diag + noise - (kqc * solved.T).sum(-1)
    if not torch.isfinite(variance).all() or variance.min().detach() < -1e-07:
        raise FloatingPointError("Invalid predictive variance")
    return predictive_distribution.normal(mean, variance)
