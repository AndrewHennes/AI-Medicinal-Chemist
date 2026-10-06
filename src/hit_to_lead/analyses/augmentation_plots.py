"""Figures for new augmentation runs; never mix them with archived NAP results."""

import os

from ..settings import artifact_root

os.environ.setdefault("MPLCONFIGDIR", str(artifact_root / "matplotlib_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf_pages


def plot_results(table, output):
    output.mkdir(parents=True, exist_ok=True)
    with pdf_pages(output / "augmentation_comparison.pdf") as document:
        for endpoint in sorted(table.endpoint.unique()):
            for study in ("initial_hits", "multi_hit", "top_removal"):
                figure, axes = plt.subplots(
                    2, 2, figsize=(12, 8), constrained_layout=True
                )
                for rank, axis in enumerate(axes.flat, 1):
                    selected = table[table.endpoint == endpoint]
                    if study == "initial_hits":
                        selected = selected[selected.cutoff == 15]
                        controls = ("baseline", "direct_ei", "random")
                        for method in controls:
                            block = selected[selected.method == method].sort_values(
                                "fraction"
                            )
                            if len(block):
                                axis.plot(
                                    100 * block.fraction,
                                    block[f"top{rank}"],
                                    marker="o",
                                    label=method,
                                )
                        matched = selected[
                            selected.method.str.startswith("initial_")
                            | (
                                (selected.method == "baseline")
                                & (selected.fraction == 0.5)
                            )
                        ].sort_values("fraction")
                        if len(matched):
                            axis.plot(
                                100 * matched.fraction,
                                matched[f"top{rank}"],
                                marker="s",
                                label="retrained_for_fraction",
                            )
                        axis.set_xlabel("Starting hit from worst percentage")
                    else:
                        prefix = (
                            "multi_hit_" if study == "multi_hit" else "top_removal_"
                        )
                        selected = selected[
                            (selected.fraction == 0.5)
                            & (
                                selected.method.str.startswith(prefix)
                                | selected.method.isin(
                                    ["baseline", "direct_ei", "random"]
                                )
                            )
                        ]
                        for method, block in selected.groupby("method"):
                            block = block.sort_values("cutoff")
                            axis.plot(
                                block.cutoff,
                                block[f"top{rank}"],
                                marker="o",
                                label=method,
                            )
                        axis.set_xlabel("Minimum pool size")
                    axis.set_title(f"Purchases to any top-{rank}")
                    axis.set_ylabel("Additional purchases, lower is better")
                    axis.grid(alpha=0.2)
                if axes.flat[0].get_legend_handles_labels()[0]:
                    axes.flat[0].legend(fontsize=7)
                qualifier = (
                    "pools with at least 15 compounds"
                    if study == "initial_hits"
                    else "fixed single-hit evaluation"
                )
                figure.suptitle(
                    f"{endpoint.replace('_', ' ')} | {study.replace('_', ' ')}\nCurrent-model replication, {qualifier}"
                )
                figure.savefig(output / f"{endpoint}_{study}.png", dpi=160)
                document.savefig(figure)
                plt.close(figure)
