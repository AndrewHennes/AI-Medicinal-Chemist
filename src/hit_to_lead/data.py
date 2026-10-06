"""Audited fold data and deterministic context/query episode construction."""

import numpy as np
import torch
from .io import read, rng_for
from .distributions import measured_context, prediction_episode
from .settings import data_root, context_sizes


class series_dataset:

    def __init__(self, fold, endpoint, include_test=False):
        self.fold = fold
        self.endpoint = endpoint
        directory = data_root / f"fold_{fold}"
        self.metadata = read(directory / "dataset.json")
        with np.load(directory / "features.npz") as features:
            self.x = features["pca_32"]
            self.pca_training_indices = set(features["training_indices"].tolist())
        pools = [dict(p) for p in self.metadata["pools"] if p["endpoint"] == endpoint]
        train = [p for p in pools if p["subset"] == "train"]
        self.scale = float(
            max(
                0.05,
                np.sqrt(
                    np.mean(
                        [
                            2
                            * np.var(p["objective"])
                            * len(p["objective"])
                            / (len(p["objective"]) - 1)
                            for p in train
                        ]
                    )
                ),
            )
        )
        self.pools = []
        for p in pools:
            if p["subset"] == "test" and (not include_test):
                continue
            p["indices"] = np.asarray(p["feature_indices"], int)
            p["y"] = np.asarray(p["objective"], float) / self.scale
            self.pools.append(p)
        self.training = [p for p in self.pools if p["subset"] == "train"]
        self.large = [p for p in self.training if len(p["y"]) >= 15]
        self.by_id = {p["pool_id"]: p for p in self.pools}
        self.audit_splits()

    def audit_splits(self):
        groups = {}
        molecules = {}
        for p in self.metadata["pools"]:
            for key, table in [(p["group"], groups)] + [
                (str(i), molecules) for i in p["feature_indices"]
            ]:
                if key in table:
                    assert table[key] == p["subset"], ("split leak", key)
                table[key] = p["subset"]
        actual_training = {
            i
            for p in self.metadata["pools"]
            if p["subset"] == "train"
            for i in p["feature_indices"]
        }
        assert (
            self.pca_training_indices == actual_training
        ), "PCA training provenance mismatch"

    def episode(self, p, observed, query, draw=0):
        assert len(observed) == len(set(observed)) and (not set(observed) & set(query))
        x = self.x[p["indices"]]
        y = p["y"] - p["y"][observed[0]]
        return prediction_episode(
            measured_context(
                torch.tensor(x[observed], dtype=torch.float32),
                torch.tensor(y[observed], dtype=torch.float32),
            ),
            torch.tensor(x[query], dtype=torch.float32),
            torch.tensor(y[query], dtype=torch.float32),
            dict(
                pool_id=p["pool_id"],
                group=p["group"],
                pool_size=len(y),
                context_size=len(observed),
                endpoint=self.endpoint,
                fold=self.fold,
                draw=draw,
                reference=int(observed[0]),
                observed=list(map(int, observed)),
                query=list(map(int, query)),
            ),
        )

    def sample(self, rng, size, max_context=24):
        episodes = []
        for _ in range(size):
            choices = self.large if self.large and rng.random() < 0.5 else self.training
            p = choices[int(rng.integers(len(choices)))]
            n = len(p["y"])
            order = rng.permutation(n)
            if rng.random() < 0.5:
                worst = order[np.argsort(-p["y"][order], kind="stable")][
                    : max(1, n // 2)
                ]
                ref = int(rng.choice(worst))
            else:
                ref = int(order[0])
            order = order[order != ref]
            qn = min(5, max(1, n // 3))
            query = order[:qn]
            rest = order[qn:]
            maximum = min(max_context, len(rest))
            k = (
                0
                if maximum == 0 or rng.random() < 0.2
                else int(rng.integers(1, maximum + 1))
            )
            if k and rng.random() < 0.5:
                x = self.x[p["indices"]]
                center = x[int(rng.choice(np.r_[ref, query]))]
                rest = rest[
                    np.argsort(
                        ((x[rest] - center) ** 2).mean(1)
                        + rng.exponential(0.15, len(rest))
                    )
                ]
            episodes.append(self.episode(p, [ref] + rest[:k].tolist(), query.tolist()))
        return episodes

    def cases(self, subset, draws=3, pool_limit=None):
        pools = [p for p in self.pools if p["subset"] == subset]
        if pool_limit and len(pools) > pool_limit:
            large = [p for p in pools if len(p["y"]) >= 15]
            small = [p for p in pools if len(p["y"]) < 15]
            rng = rng_for("meta_validation_pool_subset", self.fold, self.endpoint)
            ids = rng.permutation(len(small))[: max(0, pool_limit - len(large))]
            pools = large + [small[i] for i in ids]
        cases = []
        for p in pools:
            n = len(p["y"])
            qn = 5 if n >= 15 else 3 if n >= 5 else 1
            for draw in range(draws):
                rng = rng_for("meta_prediction_case", self.fold, p["pool_id"], draw)
                order = rng.permutation(n)
                worst = order[np.argsort(-p["y"][order], kind="stable")][
                    : max(1, n // 2)
                ]
                ref = int(rng.choice(worst))
                rest = order[order != ref]
                query = rest[:qn].tolist()
                candidates = rest[qn:].tolist()
                for count in context_sizes:
                    if count <= 1 + len(candidates):
                        cases.append(
                            self.episode(
                                p, [ref] + candidates[: count - 1], query, draw
                            )
                        )
        return cases


def validation_weights(cases):
    from collections import Counter as counter_type

    counts = counter_type((e.meta["pool_id"] for e in cases))
    large = {e.meta["pool_id"] for e in cases if e.meta["pool_size"] >= 15}
    w = np.array([1 / (len(counts) * counts[e.meta["pool_id"]]) for e in cases])
    if large:
        w = 0.5 * w + 0.5 * np.array(
            [
                int(e.meta["pool_id"] in large)
                / (len(large) * counts[e.meta["pool_id"]])
                for e in cases
            ]
        )
    assert np.isclose(w.sum(), 1)
    return w
