"""Benchmark implementations of CNP, ANP, TNP."""

import torch
from torch import nn
from torch.nn import functional
from .base import conditional_model, mlp
from ..distributions import predictive_distribution


class cnp_model(conditional_model):

    def __init__(self, c):
        super().__init__()
        self.c = c
        d = c["input_dim"]
        w = c["width"]
        self.encoder = mlp(d + 1, w, w, c["depth"])
        self.decoder = mlp(d + w, w, 2, c["depth"])

    def predict(self, context, query):
        center = context.y.mean()
        y = context.y - center
        r = self.encoder(torch.cat([context.x, y[:, None]], -1)).mean(0)
        out = self.decoder(torch.cat([query, r.expand(len(query), -1)], -1))
        return predictive_distribution.normal(
            out[:, 0] + center, functional.softplus(out[:, 1]) + 0.0001
        )


class anp_model(conditional_model):
    """Attentive Neural Process with deterministic attention AND latent ELBO."""

    def __init__(self, c):
        super().__init__()
        self.c = c
        d = c["input_dim"]
        w = c["width"]
        z = c["latent_dim"]
        self.encoder = mlp(d + 1, w, w, c["depth"])
        self.x_encoder = mlp(d, w, w, 1)
        self.self_attention = nn.MultiheadAttention(w, c["heads"], batch_first=True)
        self.cross_attention = nn.MultiheadAttention(w, c["heads"], batch_first=True)
        self.latent_encoder = mlp(d + 1, w, w, c["depth"])
        self.latent_head = nn.Linear(w, 2 * z)
        self.decoder = mlp(d + w + z, w, 2, c["depth"])
        generator = torch.Generator().manual_seed(57493)
        half = (c["latent_samples"] + 1) // 2
        eps = torch.randn(half, z, generator=generator)
        self.register_buffer(
            "eval_epsilon", torch.cat([eps, -eps])[: c["latent_samples"]]
        )

    def latent(self, x, y):
        out = self.latent_head(
            self.latent_encoder(torch.cat([x, y[:, None]], -1)).mean(0)
        )
        mu, raw = out.chunk(2)
        return torch.distributions.Normal(mu, 0.05 + 0.95 * functional.softplus(raw))

    def representation(self, context, query, center):
        values = self.encoder(
            torch.cat([context.x, (context.y - center)[:, None]], -1)
        )[None]
        values = (
            values + self.self_attention(values, values, values, need_weights=False)[0]
        )
        keys = self.x_encoder(context.x)[None]
        q = self.x_encoder(query)[None]
        return self.cross_attention(q, keys, values, need_weights=False)[0][0]

    def decode(self, query, representation, z, center):
        s = len(z)
        n = len(query)
        out = self.decoder(
            torch.cat(
                [
                    query[None].expand(s, n, -1),
                    representation[None].expand(s, n, -1),
                    z[:, None].expand(s, n, -1),
                ],
                -1,
            )
        )
        return predictive_distribution(
            out[..., 0] + center, (functional.softplus(out[..., 1]) + 0.0001).sqrt()
        )

    def predict(self, context, query):
        center = context.y.mean()
        prior = self.latent(context.x, context.y - center)
        z = prior.loc + self.eval_epsilon * prior.scale
        return self.decode(
            query, self.representation(context, query, center), z, center
        )

    def loss(self, episode):
        context = episode.context
        query = episode.query
        center = context.y.mean()
        prior = self.latent(context.x, context.y - center)
        posterior = self.latent(
            torch.cat([context.x, query]),
            torch.cat([context.y, episode.target]) - center,
        )
        prediction = self.decode(
            query,
            self.representation(context, query, center),
            posterior.rsample((1,)),
            center,
        )
        kl = torch.distributions.kl_divergence(posterior, prior).sum()
        return -prediction.log_prob(episode.target).mean() + kl / len(query)


class tnp_model(conditional_model):
    """Deterministic masked Transformer Neural Process; no positional embeddings.

    Context rows and query rows may attend only to context columns. Query labels
    never enter tokens, and queries cannot influence other query predictions.
    """

    def __init__(self, c):
        super().__init__()
        self.c = c
        w = c["width"]
        d = c["input_dim"]
        self.embed = mlp(d + 2, w, w, 1)
        layer = nn.TransformerEncoderLayer(
            w,
            c["heads"],
            2 * w,
            c["dropout"],
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            layer, c["layers"], enable_nested_tensor=False
        )
        self.decoder = mlp(w, w, 2, 1)

    def predict(self, context, query):
        center = context.y.mean()
        n = len(context.y)
        q = len(query)
        measured = torch.cat(
            [
                context.x,
                (context.y - center)[:, None],
                torch.ones(n, 1, device=query.device),
            ],
            -1,
        )
        hidden = torch.cat([query, torch.zeros(q, 2, device=query.device)], -1)
        tokens = self.embed(torch.cat([measured, hidden]))[None]
        mask = torch.zeros(n + q, n + q, dtype=torch.bool, device=query.device)
        mask[:, n:] = True
        out = self.decoder(self.transformer(tokens, mask=mask)[0, n:])
        return predictive_distribution.normal(
            out[:, 0] + center, functional.softplus(out[:, 1]) + 0.0001
        )
