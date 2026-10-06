# Distance-aware neural ensemble, K=1

This benchmark evaluates the existing trained distance-aware neural ensemble as a sequential acquisition engine, with a single purchase followed by an update of the measured context. It performs no new predictor or policy training.

The main result is in [the PDF report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty_k1/reports/distance_aware_neural_K1_report.pdf). Tables, linked-group bootstrap intervals, endpoint plots, and all saved acquisition trajectories are alongside it and in the evaluation directory.

All paths resolve against `/Users/asselism/Documents/Codex/2026-09-23/i-h`, independent of the caller's working directory. The Python runtime is `/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python`.

- `acquisition_core.py` implements measured-only states, exact Gaussian-mixture expected improvement, and retrospective acquisition evaluation.
- `run_experiment.py` locks input checkpoints and calibration, then evaluates 30 endpoint/fold bundles using eight CPU workers. It resumes completed bundles.
- `tests.py` checks cached versus original neural predictions, context permutation invariance, unseen-outcome isolation, expected improvement, GP updates, tied outcomes, and exact random expectations.
- `report.py` independently audits trajectories and generates the report. It reproduces the historical current-GP acquisition results exactly.
- `protocol.json` records the prespecified primary acquisition rule, evaluation population, controls and limitations.
- `input_lock.json` and `source_lock.json` identify the inputs and implementation.

The primary rule uses validation-calibrated mixture EI from three independently fitted neural models. The current and original GP controls each use their established seed11 predictor. All use the original predictor-role training split, five held-out folds, and four identical starting hits per test pool from its worse half. The initial hit is free. Top-k means purchases to reach any of the k best compounds, including ties.

Outcomes use the transformed objective relative to the starting hit. The neural predictor trains with up to nine additional measurements. Evaluation retains all context and records its size.

Uncalibrated EI, greedy selection, and the single-model version are reported as fixed ablations on the exploratory benchmark.
