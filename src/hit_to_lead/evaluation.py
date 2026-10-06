"""Matched fixed-query prediction and K=1 direct-EI acquisition evaluation."""

import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr
from .distributions import measured_context, mixture
from .data import series_dataset
from .io import rng_for, write
from .settings import benchmark_root
from .acquisition import log_ei


def predict(models, context, query):
    with torch.no_grad():
        return mixture([m.predict(context, query).detached() for m in models])


def rho(y, mean):
    if len(y) < 2 or np.ptp(y) == 0 or np.ptp(mean) == 0:
        return None
    return float(spearmanr(y, mean).statistic)


def prediction_rows(data, models, method, subset="test", draws=3):
    rows = []
    points = []
    for e in data.cases(subset, draws):
        p = predict(models, e.context, e.query)
        mean, var = p.moments()
        lo, hi = p.interval(0.9)
        y = e.target.numpy()
        mu = mean.numpy()
        error = (mu - y) ** 2
        row = dict(
            **e.meta,
            method=method,
            n_queries=len(y),
            spearman=rho(y, mu),
            mse=float(error.mean()),
            nll=float(-p.log_prob(e.target).mean()),
            coverage90=float(np.mean((y >= lo) & (y <= hi))),
            width90=float(np.mean(hi - lo)),
            mean_variance=float(var.mean()),
        )
        rows.append(row)
        for j, index in enumerate(e.meta["query"]):
            points.append(
                dict(
                    **{k: v for k, v in row.items() if k not in ("observed", "query")},
                    molecule_index=index,
                    target=float(y[j]),
                    prediction=float(mu[j]),
                    variance=float(var[j]),
                    point_nll=float(-p.log_prob(e.target)[j]),
                    squared_error=float(error[j]),
                )
            )
    return (rows, points)


