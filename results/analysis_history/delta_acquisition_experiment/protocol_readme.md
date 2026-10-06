# Pairwise-delta features for acquisition

This experiment implements the requested predictor and dynamic reinforcement-learning features. The predictor uses one forward pass through a multilayer perceptron on the ordered concatenation of two full 512-dimensional Minimol representations. Its target is query log10 clearance minus anchor log10 clearance. It has no sign-consistency constraint or reversed-pair averaging.

At each acquisition step, the model predicts a delta from every already measured molecule in the current series to each query. Adding the measured molecule's outcome relative to the initial hit gives several estimates of the same query outcome. Their mean and sample standard deviation are appended to the query representation. The standard deviation is zero with one measured molecule. All measurements from unpurchased molecules remain hidden.

The 1,827 curated search pools are allocated to disjoint predictor and reinforcement-learning halves of 913 and 914 pools. Shared molecules and series variants remain in the same half and data split. Each half has its own training, validation, and test subsets. The preceding experiment's 244 test pools are preserved. The delta predictor is frozen during policy training.

The policy comparison uses three paired training seeds for NAP with and without the two added features. Both variants use full 512-dimensional embeddings. The control has two constant-zero extra input coordinates, so network shapes and initial weights match. Random purchasing and greedy selection using the delta-model mean provide additional comparisons.

## Results and files

- [Prediction accuracy on identical observed contexts](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/matched_predictor_accuracy/report.md). Compares the delta predictor with NAP before and after reinforcement learning, using the same starting molecules and nested random measured contexts.
- [What the learned policy adds](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/policy_interpretation/report.md). Frozen-model diagnostics compare the acquisition head with greedy selection and expected improvement using its own predictor, and with retaining its initial ranking throughout the episode.
- [Cumulative pool-size cutoffs and line graphs](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/size_thresholds/report.md). Cutoffs run from ≥15 through ≥50; `plot_acquisition_cutoffs.py` generates the acquisition comparison with pool and provenance-group counts.
- [Performance by series size, emphasizing pools with at least 15 molecules](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/size_analysis/report.md). This is the user's primary population for future model selection and evaluation; smaller pools remain useful training data. Existing models were not retrained for this analysis.
- [Results report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/report.md)
- `delta_model.py` defines, trains, and evaluates the plain concatenation predictor.
- `experiment.py` contains `delta_summary` and the revealed-only state constructor.
- `prepare_data.py` creates the disjoint halves and training-only input scalers.
- `models.py` and `train_models.py` implement the compact NAP adaptation and training.
- `train_rl.py` runs the matched control and augmented policies.
- `evaluate_delta_rl.py` writes acquisition metrics, comparisons, and figures.
- `settings.py` contains ordinary editable constants and absolute paths.
- `data/` contains the allocation, scalers, and frozen pairwise prediction cache.
- `results/` contains the delta predictor, policy checkpoints, training logs, test trajectories, and reports.

## Run from any directory

The existing task environment already contains the dependencies. No command-line arguments are needed.

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/test_delta_features.py
```

The full experiment entry point is

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/run_experiment.py
```

A completed run is preserved. For a new run, set new absolute `DATA` and `ROOT_RESULTS` paths in `settings.py`, both inside this task's workspace. Keep each frozen delta cache with the predictor checkpoint that created it. All products are written back to the working directory. This experiment uses the CPU; GPU execution has not been tested or required.

The standard deviation measures disagreement among anchor-based estimates. Measurement curation and median-log repeat aggregation follow the preceding experiment.
