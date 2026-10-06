"""Pointwise acquisition scores with an independent, detached-feature critic."""

import numpy as np
import torch
from torch import nn


def mlp(input_size, width, output_size, depth=1, dropout=0.0):
    layers = []
    for _ in range(depth):
        layers.extend([nn.Linear(input_size, width), nn.GELU(), nn.Dropout(dropout)])
        input_size = width
    return nn.Sequential(*layers, nn.Linear(input_size, output_size))


class acquisition_policy(nn.Module):
    """The historical GP-only actor, with optional projected baseline features.

    scalar[:, :, 0] is predicted utility, the negative minimization objective.
    All inputs come from measured context and candidate structures. The critic
    cannot update the actor encoder, so a critic step preserves a TRPO step.
    """

    def __init__(self, config):
        super().__init__()
        self.c = dict(config)
        width = config.get("width", 64)
        extra = config.get("latent_dimension", 0)
        self.projection = (
            nn.Sequential(
                nn.LayerNorm(config["latent_input_size"]),
                nn.Linear(config["latent_input_size"], extra),
                nn.Tanh(),
            )
            if extra
            else None
        )
        self.scalar = mlp(config.get("feature_count", 2) + extra, width, width)
        self.acquisition = mlp(width, width, 1, config.get("decoder_depth", 2))
        self.critic = mlp(width + 2, width, 1, 2)
        self.log_temperature = nn.Parameter(
            torch.tensor(np.log(2.0), dtype=torch.float32)
        )
        # Match the earlier GP-mean initialization. Extra features learn through
        # the residual actor; no EI-imitation stage is required.
        nn.init.zeros_(self.acquisition[-1].weight)
        nn.init.zeros_(self.acquisition[-1].bias)

    def forward(self, batch):
        scalar = batch["scalar"]
        features = (
            scalar
            if self.projection is None
            else torch.cat([scalar, self.projection(batch["latent"])], -1)
        )
        encoded = self.scalar(features)
        scores = self.log_temperature.clamp(-2, 3).exp() * scalar[:, :, 0]
        scores = scores + self.acquisition(encoded).squeeze(-1)
        available = batch["available"]
        scores = scores.masked_fill(~available, -1e9)
        remaining = available.sum(1).clamp_min(1)
        pooled = (encoded.detach() * available[:, :, None]).sum(1) / remaining[:, None]
        counts = torch.stack(
            [remaining.float().log(), batch["context_valid"].sum(1).float().log()], 1
        )
        value = -(remaining.float() + 1) * torch.sigmoid(
            self.critic(torch.cat([pooled, counts], 1)).squeeze(-1)
        )
        return scores, value


def collate(states):
    if not states:
        raise ValueError("Cannot collate an empty acquisition batch")
    size = max(len(state["scalar"]) for state in states)
    context_size = max(state["context_size"] for state in states)
    scalar = np.zeros((len(states), size, states[0]["scalar"].shape[1]), np.float32)
    available = np.zeros((len(states), size), bool)
    context_valid = np.zeros((len(states), context_size), bool)
    latent_size = states[0].get("latent", np.zeros((1, 0))).shape[1]
    latent = np.zeros((len(states), size, latent_size), np.float32)
    for index, state in enumerate(states):
        count = len(state["scalar"])
        if not count:
            raise ValueError("Terminal states cannot be passed to the actor")
        scalar[index, :count] = state["scalar"]
        available[index, :count] = True
        context_valid[index, : state["context_size"]] = True
        if latent_size:
            latent[index, :count] = state["latent"]
    return {
        name: torch.from_numpy(array)
        for name, array in dict(
            scalar=scalar,
            available=available,
            context_valid=context_valid,
            latent=latent,
        ).items()
    }
