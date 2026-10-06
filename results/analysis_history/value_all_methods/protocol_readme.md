# All value-learning methods across all six datasets

This study extends the complete microsomal value-learning experiment to in vivo clearance, plasma protein binding, cellular clearance, A→B permeability and efflux ratio. It includes every method from the original comparison.

The experiment is complete. All 1,348 jobs succeeded, and the completion audit verified matched coverage, unchanged source files and identical reused results. The [20-page PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/reports/all_value_methods_all_datasets.pdf) contains all eleven methods, with endpoint-specific top-1–4 charts for pools of at least 3 and at least 15 compounds and curves across pool-size cutoffs. [Full numerical results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/reports/results.md) and the [completion audit](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/completion_audit.json) are available alongside it.

| Method | Model or acquisition rule |
| --- | --- |
| Compact value | Candidate prediction summaries with pooled set context |
| Set-pooling value | Learned MiniMol projections and mean/max pooling over observed and available molecules |
| Attention value | Learned MiniMol projections and two layers of attention over the pool |
| Selected value | Architecture and refinement selected separately within each endpoint and outer fold |
| Value + lookahead | The selected value model with shallow outcome-sampled lookahead |
| Value + tree search | The selected value model with chance-node Monte Carlo tree search |

Random expectation, delta greedy, Gaussian process plus expected improvement, original neural acquisition process (NAP), and revised NAP are retained as baselines. Every comparison uses the existing grouped five-fold split, three seeds for neural methods and four identical worst-half starting hits per held-out pool. The study covers 4,625 pools, of which 580 contain at least 15 compounds.

NAP controllers use clipped Proximal Policy Optimization (PPO), with critics providing training baselines. The value methods use Double-Q cost learning and select actions through their learned costs. The [optimizer explanation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/policy_optimization.md) documents the returns, losses, settings and distinctions from other policy optimization algorithms.

## Reuse and isolation

The complete microsomal comparison is reused exactly. The other endpoints' compact base and longer-training fits, selected checkpoints, transition banks and test trajectories are reused from the completed compact-model extension. All original files remain read-only inputs. Reused compact selected checkpoint hashes must match their prior versions exactly.

New results are written under this directory. Each endpoint has its own fold directories, training histories, model checkpoints, validation comparisons, search selections and held-out trajectories. The experiment uses CPU workers in the existing analysis environment; no manual GPU job is required.

## Training and selection

The original development procedure is repeated separately for every additional endpoint and outer fold.

1. Compare compact, set-pooling and attention architectures with seed 11 and up to 1,800 updates.
2. Refine the two strongest architectures with four predefined variants, each allowing 1,800 additional updates: longer training, balanced small/large-pool sampling, regularization toward exact random-policy returns, and auxiliary top-2/3/4 targets with that regularization.
3. Select a recipe using only that fold's validation data. The criterion weights random-normalized top-1 purchase counts 75% for pools of at least 15 compounds and 25% for all pools.
4. Repeat all three baseline architectures and the selected recipe with seeds 11, 29 and 47. Retain the better base or refinement validation checkpoint. Each recipe has at most 1,800 plus 1,800 updates.
5. Screen four planning settings, then test the strongest lookahead and tree-search settings at two additional blending weights. Select using seed 11 validation cases and apply the settings to all three final seeds.
6. Lock selected models and search settings before evaluating their new held-out trajectories.

There are 55 architecture-development comparisons and 40 planning comparisons per endpoint, before seed replication. Microsomal comparisons and eligible compact fits are reused. The five additional endpoints therefore add 275 architecture-development comparisons and 200 planning comparisons, including those reusable compact trials.

The same 40-transition-per-training-pool banks are shared by all architectures. Double-Q cost learning uses revealed relative transformed outcomes. Training cost is one until a qualifying target has been observed and zero thereafter. Full trajectories continue through pool exhaustion. Their cumulative costs match retrospective purchases to reach a qualifying compound, without supplying a hidden success flag to the policy.

The delta predictor keeps its original separate training allocation. Delta features are the mean and sample standard deviation of measured-value-plus-predicted-difference estimates over observed anchors; the standard deviation is zero for a singleton. Training-state GP summaries use source-group-excluded teachers. No sign-consistency regularization is added.

## Planning

Lookahead and tree search use the **selected value model**, so their matched parent is the “Selected value” comparison. Gaussian-process quantiles supply hypothetical observations, and conditioning updates the full covariance. The candidate shortlist includes value-preferred, expected-improvement-preferred and high-variance candidates. Learned costs estimate value beyond the search horizon.

Search is limited to the first eight real purchases, followed by direct value selection. Lookahead considers one or two future purchases. Tree search uses depth three and 32 or 64 simulations. Search costs are blended with direct value costs using a validation-selected weight. All limits depend on observable state and purchase count, never on hidden success.

## Metrics and endpoints

Only additional purchases to any top-1, top-2, top-3 or top-4 compound are used in performance charts. The initial hit is free. Ties at the rank boundary qualify, and already qualifying starts cost zero. Top-4 is therefore zero in pools of three or four. Starts are averaged within pool and seed, then seeds, then pools.

| Endpoint | Preserved objective |
| --- | --- |
| Microsomal and in vivo clearance | Lower log10 clearance |
| Cellular clearance | Lower log10 clearance |
| Protein binding | Lower log10((1−fu)/fu), hence higher unbound fraction |
| A→B permeability | Higher log10 permeability |
| Efflux ratio | Lower log10(B→A/A→B), following curated row annotations |

Efflux follows the curated B→A/A→B direction. Species and assay contexts retain separate pools. Clearance and binding use human, rat, and mouse observations; permeability and efflux use human/dog-derived assays. Dog is the reference category for the Human/Rat/Mouse indicators.

## Interpretation

The extension retains the original search space. Configuration selection uses the available validation pools within each endpoint/fold.

Paired bootstrap intervals resample source groups within endpoint, conditional on fitted models and without multiplicity adjustment. Compute budgets are recorded by method.

## Artifacts and reproducibility

- [Experiment plan](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/experiment_plan.json)
- [Progress](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/progress.json)
- [Main runner](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/experiment.py)
- [Individual training and evaluation jobs](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/worker.py)
- [Source and fold audit](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/source_audit.json)

`benchmark_completed.json` marks successful training and evaluation. `completed.json` marks verified report completion. The report produces a combined 20-page PDF, a three-page PDF for each endpoint, charts at minimum pool sizes 3 and 15, minimum-pool-size curves, full metric tables, paired uncertainty intervals, development records and inference runtimes.

To resume the CPU experiment or regenerate its reports from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/experiment.py
```

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/report.py
```

An exclusive lock prevents simultaneous runners. Successful jobs are cached. New configurations belong in a separate study directory to preserve the meaning of cached results and locked checkpoints.
