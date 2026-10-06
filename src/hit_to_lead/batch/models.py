"""Deep Sets, pair-aware attention, autoregressive batches and relaxed top-k."""

import math
import numpy as np
import torch
from torch import nn
from torch.nn import functional
from .search import collate_states, subset_search


def mlp(d, w, out, depth=2):
    layers = []
    for _ in range(depth - 1):
        layers.extend([nn.Linear(d, w), nn.SiLU()])
        d = w
    layers.append(nn.Linear(d, out))
    return nn.Sequential(*layers)


class pair_attention(nn.Module):
    """Self-attention with relation-dependent biases AND value messages."""

    def __init__(self, width, heads):
        super().__init__()
        self.heads = heads
        self.dim = width // heads
        self.qkv = nn.Linear(width, 3 * width)
        self.bias = mlp(3, 16, heads)
        self.message = mlp(3, 16, width)
        self.out = nn.Linear(width, width)
        self.norm1 = nn.LayerNorm(width)
        self.norm2 = nn.LayerNorm(width)
        self.ff = mlp(width, 2 * width, width)

    def forward(self, h, rel, valid):
        b, n, w = h.shape
        q, k, v = self.qkv(h).reshape(b, n, 3, self.heads, self.dim).unbind(2)
        scores = torch.einsum("bihd,bjhd->bhij", q, k) / math.sqrt(self.dim)
        scores = scores + self.bias(rel).permute(0, 3, 1, 2)
        weights = functional.softmax(
            scores.masked_fill(~valid[:, None, None, :], -1000000000.0), -1
        )
        message = self.message(rel).reshape(b, n, n, self.heads, self.dim)
        values = torch.einsum("bhij,bjhd->bihd", weights, v) + torch.einsum(
            "bhij,bijhd->bihd", weights, message
        )
        h = self.norm1(h + self.out(values.reshape(b, n, w)))
        return self.norm2(h + self.ff(h)) * valid[:, :, None]


class subset_scorer(nn.Module):

    def __init__(self, c):
        super().__init__()
        self.c = c
        w = c["width"]
        d = 2 * c["dimension"] + 6
        self.item = mlp(d, w, w)
        self.blocks = (
            nn.ModuleList([pair_attention(w, c["heads"]) for _ in range(c["depth"])])
            if c["family"] == "pair_transformer"
            else nn.ModuleList()
        )
        self.pool_query = nn.Parameter(torch.zeros(w))
        self.decoder = mlp(5 * w + 9, w, 2, depth=3)
        self.base = nn.Parameter(torch.tensor(1.0))

    def forward(self, b, indices, subset_valid):
        h = self.item(b["x"])
        count = b["valid"].sum(1).clamp_min(1)
        whole_mean = (h * b["valid"][:, :, None]).sum(1) / count[:, None]
        whole_max = h.masked_fill(~b["valid"][:, :, None], -1000000000.0).amax(1)
        rows = torch.arange(len(h))[:, None]
        s = h[rows, indices]
        rel = b["relations"][rows[:, :, None], indices[:, :, None], indices[:, None, :]]
        for block in self.blocks:
            s = block(s, rel, subset_valid)
        k = subset_valid.sum(1).clamp_min(1)
        mean = (s * subset_valid[:, :, None]).sum(1) / k[:, None]
        maximum = s.masked_fill(~subset_valid[:, :, None], -1000000000.0).amax(1)
        weights = functional.softmax(
            (s * self.pool_query).sum(-1).masked_fill(~subset_valid, -1000000000.0), 1
        )
        pooled = (weights[:, :, None] * s).sum(1)
        g = b["g"].clone()
        g[:, -2] = k / count
        g[:, -1] = torch.log1p(k.float())
        sizes = torch.stack([k.float().log(), k / count], 1)
        result = self.decoder(
            torch.cat([whole_mean, whole_max, mean, maximum, pooled, g, sizes], 1)
        )
        mu = b["x"][rows, indices, 2 * self.c["dimension"]]
        base = (
            torch.logsumexp(mu.masked_fill(~subset_valid, -1000000000.0), 1)
            - count.float().log()
        )
        return (result[:, 0] + self.base * base, result[:, 1])


