# Architecture development and what the comparisons support

This note summarizes saved predictor and acquisition architecture studies. The analysis-history documentation indexes the full chronology. Compare scores within each study's folds, training allocation, calibration, and context sizes.

## Conventional kernels, remapping, and Morgan similarity

The kernel-remapping study retained the current mean and geometry while comparing covariance mappings. On its large-pool, ten-measurement panel, remapping the current MiniMol kernel increased R² from approximately 0.579 to 0.581. The estimated improvement was 0.0018 with exploratory interval [0.0002, 0.0036], while the correlation improvement interval included zero. Direct Morgan Tanimoto gave R² 0.564 and correlation 0.382, compared with 0.579 and 0.399 for the existing MiniMol GP. ([kernel remapping](../results/analysis_history/pair_memory_benchmark_kernel_remapping/report_findings.md)).

Follow-up Morgan comparisons covered Tanimoto, Dice, cosine, Braun–Blanquet, Sokal, Pearson, and Hamming/Euclidean constructions. They all used the same frozen MiniMol linear mean, isolating covariance rather than comparing fully separate molecular predictors. In the direct-extension study, validation-selected Morgan gave correlation 0.383 versus 0.382 for direct Morgan Tanimoto, with a paired difference interval [−0.0053, +0.0060]. The existing MiniMol GP remained at 0.399. ([Morgan metrics](../results/analysis_history/pair_memory_benchmark_morgan_metrics/report_findings.md), [direct extension](../results/analysis_history/pair_memory_benchmark_morgan_metrics_direct_extension/report_findings.md)).

The current `kernel_comparison` recipe uses its documented scalar neural mean, training objective, PCA grid, and fresh-fit schedule. Historical frozen-linear-mean studies retain their original numerical tables.

## Moving from a neural baseline to local adaptation

A neural pair model provides a historical prediction of the difference between two compounds. Revealed measurements can then supply local evidence that the historical prediction is systematically wrong for the current series. The later architecture combines a pair baseline, a permutation-invariant measured-context encoder, a learned molecular similarity kernel, iterative residual correction, and probabilistic output heads. Three fitted members form a predictive mixture. The mean and uncertainty are distinct outputs, and acquisition can use them through calculated expected improvement (EI).

The iterative coefficients approximately solve a ridge-regularized residual interpolation problem and weight measured residuals in each correction. Neural mean gates, mean offsets, and uncertainty heads augment the kernel calculation.

## Kernel-informed uncertainty

The option-2 study added a covariance-based variance term with learned scaling while retaining the iterative mean correction. At ten measurements in pools with at least 15 compounds, the calibrated NLL was 0.580 versus 0.583 for matched continued training, with almost identical R² and Spearman correlation. Nominal 95% coverage was 94.7% versus 94.8%, with interval width 1.907 versus 1.920. Purchases to top-1 were 5.500 versus 5.509, a difference of −0.009 with a linked-group 95% interval of [−0.072, +0.053]. ([saved report](../results/analysis_history/kernel_variance_option2/report_results.md)).

Both arms continued for 1,200 updates from the same saved members. Validation selected initialization in 64 of 90 option-2 members and 49 of 90 controls. The added variance branch uses a Cholesky solve.

## Averaging several measured references

The intended averaged baseline aligns each pair prediction before averaging. With measured outcomes `z_i` expressed relative to the initial hit, a query prediction is `mean_i[z_i + predicted_delta(q,i)]`. Averaging bare deltas without aligning their references would be wrong. A measured point's residual must also avoid using its own outcome to predict itself.

Swapping the query baseline at inference changed R² from 0.5668 to 0.1665 while leaving Spearman almost unchanged, 0.3969 versus 0.3978. The resulting modification was largely a common offset across the hidden query panel. About 99.8% of its squared change was a shared shift, supporting the explanation that it overlapped with a correction already provided by the residual branch. The subsequent consistent-residual continuation gave NLL 0.6150 versus 0.5798 for the original continued model ([initial averaging](../results/analysis_history/multi_reference_mean/report_results.md), [consistent residual follow-up](../results/analysis_history/multi_reference_mean_consistent_residuals/report_results.md)).

