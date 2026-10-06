# Multitask acquisition across five pharmacokinetic endpoints

One shared model for each architecture was trained across in vivo clearance, protein binding, cellular clearance, permeability, and efflux. The controls were retrained separately per endpoint. Random is an exact expectation and has no trainable multitask version.

## Primary results for pools containing at least 15 compounds

Entries are mean additional purchases to the first recorded optimum. The starting hit is free. Pools have equal weight after averaging four matched starts and, for NAP, three training seeds. Lower is better.

| Endpoint | Pools | Groups | Random | Delta greedy single | Delta greedy multi | GP + EI single | GP + EI multi | NAP single | NAP multi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| In vivo clearance | 7 | 5 | 10.143 | 14.429 | 14.536 | 8.143 | 7.036 | 12.845 | 14.333 |
| Protein binding | 11 | 9 | 13.182 | 8.114 | 6.773 | 9.909 | 9.750 | 10.091 | 14.114 |
| Cellular clearance | 18 | 13 | 9.593 | 9.819 | 10.556 | 7.806 | 5.722 | 7.958 | 10.009 |
| A→B permeability | 12 | 12 | 10.694 | 6.125 | 6.208 | 6.125 | 7.125 | 8.590 | 10.472 |
| Efflux ratio | 8 | 8 | 9.146 | 5.125 | 4.625 | 9.688 | 8.906 | 8.906 | 9.042 |

Endpoints with a lower multitask mean: Delta greedy: 2/5, GP + EI: 4/5, NAP: 0/5.

The largest GP mean gain is on Cellular clearance, saving 2.08 purchases (26.7%); its paired 95% interval is [0.04, 4.14] purchases saved. Shared NAP has a higher mean purchase count on 5/5 endpoints. Most paired intervals include zero.

![Paired multitask gains](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/multitask_gain.png)

## Paired transfer estimates

Positive purchases saved means multitask is better. Intervals are 5,000 paired bootstrap resamples of globally linked provenance groups, conditional on fitted models.

| endpoint | method | purchases_saved | relative_reduction_percent | ci_lower | ci_upper |
| --- | --- | --- | --- | --- | --- |
| in_vivo_clearance | Delta greedy | -0.107 | -0.743 | -3.200 | 1.159 |
| in_vivo_clearance | GP + EI | 1.107 | 13.596 | -2.700 | 2.944 |
| in_vivo_clearance | NAP | -1.488 | -11.585 | -3.617 | -0.426 |
| protein_binding | Delta greedy | 1.341 | 16.527 | -0.250 | 2.625 |
| protein_binding | GP + EI | 0.159 | 1.606 | -2.643 | 3.944 |
| protein_binding | NAP | -4.023 | -39.865 | -10.590 | 2.114 |
| cellular_clearance | Delta greedy | -0.736 | -7.496 | -3.000 | 1.235 |
| cellular_clearance | GP + EI | 2.083 | 26.690 | 0.042 | 4.145 |
| cellular_clearance | NAP | -2.051 | -25.771 | -5.382 | 1.121 |
| permeability | Delta greedy | -0.083 | -1.361 | -1.312 | 1.146 |
| permeability | GP + EI | -1.000 | -16.327 | -3.188 | 1.188 |
| permeability | NAP | -1.882 | -21.908 | -3.417 | -0.291 |
| efflux | Delta greedy | 0.500 | 9.756 | -0.750 | 1.844 |
| efflux | GP + EI | 0.781 | 8.065 | -1.781 | 3.312 |
| efflux | NAP | -0.135 | -1.520 | -1.698 | 1.354 |

## All eligible test pools

| Endpoint | Pools | Groups | Random | Delta greedy single | Delta greedy multi | GP + EI single | GP + EI multi | NAP single | NAP multi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| In vivo clearance | 99 | 84 | 2.938 | 3.202 | 3.222 | 2.684 | 2.482 | 3.245 | 3.306 |
| Protein binding | 143 | 77 | 3.199 | 2.243 | 2.100 | 2.788 | 2.771 | 2.617 | 3.233 |
| Cellular clearance | 93 | 49 | 4.194 | 3.935 | 3.852 | 3.645 | 2.866 | 3.568 | 4.268 |
| A→B permeability | 104 | 87 | 3.955 | 3.022 | 2.971 | 3.123 | 3.361 | 3.267 | 3.659 |
| Efflux ratio | 68 | 53 | 3.654 | 2.665 | 2.754 | 3.456 | 3.360 | 3.059 | 3.154 |

![Cumulative size cutoffs](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/comparison.png)

## Delta prediction on larger acquisition-test pools

