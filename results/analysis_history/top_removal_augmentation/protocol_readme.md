# Cumulative removal of top compounds during NAP training

This experiment tests one mixed augmentation recipe for the old and new single-task neural acquisition process (NAP) models across all six datasets. It preserves the five grouped outer folds, three neural seeds, original transformed outcomes, worst-half single starting hits, and purchases-to-top-1/2/3/4 evaluation.

The experiment is complete. All 270 jobs and 300 neural fits succeeded, and the final audit verified that the original five methods reproduce their previous metrics exactly. The [20-page PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/reports/top_removal_augmentation_all_endpoints.pdf), [complete numerical results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/reports/results.md), and [completion audit](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/completion_audit.json) are available.

The comparison has seven curves. Random, single-task delta greedy and Gaussian process plus expected improvement are unchanged. Old NAP and new NAP each appear with and without augmentation. There are no value-based acquisition methods in this study.

## Training recipe

The existing sampler first chooses a source training pool. If it contains at least four molecules, half of draws keep the full pool and half remove a uniformly sampled feasible number of its best molecules, from one through five. At least three molecules remain. Thus a pool of size four supports removal of one; a pool of size eight or more supports all five removal depths. Pools of three remain unchanged.

Removal is cumulative. With distinct outcomes, removing the best three compounds makes the original fourth-best compound the new optimum. Exactly the requested number of molecules is removed, with random tie ordering. A best-value tie spanning the removal boundary can therefore leave the best numerical value unchanged. Survivor order is preserved to avoid encoding rank through the sequence of model inputs.

One hit is then drawn from the worst half of the remaining pool. The model observes outcomes relative to that hit. Molecular features and both axes of the pairwise delta matrix are subset consistently. Removed compounds cannot contribute candidate features, measured anchors or pool summaries. Gaussian-process caches are rebuilt for each reduced pool; group metadata and teacher assignments stay with the parent pool.

Augmentation is applied to old-NAP supervised examples and policy rollouts, the new NAP's neural forecasters, its controller warm start, and its policy rollouts. The forecasters retain source-group exclusion. Both controllers retain clipped Proximal Policy Optimization (PPO). Delta predictors and Gaussian-process models, including group-excluded GP teachers, are reused unchanged. No sign-consistency penalty or multi-hit augmentation is added.

The augmentation uses fixed supervised-step and episode budgets. Trajectory lengths determine the number of PPO minibatches.

## Evaluation and interpretation

Validation retains its original complete pools, sampled contexts, starting-hit distribution and checkpoint-selection criteria. No architecture or learning-rate search is performed. All new checkpoints are hashed before test evaluation.

Test evaluation uses original complete pools and four identical worst-half starting hits. The initial hit is free. Success means observing any compound within the target top one, two, three or four, including ties at the rank boundary. Already successful starts cost zero. Complete acquisition orders are generated without oracle stopping. The study covers 4,625 pools, including 580 with at least 15 molecules.

Charts use minimum pool sizes 3 and 15 and size-cutoff curves. Paired 95% intervals resample source groups conditional on fitted models and without multiplicity adjustment.

## Artifacts

- [Experiment plan](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/experiment_plan.json)
- [Progress](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/progress.json)
- [Augmentation implementation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/top_removal.py)
- [Source and split lock](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/source_lock.json)
- [End-to-end smoke verification](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/smoke_verification.json)

The runner executes 30 original-NAP jobs with three seeds each, 120 neural-forecaster jobs, 90 revised-NAP controller jobs, and 30 matched evaluation jobs. Original-NAP fits and independent forecaster fits run together. Controllers follow after all forecasters finish.

The combined PDF is written to `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/reports/top_removal_augmentation_all_endpoints.pdf`. This is a 20-page report with methods, a top-1 overview and three pages per endpoint. Separate endpoint PDFs, complete metric tables, matched differences and actual augmentation-sampling counts are also produced. `benchmark_completed.json` marks successful training/evaluation; `completed.json` marks verified report completion.

To resume the experiment from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/experiment.py
```

To regenerate completed results:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/report.py
```

All paths are absolute. An exclusive lock prevents simultaneous runners, and successful jobs are cached. New configurations should use a separate study directory to preserve existing results and source locks.
