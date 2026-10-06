# Prediction, local adaptation, and uncertainty findings

These findings summarize saved architecture studies. Each numerical result uses its study's training roles, reference sampling, ensembling, calibration, and aggregation. Comparisons are exploratory development-fold evaluations; within-study hyperparameters were selected on validation data.

## How many measurements make an unfamiliar series understandable?

The original diagnostic held the same five compounds hidden in 580 pools containing at least 15 compounds, using ten reveal orders and the existing five grouped folds. With species pooled, Gaussian-process within-series Spearman correlation increased from 0.122 with one measurement to 0.254 with ten. The paired gain was 0.133, with a linked-source-group bootstrap 95% interval of [0.106, 0.160]. The contemporary neural forecaster increased from 0.083 to 0.106. Its gain was 0.024 [0.001, 0.047], but the real-outcome gain relative to the expected-outcome control was −0.004 [−0.015, 0.005]. With species-specific heads, GP correlation went from 0.106 to 0.229, and the neural forecaster from 0.083 to 0.094. ([Original findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/findings.md))

The initial delta-mean baseline stayed close to 0.22 correlation as more anchors were added. Averaging observed anchor outcomes adds a common offset to every candidate score, which can improve squared error without changing ranking. Query-dependent pair predictions can change when anchor structures change, but the numerical outcome average alone cannot change candidate order. ([Learning curves](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/learning_curve_summary.csv))

## Can an unsuccessful compound be informative?

Among reveals with unfavorable outcomes, 15.6% [13.7%, 17.4%] satisfied the original informative-reveal definition for the pooled GP, compared with 7.9% [6.4%, 9.5%] for the contemporary neural forecaster. The definition required at least a 0.10 concordance increase relative both to the original context and to revealing the structure with its expected outcome. ([Original findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/findings.md), [Experiment-value summaries](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/experimental_value_summary.csv))

A post hoc rat microsomal example started from clearance 88 µL/min/mg. Another compound had measured clearance 690, despite a prediction near 43.5. Revealing it increased the neural forecaster's hidden-set correlation from 0.00 to 0.90 and changed its next preferred molecule from clearance 72 to 19. Revealing the same structure with its predicted outcome did not improve correlation. A different compound with excellent clearance 15 left the hidden ranking unchanged. ([Example record](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/illustrative_example.json), [Figure](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/useful_failure_example.png))

## Can a surprising chemical effect transfer locally?

The matched-transformation analysis found 934 pools with disjoint repeated-substitution pairs. GP direction accuracy increased from 54.5% to 60.7%, with a real-outcome contribution of 6.25 percentage points [4.52, 8.28]. The contemporary neural forecaster changed from 54.5% to 54.7%, with an outcome contribution of 0.86 points [−0.06, 1.81]. In 392 model-dependent pools with an initially near-null prediction and a surprising observed pair, GP direction accuracy increased from 52.3% to 68.3%. ([Original findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/findings.md), [Transformation summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/transformation_transfer_summary.csv))

In one human microsomal methyl-to-chlorine example, the historical mean across 34 training source groups was +0.030 log10 clearance. A measured local pair showed −0.640. The GP changed the predicted effect for a separate hidden pair from +0.005 to −0.203, while its true effect was −1.033. The local observation corrected the direction but only part of the magnitude. Structures selected matched pairs, and historical effects excluded validation/test outcomes. This supported models that can propagate measured residuals to similar compounds. ([Transformation example](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/transformation_example.json))

## Pairwise external memory versus a feedforward delta predictor

The external-memory experiment used five folds, three seeds, six endpoints, and 4,625 held-out pools. The large-pool curves used the same five hidden queries in 580 pools. The model read a key-value memory of historical or local molecular pairs. Hyperparameter searches explored representation dimension and memory/decoder dimensions. The reported primary table averaged separately fitted seeds rather than forming an ensemble. ([Memory report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/reports/findings.md), [Selected configurations](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/reports/selected_models.csv))

| Model | No local delta, \(R^2\) | No local delta, Spearman | Nine added labels, \(R^2\) | Nine added labels, Spearman |
| --- | ---: | ---: | ---: | ---: |
| Tuned pair feedforward network | 0.037 | 0.216 | 0.037 | 0.216 |
| Pair network plus anchor averaging | 0.037 | 0.216 | 0.453 | 0.218 |
| Pair network plus local ridge | 0.037 | 0.216 | 0.468 | 0.218 |
| Key-value memory | 0.006 | 0.222 | 0.433 | 0.236 |
| Residual memory | 0.018 | 0.218 | 0.468 | 0.232 |

