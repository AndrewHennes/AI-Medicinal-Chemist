"""Stable Gaussian moment expected improvement for minimization."""

import numpy as np
from scipy.special import log_ndtr


def log_ei(mean, sd, best):
    """Log expected improvement for a minimization objective, including far tails."""
    sd = np.maximum(np.asarray(sd, float), 1e-12)
    z = (best - np.asarray(mean, float)) / sd
    lp = -0.5 * z * z - 0.5 * np.log(2 * np.pi)
    lc = log_ndtr(z)
    out = np.empty_like(z)
    positive = z >= 0
    out[positive] = np.logaddexp(
        np.log(np.maximum(z[positive], 1e-300)) + lc[positive], lp[positive]
    )
    negative = ~positive
    a = np.minimum(np.log(-z[negative]) + lc[negative] - lp[negative], -1e-14)
    out[negative] = lp[negative] + np.log(-np.expm1(a))
    extreme = z < -10000.0
    out[extreme] = lp[extreme] - 2 * np.log(-z[extreme])
    return np.log(sd) + out
