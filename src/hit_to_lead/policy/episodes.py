"""Leakage-controlled predictor/policy roles and retrospective acquisition states."""

from collections import OrderedDict as ordered_dict
import hashlib
import json
import numpy as np
import torch
from scipy.special import ndtr
from ..acquisition import log_ei
from ..data import series_dataset
from ..distributions import measured_context, mixture
from ..evaluation import acquisition_counts, start_hit
from ..io import rng_for
from .network import collate


def assign_roles(data):
    """Balance pool and large-pool counts across disjoint linked-group roles."""
    groups = sorted({pool["group"] for pool in data.training})
    if len(groups) < 2:
        raise ValueError("At least two training groups are required for disjoint roles")
    counts = {
        group: np.array(
            [
                sum(pool["group"] == group for pool in data.training),
                sum(
                    pool["group"] == group and len(pool["y"]) >= 15
                    for pool in data.training
                ),
            ],
            float,
        )
        for group in groups
    }
    rng = rng_for("latent_roles", data.fold, data.endpoint)
    ties = {group: rng.random() for group in groups}
    target = np.maximum(np.sum(list(counts.values()), axis=0) / 2, 1)
    ordered = sorted(
        groups, key=lambda group: (-float(np.max(counts[group] / target)), ties[group])
    )
    loads = np.zeros((2, 2))
    roles = {}
    for group in ordered:
        scores = []
        for side in range(2):
            trial = loads.copy()
            trial[side] += counts[group]
            scores.append(((trial / target) ** 2).sum())
        side = int(np.argmin(scores))
        loads[side] += counts[group]
        roles[group] = ("predictor", "policy")[side]
    return roles


def role_data(fold, endpoint):
    data = series_dataset(fold, endpoint, include_test=True)
    roles = assign_roles(data)
    data.training = [
        pool for pool in data.training if roles[pool["group"]] == "predictor"
    ]
    data.policy_training = [
        pool for pool in data.pools if roles.get(pool["group"]) == "policy"
    ]
    data.large = [pool for pool in data.training if len(pool["y"]) >= 15]
    data.scale = float(
        max(
            0.05,
            np.sqrt(
                np.mean(
                    [
                        2
                        * np.var(pool["objective"])
                        * len(pool["objective"])
                        / (len(pool["objective"]) - 1)
                        for pool in data.training
                    ]
                )
            ),
        )
    )
    for pool in data.pools:
        pool["y"] = np.asarray(pool["objective"]) / data.scale
    data.training_role = "predictor_half_of_outer_training_groups"
    data.roles = roles
    data.roles_sha256 = hashlib.sha256(
        json.dumps(roles, sort_keys=True).encode()
    ).hexdigest()
    return data


class prediction_engine:
    """Frozen conditional predictors; cache entries contain measured-only features."""

    def __init__(self, data, models, feature_set="mean_sd", cache_limit=1024):
        self.data = data
        self.models = models
        self.feature_set = feature_set
        self.cache = ordered_dict()
        self.cache_limit = cache_limit
        for model in models:
            model.eval()
            model.requires_grad_(False)

    @torch.no_grad()
    def state(self, pool, observed):
        observed = (observed[0], *sorted(observed[1:]))
        key = (pool["pool_id"], observed)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        ids = np.array([i for i in range(len(pool["y"])) if i not in observed])
        if not len(ids):
            raise ValueError("No candidates remain")
        coordinates = torch.tensor(self.data.x[pool["indices"]], dtype=torch.float32)
        values = np.asarray(pool["y"])[list(observed)]
        relative = values - values[0]
        context = measured_context(
            coordinates[list(observed)], torch.tensor(relative, dtype=torch.float32)
        )
        query = coordinates[ids]
        predictions = mixture(
            [model.predict(context, query).detached() for model in self.models]
        )
        mean, variance = predictions.moments()
        utility = -mean.numpy()
        deviation = variance.sqrt().numpy()
        incumbent = float(-relative.min())
        features = [utility, deviation]
        if self.feature_set in ("mean_sd_best", "mean_sd_phi"):
            features.append(np.full(len(ids), incumbent))
        if self.feature_set == "mean_sd_phi":
            z = (utility - incumbent) / np.maximum(deviation, 1e-12)
            features.extend([ndtr(z), np.exp(-0.5 * z * z) / np.sqrt(2 * np.pi)])
        if self.feature_set == "mean_sd_ei":
            features.append(np.exp(log_ei(-utility, deviation, -incumbent)))
        latent = []
        for model in self.models:
            if hasattr(model, "model") and hasattr(model.model, "base"):
                count, width = len(context.x), query.shape[-1]
                pairs = torch.cat(
                    [
                        query[:, None].expand(-1, count, width),
                        context.x[None].expand(len(query), -1, -1),
                    ],
                    -1,
                )
                latent.append(model.model.base.pair(pairs).mean(1).numpy())
        state = dict(
            ids=ids,
            scalar=np.column_stack(features).astype(np.float32),
            latent=(
                np.concatenate(latent, -1)
                if latent
                else np.zeros((len(ids), 0), np.float32)
            ),
            context_size=len(observed),
            pool_id=pool["pool_id"],
            reference=int(observed[0]),
            log_ei=log_ei(-utility, deviation, -incumbent),
        )
        self.cache[key] = state
        if len(self.cache) > self.cache_limit:
            self.cache.popitem(last=False)
        return state