The external-memory study reports ranking and prediction error separately ([numeric summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/reports/summary.csv)).

## Learned mean versus learned covariance in a Gaussian process

The follow-up compared pairwise learned mean functions, conventional covariance kernels, and deep learned feature maps. With nine additional local measurements, the matched linear-mean conventional GP achieved \(R^2=0.579\), Spearman 0.399. The neural-mean conventional GP achieved 0.572 and 0.401. A deep-kernel GP reached 0.549 and 0.384; a neural mean plus deep kernel reached 0.549 and 0.372. The older GP gave 0.084 and 0.266. ([Deep-GP findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/deep_gp/reports/findings.md))

The neural mean predicts a signed pair difference from the concatenated query and reference representations. The linear mean predicts a linear function of their representation difference. The covariance is separately required to be positive semidefinite. A nonzero mean permits two compounds to have correlated residuals while different expected property values. This distinction was central to the later neural baseline plus residual-correction architecture. ([Model implementation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/gp_models.py), [Prediction table](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/deep_gp/reports/prediction_summary.csv))

## Tanimoto, Morgan metrics, and covariance remapping

For MiniMol covariance remapping at ten measurements, \(R^2\) increased from 0.579 to 0.581 and Spearman from 0.399 to 0.401. The paired \(R^2\) change was 0.0018 [0.0002, 0.0036], while the Spearman change 0.0023 had interval [−0.0010, 0.0056]. Morgan Tanimoto gave \(R^2=0.564\), Spearman 0.382 in that experiment. ([Kernel-remapping findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/kernel_remapping/reports/findings.md))

The expanded Morgan study compared Tanimoto, Dice, cosine, Braun–Blanquet, Sokal, Pearson, and Hamming/Euclidean-derived covariances. The direct-extension validation-selected alternative achieved Spearman 0.383, compared with 0.382 for direct Morgan Tanimoto and 0.399 for the existing MiniMol GP. The selected-Morgan minus direct-Tanimoto interval was [−0.0053, 0.0060]. All variants shared the same frozen MiniMol linear mean, which isolates the covariance comparison more clearly than changing the whole predictor at once. ([Direct-extension findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/morgan_metrics/direct_extension/reports/findings.md), [Initial metric sweep](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/pair_memory_benchmark/morgan_metrics/reports/findings.md))

## Pure neural prediction and uncertainty

The uncertainty benchmark compared heteroscedastic Gaussian networks, variational Bayesian neural networks, a normal-inverse-gamma evidential regression model, independently seeded ensembles, attentive context models, and a later distance-aware residual ensemble. The evidential model used a Student predictive distribution suitable for a continuous delta. It was not a Dirichlet classifier applied to a continuous target. The Bayesian network used variational weight uncertainty and episodic inputs. It did not perform exact sequential Bayesian weight conditioning after each local observation. ([Locked protocol](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty/protocol.json))

| Predictor, ten measurements | \(R^2\) | Spearman | Calibrated NLL | 95% coverage |
| --- | ---: | ---: | ---: | ---: |
| Heteroscedastic Gaussian network | 0.391 | 0.265 | 0.856 | 93.7% |
| Bayesian neural network | 0.407 | 0.270 | 0.814 | 93.3% |
| Evidential regression | 0.411 | 0.262 | 0.797 | 94.1% |
| Deep ensemble | 0.417 | 0.276 | 0.796 | 94.1% |
| Attentive ensemble | 0.507 | 0.262 | 0.697 | 94.2% |
| Distance-aware ensemble | 0.522 | 0.336 | 0.668 | 93.2% |
| Neural-mean conventional GP | 0.572 | 0.401 | 0.621 | 94.1% |

The attentive ensemble and GP had approximately 94% coverage for nominal 95% intervals. Prediction and uncertainty tables report ranking, NLL, coverage, and width, with raw and validation-calibrated results separated ([uncertainty results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty/reports/results.md)).

For the corresponding single-compound acquisition experiment, the frozen distance-aware neural mixture plus expected improvement required 6.09784 purchases to reach any optimum, versus 5.52457 for GP expected improvement in the 580 large pools. The difference was +0.57328 purchases, with interval [+0.18784, +0.95279]. It used 9.29% fewer purchases than greedy delta and 36.40% fewer than random. Its difference from its own greedy rule was −0.05431 purchases [−0.17287, +0.07537]. This acquisition table averaged pools directly; endpoint-macro results were separately reported. ([Single-compound acquisition findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty_k1/reports/results.md))

## Consequences for the project

The [local adaptation recipe](local_adaptation.md) evaluates these questions using the current model and saved GP and transfer baselines.