The lesson was not that multiple measurements contain no useful information. They already entered the correction branch. An isolated change to the mean's coordinate system can cause the baseline and residual definitions to disagree. This motivated changing covariance, measurement-noise treatment, and mean centering consistently.

## Fresh training separated architecture changes from checkpoint continuation

Early averaging, covariance, and weighting tables used 1,200-update checkpoint continuations. The later matched study initialized 720 fresh fits. Its primary panel used six equally weighted endpoints, five linked-group folds, pools of at least 15 molecules, ten measurements, fixed hidden queries, and three-member ensembles ([fresh-training report](../results/analysis_history/from_scratch_mean_kernel/report_results.md)).

| Freshly trained model | R² | Spearman rho | Calibrated NLL |
|---|---:|---:|---:|
| GP with neural mean and conventional kernel | 0.5806 | 0.4107 | 0.6139 |
| Original neural model | 0.5644 | 0.3964 | 0.5832 |
| Average mean only | 0.5709 | 0.3996 | 0.5939 |
| Average-reference kernel only | 0.5810 | 0.4045 | 0.5809 |
| Average mean and average-reference kernel | 0.5810 | 0.4075 | 0.5831 |
| Kernel-softmax weighted mean and average kernel | 0.5809 | 0.4045 | 0.5837 |

The average-reference kernel changes R² by +0.0166 (paired 95% interval [+0.0093, +0.0212]). The combined model was selected as the baseline; the tables report each component comparison separately.

The neural-versus-GP NLL difference was 0.0308, with interval [−0.0060, +0.0668]. Three-member GP ensembling changed R² by 0.0076, correlation by 0.0109, and NLL by 0.0121 relative to a single GP. Earlier tables used one GP and three neural members.

Fresh fits use previously selected architectural hyperparameters. All 720 fits completed at least 4,000 updates; validation selected initialization in 120 fits.

## Similarity-weighted references

The simple weighting experiment used `softmax(RBF(q,i)/temperature)` over measured references, with temperatures 0.1, 0.3, and 1.0. ([weighting study](../results/analysis_history/kernel_weighted_mean/report_results.md)).

Before correction, weighting raised R² from 0.5059 to 0.5445 and correlation from 0.2586 to 0.3526. After correction, the weighted-versus-uniform R² difference was −0.0001, with interval [−0.0031, +0.0035].

## Multitask task combinations

The subsequent prediction study tested every nonempty subset of the six endpoints, all 63 combinations, with two sharing designs for multitask subsets. It completed 1,800 fresh fits across five globally linked folds and three seeds. One design shared the pair encoder; the broader design also shared the measured-context encoder and decoder hidden layer. Endpoint-specific heads, geometry parameters, and likelihood treatment remained private. Human, rat, and mouse were pooled within each endpoint rather than evaluated as separate transfer tasks ([multitask study](../results/analysis_history/multitask_mean_kernel_search/report_results.md)).

Task subsets were selected on validation data within each outer fold. At ten measurements in large pools, equal-endpoint R² changed from 0.5958 for single-task controls to 0.5972 for exhaustive NLL-based selection; correlation changed from 0.4368 to 0.4377 and calibrated NLL from 0.5489 to 0.5295. The tables report exploratory, unadjusted intervals by endpoint.

Forward task addition gave macro NLL 0.5345, compared with 0.5295 for exhaustive selection and 0.5353 when all six endpoints were forced together. Fixed combinations recommended from average validation scores are future deployment choices, distinct from the fold-specific selection procedure whose performance was measured.

This prediction study used globally linked folds incorporating molecules and source documents, with full outer-training data for each predictor. Inference used measurements from the evaluated assay.

## Learned acquisition features beyond mean and standard deviation

