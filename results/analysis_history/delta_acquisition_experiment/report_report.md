# Pairwise-delta predictor and augmented NAP

The plain pairwise predictor and both variants of the compact Neural Acquisition Process (NAP) adaptation have been trained and evaluated. On 244 held-out pools, the augmented policy needs 2.311 additional purchases on average to find an optimum, versus 2.326 for the matched control. The paired improvement is 0.015 purchases, with a 95% group-bootstrap interval of [-0.030, 0.058]. Greedy selection by the delta-model mean performs similarly at 2.316 purchases. No sign-consistency constraint was used.

## Requested features

The predictor takes the ordered concatenation of two full 512-dimensional Minimol vectors and predicts the difference in log10 clearance between the query and anchor. Each input half is standardized using only delta-training molecules. The input has 1,024 dimensions. A multilayer perceptron with hidden widths 256, 128, and 64 and Gaussian Error Linear Unit activations predicts one scalar using one forward pass. There is no sign-consistency constraint, reversed-pair averaging, transitivity constraint, or enforced self-zero value.

Training pairs come from the same analog series and species. Pools are sampled uniformly, then two distinct molecules are sampled uniformly in order. The loss is mean squared error on their log10-clearance difference. Predictor training runs 3,000 steps, with its checkpoint chosen only by grouped predictor-validation error. The predictor is frozen during policy training.

At each purchase step, for query \(q\) and each already measured molecule \(j\), form

\[
\widehat z_q^{(j)} = z_j + \widehat\Delta(q,j),
\qquad z_j=\log_{10}c_j-\log_{10}c_{\mathrm{initial}}.
\]

The two added coordinates are the mean and sample standard deviation of these estimates. Sample standard deviation uses denominator \(n-1\), with an explicit value of zero when \(n=1\). These statistics are recomputed from the measured set after every purchase. They never use an unmeasured clearance. Frozen pairwise predictions can be cached because they depend only on molecular features; aggregation uses only the currently measured anchor columns.

The standard deviation measures disagreement among estimates from different measured anchors and is set to zero for one anchor.

## Disjoint allocation

The 1,827 curated nonconstant pools are allocated as 913 predictor pools and 914 RL pools, keeping shared molecules, provenance groups, and species versions of each series together. These contain 382 and 515 groups respectively. The original 244 test pools remain completely outside predictor fitting, predictor validation, and RL fitting. All six subsets have disjoint standardized molecules and groups.

| Role | Training pools | Validation pools | Test pools |
|---|---:|---:|---:|
| Delta predictor | 767 | 69 | 77 |
| Reinforcement learning | 524 | 146 | 244 |

The predictor fitting subset contains 73,221 unordered pairs, equivalent to 146,442 possible ordered distinct pairs. Pair sampling weights pools equally so large series do not dominate. The half allocation refers to search pools, with internal validation and test subsets reserved inside each half.

## Predictor performance

On the predictor's independent 77-pool test subset, root mean squared error is 0.571 log10 units and mean absolute error is 0.446. Always predicting zero gives root mean squared error 0.607 and mean absolute error 0.464. Direction accuracy for nonzero deltas is 62.9%. These metrics average losses within pools before averaging pools, and evaluate both ordered directions without enforcing consistency between them.

On the separate 244-pool RL test subset, the frozen predictor's root mean squared error is 0.633, compared with 0.661 for always predicting zero. The mean absolute error is 0.474. These test measurements are reporting metrics and did not select the predictor checkpoint or policy configuration.

## Acquisition comparison

Both NAP variants receive the same 512 original embedding coordinates, standardized using only RL-training molecules, and two additional coordinates. The control sets both added coordinates to zero. The augmented model receives the requested mean and standard deviation. This keeps network dimensions and paired initial weights identical. There is no principal-component projection in this experiment.

Both variants use the same 524 RL-training pools, 800 auxiliary prediction steps, 500 Proximal Policy Optimization iterations, eight episodes per iteration, and training seeds 11, 29, and 47. The transformer has two layers, 64-dimensional tokens, four attention heads, and a 101-bin prediction head. Checkpoints are selected on the same fixed validation cases. Every evaluated policy starts from the same four initial-molecule draws per test pool, sampled from the higher-clearance half. Outcomes are relative to the initial molecule. Policies generate complete trajectories without being told whether the optimum has been found, then the first optimal purchase is scored retrospectively.

