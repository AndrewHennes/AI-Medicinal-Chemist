"""Fixed-query learning and counterfactual experiment value from frozen models.

The same hidden compounds are used before and after every reveal. This module
does not train or select models and never supplies hidden targets to a predictor.
It reruns historical scientific questions under the current package protocol.
"""

from pathlib import Path as path_type

import numpy as np
import pandas as pd
import torch

from ..data import series_dataset
from ..distributions import measured_context, mixture
from ..evaluation import rho
from ..io import digest, read, rng_for, write
from ..training import load


def absolute_path(value):
    path = path_type(value)
    if not path.is_absolute():
        raise ValueError(f"An absolute path is required: {value}")
    return path


def design(pool, draw, query_count=5, seed=2026):
    """One reference, a permanently hidden set, and an outcome-blind reveal order.

    Only selection of the initial worse-half hit uses retrospective outcomes.
    Ties at the worse-half boundary are resolved by a seeded random permutation.
    """
    values = np.asarray(pool["y"])
    if len(values) < 3:
        raise ValueError("At least three compounds are required")
    rng = rng_for("local_adaptation_design", seed, pool["pool_id"], draw)
    order = rng.permutation(len(values))
    worse = order[np.argsort(-values[order], kind="stable")][: max(1, len(values) // 2)]
    reference = int(rng.choice(worse))
    remaining = order[order != reference]
    hidden_count = min(query_count, max(1, len(values) // 3))
    return (
        reference,
        remaining[:hidden_count].tolist(),
        remaining[hidden_count:].tolist(),
    )


def distribution(models, features, values, observed, queries, replacements=None):
    """Models receive measured outcomes only; replacements are synthetic controls."""
    observed = list(map(int, observed))
    queries = list(map(int, queries))
    if len(set(observed)) != len(observed) or set(observed) & set(queries):
        raise ValueError("Measured and hidden compounds must be distinct")
    if not observed or not queries:
        raise ValueError("Both a context and hidden queries are required")
    measured_values = np.asarray(values)[observed].copy()
    for index, value in (replacements or {}).items():
        if index not in observed or index == observed[0]:
            raise ValueError("Replace only a non-reference measured outcome")
        measured_values[observed.index(index)] = value
    context = measured_context(
        torch.as_tensor(features[observed], dtype=torch.float32),
        torch.as_tensor(measured_values - measured_values[0], dtype=torch.float32),
    )
    query = torch.as_tensor(features[queries], dtype=torch.float32)
    with torch.no_grad():
        return mixture([model.predict(context, query).detached() for model in models])


def metrics(prediction, targets, scale=1.0):
    """Use native Gaussian/Student mixtures, including mixture quantile intervals."""
    targets = np.asarray(targets, dtype=np.float32)
    target_tensor = torch.as_tensor(targets)
    mean, variance = prediction.moments()
    mean = mean.numpy()
    lower, upper = prediction.interval(0.9)
    nll = float(-prediction.log_prob(target_tensor).mean())
    if not np.isfinite(nll) or not np.isfinite(mean).all():
        raise FloatingPointError("Nonfinite held-out prediction")
    return dict(
        spearman=rho(targets, mean),
        mse=float(np.mean((mean - targets) ** 2)),
        nll=nll,
        nll_transformed=nll + float(np.log(scale)),
        coverage90=float(np.mean((targets >= lower) & (targets <= upper))),
        width90=float(np.mean(upper - lower)),
        mean_variance=float(variance.mean()),
        target_mean=float(targets.mean()),
        target_second_moment=float(np.mean(targets**2)),
        query_count=len(targets),
    )


def common_metadata(data, pool, method, draw, reference, queries):
    return dict(
        fold=data.fold,
        endpoint=data.endpoint,
        method=method,
        pool_id=pool["pool_id"],
        group=pool["group"],
        pool_size=len(pool["y"]),
        draw=draw,
        reference=reference,
        queries=queries,
        outcome_scale=float(data.scale),
    )


def learning_rows(data, models, method, config):
    rows = []
    counts = sorted(set(config["context_sizes"]))
    for pool in data.pools:
        if pool["subset"] != "test" or len(pool["y"]) < config["minimum_pool_size"]:
            continue
        features = data.x[pool["indices"]]
        values = np.asarray(pool["y"])
        for draw in range(config["draws"]):
            reference, queries, candidates = design(
                pool, draw, config["query_count"], config["seed"]
            )
            meta = common_metadata(data, pool, method, draw, reference, queries)
            targets = values[queries] - values[reference]
            complete = len(queries) == config["query_count"] and len(
                candidates
            ) + 1 >= max(counts)
            expected_values = {}
            if candidates and config["expected_outcome_control"]:
                prior = distribution(models, features, values, [reference], candidates)
                prior_mean = prior.moments()[0].numpy()
                expected_values = dict(zip(candidates, prior_mean + values[reference]))
            for count in counts:
                if count > len(candidates) + 1:
                    continue
                observed = [reference] + candidates[: count - 1]
                for control in ("actual", "expected_initial"):
                    if control != "actual" and not config["expected_outcome_control"]:
                        continue
                    replacements = (
                        {index: expected_values[index] for index in observed[1:]}
                        if control == "expected_initial"
                        else None
                    )
                    prediction = distribution(
                        models, features, values, observed, queries, replacements
                    )
                    rows.append(
                        dict(
                            **meta,
                            observed=observed,
                            context_size=count,
                            complete_cohort=complete,
                            control=control,
                            **metrics(prediction, targets, data.scale),
                        )
                    )
    return rows


def difference(after, before):
    if after is None or before is None:
        return None
    return float(after - before)


def experiment_rows(data, models, method, config):
    """Reveal each candidate independently, never accumulating other candidates."""
    rows = []
    count = config["experiment_context_size"]
    for pool in data.pools:
        if pool["subset"] != "test" or len(pool["y"]) < config["minimum_pool_size"]:
            continue
        features = data.x[pool["indices"]]
        values = np.asarray(pool["y"])
        for draw in range(config["experiment_draws"]):
            reference, queries, candidates = design(
                pool, draw, config["query_count"], config["seed"]
            )
            if len(candidates) < count:
                continue
            observed = [reference] + candidates[: count - 1]
            candidates = candidates[count - 1 :]
            limit = config["maximum_candidates"]
            if limit is not None:
                candidates = candidates[:limit]
            targets = values[queries] - values[reference]
            before = metrics(
                distribution(models, features, values, observed, queries),
                targets,
                data.scale,
            )
            prior = distribution(models, features, values, observed, candidates)
            expected = prior.moments()[0].numpy() + values[reference]
            incumbent = float(values[observed].min())
            meta = common_metadata(data, pool, method, draw, reference, queries)
            for candidate, expected_value in zip(candidates, expected):
                after = metrics(
                    distribution(
                        models, features, values, observed + [candidate], queries
                    ),
                    targets,
                    data.scale,
                )
                control = metrics(
                    distribution(
                        models,
                        features,
                        values,
                        observed + [candidate],
                        queries,
                        {candidate: expected_value},
                    ),
                    targets,
                    data.scale,
                )
                rows.append(
                    dict(
                        **meta,
                        observed=observed,
                        candidate=candidate,
                        context_size=count,
                        candidate_outcome=float(values[candidate] - values[reference]),
                        predicted_outcome=float(expected_value - values[reference]),
                        outcome_surprise=float(values[candidate] - expected_value),
                        signed_improvement=float(incumbent - values[candidate]),
                        improvement=float(max(0.0, incumbent - values[candidate])),
                        disappointing=bool(values[candidate] >= incumbent),
                        spearman_gain=difference(after["spearman"], before["spearman"]),
                        mse_gain=before["mse"] - after["mse"],
                        nll_gain=before["nll"] - after["nll"],
                        outcome_spearman_gain=difference(
                            after["spearman"], control["spearman"]
                        ),
                        outcome_mse_gain=control["mse"] - after["mse"],
                        outcome_nll_gain=control["nll"] - after["nll"],
                        before=before,
                        after=after,
                        expected_control=control,
                    )
                )
    return rows


def summaries(curves, experiments):
    """Aggregate curves by draw/pool/assay and experiments by candidate/pool/assay.

    Curve draws receive equal weight within each pool. Experiment candidates are
    averaged within each pool/outcome category, so draws containing more eligible
    candidates in that category contribute more. Both then weight pools equally
    within an assay and assays equally in the macro average.
    """
    curve_frame = pd.DataFrame(curves)
    curve_tables = []
    curve_metrics = [
        "spearman",
        "mse",
        "nll",
        "nll_transformed",
        "coverage90",
        "width90",
        "mean_variance",
        "target_mean",
        "target_second_moment",
    ]
    if not curve_frame.empty:
        for cohort in ("complete", "available"):
            eligible = (
                curve_frame[curve_frame.complete_cohort]
                if cohort == "complete"
                else curve_frame
            )
            group_columns = ["endpoint", "method", "control", "context_size"]
            pool = (
                eligible.groupby(group_columns + ["fold", "pool_id"], dropna=False)[
                    curve_metrics
                ]
                .mean()
                .reset_index()
            )
            table = pool.groupby(group_columns)[curve_metrics].mean().reset_index()
            counts = pool.groupby(group_columns).size().rename("pools").reset_index()
            table = table.merge(counts, on=group_columns)
            denominator = table.target_second_moment - table.target_mean**2
            table["r2"] = np.where(denominator > 0, 1 - table.mse / denominator, np.nan)
            table["cohort"] = cohort
            macro = (
                table.groupby(["method", "control", "context_size", "cohort"])[
                    curve_metrics + ["r2"]
                ]
                .mean()
                .reset_index()
            )
            macro["endpoint"] = "macro"
            macro["pools"] = (
                table.groupby(["method", "control", "context_size", "cohort"])["pools"]
                .sum()
                .to_numpy()
            )
            curve_tables.extend([table, macro])
    experiment_frame = pd.DataFrame(experiments)
    experiment_table = pd.DataFrame()
    if not experiment_frame.empty:
        columns = [
            "signed_improvement",
            "improvement",
            "spearman_gain",
            "mse_gain",
            "nll_gain",
            "outcome_spearman_gain",
            "outcome_mse_gain",
            "outcome_nll_gain",
        ]
        pool = (
            experiment_frame.groupby(
                ["endpoint", "method", "fold", "pool_id", "disappointing"]
            )[columns]
            .mean()
            .reset_index()
        )
        experiment_table = (
            pool.groupby(["endpoint", "method", "disappointing"])[columns]
            .mean()
            .reset_index()
        )
        experiment_table["pools"] = (
            pool.groupby(["endpoint", "method", "disappointing"]).size().to_numpy()
        )
        macro = (
            experiment_table.groupby(["method", "disappointing"])[columns]
            .mean()
            .reset_index()
        )
        macro["endpoint"] = "macro"
        macro["pools"] = (
            experiment_table.groupby(["method", "disappointing"])["pools"]
            .sum()
            .to_numpy()
        )
        experiment_table = pd.concat([experiment_table, macro], ignore_index=True)
    return (
        pd.concat(curve_tables, ignore_index=True) if curve_tables else pd.DataFrame()
    ), experiment_table


def make_figures(curves, experiments, directory):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages as pdf_pages

    directory.mkdir(parents=True, exist_ok=True)
    with pdf_pages(directory / "local_adaptation.pdf") as report:
        for endpoint in sorted(curves.endpoint.unique()) if not curves.empty else []:
            for cohort in ("complete", "available"):
                block = curves[
                    (curves.endpoint == endpoint) & (curves.cohort == cohort)
                ]
                if block.empty:
                    continue
                figure, axes = plt.subplots(
                    1, 3, figsize=(13, 4), constrained_layout=True
                )
                for (method, control), data in block.groupby(["method", "control"]):
                    data = data.sort_values("context_size")
                    for axis, metric in zip(axes, ["r2", "spearman", "nll"]):
                        axis.plot(
                            data.context_size,
                            data[metric],
                            marker="o",
                            linestyle="-" if control == "actual" else "--",
                            label=f"{method}: {control}",
                        )
                        axis.set(xlabel="Measured compounds", ylabel=metric)
                        axis.grid(alpha=0.2)
                axes[-1].legend(fontsize=6)
                figure.suptitle(f"{endpoint}: {cohort} cohort, fixed hidden compounds")
                report.savefig(figure)
                figure.savefig(directory / f"{endpoint}_{cohort}_learning.png", dpi=160)
                plt.close(figure)
        frame = pd.DataFrame(experiments)
        for (endpoint, method), block in (
            frame.groupby(["endpoint", "method"]) if not frame.empty else []
        ):
            figure, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
            for axis, metric in zip(axes, ["spearman_gain", "mse_gain", "nll_gain"]):
                axis.scatter(block.signed_improvement, block[metric], s=8, alpha=0.25)
                axis.axhline(0, color="grey", linewidth=0.8)
                axis.axvline(0, color="grey", linewidth=0.8)
                axis.set(xlabel="Immediate improvement (signed)", ylabel=metric)
            figure.suptitle(f"{endpoint}: {method}, separate counterfactual reveals")
            report.savefig(figure)
            figure.savefig(
                directory / f"{endpoint}_{method}_experiment_value.png", dpi=160
            )
            plt.close(figure)


def load_verified_models(data, model_config, seeds):
    """Reject an unrelated split, feature transform, endpoint, or training scale."""
    from ..settings import data_root

    dataset_hash = digest(data_root / f"fold_{data.fold}" / "dataset.json")
    feature_hash = digest(data_root / f"fold_{data.fold}" / "features.npz")
    models, provenance = [], []
    for seed in seeds:
        checkpoint = absolute_path(
            model_config["checkpoint_template"].format(
                fold=data.fold, endpoint=data.endpoint, seed=seed
            )
        )
        specification_path = checkpoint.parent / "specification.json"
        specification = read(specification_path)
        expected = dict(
            endpoint=data.endpoint,
            fold=data.fold,
            seed=seed,
            dataset_sha256=dataset_hash,
            feature_sha256=feature_hash,
        )
        for name, value in expected.items():
            if specification.get(name) != value:
                raise ValueError(f"Checkpoint {name} mismatch: {checkpoint}")
        if not np.isclose(specification["scale"], data.scale, rtol=1e-9, atol=0):
            raise ValueError(f"Checkpoint outcome scale mismatch: {checkpoint}")
        if specification.get("training_role", "full_outer_train") != "full_outer_train":
            raise ValueError(
                "This recipe expects predictors fit on the full outer training split"
            )
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if (
            saved["configuration"] != specification["configuration"]
            or saved["endpoint"] != data.endpoint
            or saved["seed"] != seed
        ):
            raise ValueError(
                f"Checkpoint payload does not match its training specification: {checkpoint}"
            )
        if saved["configuration"]["method"] != model_config["method"]:
            raise ValueError(f"Checkpoint model family mismatch: {checkpoint}")
        models.append(load(checkpoint))
        provenance.append(
            dict(
                checkpoint=str(checkpoint),
                checkpoint_sha256=digest(checkpoint),
                specification=str(specification_path),
                specification_sha256=digest(specification_path),
            )
        )
    return models, provenance


def run(configuration_file):
    """Run a fixed recipe, writing separate current-protocol outputs and reports."""
    from ..settings import artifact_root, data_root
    from ..training import implementation_hashes
    from ..data_import import import_prepared_data

    config = read(absolute_path(configuration_file))
    counts = config["context_sizes"]
    if not counts or min(counts) < 1 or 1 not in counts:
        raise ValueError("context_sizes must contain 1 and positive counts")
    if config["experiment_context_size"] < 1 or config["query_count"] < 1:
        raise ValueError("Context and query counts must be positive")
    if config["maximum_candidates"] is not None and config["maximum_candidates"] < 1:
        raise ValueError("maximum_candidates must be null or positive")
    directory = absolute_path(config["output_directory"])
    if not directory.is_relative_to(artifact_root):
        raise ValueError(
            "Write analysis products beneath the configured artifacts_root"
        )
    torch.set_num_threads(1)
    import_prepared_data()
    signature = dict(
        configuration=config,
        implementation=implementation_hashes(),
        datasets={
            str(data_root / f"fold_{fold}" / name): digest(
                data_root / f"fold_{fold}" / name
            )
            for fold in config["folds"]
            for name in ("dataset.json", "features.npz")
        },
    )
    provenance_file = directory / "provenance.json"
    if provenance_file.exists() and read(provenance_file) != signature:
        raise ValueError(
            "Existing analysis provenance differs; choose a new output_directory"
        )
    write(provenance_file, signature)
    curves, experiments = [], []
    for fold in config["folds"]:
        for endpoint in config["endpoints"]:
            data = series_dataset(fold, endpoint, include_test=True)
            for model_config in config["models"]:
                method = model_config["method"]
                models, provenance = load_verified_models(
                    data, model_config, config["seeds"]
                )
                part = directory / "cases" / f"fold_{fold}" / endpoint / method
                completed = part / "completed.json"
                if completed.exists():
                    if read(completed)["checkpoints"] != provenance:
                        raise ValueError(f"Checkpoint provenance changed: {part}")
                    current_curves = read(part / "learning_cases.json")
                    current_experiments = read(part / "experiment_cases.json")
                else:
                    current_curves = learning_rows(data, models, method, config)
                    current_experiments = experiment_rows(data, models, method, config)
                    write(part / "learning_cases.json", current_curves)
                    write(part / "experiment_cases.json", current_experiments)
                    write(
                        completed,
                        dict(
                            checkpoints=provenance,
                            learning_cases=len(current_curves),
                            experiment_cases=len(current_experiments),
                        ),
                    )
                curves.extend(current_curves)
                experiments.extend(current_experiments)
                write(
                    directory / "progress.json",
                    dict(
                        fold=fold,
                        endpoint=endpoint,
                        method=method,
                        learning_cases=len(curves),
                        experiment_cases=len(experiments),
                    ),
                )
    curve_summary, experiment_summary = summaries(curves, experiments)
    reports = directory / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    curve_summary.to_csv(reports / "learning_summary.csv", index=False)
    experiment_summary.to_csv(reports / "experiment_summary.csv", index=False)
    pd.DataFrame(curves).to_csv(reports / "learning_cases.csv.gz", index=False)
    pd.DataFrame(experiments).to_csv(reports / "experiment_cases.csv.gz", index=False)
    make_figures(curve_summary, experiments, reports)
    write(
        directory / "completed.json",
        dict(
            status="complete",
            historical_reproduction="current_protocol_replication",
            learning_cases=len(curves),
            experiment_cases=len(experiments),
            report=str(reports / "local_adaptation.pdf"),
        ),
    )
    return directory