def start_hit(p, draw):
    rng = rng_for("latent_test_start", p["pool_id"], draw)
    order = rng.permutation(len(p["y"]))
    worst = order[np.argsort(-p["y"][order], kind="stable")][: max(1, len(order) // 2)]
    return int(rng.choice(worst))


def acquisition(data, models, p, ref):
    observed = [ref]
    order = []
    x = torch.tensor(data.x[p["indices"]], dtype=torch.float32)
    y = np.asarray(p["y"]) - p["y"][ref]
    while y[observed].min() > y.min():
        ids = np.array([i for i in range(len(y)) if i not in observed])
        context = measured_context(
            x[observed], torch.tensor(y[observed], dtype=torch.float32)
        )
        pred = predict(models, context, x[ids])
        mean, var = pred.moments()
        scores = log_ei(mean.numpy(), var.sqrt().numpy(), y[observed].min())
        chosen = int(ids[np.argmax(scores)])
        observed.append(chosen)
        order.append(chosen)
    counts, random = acquisition_counts(y, ref, order)
    return (counts, random, order)


def acquisition_counts(y, ref, order):
    y = np.asarray(y)
    counts = []
    random = []
    for k in range(1, 5):
        threshold = np.sort(y)[min(k, len(y)) - 1]
        if y[ref] <= threshold:
            counts.append(0.0)
            random.append(0.0)
            continue
        counts.append(
            float(next((i + 1 for i, a in enumerate(order) if y[a] <= threshold)))
        )
        random.append(float(len(y) / (np.sum(y <= threshold) + 1)))
    return (counts, random)


def acquisition_rows(data, models, method, subset="test", draws=4):
    rows = []
    for p in data.pools:
        if p["subset"] != subset:
            continue
        for draw in range(draws):
            ref = start_hit(p, draw)
            tau, random, order = acquisition(data, models, p, ref)
            rows.append(
                dict(
                    method=method,
                    fold=data.fold,
                    endpoint=data.endpoint,
                    pool_id=p["pool_id"],
                    group=p["group"],
                    pool_size=len(p["y"]),
                    draw=draw,
                    reference=ref,
                    order=order,
                    **{f"top{k}": tau[k - 1] for k in range(1, 5)},
                    **{f"random_top{k}": random[k - 1] for k in range(1, 5)},
                )
            )
    return rows


def evaluate_family(fold, endpoint, method):
    from .training import load_ensemble, implementation_hashes
    from .io import read, digest
    from .settings import ensemble_seeds

    path = benchmark_root / "evaluations" / f"fold_{fold}" / endpoint / method
    base = benchmark_root / "runs" / f"fold_{fold}" / endpoint
    trained = "transfer" if method == "finetune" else method
    provenance = dict(
        selection=read(base / method / "selection.json"),
        implementation=implementation_hashes(),
        checkpoints={
            str(base / trained / "final" / f"seed_{s}/best.pt"): digest(
                base / trained / "final" / f"seed_{s}/best.pt"
            )
            for s in ensemble_seeds
        },
    )
    if (path / "completed.json").exists():
        if read(path / "completed.json")["provenance"] != provenance:
            raise RuntimeError("Evaluation provenance changed: " + str(path))
        return
    models = load_ensemble(fold, endpoint, method)
    data = series_dataset(fold, endpoint, True)
    rows, points = prediction_rows(data, models, method)
    write(path / "prediction_cases.json", rows)
    write(path / "prediction_points.json", points)
    rows = acquisition_rows(data, models, method)
    write(path / "acquisition.json", rows)
    write(
        path / "completed.json",
        dict(
            method=method,
            fold=fold,
            endpoint=endpoint,
            acquisition_episodes=len(rows),
            provenance=provenance,
        ),
    )


def summaries(prediction_cases, prediction_points, acquisition_cases):
    cases = pd.DataFrame(prediction_cases)
    points = pd.DataFrame(prediction_points)
    acq = pd.DataFrame(acquisition_cases)
    pred = []
    acquisition_summary = []
    for cutoff in (3, 15, 20, 25, 30):
        eligible = cases[cases.pool_size >= cutoff]
        for (endpoint, method, count), block in eligible.groupby(
            ["endpoint", "method", "context_size"]
        ):
            b = points[
                (points.pool_size >= cutoff)
                & (points.endpoint == endpoint)
                & (points.method == method)
                & (points.context_size == count)
            ]
            weights = 1 / b.groupby("pool_id").pool_id.transform("size").to_numpy()
            weights /= weights.sum()
            y = b.target.to_numpy()
            mean_y = weights @ y
            denominator = weights @ (y - mean_y) ** 2
            r2 = (
                None
                if denominator <= 0
                else float(1 - weights @ b.squared_error.to_numpy() / denominator)
            )
            macro = block.groupby("pool_id")[
                ["spearman", "nll", "coverage90", "width90", "mse"]
            ].mean()
            pred.append(
                dict(
                    endpoint=endpoint,
                    method=method,
                    context_size=int(count),
                    cutoff=cutoff,
                    pools=len(macro),
                    rank_eligible_pools=int(macro.spearman.notna().sum()),
                    r2=r2,
                    **{
                        k: None if pd.isna(v) else float(v)
                        for k, v in macro.mean().items()
                    },
                )
            )
        for (endpoint, method), block in acq[acq.pool_size >= cutoff].groupby(
            ["endpoint", "method"]
        ):
            macro = block.groupby("pool_id")[[f"top{k}" for k in range(1, 5)]].mean()
            acquisition_summary.append(
                dict(
                    endpoint=endpoint,
                    method=method,
                    cutoff=cutoff,
                    pools=len(macro),
                    **macro.mean().to_dict(),
                )
            )
    return (pred, acquisition_summary)


def paired_acquisition_intervals(acquisition_cases, replicates=2000):
    frame = pd.DataFrame(acquisition_cases)
    rows = []
    index = ["endpoint", "fold", "pool_id", "group", "draw", "pool_size"]
    for cutoff in (3, 15):
        subset = frame[frame.pool_size >= cutoff]
        for method in sorted(set(subset.method) - {"reference"}):
            a = subset[subset.method == method].set_index(index)
            b = subset[subset.method == "reference"].set_index(index)
            shared = a.index.intersection(b.index)
            if len(shared) == 0:
                continue
            diff = (
                a.loc[shared, [f"top{k}" for k in range(1, 5)]]
                - b.loc[shared, [f"top{k}" for k in range(1, 5)]]
            ).reset_index()
            pools = (
                diff.groupby(["endpoint", "pool_id", "group"])[
                    [f"top{k}" for k in range(1, 5)]
                ]
                .mean()
                .reset_index()
            )
            groups = sorted(pools.group.unique())
            rng = rng_for("meta_paired_bootstrap", method, cutoff)
            values = {e: [] for e in list(pools.endpoint.unique()) + ["macro"]}
            for _ in range(replicates):
                sampled = rng.choice(groups, len(groups), replace=True)
                frequency = pd.Series(sampled).value_counts()
                w = pools.group.map(frequency).fillna(0).to_numpy()
                endpoint_values = []
                for endpoint, block in pools.groupby("endpoint"):
                    ew = w[block.index]
                    v = block[[f"top{k}" for k in range(1, 5)]].to_numpy()
                    if ew.sum():
                        result = np.average(v, axis=0, weights=ew)
                        values[endpoint].append(result)
                        endpoint_values.append(result)
                if endpoint_values:
                    values["macro"].append(np.mean(endpoint_values, axis=0))
            actual = pools.groupby("endpoint")[[f"top{k}" for k in range(1, 5)]].mean()
            for endpoint, samples in values.items():
                if not samples:
                    continue
                point = (
                    actual.mean().to_numpy()
                    if endpoint == "macro"
                    else actual.loc[endpoint].to_numpy()
                )
                ci = np.quantile(samples, [0.025, 0.975], axis=0)
                for k in range(4):
                    rows.append(
                        dict(
                            endpoint=endpoint,
                            method=method,
                            reference="reference",
                            cutoff=cutoff,
                            top=k + 1,
                            difference=float(point[k]),
                            lower=float(ci[0, k]),
                            upper=float(ci[1, k]),
                            linked_groups=len(groups),
                        )
                    )
    return rows