def starting_case(pools, rng):
    large = [pool for pool in pools if len(pool["y"]) >= 15]
    for _ in range(100):
        choices = large if large and rng.random() < 0.5 else pools
        pool = choices[int(rng.integers(len(choices)))]
        order = rng.permutation(len(pool["y"]))
        worst = order[np.argsort(-pool["y"][order], kind="stable")][
            : max(1, len(order) // 2)
        ]
        reference = int(rng.choice(worst))
        if pool["y"][reference] > np.min(pool["y"]):
            return pool, reference
    raise ValueError("No nonterminal starting context in the policy-training pools")


@torch.no_grad()
def trajectory(model, engine, pool, reference, rng=None, rule="policy"):
    observed = [reference]
    records = []
    order = []
    while np.min(pool["y"][observed]) > np.min(pool["y"]):
        state = engine.state(pool, observed)
        if rule == "direct_ei":
            action = int(np.argmax(state["log_ei"]))
            logp, value = 0.0, 0.0
        else:
            model.eval()
            scores, values = model(collate([state]))
            probabilities = torch.softmax(scores[0], -1).double().numpy()
            probabilities /= probabilities.sum()
            action = (
                int(np.argmax(probabilities))
                if rng is None
                else int(rng.choice(len(probabilities), p=probabilities))
            )
            logp = float(torch.log_softmax(scores[0], -1)[action])
            value = float(values[0])
        molecule = int(state["ids"][action])
        records.append((state, action, logp, value))
        order.append(molecule)
        observed.append(molecule)
    counts, random = acquisition_counts(pool["y"], reference, order)
    return records, dict(
        pool_id=pool["pool_id"],
        group=pool["group"],
        pool_size=len(pool["y"]),
        reference=reference,
        order=order,
        **{f"top{k}": counts[k - 1] for k in range(1, 5)},
        **{f"random_top{k}": random[k - 1] for k in range(1, 5)},
    )


def grouped_rollouts(model, engine, pools, rng, groups=2, group_size=4):
    result = []
    for _ in range(groups):
        pool, reference = starting_case(pools, rng)
        result.append(
            [
                trajectory(model, engine, pool, reference, rng)[0]
                for _ in range(group_size)
            ]
        )
    return result


def evaluate_policy(
    model, engine, subset="validation", draws=2, pool_limit=None, rule="policy"
):
    pools = [pool for pool in engine.data.pools if pool["subset"] == subset]
    if pool_limit and len(pools) > pool_limit:
        rng = rng_for(
            "policy_validation_subset", engine.data.fold, engine.data.endpoint
        )
        indices = rng.permutation(len(pools))[:pool_limit]
        pools = [pools[index] for index in indices]
    rows = []
    for pool in pools:
        for draw in range(draws):
            _, row = trajectory(model, engine, pool, start_hit(pool, draw), rule=rule)
            rows.append(dict(row, draw=draw))
    return rows


def validation_score(rows):
    if not rows:
        raise ValueError("Validation set is empty")
    all_score = np.mean([row["top1"] for row in rows])
    large = [row["top1"] for row in rows if row["pool_size"] >= 15]
    return float((all_score + np.mean(large)) / 2 if large else all_score)
