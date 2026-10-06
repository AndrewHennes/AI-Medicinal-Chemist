"""Archived mean, reference-kernel, and softmax-weighting ablations.

The numerical forward maps are preserved from the completed scratch comparison.
The common benchmark runner supplies the current audited episode protocol.
"""

import torch
from torch.nn import functional
from .reference import centered_kernel_model, reference_model, conditional_variance
from .base import conditional_model


class initial_reference_kernel_model(centered_kernel_model):

    def forward(self, b, diagnostics=False):
        q = self.base.pair(b["query"])
        encoded_local = self.base.pair(b["local"])
        mask = b["local_valid"].float()
        n = mask.sum(1)
        prior = self.base.prior(q).squeeze(-1)
        local_prior = self.base.prior(encoded_local).squeeze(-1)
        residual = (b["local_values"] - local_prior) * mask
        z = self.base.context(torch.cat([b["local"], b["local_values"][..., None]], -1))
        pooled = (z * mask[..., None]).sum(1) / n.clamp_min(1)[:, None]
        avg = (residual * mask).sum(1) / n.clamp_min(1)
        second = (residual.square() * mask).sum(1) / n.clamp_min(1)
        stats = torch.stack([torch.log1p(n), avg, second], -1)
        distance = self.distance(b["query"], b["local"])
        ref = b["query"][:, :1, self.d :]
        local = b["local"][..., : self.d]
        query = b["query"][..., : self.d]
        scale = self.base.log_metric_scale.exp().clamp(0.05, 20)
        bandwidth = self.log_bandwidth.exp().clamp(0.02, 100)

        def sim(a, b):
            dist = (((a[:, :, None] - b[:, None, :]) / scale) ** 2).mean(-1) / bandwidth
            if self.c.get("similarity", "rbf") == "matern":
                radius = (5 * dist.clamp_min(1e-12)).sqrt()
                return (1 + radius + 5 * dist / 3) * torch.exp(-radius)
            return torch.exp(-dist)

        ll, qr, lr = (sim(local, local), sim(query, ref), sim(local, ref))
        gram = (ll - lr - lr.transpose(1, 2) + 1) * mask[:, :, None] * mask[:, None, :]
        cross = (sim(query, local) - qr - lr.transpose(1, 2) + 1) * mask[:, None, :]
        ridge = self.log_ridge.exp().clamp(0.001, 5)
        matrix = gram + torch.diag_embed(mask * ridge + (1 - mask))
        bound = matrix.abs().sum(-1).amax(-1).clamp_min(1.0)
        alpha = torch.zeros_like(residual)
        for step in self.step_logits:
            alpha = alpha + 1.8 * step.sigmoid() / bound[:, None] * (
                residual - (matrix @ alpha[..., None]).squeeze(-1)
            )
        correction = (cross @ alpha[..., None]).squeeze(-1)
        weights = (-distance / 0.3).masked_fill(
            ~b["local_valid"][:, None, :], -1000000000.0
        )
        weights = torch.cat([torch.zeros_like(weights[..., :1]), weights], -1).softmax(
            -1
        )[..., 1:]
        near = (distance + 1000000.0 * (1 - mask[:, None, :])).amin(-1).clamp(max=100)
        extras = torch.stack(
            [
                correction,
                (weights * residual[:, None]).sum(-1),
                weights.sum(-1),
                near,
                cross.square().sum(-1) / (n[:, None] + 1),
            ],
            -1,
        )
        count = q.shape[1]
        features = torch.cat(
            [
                q,
                pooled[:, None].expand(-1, count, -1),
                stats[:, None].expand(-1, count, -1),
                extras,
            ],
            -1,
        )
        v = self.output(features)
        mean = (
            prior
            + 2 * torch.sigmoid(v[..., 0]) * correction
            + v[..., 1] * (n[:, None] > 0)
        )
        kernel_variance = conditional_variance(matrix, cross, 2 - 2 * qr.squeeze(-1))
        gamma = functional.softplus(v[..., 3]) + 1e-06
        extra_variance = functional.softplus(v[..., 2]) + 0.0001
        df = None
        if self.c["likelihood"] == "student":
            df = (2.1 + functional.softplus(self.log_df)).expand_as(mean)
            extra_variance = extra_variance * df / (df - 2)
        variance = gamma * kernel_variance + extra_variance
        scale_squared = variance if df is None else variance * (df - 2) / df
        out = dict(mu=mean, scale=scale_squared.sqrt())
        if df is not None:
            out["df"] = df
        if diagnostics:
            out.update(
                kernel_variance=kernel_variance,
                gamma=gamma,
                extra_variance=extra_variance,
                variance=variance,
                kernel_fraction=gamma * kernel_variance / variance,
            )
        return out


