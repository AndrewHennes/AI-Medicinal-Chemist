# Clearance acquisition experiment

This folder contains a completed CPU pilot comparing a compact Neural Acquisition Processes (NAP) adaptation, a transfer Gaussian-process Expected Improvement (GP-EI) baseline, the pretrained neural predictor with EI, and exact random-search expectations. Read the [results report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_experiment/results_cpu_pilot/report.md) for methods, results, and limitations.

The objective is the number of additional purchases until an optimal compound is first acquired. Starts are sampled from the higher-clearance half of a species-specific analog series. Outcomes are log10 clearance relative to the start. The initial molecule is free. The policy receives no hidden labels, oracle success flag, or early termination signal. Complete purchase trajectories are scored retrospectively.

## Files

- `settings.py` contains editable constants and absolute input/output paths.
- `prepare_dataset.py` selects assay groups, aggregates comparable repeats on the log scale, creates grouped splits, and fits feature preprocessing only on training molecules.
- `models.py` defines the NAP adaptation and reference-relative Matérn Gaussian process.
- `experiment.py` constructs revealed-only observations and complete trajectories.
- `train_models.py` trains the shared GP prior and NAP with auxiliary prediction plus Proximal Policy Optimization.
- `evaluate_models.py` evaluates matched test starts, calculates group-bootstrap intervals, and writes tables, plots, and the report.
- `test_experiment.py` checks masking, leakage, reference invariance, scoring, GP conditioning, and EI numerics.
- `data/` contains prepared labels, frozen preprocessing, split assignments, and audit tables.
- `results_cpu_pilot/` contains validation logs, trained checkpoints, test trajectories, and results.

## Running from any directory

The task's isolated Python environment is already installed. No command-line options are needed.

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_experiment/test_experiment.py
```

The complete experiment entry point is

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_experiment/run_cpu_pilot.py
```

The completed pilot is preserved. To train a new configuration, first change `RESULTS` in `settings.py` to a new absolute directory within this workspace. The existing dataset and grouped split can be reused. If changing the feature dimension or preparation protocol, also choose a new `DATA` directory so preprocessing is regenerated. All model checkpoints, datasets, and reports are written within this task's workspace.

The pilot uses CPU execution with `DEVICE` set to `cpu`.

## Interpretation

This experiment uses one grouped split and two neural training seeds. Both models use the same 32-dimensional projection of supplied Minimol embeddings, fitted only on unique training molecules. The GP receives historical training outcomes through its shared mean and covariance parameters. The NAP reward and rollout protocol implement the first-optimum objective.

Methods are evaluated against fixed consensus labels. Repeat aggregation and source conversions are documented in the audit.
