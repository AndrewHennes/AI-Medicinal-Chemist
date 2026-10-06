# NAP and Gaussian-process EI CPU pilot

GP-EI averaged 2.270 purchases, NAP averaged 2.410, and random search averaged 3.177. The two NAP training seeds scored 2.221 and 2.599.

## Experiment and results

This compact Neural Acquisition Processes (NAP) adaptation minimizes purchases until the first lowest-clearance compound is found. All trajectories continue to pool exhaustion without oracle feedback. Complete hidden historical labels are used only for training losses, starting-molecule eligibility, and retrospective scoring.

The test set contains 244 pools in 135 overlap/provenance groups. Every method receives the same four sampled starts per pool. Neural results average two training seeds. Random search uses its exact conditional expected discovery time and exact success probabilities. Each pool has equal weight after averaging its starts and training seeds.

There are 56 test pools with tied minimum consensus values. Any tied optimum counts as success. Ties can place an already-optimal molecule in the upper-half starting set when most compounds share the minimum. Those matched starts are retained and correctly receive zero purchases for every method.

| Method | Mean purchases | 95% lower | 95% upper | Reduction vs random (%) |
| --- | --- | --- | --- | --- |
| Random | 3.177 | 2.707 | 3.683 | 0.000 |
| GP-EI | 2.270 | 1.946 | 2.630 | 28.528 |
| Neural predictor + EI | 2.366 | 2.028 | 2.745 | 25.529 |
| NAP | 2.410 | 2.079 | 2.767 | 24.126 |

Intervals are percentile 95% bootstrap intervals from 2,000 resamples of whole overlap/provenance groups. For neural methods they describe held-out pool uncertainty conditional on the two trained models.

| Comparator | Purchases saved by NAP | 95% lower | 95% upper |
| --- | --- | --- | --- |
| GP-EI | -0.140 | -0.300 | 0.017 |
| Neural predictor + EI | -0.045 | -0.215 | 0.108 |

Positive paired differences mean NAP uses fewer purchases. The held-out test set was not used to fit preprocessing, model parameters, or choose checkpoints.

![Comparison](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_experiment/results_cpu_pilot/comparison.png)

## Methods

