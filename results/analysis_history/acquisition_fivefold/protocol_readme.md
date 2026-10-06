# Five-fold acquisition comparison

All training and evaluation are complete. The current reports contain only purchases needed to reach any top-1, top-2, top-3 or top-4 compound. The initial hit is free, boundary ties qualify, and top-k includes every molecule when k is at least the pool size.

[Open the charts](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/five_fold_acquisition_comparison.pdf) or [read the results and model definition](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/report.md). Individual endpoint PDFs and numerical tables are in [the report directory](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports). Previous metric reports are stored in the historical archive.

The comparison now contains 13 methods. The added single-task and multitask delta + expected improvement baselines reuse the existing fold-specific delta predictors and use every unique training molecule from the corresponding predictor’s delta-training partition as an anchor. The normal approximation uses the mean and sample standard deviation of delta(query, anchor) minus delta(current best measured molecule, same anchor). No training-anchor labels, validation molecules, or test molecules enter the anchor set. No predictor was retrained and no sign-consistency constraint was added. The spread measures anchor disagreement.

Every one of the 2,798 curated pools appears in exactly one of five outer test folds. All 269 pools with at least 15 compounds are included. Related source documents, molecules and species/endpoint pools remain together. Four matched worse-half starting draws are used per pool. Three neural-policy seeds are averaged; deterministic delta and GP baselines each use one model per fold.

| Fold | Test pools | Source groups | Test pools ≥15 |
| --- | ---: | ---: | ---: |
| 1 | 757 | 138 | 54 |
| 2 | 509 | 244 | 53 |
| 3 | 511 | 244 | 54 |
| 4 | 511 | 244 | 54 |
| 5 | 510 | 244 | 54 |

One source group contains 620 pools and is kept intact. Allocation used endpoint counts and pool sizes, never model performance. Within each outer training partition, target proportions were 45% delta training, 5% delta validation, 45% acquisition training and 5% acquisition validation. Actual fractions differ because groups stay intact. Feature scalers, outcome scales, predictors, Gaussian processes and policies were originally refitted per outer fold. Revised policies also use three inner teacher folds within acquisition training, retaining common outer-training scales.

This update changes reported evaluation metrics and adds two acquisition strategies. Policy rewards and checkpoint selection criteria follow the original training protocol. Paired intervals use source-group resampling conditional on saved predictions.

[run_cross_validation.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/run_cross_validation.py) is the complete resumable runner. [run_delta_ei.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/run_delta_ei.py) evaluates the added baselines from saved delta checkpoints. [report_cross_validation.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/report_cross_validation.py) audits the folds and rebuilds only the current purchase-count reports. All entry points use absolute paths and require no command-line options. Models and data remain under this workspace.

## Microsomal stability extension

The [simplified single-task PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/single_task_minimum_pool_cutoff.pdf) includes microsomal stability, with seven pages covering all six endpoints and an equally weighted overall curve. The extension contributes 1,827 pools, including 311 with at least 15 molecules, evaluated using fresh microsomal-only grouped folds. The original five endpoint results are unchanged. [Microsomal methods and results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/microsomal_stability/reports/report.md).