Errors are in original transformed endpoint units, before the training-only scale division. R-squared compares equally weighted pool MSE against predicting zero difference. Spearman correlations rank queries against each fixed anchor, then average over anchors and pools.

| endpoint | mode | pools | rmse | r2 | mean_fixed_anchor_rho |
| --- | --- | --- | --- | --- | --- |
| cellular_clearance | multitask | 18 | 0.665 | -0.369 | 0.121 |
| cellular_clearance | single_task | 18 | 0.620 | -0.189 | 0.224 |
| efflux | multitask | 8 | 0.703 | 0.021 | 0.357 |
| efflux | single_task | 8 | 0.731 | -0.058 | 0.280 |
| in_vivo_clearance | multitask | 7 | 0.578 | -0.238 | 0.030 |
| in_vivo_clearance | single_task | 7 | 0.587 | -0.281 | -0.013 |
| permeability | multitask | 12 | 0.716 | 0.111 | 0.398 |
| permeability | single_task | 12 | 0.723 | 0.095 | 0.418 |
| protein_binding | multitask | 11 | 0.860 | -0.295 | 0.322 |
| protein_binding | single_task | 11 | 0.863 | -0.302 | 0.359 |

## Shared architectures

The delta model concatenates the full 512-dimensional query and anchor representations, processes them through a shared 256/128/64-unit network, and uses five endpoint-specific output heads. The single-task control has identical dimensions but trains only the active endpoint. There is no sign consistency, antisymmetry, reversed-pair averaging, self-zero constraint, or cycle loss.

