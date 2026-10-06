# Compact value model across all six datasets

This completed extension evaluates the compact value architecture from the microsomal study independently on microsomal clearance, in vivo clearance, plasma protein binding, cellular clearance, A→B permeability and efflux ratio. It uses the existing five grouped outer folds and three neural seeds. The completed microsomal compact-model results are reused exactly. Seventy-five additional endpoint/fold/seed models were fitted for the other five datasets.

The architecture and training settings are fixed across endpoints. This is an endpoint-specific model comparison, not multitask training or cross-endpoint checkpoint transfer. The larger value architectures and explicit search variants are not repeated in this extension.

## Model and training

The candidate model consumes 12 prediction and observation summaries, pooled observed/available-set summaries, and eight context features. These are the same inputs as the previous compact microsomal model. The underlying Gaussian-process and delta predictors use MiniMol embeddings. The value network does not learn another projection of the raw MiniMol representation.

Each fit receives 1,800 initial updates and 1,800 further updates initialized from its best base checkpoint. The better validation checkpoint across both phases is retained. The training bank contains 40 transitions per training pool. Double-Q updates target expected additional purchases to reach a top-1 item. The initial warm-up uses exact expected returns for buying the specified candidate and then sampling randomly.

Measured outcomes are differences from the initial hit, in the existing transformed units divided by a training-derived scale. At training time, hidden target ranks determine cost labels, but hidden outcomes and optimum-found signals never enter model inputs. Trajectories continue to pool exhaustion and are scored retrospectively. The tests cover the information boundary, metric/return agreement, GP conditioning, and permutation behavior.

There is no sign-consistency loss. The delta feature for a query is the mean and sample standard deviation of observed-value-plus-predicted-difference estimates. Its standard deviation is zero for a single observed anchor. Gaussian-process summaries for training pools come from group-excluded teachers; validation and test use the corresponding full acquisition-training GP. The frozen delta model retains its disjoint training allocation.

Species context retains Human/Rat/Mouse indicators. Dog, which occurs in permeability and efflux pools, is the implicit reference category with all three indicators zero. The generic data loader was checked against the original microsomal implementation and produces identical microsomal input arrays.

## Objectives and data

| Endpoint | Existing objective |
| --- | --- |
| Microsomal clearance | Lower log10 clearance |
| In vivo clearance | Lower log10 clearance |
| Protein binding | Lower log10((1−fu)/fu), hence higher unbound fraction |
| Cellular clearance | Lower log10 clearance |
| A→B permeability | Higher log10 permeability |
| Efflux ratio | Lower log10(B→A/A→B), following curated row annotations |

Efflux uses the curated B→A/A→B direction. Clearance and protein-binding pools use human, rat, and mouse observations. Permeability and efflux use human/dog-derived assays. Species and assay contexts retain separate pools.

The study covers 4,625 pools, including 580 pools with at least 15 compounds. Four held-out starting molecules per pool are exactly matched to the existing 50% starting-hit benchmark. Each start comes from the least favorable half of its pool.

## Evaluation

The six displayed methods are random expectation, delta greedy, Gaussian process plus expected improvement, original NAP, revised NAP, and the compact value model. NAP means neural acquisition process. Existing baseline trajectories are reused on identical test starts.

Only additional purchases to any top-1, top-2, top-3 or top-4 compound are performance metrics. The initial hit is free. Rank-boundary ties qualify, and already successful starts score zero. Top-4 is consequently zero in pools of three or four. Results average starts within pool and seed, then neural seeds, then pools. Pools of at least three and at least 15 compounds are reported separately, with additional minimum-pool-cutoff curves.

Paired bootstrap intervals resample source groups within endpoint, conditional on fitted models and without multiplicity adjustment.

Checkpoint selection weights normalized large-pool top-1 counts 75% and all-pool top-1 counts 25%, using validation data.

## Files and execution

- [Experiment specification](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/experiment_plan.json)
- [Training and evaluation runner](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/experiment.py)
- [Training implementation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/learning.py)
- [Source and fold audit](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/source_audit.json)
- [Progress](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/progress.json)

Each endpoint has its own fold directories containing transition banks, model checkpoints, validation histories and held-out trajectories. `implementation_lock.json` records the code hashes before training. `checkpoint_lock.json` records all selected model hashes before test evaluation. Original source data, frozen predictors, prior microsomal results and baseline trajectories are also hashed and verified unchanged.

`benchmark_completed.json` marks completion of training and testing. `completed.json` marks completion of verified reports. The report script produces a 13-page combined PDF, individual two-page endpoint PDFs, charts, CSV tables and a written summary in the `reports` directory.

To resume the existing CPU benchmark from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/experiment.py
```

After benchmarking is complete, regenerate reports with:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_endpoints/report.py
```

The runner has an exclusive lock and resumes successful jobs. Changed model settings should be run in a separate experiment directory to preserve the meaning of cached results and locked checkpoints.
