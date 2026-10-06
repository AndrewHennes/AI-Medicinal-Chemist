"""Recreate earlier comparison charts exclusively from archived numeric tables.

Studies retain their original aggregation, calibration, and data protocols.
Values are never pooled across studies. Newly run comparisons have separate
artifact directories and are not substituted into historical figures.
"""

from pathlib import Path as path_type
import pandas as pd
from .settings import repository_root
from .io import read, write, digest
from .reporting import plt, pdf_pages, plot_style, endpoint_labels


def label(name):
    names = {
        "original_ppo": "Original GP + PPO",
        "original_trpo": "Original GP + TRPO",
        "original_dpo": "Original GP + DPO",
        "auxiliary_ppo": "Auxiliary GP + PPO",
        "auxiliary_trpo": "Auxiliary GP + TRPO",
        "auxiliary_dpo": "Auxiliary GP + DPO",
        "original_gp_ei": "Original GP + EI",
        "auxiliary_gp_ei": "Auxiliary GP + EI",
        "original_warm": "Original GP warm start",
        "auxiliary_warm": "Auxiliary GP warm start",
        "historical_ppo": "Earlier PPO",
        "mean_sd": "Mean + SD",
        "latent_2": "+ 2 latent features",
        "latent_4": "+ 4 latent features",
        "latent_8": "+ 8 latent features",
        "latent_16": "+ 16 latent features",
        "validation_selected": "Validation-selected dimension",
        "random": "Random expectation",
        "direct_ei": "Direct EI",
        "analytic_ei": "Analytic EI",
        "unchanged": "Original neural model",
        "mean_only": "Average mean",
        "kernel_only": "Average-reference kernel",
        "mean_and_kernel": "Average mean and kernel",
        "weighted_selected": "Kernel-softmax weighting",
        "gp": "Neural mean + GP",
        "deep_sets": "Deep Sets",
        "pair_transformer": "Pair-aware Transformer",
        "batch_ppo": "Batch PPO",
        "gumbel": "Gumbel top-k",
        "qei": "Joint batch EI",
        "fantasy_ei": "GP mean-fantasy EI",
        "ei_topk": "Top-k EI",
        "gp_topk": "Top-k GP mean",
        "delta_topk": "Top-k delta",
        "nap_topk": "Top-k NAP",
        "prob_best": "Probability of best",
    }
    return names.get(name, name.replace("_", " "))


def add_macro(table, keys, metrics):
    """Equal-assay aggregation for new runs only; require every endpoint."""
    if "all" in set(table.endpoint):
        return table
    expected = set(table.endpoint)
    rows = []
    for key, block in table.groupby(keys):
        if set(block.endpoint) != expected or len(block) != len(expected):
            continue
        if not isinstance(key, tuple):
            key = (key,)
        rows.append(
            dict(
                zip(keys, key),
                endpoint="all",
                **{metric: block[metric].mean(skipna=False) for metric in metrics},
            )
        )
    return pd.concat([table, pd.DataFrame(rows)], ignore_index=True)


def finish_panel(figure, axes, title, note):
    handles, labels = axes.flat[0].get_legend_handles_labels()
    figure.suptitle(title, x=0.05, ha="left", weight="bold", fontsize=16)
    figure.legend(
        handles,
        labels,
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.045),
        fontsize=8,
    )
    figure.text(0.05, 0.018, note, fontsize=8, color="#444444")
    figure.tight_layout(rect=(0.025, 0.23, 0.99, 0.93))


def acquisition_figures(
    table, output, title, note="New common-protocol run; equal-assay aggregate."
):
    output = path_type(output)
    output.mkdir(parents=True, exist_ok=True)
    metrics = [f"top{k}" for k in range(1, 5)]
    table = add_macro(table, ["method", "cutoff"], metrics)
    table.to_csv(output / "plot_values.csv", index=False)
    endpoints = sorted(set(table.endpoint), key=lambda item: (item != "all", item))
    with plt.rc_context(plot_style), pdf_pages(output / "comparison.pdf") as report:
        for endpoint in endpoints:
            block = table[(table.endpoint == endpoint) & (table.cutoff <= 30)]
            figure, axes = plt.subplots(2, 2, figsize=(13, 10))
            for top, axis in enumerate(axes.flat, 1):
                for method, values in block.groupby("method"):
                    values = values.sort_values("cutoff")
                    methods = sorted(set(block.method))
                    color = (
                        "#888888"
                        if method == "random"
                        else plt.get_cmap("tab20")(methods.index(method) % 20)
                    )
                    axis.plot(
                        values.cutoff,
                        values[f"top{top}"],
                        marker="o",
                        markersize=3,
                        color=color,
                        linestyle="--" if method == "random" else "-",
                        label=label(method),
                    )
                axis.set(
                    title=f"Purchases to any top-{top} · lower",
                    xlabel="Minimum pool size",
                )
            name = (
                "All assays"
                if endpoint == "all"
                else endpoint_labels.get(endpoint, endpoint)
            )
            finish_panel(figure, axes, title + " | " + name, note)
            figure.savefig(output / f"{endpoint}.png", dpi=160)
            figure.savefig(output / f"{endpoint}.pdf")
            report.savefig(figure)
            plt.close(figure)
    return output / "comparison.pdf"