The greedy delta baseline selects the unmeasured query with the lowest current predicted mean. Random search uses its exact expected first-optimum purchase count, accounting for tied minima and already-optimal starting molecules.

| method | mean_purchases | ci_lower | ci_upper | reduction_vs_random_percent |
| --- | --- | --- | --- | --- |
| Random | 3.177 | 2.697 | 3.680 | 0.000 |
| Delta mean greedy | 2.316 | 1.984 | 2.691 | 27.109 |
| NAP control | 2.326 | 2.018 | 2.678 | 26.776 |
| NAP + delta mean/SD | 2.311 | 1.997 | 2.671 | 27.259 |

| comparator | purchases_saved_by_augmented | ci_lower | ci_upper |
| --- | --- | --- | --- |
| NAP control | 0.015 | -0.030 | 0.058 |
| Delta mean greedy | 0.005 | -0.170 | 0.190 |
| Random | 0.866 | 0.526 | 1.256 |

Positive purchases saved means the augmented NAP is better than its comparator. Intervals are percentile 95% intervals from 2,000 bootstrap resamples of whole overlap/provenance groups. Each pool receives equal weight after averaging starts and training seeds. These intervals condition on the fitted predictor and three fitted policy seeds.

![Acquisition comparison](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/comparison.png)

## Training seeds

| method | seed | tau |
| --- | --- | --- |
| Delta mean greedy | -1 | 2.316 |
| NAP + delta mean/SD | 11 | 2.419 |
| NAP + delta mean/SD | 29 | 2.298 |
| NAP + delta mean/SD | 47 | 2.215 |
| NAP control | 11 | 2.424 |
| NAP control | 29 | 2.314 |
| NAP control | 47 | 2.241 |
| Random | -1 | 3.177 |

## Species and pool size

| species | method | mean_purchases | pools |
| --- | --- | --- | --- |
| Human | Delta mean greedy | 2.316 | 121 |
| Human | NAP + delta mean/SD | 2.211 | 121 |
| Human | NAP control | 2.244 | 121 |
| Human | Random | 3.143 | 121 |
| Mouse | Delta mean greedy | 2.311 | 53 |
| Mouse | NAP + delta mean/SD | 2.517 | 53 |
| Mouse | NAP control | 2.519 | 53 |
| Mouse | Random | 3.450 | 53 |
| Rat | Delta mean greedy | 2.318 | 70 |
| Rat | NAP + delta mean/SD | 2.327 | 70 |
| Rat | NAP control | 2.323 | 70 |
| Rat | Random | 3.029 | 70 |

| size_group | method | mean_purchases | pools |
| --- | --- | --- | --- |
| 3–4 | Delta mean greedy | 1.538 | 113 |
| 3–4 | NAP + delta mean/SD | 1.395 | 113 |
| 3–4 | NAP control | 1.405 | 113 |
| 3–4 | Random | 1.603 | 113 |
| 5–10 | Delta mean greedy | 2.409 | 74 |
| 5–10 | NAP + delta mean/SD | 2.572 | 74 |
| 5–10 | NAP control | 2.572 | 74 |
| 5–10 | Random | 3.050 | 74 |
| 11+ | Delta mean greedy | 3.737 | 57 |
| 11+ | NAP + delta mean/SD | 3.787 | 57 |
| 11+ | NAP control | 3.833 | 57 |
| 11+ | Random | 6.461 | 57 |

## Limits and reproducibility

Use the matched control to compare the added features. The split and full embedding input differ from the preceding pilot. The augmented model additionally uses predictor-half labels.

The neighboring code, frozen predictor, feature scalers, cached pairwise predictions, split manifest, model checkpoints, validation logs, complete test trajectories, and tabulated metrics reproduce this experiment. Ten behavioral checks cover plain concatenation, sample standard deviation, the singleton case, reference alignment, dynamic updates, hidden-label exclusion, offset invariance, the matched control, and separation of all six subsets. The frozen predictor checkpoint hash is checked before and after RL training. All training used the CPU.
