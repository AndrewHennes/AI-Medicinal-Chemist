# Initial-hit experiments

Both experiments were implemented and their isolated two-step end-to-end checks passed on 2026-09-24. Scientific training runs on CPU in detached, resumable runners. Do not start duplicate runners. Each holds an exclusive runner.lock.

## Percentile study

Runner: `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/run_hit_sensitivity.py`

Output: `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/initial_hit_sensitivity`

The original and revised single-task NAPs, GP + EI, delta greedy and exact random expectation are compared over six endpoints and five unchanged grouped folds. New training conditions use the worst 10, 20, 30 and 40 percent. The original 50-percent checkpoints are reused and evaluated at all five test percentages as a control. Delta fits are independent of initial hits and reused throughout. Four matched starts and three neural-policy seeds per pool. The fresh matched test bank also applies to the existing 50-percent checkpoints, so scores can differ slightly from earlier PDFs.

Read progress.json, runner.log, and jobs/*.json for current progress. Stages: 120 baseline jobs, 480 teacher jobs, 360 revised-controller jobs, 150 evaluation jobs, then reports. The large baseline jobs each include a GP and three original NAP seeds. Six processes run concurrently. All scientific fits lock before evaluation.

Final reports, once completed.json exists:

- reports/starting_hit_sensitivity.pdf (15 pages)
- reports/all_fractions_minimum_pool_cutoff.pdf (36 pages)
- reports/worst_XX_minimum_pool_cutoff.pdf (7 pages each)
- reports/paired_retraining_purchase_differences.csv

## Additional lower-half measured sets

Runner: `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/run_multihit_augmentation.py`

Output: `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/lower_half_multihit_augmentation`

The runner is already launched and waits for initial_hit_sensitivity/completed.json. It then trains automatically; it does not choose settings from percentile test results.

Reference sampling remains worst 50 percent. Half of eligible training draws use random measured sets of size 2, 3, 4 or 5 drawn entirely from the worse half, uniformly over feasible sizes. The original reference is included; all outcomes remain relative to it. The other half retain the original recipe. Pools with three compounds cannot provide extra worse-half measurements. Validation and test remain single-hit. All existing transforms, grouping and seeds are preserved, with no sign-consistency additions.

Both NAPs and the revised policy's neural teachers retrain; all GP and delta fits are reused. The same supervised-iteration and sampled-episode budgets are retained. Multi-hit episodes contain fewer acquisition steps, so actual PPO state/update counts can be lower. This is one combined augmentation experiment, not four separately tuned architectures.

Stages: 30 original-policy jobs (three seeds each), 120 neural-teacher jobs, 90 revised-controller jobs, 30 evaluations, then report. The reference 50-percent scores come from the first experiment's identical case bank. Final PDF: reports/single_task_multihit_augmentation.pdf (8 pages).

## Verification and cautions

Four sampler unit tests and four multi-hit sampling/reward tests passed. Both studies passed isolated tiny full-pipeline checks with a nonzero task index (permeability, task 3). Existing 50-percent checkpoints were also tested on all five hit fractions in a separate smoke root. Scientific roots retain all original training budgets. All source data, feature scalers, original checkpoints and inner teacher assignments are preserved. Immutable features and reused checkpoints may be hardlinks: never train over those files or modify them in place.

Reports contain only purchases to any top-1, top-2, top-3 and top-4 compound. Initial observations are free, boundary ties count, and random is analytical. Top-4 is zero for pools of size 3 or 4. Overall means are equal-weighted across endpoints. Augmentation's paired bootstrap resamples evaluation source groups with models fixed, not a full refit bootstrap.

Use the Python runtime at `/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python`. Check completed.json before describing either scientific benchmark as finished. Smoke results are explicitly excluded from reports. Earlier user PDFs are left intact.
