"""Prediction and K=1 acquisition on a new measured context.

Inputs are 512-dimensional MiniMol vectors and already transformed objective
values, all oriented to minimize. These APIs never accept unmeasured labels.
The audited implementations run on CPU. Model tensors and preprocessing must
come from the same endpoint/fold; unrelated preprocessing is not interchangeable.
"""

from dataclasses import dataclass
from pathlib import Path as path_type
import numpy as np
import torch
from .acquisition import log_ei
from .distributions import measured_context, predictive_distribution, mixture
from .training import load


@dataclass
class posterior_summary:
    """Marginals in transformed assay units, relative to the supplied first hit."""

    mean: np.ndarray
    standard_deviation: np.ndarray
    lower90: np.ndarray
    upper90: np.ndarray


class predictor:
    """Frozen ensemble with analytic or amortized local adaptation."""

    def __init__(self, checkpoints, features_file, outcome_scale, configuration=None):
        paths = [path_type(path) for path in checkpoints]
        if not paths or any(not path.is_absolute() for path in paths):
            raise ValueError("Supply at least one absolute checkpoint path")
        features_file = path_type(features_file)
        if not features_file.is_absolute():
            raise ValueError("features_file must be absolute")
        self.models = [load(path, configuration) for path in paths]
        if not np.isfinite(outcome_scale) or outcome_scale <= 0:
            raise ValueError("outcome_scale must be positive and training-derived")
        self.outcome_scale = float(outcome_scale)
        with np.load(features_file) as arrays:
            self.center = arrays["center"].copy()
            self.components = arrays["components"][:, :32].copy()
            self.feature_scale = np.sqrt(max(arrays["eigenvalues"][:32].mean(), 1e-8))

    def project(self, embeddings):
        vectors = np.asarray(embeddings, dtype=float)
        if (
            vectors.ndim != 2
            or vectors.shape[1] != 512
            or not np.isfinite(vectors).all()
        ):
            raise ValueError("Expected a finite [molecules, 512] MiniMol array")
        return torch.tensor(
            (vectors - self.center) @ self.components / self.feature_scale,
            dtype=torch.float32,
        )

    def distribution(self, measured_embeddings, measured_objectives, query_embeddings):
        measured = self.project(measured_embeddings)
        query = self.project(query_embeddings)
        values = np.asarray(measured_objectives, dtype=float)
        if (
            values.shape != (len(measured),)
            or not len(values)
            or not np.isfinite(values).all()
        ):
            raise ValueError(
                "Provide one finite transformed objective per measured molecule"
            )
        if len(query) == 0:
            raise ValueError("Provide at least one unmeasured query")
        context = measured_context(
            measured,
            torch.tensor(
                (values - values[0]) / self.outcome_scale, dtype=torch.float32
            ),
        )
        with torch.no_grad():
            standardized = mixture(
                [model.predict(context, query).detached() for model in self.models]
            )
        return predictive_distribution(
            standardized.loc * self.outcome_scale,
            standardized.scale * self.outcome_scale,
            standardized.df,
        )

    def predict(self, measured_embeddings, measured_objectives, query_embeddings):
        distribution = self.distribution(
            measured_embeddings, measured_objectives, query_embeddings
        )
        mean, variance = distribution.moments()
        lower, upper = distribution.interval(0.9)
        return posterior_summary(mean.numpy(), variance.sqrt().numpy(), lower, upper)

    def select_next(self, measured_embeddings, measured_objectives, query_embeddings):
        """Return the row index and log-EI scores over the supplied unmeasured pool."""
        posterior = self.predict(
            measured_embeddings, measured_objectives, query_embeddings
        )
        values = np.asarray(measured_objectives, dtype=float)
        scores = log_ei(
            posterior.mean, posterior.standard_deviation, values.min() - values[0]
        )
        return int(np.argmax(scores)), scores
