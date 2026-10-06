"""Tables and figures from saved evaluations or published summaries.

All-assay aggregates require complete data for every assay.
"""

from pathlib import Path as path_type
import numpy as np
import pandas as pd
import os
from .settings import artifact_root

os.environ.setdefault("MPLCONFIGDIR", str(artifact_root / "matplotlib_cache"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf_pages
from .io import read, write, digest
from .settings import (
    repository_root,
    benchmark_root,
    configured_methods,
    outer_folds,
    configured_endpoints,
)

method_labels = {
    "reference_unchanged": "Original reference architecture",
    "reference_mean_only": "Average mean only",
    "reference_kernel_only": "Average-reference kernel only",
    "reference_weighted": "Kernel-softmax weighted mean",
    "reference": "Current reference",
    "transfer": "Frozen neural ensemble",
    "finetune": "Ordinary fine-tuning",
    "neural_mean_gp": "Neural mean + GP",
    "alpaca": "alpaca_model",
    "alpaca_no_offset": "ALPaCA without offset",
    "maml": "MAML",
    "anil": "ANIL",
    "cnp": "cnp_model",
    "anp": "anp_model",
    "tnp_d": "TNP-D",
    "dkt": "Deep-kernel transfer",
    "adkf_ift": "ADKF-IFT",
    "random": "Random expectation",
}
endpoint_labels = {
    "microsomal_clearance": "Microsomal clearance",
    "in_vivo_clearance": "In vivo clearance",
    "protein_binding": "Plasma protein binding",
    "cellular_clearance": "Cellular clearance",
    "permeability": "Permeability",
    "efflux": "Efflux ratio",
}
method_colors = dict(zip(method_labels, plt.get_cmap("tab20").colors))
method_colors.update(
    reference="#192a3a",
    neural_mean_gp="#0072b2",
    alpaca="#009e73",
    alpaca_no_offset="#d55e00",
    random="#8b8b8b",
)
plot_style = {
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.16,
    "figure.facecolor": "white",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def macro_curves(frame, group, metrics, endpoints):
    """Require each assay at every plotted x value; propagate undefined scores."""
    required = set(endpoints)
    positions = set(frame[group])
    eligible = []
    for method, block in frame.groupby("method"):
        if set(block[group]) != positions:
            continue
        complete = all(
            set(point.endpoint) == required and len(point) == len(required)
            for _, point in block.groupby(group)
        )
        if complete:
            eligible.append(method)
    data = frame[frame.method.isin(eligible)]
    aggregate = (
        data.groupby(["method", group])[metrics]
        .agg(lambda values: values.mean(skipna=False))
        .reset_index()
    )
    return aggregate, eligible


def line_panel(ax, data, x, y, methods, title, xlabel):
    for method in methods:
        block = data[data.method == method].sort_values(x)
        if block.empty:
            continue
        ax.plot(
            block[x],
            block[y],
            marker="o",
            markersize=3,
            linewidth=2.2 if method == "reference" else 1.4,
            linestyle="--" if method in ("random", "alpaca_no_offset") else "-",
            color=method_colors.get(method),
            label=method_labels.get(method, method),
        )
    ax.set(title=title, xlabel=xlabel)
    if x == "context_size":
        ax.set_xticks([1, 2, 3, 5, 10])
    elif x == "cutoff":
        ax.set_xticks([3, 15, 20, 25, 30])


def finish(fig, axes, title, note):
    fig.suptitle(title, x=0.055, ha="left", fontsize=18, weight="bold")
    handles, labels = [], []
    for ax in np.asarray(axes).flat:
        hs, ls = ax.get_legend_handles_labels()
        for h, label in zip(hs, ls):
            if label not in labels:
                handles.append(h)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=9,
        bbox_to_anchor=(0.5, 0.037),
    )
    fig.text(0.055, 0.017, note, fontsize=8, color="#444444")
    fig.tight_layout(rect=(0.035, 0.17, 0.99, 0.93))


def save_figure(fig, name, destination, pdf):
    fig.savefig(destination / f"{name}.png", dpi=180)
    fig.savefig(destination / f"{name}.pdf")
    pdf.savefig(fig)
    plt.close(fig)


def render(prediction, acquisition, coverage, destination, title):
    """Render aggregate and endpoint results; return the saved report path."""
    destination = path_type(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    endpoints = sorted({row["endpoint"] for row in coverage})
    if not endpoints:
        raise ValueError("No complete endpoint results are available")
    metrics = ["r2", "spearman", "nll", "coverage90", "width90"]
    p, prediction_methods = macro_curves(
        prediction[prediction.cutoff == 15], "context_size", metrics, endpoints
    )
    a, acquisition_methods = macro_curves(
        acquisition, "cutoff", [f"top{k}" for k in range(1, 5)], endpoints
    )
    p.to_csv(destination / "all_assays_prediction.csv", index=False)
    a.to_csv(destination / "all_assays_acquisition.csv", index=False)
    report = destination / "performance_report.pdf"
    with plt.rc_context(plot_style), pdf_pages(report) as pdf:
        fig, axes = plt.subplots(2, 3, figsize=(15, 9.8))
        for ax, metric, label in zip(
            axes[0],
            ["r2", "spearman", "nll"],
            [
                "R² · higher is better",
                "Within-series Spearman ρ · higher",
                "Mixture NLL · lower",
            ],
        ):
            line_panel(
                ax,
                p,
                "context_size",
                metric,
                prediction_methods,
                label,
                "Measured compounds",
            )
        for k, ax in enumerate(axes[1], 1):
            line_panel(
                ax,
                a,
                "cutoff",
                f"top{k}",
                acquisition_methods,
                f"Purchases to any top-{k} · lower",
                "Minimum pool size",
            )
        omitted = sorted(set(prediction.method) - set(prediction_methods))
        note = "Equal assay averages. Prediction pools ≥15; fixed hidden queries. One free hit; K=1 Gaussian moment EI."
        if omitted:
            note += (
                " Incomplete aggregate: "
                + ", ".join(method_labels[m] for m in omitted)
                + "."
            )
        finish(fig, axes, title, note)
        save_figure(fig, "all_assays_overview", destination, pdf)

        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        for k, ax in enumerate(axes.flat, 1):
            line_panel(
                ax,
                a,
                "cutoff",
                f"top{k}",
                acquisition_methods,
                f"Purchases to any top-{k} · lower",
                "Minimum pool size",
            )
        finish(
            fig,
            axes,
            "Acquisition | equal assay averages",
            "One free worse-half hit; ties qualify. Every curve requires all configured assays and folds.",
        )
        save_figure(fig, "all_assays_acquisition", destination, pdf)

        # Relative scores use an explicit common comparator and matching panel.
        score = a[a.cutoff == 15].set_index("method")
        nll = p[p.context_size == 5].set_index("method")
        methods = [m for m in score.index if m != "random"]
        if "random" in score.index and "reference" in nll.index:
            values = pd.DataFrame(
                {
                    "method": methods,
                    "fewer_top1_purchases_vs_random_percent": [
                        100 * (1 - score.loc[m, "top1"] / score.loc["random", "top1"])
                        for m in methods
                    ],
                    "nll_difference_vs_reference": [
                        (
                            nll.loc[m, "nll"] - nll.loc["reference", "nll"]
                            if m in nll.index
                            else np.nan
                        )
                        for m in methods
                    ],
                }
            )
            values.sort_values("fewer_top1_purchases_vs_random_percent", inplace=True)
            values.to_csv(destination / "relative_performance.csv", index=False)
            fig, axes = plt.subplots(1, 2, figsize=(14, 8))
            labels = [method_labels[m] for m in values.method]
            for ax, field, label in zip(
                axes,
                [
                    "fewer_top1_purchases_vs_random_percent",
                    "nll_difference_vs_reference",
                ],
                [
                    "Fewer top-1 purchases than random (%) · higher",
                    "NLL minus current reference · lower",
                ],
            ):
                ax.barh(
                    labels,
                    values[field],
                    color=[method_colors[m] for m in values.method],
                )
                ax.axvline(0, color="#222222", linewidth=0.8)
                ax.set_xlabel(label)
            fig.suptitle(
                "Relative performance on series with at least 15 compounds",
                fontsize=17,
                weight="bold",
            )
            fig.text(
                0.035,
                0.025,
                "Equal assay averages; NLL at five measured compounds. Descriptive comparisons, without significance claims.",
                fontsize=9,
            )
            fig.tight_layout(rect=(0, 0.055, 1, 0.94))
            save_figure(fig, "relative_performance", destination, pdf)

        for endpoint in endpoints:
            pred = prediction[
                (prediction.endpoint == endpoint) & (prediction.cutoff == 15)
            ]
            acq = acquisition[acquisition.endpoint == endpoint]
            methods = sorted(set(pred.method))
            fig, axes = plt.subplots(2, 3, figsize=(15, 9.8))
            for ax, metric, label in zip(
                axes.flat,
                metrics + ["pools"],
                [
                    "R² · higher",
                    "Within-series Spearman ρ · higher",
                    "Mixture NLL · lower",
                    "90% interval coverage",
                    "90% interval width",
                    "Eligible series",
                ],
            ):
                line_panel(
                    ax,
                    pred,
                    "context_size",
                    metric,
                    methods,
                    label,
                    "Measured compounds",
                )
                if metric == "coverage90":
                    ax.axhline(0.9, color="#777777", linestyle=":", linewidth=1)
            finish(
                fig,
                axes,
                endpoint_labels.get(endpoint, endpoint) + " | prediction",
                "Five-fold held-out predictions; pools ≥15; fixed hidden queries. Uncalibrated native mixture intervals.",
            )
            save_figure(fig, endpoint + "_prediction", destination, pdf)
            fig, axes = plt.subplots(2, 2, figsize=(13, 9))
            for k, ax in enumerate(axes.flat, 1):
                line_panel(
                    ax,
                    acq,
                    "cutoff",
                    f"top{k}",
                    sorted(set(acq.method)),
                    f"Purchases to any top-{k} · lower",
                    "Minimum pool size",
                )
            finish(
                fig,
                axes,
                endpoint_labels.get(endpoint, endpoint) + " | acquisition",
                "One free worse-half hit; ties qualify. Random curve is an exact expectation. No hidden labels enter model calls.",
            )
            save_figure(fig, endpoint + "_acquisition", destination, pdf)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.axis("off")
        incomplete = [r for r in coverage if not r.get("included", False)]
        text = [
            "Coverage and interpretation",
            "",
            "Only complete endpoint/method fold sets enter the plotted summaries.",
            f"All-assay averages additionally require all {len(endpoints)} configured assays at every plotted position.",
            "ALPaCA without offset reuses the selected offset-model hyperparameters and trains fresh weights.",
            "R² is a weighted pooled statistic; Spearman is an average of within-series rankings.",
            "NLL evaluates the native predictive mixture, while EI uses its Gaussian moments.",
            "Charts summarize the saved development-fold evaluations.",
            "",
        ]
        text += [
            f"Unavailable: {r['endpoint']} / {r['method']} ({r['completed_folds']} complete folds)"
            for r in incomplete
        ]
        ax.text(0.03, 0.95, "\n".join(text), va="top", fontsize=12, linespacing=1.7)
        pdf.savefig(fig)
        plt.close(fig)
    write(
        destination / "figure_manifest.json",
        dict(
            report=report.name,
            source="saved summary tables; no training by plotting",
            endpoints=endpoints,
            aggregate_prediction_methods=prediction_methods,
            aggregate_acquisition_methods=acquisition_methods,
            incomplete_conditions=[r for r in coverage if not r.get("included", False)],
        ),
    )
    return report


def report_published():
    """Recreate the repository figures from the included published numeric tables."""
    source = repository_root / "results" / "published"
    main, offset = source / "main", source / "offset"
    prediction = pd.concat(
        [
            pd.read_csv(main / "prediction_summary.csv"),
            pd.read_csv(offset / "prediction_summary.csv").query(
                "method == 'alpaca_no_offset'"
            ),
        ],
        ignore_index=True,
    )
    acquisition = pd.concat(
        [
            pd.read_csv(main / "acquisition_summary.csv"),
            pd.read_csv(offset / "acquisition_summary.csv").query(
                "method == 'alpaca_no_offset'"
            ),
        ],
        ignore_index=True,
    )
    coverage = read(main / "coverage.json") + [
        dict(
            endpoint=e,
            method="alpaca_no_offset",
            completed_folds=5,
            included=True,
            failures=[],
        )
        for e in prediction.endpoint.unique()
    ]
    destination = repository_root / "results" / "figures"
    report = render(
        prediction,
        acquisition,
        coverage,
        destination,
        "Chemical-series adaptation | all assays",
    )
    write(
        destination / "input_hashes.json",
        {str(p.relative_to(repository_root)): digest(p) for p in source.rglob("*.csv")},
    )
    print(report)


def report_run():
    """Summarize a newly completed run, excluding incomplete fold comparisons."""
    from .evaluation import summaries, paired_acquisition_intervals

    prediction, points, acquisition, coverage = [], [], [], []
    for endpoint in configured_endpoints:
        random_added = False
        for method in configured_methods:
            paths = [
                benchmark_root / "evaluations" / f"fold_{f}" / endpoint / method
                for f in outer_folds
            ]
            complete = [(p / "completed.json").exists() for p in paths]
            coverage.append(
                dict(
                    endpoint=endpoint,
                    method=method,
                    completed_folds=sum(complete),
                    included=all(complete),
                    required_folds=len(outer_folds),
                )
            )
            if not all(complete):
                continue
            for path in paths:
                prediction.extend(read(path / "prediction_cases.json"))
                points.extend(read(path / "prediction_points.json"))
                rows = read(path / "acquisition.json")
                acquisition.extend(rows)
                if not random_added:
                    for row in rows:
                        baseline = {
                            k: v
                            for k, v in row.items()
                            if k
                            not in ("method", "order", "top1", "top2", "top3", "top4")
                        }
                        baseline.update(
                            method="random",
                            **{f"top{k}": row[f"random_top{k}"] for k in range(1, 5)},
                        )
                        acquisition.append(baseline)
            random_added = True
    destination = benchmark_root / "reports"
    write(destination / "coverage.json", coverage)
    if not prediction:
        raise RuntimeError("No complete fold comparison to report; see coverage.json")
    pred, acq = summaries(prediction, points, acquisition)
    pred, acq = pd.DataFrame(pred), pd.DataFrame(acq)
    pred.to_csv(destination / "prediction_summary.csv", index=False)
    acq.to_csv(destination / "acquisition_summary.csv", index=False)
    pd.DataFrame(paired_acquisition_intervals(acquisition)).to_csv(
        destination / "paired_acquisition_intervals.csv", index=False
    )
    return render(
        pred, acq, coverage, destination, "Chemical-series adaptation | new run"
    )