A separate single-task PPO study held predictors fixed and compared a feedforward acquisition actor using mean and standard deviation with actors also receiving 2, 4, 8, or 16 learned projections of the frozen pair-network hidden features. Pair embeddings were averaged over measured anchors before projection. The experiment tested acquisition representations, not predictive R², correlation, or NLL ([latent-feature study](../results/analysis_history/neural_latent_acquisition/report_results.md)).

| Actor input | Mean purchases to top-1, pool size at least 15 |
|---|---:|
| Mean and standard deviation | 6.325 |
| Plus 2 learned features | 6.551 |
| Plus 4 learned features | 6.523 |
| Plus 8 learned features | 6.733 |
| Plus 16 learned features | 6.748 |
| Random expectation | 10.423 |

Feature-versus-baseline intervals and endpoint-specific estimates are reported for the fixed PPO budget. Direct single-task EI was selected as the standard acquisition rule.

## Standard meta-learning and transfer-learning baselines

The common benchmark included the reference neural model, frozen transfer, ordinary fine-tuning, neural-mean conventional GP, ALPaCA, MAML, ANIL, conditional and attentive neural processes, a diagonal transformer neural process, deep-kernel transfer, and an implicit-gradient adaptive deep-kernel model. The following selected rows use five measurements for prediction and direct EI starting from one free worse-half hit for acquisition. Endpoint means are equally weighted, and pools have at least 15 compounds ([overall saved report](../results/analysis_history/meta_learning_benchmark/report_overall_results.md)).

| Method | R² | Spearman rho | Marginal NLL | Top-1 purchases |
|---|---:|---:|---:|---:|
| Current reference and EI | 0.344 | 0.376 | 0.933 | 5.907 |
| Neural mean and conventional GP | 0.322 | 0.371 | 1.019 | 5.721 |
| ALPaCA | 0.268 | 0.345 | 1.050 | 5.869 |
| Ordinary fine-tuning | 0.291 | 0.294 | 0.994 | 6.921 |
| Frozen neural ensemble | 0.271 | 0.279 | 1.039 | 7.094 |
| Random expectation | — | — | — | 10.423 |

Among methods with complete endpoint coverage, the reference had the highest macro R² and correlation and lowest NLL. Its 90% interval coverage was 87.4%. Prediction metrics are point estimates. GP used 0.186 fewer top-1 purchases, with paired interval [−0.576, +0.277]. ALPaCA's difference was −0.038 purchases, with interval crossing zero.

MAML is reported for endpoints with complete five-fold coverage: microsomal clearance, permeability, and efflux. The six-endpoint average requires complete coverage. Six configurations were unavailable after training and one failed numerically at test evaluation; selected hyperparameters were retained. All methods used full outer-training data.

## ALPaCA series-offset ablation

ALPaCA uses a learned neural basis followed by Bayesian linear adaptation. Our added series offset is an analytically inferred intercept with a flat prior, not an extra neural network. The no-offset ablation removes its mean and variance contributions but retains learned observation noise, the neural basis, and the Gaussian weight prior. Basis biases can still represent constants under a finite prior, so this is not removal of all capacity for constant shifts ([offset ablation](../results/analysis_history/alpaca_offset_ablation/report_results.md)).

At five measurements in large pools, retaining versus removing the offset gave R² 0.2675 versus 0.2646, correlation 0.3454 versus 0.3304, and NLL 1.0497 versus 1.0391. At ten measurements, R² was 0.3986 versus 0.3938, correlation 0.4101 versus 0.4246, and NLL 0.9863 versus 0.9914. Top-1 purchases were 5.8690 versus 5.8092, while top-2 and top-3 slightly favored the offset and top-4 favored its removal.

The ablation trained 90 fresh no-offset members, matching original seeds, episode streams, architecture sizes, 4,000 updates, and checkpoint selection. Offset checkpoints and their selected hyperparameters were reused. The analytic offset provides invariance to arbitrary common shifts of reference labels.

## Conclusions to carry forward

The studies report predictive accuracy, probabilistic scores, coverage, and acquisition cost separately. Intervals summarize exploratory development-fold comparisons conditional on fitted models.
