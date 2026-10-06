"""Optional off-policy GP pair supervision with compound-proportional sampling."""

import math
import numpy as np
import torch


def sample_pairs(data, rng, count):
    sizes = np.array([len(pool["y"]) for pool in data.training], dtype=float)
    if not len(sizes) or np.any(sizes < 2) or count < 1:
        raise ValueError(
            "Pair supervision requires a positive batch and pools of at least two molecules"
        )
    pairs = []
    for index in rng.choice(len(sizes), count, p=sizes / sizes.sum()):
        pool = data.training[index]
        first, second = map(int, rng.choice(len(pool["y"]), 2, replace=False))
        pairs.append((pool, first, second))
    return pairs


def pair_loss(model, data, rng, count):
    if model.c["method"] != "neural_mean_gp":
        raise ValueError("Pair supervision is implemented for neural_mean_gp")
    losses = []
    noise = model.hyperparameters(model.phi)[2]
    for pool, first, second in sample_pairs(data, rng, count):
        coordinates = torch.tensor(
            data.x[pool["indices"][[first, second]]], dtype=torch.float32
        )
        means = model.mean_net(coordinates)[:, 0].double()
        embeddings = model.adapter(coordinates).double()
        covariance = model.kernel(embeddings, embeddings, model.phi)
        variance = (
            covariance[0, 0] + covariance[1, 1] - 2 * covariance[0, 1] + 2 * noise
        )
        residual = float(pool["y"][second] - pool["y"][first]) - (means[1] - means[0])
        losses.append(
            0.5
            * (residual.square() / variance + variance.log() + math.log(2 * math.pi))
        )
    return torch.stack(losses).mean()