class batch_policy(nn.Module):

    def __init__(self, c):
        super().__init__()
        self.c = c
        w = c["width"]
        d = 2 * c["dimension"] + 6
        self.item = mlp(d, w, w, depth=c["depth"] + 1)
        self.actor = mlp(3 * w + 11, w, 1)
        self.critic = mlp(2 * w + 8, w, 1)
        self.log_temperature = nn.Parameter(torch.tensor(0.0))
        nn.init.zeros_(self.actor[-1].weight)
        nn.init.zeros_(self.actor[-1].bias)

    def forward(self, b):
        h = self.item(b["x"])
        valid = b["valid"]
        pending = b["pending"]
        n = valid.sum(1).clamp_min(1)
        p = pending.sum(1)
        pool = (h * valid[:, :, None]).sum(1) / n[:, None]
        chosen = (h * pending[:, :, None]).sum(1) / p.clamp_min(1)[:, None]
        correlation = b["relations"][..., 0]
        corrmean = (correlation * pending[:, None, :]).sum(-1) / p.clamp_min(1)[:, None]
        corrmax = correlation.masked_fill(~pending[:, None, :], -1000000000.0).amax(-1)
        corrmax = torch.where((p > 0)[:, None], corrmax, torch.zeros_like(corrmax))
        requested_count = torch.expm1(b["g"][:, -1]).clamp_min(1)
        extra = torch.stack(
            [
                corrmean,
                corrmax,
                (p / requested_count)[:, None].expand_as(corrmean),
                ((requested_count - p) / requested_count)[:, None].expand_as(corrmean),
            ],
            -1,
        )
        inputs = torch.cat(
            [
                h,
                pool[:, None].expand_as(h),
                chosen[:, None].expand_as(h),
                b["g"][:, None].expand(-1, h.shape[1], -1),
                extra,
            ],
            -1,
        )
        scores = self.log_temperature.clamp(-2, 3).exp() * b["x"][
            :, :, 2 * self.c["dimension"]
        ] + self.actor(inputs).squeeze(-1)
        scores = scores.masked_fill(~valid | pending, -1000000000.0)
        value = -(torch.ceil(n / requested_count) + 1) * torch.sigmoid(
            self.critic(
                torch.cat(
                    [
                        pool.detach(),
                        chosen.detach(),
                        b["g"],
                        (p / requested_count)[:, None],
                    ],
                    1,
                )
            ).squeeze(-1)
        )
        return (scores, value)


def make_model(c):
    return (
        subset_scorer(c)
        if c["family"] in ["deep_sets", "pair_transformer"]
        else batch_policy(c)
    )


@torch.no_grad()
def score_subsets(model, state, sets):
    b = collate_states([state])
    outputs = []
    for start in range(0, len(sets), 128):
        part = sets[start : start + 128]
        n = len(part)
        k = max(map(len, part))
        idx = torch.zeros((n, k), dtype=torch.long)
        valid = torch.zeros((n, k), dtype=torch.bool)
        for i, s in enumerate(part):
            idx[i, : len(s)] = torch.tensor(s)
            valid[i, : len(s)] = True
        repeated = {key: value.expand(n, *value.shape[1:]) for key, value in b.items()}
        outputs.extend(model(repeated, idx, valid)[0].tolist())
    return np.asarray(outputs)


@torch.no_grad()
def select_neural(model, state, requested_count, search=None):
    model.eval()
    n = len(state["ids"])
    k = min(requested_count, n)
    if k == n:
        return (list(range(n)), dict(evaluations=0))
    family = model.c["family"]
    if family in ["deep_sets", "pair_transformer"]:
        config = dict(beam=4, swaps=1, lookahead=0)
        if search:
            config.update(search)
        return subset_search(
            lambda sets: score_subsets(model, state, sets),
            n,
            k,
            **config,
            rng=np.random.default_rng(921)
        )
    b = collate_states([state])
    selected = []
    if family == "gumbel":
        return (torch.topk(model(b)[0][0], k).indices.tolist(), dict(evaluations=1))
    for _ in range(k):
        score, _ = model(b)
        a = int(score[0].argmax())
        selected.append(a)
        b["pending"][0, a] = True
    return (selected, dict(evaluations=k))


def relaxed_slots(scores, requested_count, temperature):
    """Xie/Ermon-style iterative relaxed sampling; slots each sum to one."""
    uniform = torch.rand_like(scores).clamp(1e-06, 1 - 1e-06)
    logits = scores - torch.log(-torch.log(uniform))
    slots = []
    for _ in range(requested_count):
        probability = functional.softmax(logits / temperature, dim=-1)
        slots.append(probability)
        logits = logits + torch.log((1 - probability).clamp_min(1e-06))
    return torch.stack(slots, 1)