The multitask Gaussian process uses a shared Matérn-5/2 kernel with learned feature lengthscales, a rank-two-plus-diagonal positive-definite task covariance, task-specific amplitude and nugget, and a shared linear mean plus regularized task residuals. This implements intrinsic coregionalization following the shared-input/task-covariance construction of Bonilla et al. ([paper](https://papers.nips.cc/paper_files/paper/2007/hash/66368270ffd51418ec58bd793f2d9b1b-Abstract.html)). Each linked training pool is differenced against its own reference before joint likelihood evaluation, so additive pool offsets cancel.

GP training first samples a focal endpoint and pool. When available, it adds up to two other endpoints from the same species and global provenance group, with at most 32 total points and separate references per pool. These cross-endpoint training observations identify the task covariance. No historical labels or other endpoint measurements are directly conditioned on at test time. Transfer reaches a new series through the learned prior parameters.

The Neural Acquisition Process (NAP) remains the compact two-layer, four-head, 64-dimensional adaptation of the earlier experiment, based on Maraval et al. ([paper](https://arxiv.org/abs/2305.15930)). A five-coordinate endpoint indicator is appended to each full Minimol representation, followed by the frozen delta mean and sample standard deviation. A shared transformer predicts 101-bin outcome distributions; shared policy and critic networks train with Proximal Policy Optimization and an auxiliary prediction loss. Bucket widths are endpoint-specific and determined only from acquisition-training spans.

Each query estimate is the observed relative outcome of a measured anchor plus the predicted query-minus-anchor delta. Statistics use only measured anchors; the standard deviation is zero for one anchor. The shared NAP uses the shared frozen delta model, and each independent NAP uses its independent delta model.

## Matched experiment and scaling

The existing curated pools and transformed objective values are reused unchanged. Clearance and efflux minimize log10 values; permeability maximizes log10 permeability, implemented by negating the objective. Protein binding minimizes log10((1−fu)/fu), preferring higher unbound fraction. This binding preference is the prior experiment's assumption. Species remain separate pools and the task identifier here is endpoint, not endpoint-by-species.

All observations are relative to the initial molecule after transformation. Within each endpoint and training role, targets are divided by the training-pool root-mean-square pair difference, without mean subtraction. This preserves a zero reference and prevents scale differences from dominating multitask losses. The same endpoint factors are used in matched controls. Embedding standardization fits only the relevant training molecules: all endpoints for shared models and one endpoint for controls. No test pool contributes to scaling.

Multitask training cycles equally across endpoints and samples pools uniformly within an endpoint. Each endpoint gets 3,000 delta updates, 700 focal GP updates, 800 NAP prediction updates, and 500 NAP policy iterations per seed. Shared totals are five times those counts. NAP seeds are 11, 29, and 47; delta and GP each have one training seed. This balances endpoint exposure; it does not rebalance small versus large pools within each endpoint.

Checkpoint selection uses validation data only. Delta selection minimizes endpoint-balanced normalized MSE. NAP supervised pretraining minimizes endpoint-balanced cross entropy. Acquisition selection averages each endpoint's mean purchases divided by its mean random expectation, so one endpoint's pool sizes cannot dominate the shared checkpoint. Within each endpoint, acquisition validation prioritizes pools ≥15 only when at least five such pools across at least three provenance groups exist; otherwise it uses all validation pools.

Initial hits are sampled uniformly from the worse half with random tie breaking. Every method gets the same four starts per test pool. Policies generate complete purchase orders without knowing the optimum or receiving a success/termination flag. First-optimum timing is scored retrospectively, with any recorded tied minimum accepted. Random expectations include ties and initially optimal hits.

## Global split and historical data access

There are 2798 retained pools in 1114 global groups. Across endpoints, 362 groups contain multiple endpoints and 298 groups crossed the previous independent subsets. The largest connected group contains 620 pools. Molecules, known source documents, and pre-existing within-endpoint provenance links stay in one group. Metadata from retained series, including unselected source rows, is used conservatively for these links. Numeric series identifiers are endpoint-local and are not treated as shared identifiers.

A new seeded split was selected using endpoint counts and pool-size counts only, never labels or results. Target fractions are 40% delta train, 5% delta validation, 5% delta test, 24% acquisition train, 6% acquisition validation, and 20% acquisition test. Large connected groups prevent exact fractions. The actual allocations are below. These new controls are the proper comparator; the previous independent-split table is not a matched comparison.

| endpoint | role | split | pools | groups | pools_ge15 |
| --- | --- | --- | --- | --- | --- |
| cellular_clearance | delta | test | 18 | 8 | 3 |
| cellular_clearance | delta | train | 262 | 71 | 33 |
| cellular_clearance | delta | validation | 21 | 13 | 6 |
| cellular_clearance | rl | test | 93 | 49 | 18 |
| cellular_clearance | rl | train | 110 | 66 | 18 |
| cellular_clearance | rl | validation | 20 | 15 | 1 |
| efflux | delta | test | 14 | 13 | 2 |
| efflux | delta | train | 147 | 92 | 23 |
| efflux | delta | validation | 21 | 15 | 4 |
| efflux | rl | test | 68 | 53 | 8 |
| efflux | rl | train | 77 | 64 | 12 |
| efflux | rl | validation | 14 | 14 | 5 |
| in_vivo_clearance | delta | test | 22 | 20 | 1 |
| in_vivo_clearance | delta | train | 265 | 157 | 9 |
| in_vivo_clearance | delta | validation | 22 | 19 | 0 |
| in_vivo_clearance | rl | test | 99 | 84 | 7 |
| in_vivo_clearance | rl | train | 111 | 103 | 3 |
| in_vivo_clearance | rl | validation | 18 | 16 | 0 |
| permeability | delta | test | 23 | 17 | 3 |
| permeability | delta | train | 226 | 143 | 30 |
| permeability | delta | validation | 26 | 18 | 4 |
| permeability | rl | test | 104 | 87 | 12 |
| permeability | rl | train | 110 | 88 | 17 |
| permeability | rl | validation | 27 | 23 | 6 |
| protein_binding | delta | test | 29 | 18 | 2 |
| protein_binding | delta | train | 490 | 133 | 21 |
| protein_binding | delta | validation | 26 | 13 | 0 |
| protein_binding | rl | test | 143 | 77 | 11 |
| protein_binding | rl | train | 148 | 85 | 9 |
| protein_binding | rl | validation | 44 | 29 | 1 |

All six subsets are disjoint across endpoints by molecules, provenance groups, and known documents. Delta models fit their allocation and remain frozen. GP fits acquisition training. NAP fits acquisition training and inherits information from delta training. The single-task versus multitask comparison within an architecture is the principal transfer comparison.

## Sensitivity and limitations

![Unique-optimum sensitivity](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/comparison_unique_optima.png)

The experiment uses a single grouped split, fixed CPU training budgets, and fixed hyperparameters. GP task correlations are learned model parameters. Endpoint comparisons use matched results and uncertainty intervals.

## Saved artifacts

- [Acquisition summary CSV](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/acquisition_summary.csv)
- [Paired transfer CSV](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/paired_transfer_results.csv)
- [Predictor results CSV](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/predictor_summary.csv)
- [Results by training seed](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/seed_results_by_cutoff.csv)
- [Learned GP task correlations](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/multitask/gp_task_correlation.csv)
- [Reproduction instructions](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/README.md)

Prepared data, global split manifests, scalers, complete test purchase orders, frozen predictions, training logs, and all checkpoints are retained in this directory. Original source files and previous experiment outputs are unchanged.