class averaged_reference_model(initial_reference_kernel_model):

    def averaged_prior(self, b):
        original = self.base.prior(self.base.pair(b["query"])).squeeze(-1)
        query = b["query"][..., : self.d]
        anchors = b["local"][..., : self.d]
        valid = b["local_valid"]
        anchors = torch.where(valid[..., None], anchors, torch.zeros_like(anchors))
        offsets = torch.where(
            valid, b["local_values"], torch.zeros_like(b["local_values"])
        )
        batch_count, query_count, embedding_width = query.shape
        context_capacity = anchors.shape[1]
        pair = torch.cat(
            [
                query[:, :, None, :].expand(
                    batch_count, query_count, context_capacity, embedding_width
                ),
                anchors[:, None, :, :].expand(
                    batch_count, query_count, context_capacity, embedding_width
                ),
            ],
            -1,
        )
        deltas = self.base.prior(self.base.pair(pair)).squeeze(-1)
        estimates = torch.where(
            valid[:, None, :], deltas + offsets[:, None, :], torch.zeros_like(deltas)
        )
        average = (original + estimates.sum(-1)) / (1 + valid.sum(-1))[:, None]
        return (average, original)


class average_mean_model(averaged_reference_model):

    def local_averaged_prior(self, b):
        """Predict each measured item using the initial hit and the other items.

        The item's own measured value is excluded from its baseline.
        """
        original = self.base.prior(self.base.pair(b["local"])).squeeze(-1)
        valid = b["local_valid"]
        x = torch.where(
            valid[..., None],
            b["local"][..., : self.d],
            torch.zeros_like(b["local"][..., : self.d]),
        )
        values = torch.where(
            valid, b["local_values"], torch.zeros_like(b["local_values"])
        )
        batch_count, context_capacity, embedding_width = x.shape
        pair = torch.cat(
            [
                x[:, :, None, :].expand(
                    batch_count, context_capacity, context_capacity, embedding_width
                ),
                x[:, None, :, :].expand(
                    batch_count, context_capacity, context_capacity, embedding_width
                ),
            ],
            -1,
        )
        predicted = self.base.prior(self.base.pair(pair)).squeeze(-1)
        eligible = (
            valid[:, None, :]
            & ~torch.eye(context_capacity, dtype=torch.bool, device=x.device)[None]
        )
        votes = torch.where(
            eligible, predicted + values[:, None, :], torch.zeros_like(predicted)
        )
        return (original + votes.sum(-1)) / (1 + eligible.sum(-1))

    def forward(self, b, diagnostics=False):
        q = self.base.pair(b["query"])
        mask = b["local_valid"].float()
        n = mask.sum(1)
        prior, first_hit_prior = self.averaged_prior(b)
        local_prior = self.local_averaged_prior(b)
        residual = (b["local_values"] - local_prior) * mask
        z = self.base.context(torch.cat([b["local"], b["local_values"][..., None]], -1))
        pooled = (z * mask[..., None]).sum(1) / n.clamp_min(1)[:, None]
        avg = (residual * mask).sum(1) / n.clamp_min(1)
        second = (residual.square() * mask).sum(1) / n.clamp_min(1)
        stats = torch.stack([torch.log1p(n), avg, second], -1)
        distance = self.distance(b["query"], b["local"])
        ref = b["query"][:, :1, self.d :]
        local = b["local"][..., : self.d]
        query = b["query"][..., : self.d]
        scale = self.base.log_metric_scale.exp().clamp(0.05, 20)
        bandwidth = self.log_bandwidth.exp().clamp(0.02, 100)

        def sim(a, b):
            dist = (((a[:, :, None] - b[:, None, :]) / scale) ** 2).mean(-1) / bandwidth
            if self.c.get("similarity", "rbf") == "matern":
                radius = (5 * dist.clamp_min(1e-12)).sqrt()
                return (1 + radius + 5 * dist / 3) * torch.exp(-radius)
            return torch.exp(-dist)

        ll, qr, lr = (sim(local, local), sim(query, ref), sim(local, ref))
        gram = (ll - lr - lr.transpose(1, 2) + 1) * mask[:, :, None] * mask[:, None, :]
        cross = (sim(query, local) - qr - lr.transpose(1, 2) + 1) * mask[:, None, :]
        ridge = self.log_ridge.exp().clamp(0.001, 5)
        matrix = gram + torch.diag_embed(mask * ridge + (1 - mask))
        bound = matrix.abs().sum(-1).amax(-1).clamp_min(1.0)
        alpha = torch.zeros_like(residual)
        for step in self.step_logits:
            alpha = alpha + 1.8 * step.sigmoid() / bound[:, None] * (
                residual - (matrix @ alpha[..., None]).squeeze(-1)
            )
        correction = (cross @ alpha[..., None]).squeeze(-1)
        weights = (-distance / 0.3).masked_fill(
            ~b["local_valid"][:, None, :], -1000000000.0
        )
        weights = torch.cat([torch.zeros_like(weights[..., :1]), weights], -1).softmax(
            -1
        )[..., 1:]
        near = (distance + 1000000.0 * (1 - mask[:, None, :])).amin(-1).clamp(max=100)
        extras = torch.stack(
            [
                correction,
                (weights * residual[:, None]).sum(-1),
                weights.sum(-1),
                near,
                cross.square().sum(-1) / (n[:, None] + 1),
            ],
            -1,
        )
        count = q.shape[1]
        features = torch.cat(
            [
                q,
                pooled[:, None].expand(-1, count, -1),
                stats[:, None].expand(-1, count, -1),
                extras,
            ],
            -1,
        )
        v = self.output(features)
        mean = (
            prior
            + 2 * torch.sigmoid(v[..., 0]) * correction
            + v[..., 1] * (n[:, None] > 0)
        )
        kernel_variance = conditional_variance(matrix, cross, 2 - 2 * qr.squeeze(-1))
        gamma = functional.softplus(v[..., 3]) + 1e-06
        extra_variance = functional.softplus(v[..., 2]) + 0.0001
        df = None
        if self.c["likelihood"] == "student":
            df = (2.1 + functional.softplus(self.log_df)).expand_as(mean)
            extra_variance = extra_variance * df / (df - 2)
        variance = gamma * kernel_variance + extra_variance
        scale_squared = variance if df is None else variance * (df - 2) / df
        out = dict(mu=mean, scale=scale_squared.sqrt())
        if df is not None:
            out["df"] = df
        if diagnostics:
            out.update(
                baseline_mean=prior,
                first_hit_baseline_mean=first_hit_prior,
                correction_to_baseline=mean - prior,
                kernel_variance=kernel_variance,
                gamma=gamma,
                extra_variance=extra_variance,
                variance=variance,
                kernel_fraction=gamma * kernel_variance / variance,
            )
        return out