def batch_figures(
    table,
    output,
    title,
    note="New common-protocol run; all purchases in the final batch count.",
):
    output = path_type(output)
    output.mkdir(parents=True, exist_ok=True)
    table = add_macro(
        table, ["method", "batch_size", "metric", "top_k", "cutoff"], ["value"]
    )
    table.to_csv(output / "plot_values.csv", index=False)
    with plt.rc_context(plot_style), pdf_pages(output / "comparison.pdf") as report:
        for endpoint in sorted(
            set(table.endpoint), key=lambda item: (item != "all", item)
        ):
            for metric in ("rounds", "compounds"):
                block = table[
                    (table.endpoint == endpoint)
                    & (table.cutoff == 15)
                    & (table.metric == metric)
                    & table.batch_size.isin([1, 2, 5])
                ]
                figure, axes = plt.subplots(2, 2, figsize=(13, 10))
                for top, axis in enumerate(axes.flat, 1):
                    for method, values in block[block.top_k == top].groupby("method"):
                        values = values.sort_values("batch_size")
                        axis.plot(
                            values.batch_size,
                            values.value,
                            "o-",
                            label=label(method),
                            markersize=4,
                        )
                    axis.set(
                        title=f"{metric.title()} to any top-{top} · lower",
                        xlabel="Batch size",
                        xticks=[1, 2, 5],
                    )
                name = (
                    "All assays"
                    if endpoint == "all"
                    else endpoint_labels.get(endpoint, endpoint)
                )
                finish_panel(figure, axes, title + " | " + name + " | pools ≥15", note)
                figure.savefig(output / f"{endpoint}_{metric}.png", dpi=160)
                figure.savefig(output / f"{endpoint}_{metric}.pdf")
                report.savefig(figure)
                plt.close(figure)
    return output / "comparison.pdf"


def prediction_figures(table, output, title):
    table = table.copy()
    table["endpoint"] = table.endpoint.replace({"macro": "all"})
    output = path_type(output)
    output.mkdir(parents=True, exist_ok=True)
    methods = [
        "gp",
        "unchanged",
        "mean_only",
        "kernel_only",
        "mean_and_kernel",
        "weighted_selected",
    ]
    table = table[
        (table.cutoff == 15)
        & (table.calibration == "calibrated")
        & table.method.isin(methods)
    ]
    table.to_csv(output / "plot_values.csv", index=False)
    with plt.rc_context(plot_style), pdf_pages(output / "comparison.pdf") as report:
        for endpoint in sorted(
            set(table.endpoint), key=lambda item: (item != "all", item)
        ):
            figure, axes = plt.subplots(1, 3, figsize=(15, 6.5))
            for axis, metric, title_metric in zip(
                axes,
                ["r2", "rho", "nll"],
                [
                    "R² · higher",
                    "Within-series Spearman ρ · higher",
                    "Calibrated NLL · lower",
                ],
            ):
                for method in methods:
                    values = table[
                        (table.endpoint == endpoint) & (table.method == method)
                    ].sort_values("measurements")
                    axis.plot(
                        values.measurements,
                        values[metric],
                        "o-",
                        label=label(method),
                        markersize=3,
                    )
                axis.set(
                    title=title_metric,
                    xlabel="Measured compounds",
                    xticks=[1, 2, 3, 5, 10],
                )
            name = (
                "All assays"
                if endpoint == "all"
                else endpoint_labels.get(endpoint, endpoint)
            )
            finish_panel(
                figure,
                axes,
                title + " | " + name,
                "Archived scratch-trained results; pools ≥15; fixed hidden queries; validation-calibrated NLL.",
            )
            figure.savefig(output / f"{endpoint}.png", dpi=160)
            figure.savefig(output / f"{endpoint}.pdf")
            report.savefig(figure)
            plt.close(figure)
    return output / "comparison.pdf"


def recreate_history():
    source = repository_root / "results/historical"
    manifest = read(source / "manifest.json")
    output = repository_root / "results/historical_figures"
    reports = {}
    for study in manifest["studies"]:
        entry = source / study["name"]
        table = pd.read_csv(entry / study["table"])
        destination = output / study["name"]
        note = study["plot_note"]
        if study["kind"] == "prediction":
            report = prediction_figures(table, destination, study["title"])
        elif study["kind"] == "batch":
            table = table.rename(
                columns={"minimum_pool_size": "cutoff", "mean": "value"}
            )
            report = batch_figures(table, destination, study["title"], note)
        else:
            if study["name"] == "latent_features":
                table["method"] = table.dimension.map(
                    {
                        0: "mean_sd",
                        2: "latent_2",
                        4: "latent_4",
                        8: "latent_8",
                        16: "latent_16",
                        -1: "random",
                        -2: "validation_selected",
                    }
                )
                table = table.rename(columns={"purchases": "value"})
            else:
                table = table.rename(
                    columns={
                        "minimum_pool_size": "cutoff",
                        "mean_acquisitions": "value",
                        "mean": "value",
                    }
                )
            table = (
                table.pivot(
                    index=["endpoint", "method", "cutoff"],
                    columns="top_k",
                    values="value",
                )
                .rename(columns=lambda value: f"top{value}")
                .reset_index()
            )
            report = acquisition_figures(table, destination, study["title"], note)
        reports[study["name"]] = str(report.relative_to(repository_root))
    write(
        output / "manifest.json",
        dict(
            reports=reports,
            grpo_status="Implementation tested; archived plots cover completed experiments",
            input_sha256={
                str(path.relative_to(repository_root)): digest(path)
                for path in source.rglob("*.csv")
            },
        ),
    )
    print(output)
