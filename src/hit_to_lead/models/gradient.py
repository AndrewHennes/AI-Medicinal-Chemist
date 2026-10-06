"""Benchmark implementations of PointNetwork, GradientModel."""

import torch
from torch import nn
from torch.nn import functional
from collections import OrderedDict as ordered_dict
from .base import conditional_model, mlp
from .posterior import contrast_nll
from ..distributions import predictive_distribution


class point_network(nn.Module):

    def __init__(self, c):
        super().__init__()
        self.body = mlp(c["input_dim"], c["width"], c["width"], c["depth"])
        self.head = nn.Linear(c["width"], 2)

    def forward(self, x):
        o = self.head(self.body(x))
        return (o[:, 0], functional.softplus(o[:, 1]) + 0.0001)


class gradient_model(conditional_model):
    """Transfer, ordinary fine-tuning, full second-order MAML, and ANIL.

    A pointwise mean/variance network is anchored by measured mean residual.
    Support updates use n-1 orthogonal contrasts, not n independent noisy deltas.
    """

    def __init__(self, c):
        super().__init__()
        self.c = c
        self.net = point_network(c)

    def call(self, x, params):
        return torch.func.functional_call(self.net, params, (x,))

    def support_loss(self, context, params):
        mean, var = self.call(context.x, params)
        return contrast_nll(mean.double(), torch.diag(var.double()), context.y.double())

    def adapted(self, context, meta=False):
        base = ordered_dict(self.net.named_parameters())
        if self.c["method"] == "transfer" or len(context.y) == 1:
            return base
        params = (
            base
            if meta
            else ordered_dict(
                ((k, v.detach().clone().requires_grad_(True)) for k, v in base.items())
            )
        )
        origin = ordered_dict(((k, v) for k, v in params.items()))
        keys = [
            k for k in params if self.c["method"] != "anil" or k.startswith("head.")
        ]
        with torch.enable_grad():
            for _ in range(self.c["inner_steps"]):
                loss = self.support_loss(context, params)
                penalty = sum(((params[k] - origin[k]).square().sum() for k in keys))
                loss = loss + self.c["inner_penalty"] * penalty / 2
                gradients = torch.autograd.grad(
                    loss, [params[k] for k in keys], create_graph=meta
                )
                updates = dict(zip(keys, gradients))
                params = ordered_dict(
                    (
                        (k, v - self.c["inner_lr"] * updates[k] if k in updates else v)
                        for k, v in params.items()
                    )
                )
        return params

    def predict(self, context, query, meta=False):
        params = self.adapted(context, meta)
        mc, vc = self.call(context.x, params)
        mq, vq = self.call(query, params)
        mean = mq + (context.y - mc).mean()
        return predictive_distribution.normal(mean, vq + vc.sum() / len(vc) ** 2)

    def loss(self, episode):
        if self.c["method"] == "finetune":
            raise RuntimeError(
                "Fine-tuning reuses a transfer checkpoint; do not meta-train this control."
            )
        return (
            -self.predict(
                episode.context,
                episode.query,
                meta=self.c["method"] in ("maml", "anil"),
            )
            .log_prob(episode.target)
            .mean()
        )