class weighted_reference_model(centered_kernel_model):

    def anchor_weights(self, query, anchors, eligible):
        """Compute softmax(RBF / temperature)."""
        scale = self.base.log_metric_scale.exp().clamp(0.05, 20)
        bandwidth = self.log_bandwidth.exp().clamp(0.02, 100)
        distance = (((query[:, :, None] - anchors[:, None]) / scale) ** 2).mean(
            -1
        ) / bandwidth
        logits = torch.exp(-distance) / self.c["weight_temperature"]
        logits = logits.masked_fill(~eligible, -1000000000.0)
        weights = torch.softmax(logits, -1) * eligible
        return weights / weights.sum(-1, keepdim=True).clamp_min(1e-20)

    def raw_baselines(self, b, anchors, valid):
        """Align weighted votes to the existing common-reference coordinates.

        q_raw = sum_j w_qj delta(q,j) + sum_j(w_qj - 1/n) z_j.
        i_raw uses off-diagonal weights with total mass (n-1)/n, replacing w_qj.
        A measured item's own outcome never enters its raw baseline. This is
        equivalent to scaled leave-one-out prediction errors after centering.
        Uniform weights exactly recover the current combined architecture.
        """
        batch_count, anchor_count, embedding_width = anchors.shape
        n = valid.sum(-1).float()
        query = b["query"][..., :embedding_width]
        query_count = query.shape[1]
        values = torch.cat(
            [torch.zeros_like(b["local_values"][:, :1]), b["local_values"]], -1
        )
        values = torch.where(valid, values, torch.zeros_like(values))
        eligible_q = valid[:, None, :].expand(batch_count, query_count, anchor_count)
        wq = self.anchor_weights(query, anchors, eligible_q)
        uniform_q = valid[:, None, :] / n[:, None, None]
        pairs = torch.cat(
            [
                query[:, :, None].expand(
                    batch_count, query_count, anchor_count, embedding_width
                ),
                anchors[:, None].expand(
                    batch_count, query_count, anchor_count, embedding_width
                ),
            ],
            -1,
        )
        dq = self.base.prior(self.base.pair(pairs)).squeeze(-1)
        query_prior = (wq * dq + (wq - uniform_q) * values[:, None]).sum(-1)
        eligible_c = (
            valid[:, :, None]
            & valid[:, None, :]
            & ~torch.eye(anchor_count, dtype=torch.bool, device=anchors.device)[None]
        )
        wc = (
            self.anchor_weights(anchors, anchors, eligible_c)
            * ((n - 1) / n)[:, None, None]
        )
        uniform_c = eligible_c / n[:, None, None]
        pairs = torch.cat(
            [
                anchors[:, :, None].expand(
                    batch_count, anchor_count, anchor_count, embedding_width
                ),
                anchors[:, None].expand(
                    batch_count, anchor_count, anchor_count, embedding_width
                ),
            ],
            -1,
        )
        dc = self.base.prior(self.base.pair(pairs)).squeeze(-1)
        anchor_prior = (wc * dc + (wc - uniform_c) * values[:, None]).sum(-1)
        return (query_prior, anchor_prior, wq, wc)

    def centered_baselines(self, b, anchors, valid):
        query_prior, anchor_prior, _, _ = self.raw_baselines(b, anchors, valid)
        offset = (anchor_prior * valid).sum(-1) / valid.sum(-1)
        return (query_prior - offset[:, None], (anchor_prior - offset[:, None]) * valid)


class reference_ablation_model(reference_model):
    """Select an archived forward map with the current conditional-prediction API."""

    def __init__(self, configuration, endpoint):
        conditional_model.__init__(self)
        self.c = configuration
        method = configuration["method"]
        config = dict(
            family="residual_graph",
            input_dim=32,
            width=64,
            graph_steps=24,
            average_mean=method != "reference_kernel_only",
            similarity="rbf",
            temperature=0.3,
            weight_temperature=configuration.get("weight_temperature", 0.3),
            likelihood=(
                "normal"
                if endpoint in ("microsomal_clearance", "in_vivo_clearance")
                else "student"
            ),
        )
        constructors = {
            "reference_unchanged": initial_reference_kernel_model,
            "reference_mean_only": average_mean_model,
            "reference_kernel_only": centered_kernel_model,
            "reference_weighted": weighted_reference_model,
        }
        self.model = constructors[method](config)