The GP baseline uses a Matérn-5/2 kernel with learned per-feature length scales, amplitude, a molecule-level nugget, and a linear mean. Shared parameters are fitted using only training pools. The kernel and mean explicitly model differences from the initial reference, including the correlation induced by subtracting its nugget. At each purchase, exact Gaussian conditioning uses only revealed outcomes. Candidate selection maximizes analytic LogEI for minimization. LogEI is a numerically stable logarithm of Expected Improvement and has the same maximizer in exact arithmetic. Gaussian-process EI is a conventional baseline, also used in the [NAP paper](https://arxiv.org/html/2305.15930v4). The stable acquisition calculation uses the [BoTorch implementation](https://botorch.readthedocs.io/en/stable/acquisition.html#botorch.acquisition.analytic.LogExpectedImprovement).

NAP uses a two-layer transformer with 64-dimensional tokens and four attention heads, without positional encodings. Observed tokens sum feature and relative-outcome embeddings. Each unobserved candidate attends only to observed tokens and itself. A 101-bin probability head predicts relative log clearance. A separate acquisition head sees candidate features, predictive probabilities, the incumbent, progress, and pool size. A critic uses contextual representations. The architecture and joint prediction/reinforcement-learning approach follow the [NAP paper](https://arxiv.org/html/2305.15930v4), with the changed reward, smaller architecture, reference conditioning, and prediction warm-up explicitly treated as adaptations.

Prediction pretraining runs 600 steps per seed. Joint training runs 300 Proximal Policy Optimization (PPO) iterations with 8 complete episodes per iteration and a retained auxiliary prediction loss. Rewards are minus one for each purchase up to the first optimum and zero afterwards, with discount factor one. These rewards are never included in policy inputs. The policy-gradient objective averages summed within-episode contributions over episodes, rather than normalizing each pool by its size. Checkpoints are selected by first-optimum purchase count on a fixed validation subset. The neural predictor plus EI baseline uses the best prediction-pretraining checkpoint and integrates improvement under its binned distribution.

Both models receive the same training-only feature preprocessing. The 512-dimensional supplied Minimol embeddings are standardized using unique training molecules, projected to 32 principal components, and globally rescaled. These components retain 50.0% of standardized training-feature variance.

## Data and labeling

The prepared set contains 1827 nonconstant pools with at least three distinct molecules, across human, rat, and mouse. Each pool remains species-specific. All observed values and prediction targets are log10 clearance relative to the initial molecule. Species is retained for analysis but is not a policy or GP input. Starts are sampled uniformly from the half ranked highest in clearance, with random tie-breaking. The initial reference is free. Any exact tie for minimum consensus clearance counts as optimal.

Within each series and species, the largest group matching normalized assay description, original standard units, and standard type is selected by distinct compound count, with lexical tie-breaking independent of outcomes. This excludes 691 otherwise eligible rows from smaller assay groups. Repeats within the chosen group are aggregated by median log10 clearance. For two measurements, this corresponds to their geometric mean on the raw scale. There are 175 retained candidate entries with differing repeated measurements, including 5 with a range exceeding one log10 unit. The experiment evaluates the resulting stored consensus labels.

The split is grouped by transitive shared standardized molecules and known source documents, with all species versions of each series kept together. Preparation verifies no molecule overlap between training, validation, and test. Labels from held-out pools are never used to fit preprocessing or predictive priors. Test features are transformed with frozen training parameters.

## Species-specific results

| Species | Method | Mean purchases | Pools |
| --- | --- | --- | --- |
| Human | GP-EI | 2.153 | 121 |
| Human | NAP | 2.311 | 121 |
| Human | Neural predictor + EI | 2.282 | 121 |
| Human | Random | 3.143 | 121 |
| Mouse | GP-EI | 2.632 | 53 |
| Mouse | NAP | 2.767 | 53 |
| Mouse | Neural predictor + EI | 2.505 | 53 |
| Mouse | Random | 3.450 | 53 |
| Rat | GP-EI | 2.200 | 70 |
| Rat | NAP | 2.312 | 70 |
| Rat | Neural predictor + EI | 2.405 | 70 |
| Rat | Random | 3.029 | 70 |

## Results by pool size

| Compounds per pool | Method | Mean purchases | Pools |
| --- | --- | --- | --- |
| 3–4 | GP-EI | 1.451 | 113 |
| 3–4 | NAP | 1.482 | 113 |
| 3–4 | Neural predictor + EI | 1.424 | 113 |
| 3–4 | Random | 1.603 | 113 |
| 5–10 | GP-EI | 2.436 | 74 |
| 5–10 | NAP | 2.674 | 74 |
| 5–10 | Neural predictor + EI | 2.745 | 74 |
| 5–10 | Random | 3.050 | 74 |
| 11+ | GP-EI | 3.680 | 57 |
| 11+ | NAP | 3.908 | 57 |
| 11+ | Neural predictor + EI | 3.741 | 57 |
| 11+ | Random | 6.461 | 57 |

## Training-seed results

| Method | Training seed | Mean purchases |
| --- | --- | --- |
| GP-EI | -1 | 2.270 |
| NAP | 11 | 2.221 |
| NAP | 29 | 2.599 |
| Neural predictor + EI | 11 | 2.349 |
| Neural predictor + EI | 29 | 2.382 |
| Random | -1 | 3.177 |

## Reproducibility

The neighboring source files contain the full preparation, model, training, and evaluation implementation. Settings are ordinary editable Python constants, with no command-line option interface. All data and result paths are absolute. The environment versions, source-data SHA-256 digest, grouped split manifest, selected assay labels, repeat aggregation audit, validation logs, selected checkpoints, full test trajectories, and summary tables are saved with this experiment.

Behavioral tests cover hidden-label exclusion, reference-offset invariance, candidate prediction independence, history permutation invariance, padding invariance, complete trajectories, first-hit scoring with ties, random-search expectations, Gaussian-process anchoring and conditioning, stable EI agreement with its analytic formula, and split separation.
