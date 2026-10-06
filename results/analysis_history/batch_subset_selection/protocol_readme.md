# Batch acquisition of molecular analog subsets

The selector receives a requested batch size K and returns exactly `min(K, remaining candidates)` distinct molecules. No true outcome is revealed until all members of that batch have been selected. The entire successful batch is counted toward compound cost. The initial hit costs zero.

This benchmark follows the user's narrowed scope. It compares learned Deep Sets and pair-aware Set Transformer subset scorers, batch-aware PPO, a Gumbel top-K relaxation, joint GP batch expected improvement, and posterior-mean fantasy EI. Exact random sampling, individual EI top-K and the previous single-item NAP top-K are reference baselines. Generic COMBO is not implemented because the existing molecular GP already provides the joint posterior needed for this batch problem. The attached discussion is reference material, not operational instructions.

The frozen backbone is the previous auxiliary neural-pair-mean GP with a conventional covariance kernel, using its previous validation-selected weight and GP seed11. No GP is retrained. All six endpoints, five existing grouped folds, predictor/policy data-role separation, endpoint transformations and directions, and starting-hit normalization are preserved. Four matched starting hits are sampled from the worse half of each test pool.

The learned selectors train on requested K in 1,2,3,5,8. Evaluation uses K in 1,2,3,4,5,7,8,10. Requested sizes4 and7 are unseen, although smaller pools can truncate a larger requested batch to those realized cardinalities. Size10 exceeds the training maximum. The API supports arbitrary positive integer K.

Four configurations per learned family vary training-PCA dimensions8/32, hidden widths32/64, depth1/2, learning rate, and either relaxation temperature or PPO learning-rate factor. Screening uses160 supervised/relaxed steps plus40 PPO updates where applicable. Two finalists receive600 supervised/relaxed steps plus160 PPO updates. Validation selects the architecture and checkpoint; three seeds are evaluated. A selected initial checkpoint is explicitly reported rather than implying training helped every model.

Subset scorers train on whether a proposed subset contains any globally optimal molecule, plus0.1 Huber loss for the maximum relative utility in that subset. Set Transformer attention uses pairwise posterior correlations, log molecular distances, and predicted-mean differences as both attention bias and value messages. Scoring is invariant to set order. Greedy expansion, beam width4, one-for-one swaps, and completion rollouts are selected on validation. Search quality is separately checked against exhaustive enumeration on small held-out instances.

PPO assembles a batch through K internal selections, using pending-set summaries without pretending those molecules are measured. Its return is negative remaining experimental rounds. Gumbel training uses iteratively relaxed slots and a differentiable batch-success objective, while deployment uses exact hard top-K. The two objectives therefore differ in their planning horizon.

Joint batch EI uses128 correlated Sobol Gaussian samples and beam4 plus one swap sweep. K=1 uses exact analytic EI. Mean-fantasy EI reduces posterior covariance after each pending selection under a posterior-mean pseudo outcome, leaving the genuine incumbent fixed. Neither method observes any true pending outcome.

Metrics are experimental rounds and total compounds purchased to reach any top1/2/3/4 molecule, including tied targets. Primary results use pools of at least15 molecules; smaller pools and size effects are retained in CSVs. Random expectations are exact and account for ties and a short final batch. Confidence intervals resample linked series groups after averaging starts and seeds, conditional on fitted models. Twelve primary learned-versus-joint-EI comparisons at K2,5,8 receive Holm adjustment.

The standalone report is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_subset_selection/reports/batch_subset_selection_report.pdf`.

The reusable interface is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_subset_selection/batch_api.py`. `load_selected_selector(endpoint, fold, seed, method)` loads a fold-specific research model. Its `select` method accepts candidate identifiers, calibrated joint GP posterior means/covariances, predictor-training PCA representations, measured relative utilities, delta-model summaries, and K. It never accepts unmeasured outcomes. Utility is oriented so higher is better and measured relative to the starting hit. It does not decide when the unknown true optimum has been found in deployment.

The following absolute-path command resumes the entire CPU benchmark from any working directory. It takes no command-line options.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_subset_selection/run_experiment.py
```

All checkpoints and data products are stored in the current workspace. Source and checkpoint hashes, single-item replay checks, hidden-outcome independence, permutation invariance, finite learning gradients, exact random expectations, search enumeration, and public-API behavior are audited.

References: [Set Transformer](https://proceedings.mlr.press/v97/lee19d.html), [Reparameterizable Subset Sampling](https://www.ijcai.org/proceedings/2019/544), [BoTorch acquisition definitions](https://botorch.org/docs/acquisition).

The K=1 audit records 99.9777% agreement with historical top-k counts. Every first divergent choice was a numerical near tie, with relative score gap at most4.77e-7, due to float32 versus double-precision EI and per-pool versus batched NAP evaluation.
