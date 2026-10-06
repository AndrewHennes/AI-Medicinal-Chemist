"""Archived fixed-cardinality search, joint-Gaussian acquisitions, and costs."""

import math
import numpy as np
import torch
from scipy.special import ndtri
from scipy.stats import qmc
from ..io import rng_for
from ..acquisition import log_ei as minimization_log_ei


def log_ei(mean, standard_deviation, best):
    """Batch states use utility (larger is better); package objectives minimize."""
    return minimization_log_ei(-np.asarray(mean), standard_deviation, -best)


def collate_states(states, pending=None):
    b = len(states)
    n = max((len(s["ids"]) for s in states))
    d = states[0]["features"].shape[1]
    x = np.zeros((b, n, d), np.float32)
    rel = np.zeros((b, n, n, 3), np.float32)
    valid = np.zeros((b, n), bool)
    p = np.zeros((b, n), bool)
    for i, s in enumerate(states):
        size = len(s["ids"])
        x[i, :size] = s["features"]
        rel[i, :size, :size] = s["relations"]
        valid[i, :size] = True
        if pending is not None:
            p[i, np.asarray(pending[i], int)] = True
    return dict(
        x=torch.from_numpy(x),
        relations=torch.from_numpy(rel),
        valid=torch.from_numpy(valid),
        pending=torch.from_numpy(p),
        g=torch.from_numpy(np.stack([s["global_features"] for s in states])),
    )


def stable_top(values, k):
    return np.argsort(-np.asarray(values), kind="stable")[:k].astype(int).tolist()


def posterior_samples(state, count=128, seed=0):
    n = len(state["ids"])
    cov = 0.5 * (state["covariance"] + state["covariance"].T)
    try:
        factor = np.linalg.cholesky(cov + np.eye(n) * 1e-09)
    except np.linalg.LinAlgError:
        eig, v = np.linalg.eigh(cov)
        factor = v @ np.diag(np.sqrt(np.maximum(eig, 1e-09)))
    sampler = qmc.Sobol(n, scramble=True, seed=int(seed) % 2**32)
    u = sampler.random_base2(int(np.ceil(np.log2(count))))[:count]
    return state["mu"][None, :] + ndtri(np.clip(u, 1e-09, 1 - 1e-09)) @ factor.T


def subset_search(score, n, k, beam=4, swaps=1, lookahead=0, rng=None):
    """Compare only equal-size sets. Cached scores; swaps preserve cardinality."""
    if k >= n:
        return (list(range(n)), dict(evaluations=0))
    cache = {}

    def values(sets):
        missing = list(
            dict.fromkeys(
                (tuple(sorted(s)) for s in sets if tuple(sorted(s)) not in cache)
            )
        )
        for start in range(0, len(missing), 256):
            chunk = missing[start : start + 256]
            cache.update(zip(chunk, map(float, score(chunk))))
        return np.array([cache[tuple(sorted(s))] for s in sets])

    retained = [()]
    for length in range(1, k + 1):
        proposals = sorted(
            {tuple(sorted(s + (i,))) for s in retained for i in range(n) if i not in s}
        )
        v = values(proposals)
        if lookahead and length < k:
            completed = []
            for s in proposals:
                available = np.array([i for i in range(n) if i not in s])
                completed.extend(
                    (
                        tuple(
                            sorted(
                                s
                                + tuple(
                                    rng.choice(available, k - length, replace=False)
                                )
                            )
                        )
                        for _ in range(lookahead)
                    )
                )
            v = values(completed).reshape(len(proposals), lookahead).max(1)
        retained = [proposals[i] for i in np.argsort(-v, kind="stable")[:beam]]
    best = retained[int(np.argmax(values(retained)))]
    for _ in range(swaps):
        proposals = sorted(
            {
                tuple(sorted(set(best) - {a} | {b}))
                for a in best
                for b in range(n)
                if b not in best
            }
            | {best}
        )
        v = values(proposals)
        next_best = proposals[int(np.argmax(v))]
        if cache[next_best] <= cache[best] + 1e-12:
            break
        best = next_best
    return (list(best), dict(evaluations=len(cache)))


def select_classical(state, requested_count, method, seed=0, nap=None):
    n = len(state["ids"])
    k = min(requested_count, n)
    if k == n:
        return list(range(n))
    if method == "gp_topk":
        return stable_top(state["mu"], k)
    if method == "delta_topk":
        return stable_top(state["delta"], k)
    if method == "ei_topk":
        return stable_top(state["log_ei"], k)
    if method == "random":
        return rng_for("batch_random", seed).choice(n, k, replace=False).tolist()
    if method == "nap_topk":
        with torch.no_grad():
            s = torch.tensor(
                np.stack([state["mu"], state["sd"]], -1), dtype=torch.float32
            )[None]
            h = nap.scalar(s)
            scores = nap.log_temperature.clamp(-2, 3).exp() * s[
                :, :, 0
            ] + nap.acquisition(h).squeeze(-1)
        return stable_top(scores[0].numpy(), k)
    if method == "fantasy_ei":
        cov = state["covariance"].copy()
        selected = []
        for _ in range(k):
            sd = np.sqrt(np.diag(cov).clip(1e-12))
            scores = log_ei(state["mu"], sd, state["best"])
            scores[selected] = -np.inf
            a = int(np.argmax(scores))
            selected.append(a)
            v = cov[:, a].copy()
            cov -= np.outer(v, v) / max(cov[a, a], 1e-09)
        return selected
    samples = posterior_samples(state, 128, seed)
    if method == "prob_best":
        mass = np.bincount(samples.argmax(1), minlength=n) / len(samples)
        return np.lexsort((-state["mu"], -mass))[:k].tolist()
    if method == "qei":
        if k == 1:
            return stable_top(state["log_ei"], 1)

        def score(sets):
            return np.maximum(
                samples[:, np.asarray(sets)].max(-1) - state["best"], 0
            ).mean(0)

        return subset_search(score, n, k, beam=4, swaps=1)[0]
    raise ValueError(method)


def batch_times(p, ref, batches):
    thresholds = np.sort(p["y"])[[min(k, len(p["y"])) - 1 for k in [1, 2, 3, 4]]]
    rounds = []
    compounds = []
    for value in thresholds:
        if p["y"][ref] <= value:
            rounds.append(0)
            compounds.append(0)
            continue
        total = 0
        for round_index, b in enumerate(batches, 1):
            total += len(b)
            if np.any(p["y"][b] <= value):
                rounds.append(round_index)
                compounds.append(total)
                break
        else:
            raise AssertionError("No target compound found")
    return (rounds, compounds)


def random_expectation(p, ref, requested_count):
    n = len(p["y"]) - 1
    thresholds = np.sort(p["y"])[[min(k, len(p["y"])) - 1 for k in [1, 2, 3, 4]]]
    rounds = []
    compounds = []
    for threshold in thresholds:
        if p["y"][ref] <= threshold:
            rounds.append(0.0)
            compounds.append(0.0)
            continue
        m = int((p["y"] <= threshold).sum())
        den = math.comb(n, m)
        er = ec = 0.0
        for spent in range(0, n, requested_count):
            survival = math.comb(n - spent, m) / den if n - spent >= m else 0.0
            er += survival
            ec += min(requested_count, n - spent) * survival
        rounds.append(er)
        compounds.append(ec)
    return (rounds, compounds)
