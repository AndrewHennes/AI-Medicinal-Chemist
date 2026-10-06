"""Recreate original augmentation figures without retraining or changing weighting."""

import os
from pathlib import Path as path_type

import pandas as pd

from ..io import digest, write
from ..settings import artifact_root

os.environ.setdefault("MPLCONFIGDIR", str(artifact_root / "matplotlib_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf_pages

study_names = {
    "acquisition_fivefold_initial_hit_sensitivity": "Initial-hit sensitivity",
    "acquisition_fivefold_lower_half_multihit_augmentation": "Multi-hit training augmentation",
    "top_removal_augmentation": "Cumulative top-removal augmentation",
    "nap_topk_auxiliary": "Top-k auxiliary acquisition tasks",
}


def display_method(method):
    return {
        "Cross-fitted single-task NAP": "Revised NAP",
        "Cross-fitted single-task NAP with multi-hit augmentation": "Revised NAP + multi-hit",
        "Single-task NAP with multi-hit augmentation": "Original NAP + multi-hit",
        "single_task_NAP": "Original NAP",
        "single_task_GP + EI": "GP + EI",
        "single_task_Delta greedy": "Delta greedy",
        "Original NAP + top-removal augmentation": "Original NAP + top removal",
        "Revised NAP + top-removal augmentation": "Revised NAP + top removal",
        "Original NAP + top-k auxiliary tasks": "Original NAP + auxiliary",
        "Revised NAP + top-k auxiliary tasks": "Revised NAP + auxiliary",
    }.get(method, method)


def checked_table(path):
    table = pd.read_csv(path)
    table = table[
        (table.axis == "minimum_size") & (table.population == "all_starts")
    ].copy()
    keys = ["endpoint", "pool_size", "k", "method"]
    if "train_percent" in table:
        keys.extend(["train_percent", "test_percent"])
    if table.duplicated(keys).any():
        raise ValueError(f"Duplicate archived aggregate rows in {path}")
    return table


def format_figure(figure, axes, title):
    for rank, axis in enumerate(axes.flat, 1):
        axis.set_title(f"Purchases to any top-{rank}")
        axis.set_ylabel("Additional purchases, lower is better")
        axis.grid(alpha=0.2)
    if axes.flat[0].get_legend_handles_labels()[0]:
        axes.flat[0].legend(fontsize=7)
    figure.suptitle(title)


def plot_initial(table, destination, title):
    selected = table[table.pool_size.isin([3, 15])].copy()
    selected.to_csv(destination / "plotted_values.csv", index=False)
    count = 0
    with pdf_pages(destination / "historical_comparison.pdf") as document:
        for endpoint in sorted(selected.endpoint.unique()):
            for cutoff in (3, 15):
                block = selected[
                    (selected.endpoint == endpoint) & (selected.pool_size == cutoff)
                ]
                if block.empty:
                    continue
                methods = sorted(block.method.unique())
                colors = {
                    method: plt.get_cmap("tab10")(index)
                    for index, method in enumerate(methods)
                }
                figure, axes = plt.subplots(
                    2, 2, figsize=(12, 8), constrained_layout=True
                )
                for rank, axis in enumerate(axes.flat, 1):
                    for method in methods:
                        curve = block[(block.k == rank) & (block.method == method)]
                        fixed = curve[curve.train_percent == 50].sort_values(
                            "test_percent"
                        )
                        axis.plot(
                            fixed.test_percent,
                            fixed.purchases,
                            linestyle="--",
                            color=colors[method],
                            marker="o",
                            label=display_method(method)
                            + (
                                ""
                                if method in ("Random", "single_task_Delta greedy")
                                else " trained at 50%"
                            ),
                        )
                        if method not in ("Random", "single_task_Delta greedy"):
                            matched = curve[
                                curve.train_percent == curve.test_percent
                            ].sort_values("test_percent")
                            axis.plot(
                                matched.test_percent,
                                matched.purchases,
                                color=colors[method],
                                marker="s",
                                label=display_method(method) + " retrained",
                            )
                    axis.set_xlabel("Starting hit from worst percentage")
                    axis.set_xticks([10, 20, 30, 40, 50])
                format_figure(
                    figure,
                    axes,
                    f"{title} | {endpoint.replace('_', ' ')} | pools ≥{cutoff}\nArchived results, original aggregation",
                )
                figure.savefig(destination / f"{endpoint}_cutoff_{cutoff}.png", dpi=160)
                document.savefig(figure)
                plt.close(figure)
                count += 1
    return count


def plot_augmentation(table, destination, title):
    selected = table[table.pool_size <= 40].copy()
    selected.to_csv(destination / "plotted_values.csv", index=False)
    count = 0
    with pdf_pages(destination / "historical_comparison.pdf") as document:
        for endpoint in sorted(selected.endpoint.unique()):
            block = selected[selected.endpoint == endpoint]
            methods = sorted(block.method.unique())
            colors = {
                method: plt.get_cmap("tab10")(index)
                for index, method in enumerate(methods)
            }
            figure, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
            for rank, axis in enumerate(axes.flat, 1):
                for method in methods:
                    curve = block[
                        (block.k == rank) & (block.method == method)
                    ].sort_values("pool_size")
                    axis.plot(
                        curve.pool_size,
                        curve.purchases,
                        color=colors[method],
                        marker="o",
                        markersize=3,
                        linestyle="--" if method == "Random" else "-",
                        label=display_method(method),
                    )
                axis.set_xlabel("Minimum pool size")
            format_figure(
                figure,
                axes,
                f"{title} | {endpoint.replace('_', ' ')}\nArchived results, original aggregation; sample size decreases along each curve",
            )
            figure.savefig(destination / f"{endpoint}.png", dpi=160)
            document.savefig(figure)
            plt.close(figure)
            count += 1
    return count


def recreate_history(output):
    """Write four PDFs plus PNGs/CSV/audit under an absolute output directory.

    Original overall rows are plotted only when the archived table has them.
    There is no new pooling across assays or across separate experiments.
    """
    output = path_type(output)
    if not output.is_absolute():
        raise ValueError("Historical figure output must be an absolute path")
    source_root = path_type(__file__).resolve().parents[3] / "results/analysis_history"
    manifest = []
    for name, title in study_names.items():
        source = source_root / name / "performance_by_minimum_pool_size.csv"
        table = checked_table(source)
        destination = output / name
        destination.mkdir(parents=True, exist_ok=True)
        plot = plot_initial if "initial_hit" in name else plot_augmentation
        pages = plot(table, destination, title)
        manifest.append(
            dict(
                study=name,
                source=str(source),
                source_sha256=digest(source),
                rows=len(table),
                original_overall_present=bool((table.endpoint == "overall").any()),
                pdf_pages=pages,
                output=str(destination / "historical_comparison.pdf"),
            )
        )
    write(output / "augmentation_history_manifest.json", manifest)
    return manifest
