# Project summary and conclusions

Updated October 6, 2026. This synthesis covers saved analyses from the microsomal-clearance pilot through the current neural reference, meta-learning comparison, and ALPaCA offset ablation, with links to reproduction code.

The [searchable history](../results/analysis_history/index.html) indexes 62 recorded branches, including experiments, validation pilots, design documents and checkpoint work. Its [catalog](../results/analysis_history/catalog.json) links archived protocols and reports, numerical tables, and historical source hashes. Detailed findings are organized into [early acquisition and augmentation](early_analysis_findings.md), [local prediction and uncertainty](prediction_analysis_findings.md), and [later architecture comparisons](architecture_analysis_findings.md).

## Main conclusions

1. **Historical molecular information improves acquisition relative to random search.** In the six-endpoint NAP comparison, the equal-endpoint top-1 purchase mean for pools of at least 15 compounds was 10.42 for random and 7.20 for New NAP.
2. **Evaluate prediction and acquisition separately.** The comparisons include neural-mean Gaussian processes and analytic expected improvement (EI).
3. **Use matched controls for architectural changes.** The studies evaluate model capacity, auxiliary tasks, multitask sharing, and augmentation within their recorded protocols.
4. **The current reference is a single-task predictor with average pairwise means, an average-reference residual kernel, learned residual correction, kernel-informed variance and an ensemble, followed by direct Gaussian EI.** It is a learned neural/kernel hybrid. The variance calculation contains an exact matrix solve, so the complete current model is not solely a feedforward neural network.
5. **Compare results within each study.** Each study records its data splits, predictor/policy label access, outcome scales, query panels, aggregation, and training budgets. Cross-validation results are exploratory.

The early acquisition totals are supported by the [earlier synthesis](../results/analysis_history/project_summary/protocol_project_summary.md). The latest equal-access comparison is supported by the [meta-learning results](../results/analysis_history/meta_learning_benchmark/report_overall_results.md).

## Scientific problem, data and metrics

The task is retrospective sequential acquisition within an analog series. Candidate structures and their MiniMol representations are known. Only acquired compounds have revealed outcomes. The initial hit is free, and subsequent purchases reveal stored assay measurements. The main deployment benchmark starts from a hit sampled from the worse half of a pool. The training environment can identify terminal success using complete retrospective labels; the deployed selector does not receive a certificate that the true optimum has been found.

The historical curated dataset has 4,625 nonconstant pools with at least three distinct compounds. Only 580 pools contain at least 15 compounds. This imbalance motivated both all-size results and the large-pool emphasis. An assay/species pool is not necessarily an independent chemical series or source group.

| Endpoint | Objective minimized | Pools | Pools with at least 15 compounds |
|---|---|---:|---:|
| Microsomal clearance | Log clearance | 1,827 | 311 |
| In vivo clearance | Log clearance | 537 | 20 |
| Plasma protein binding | Log bound/free ratio | 880 | 44 |
| Cellular clearance | Log clearance | 524 | 79 |
| Apical-to-basolateral permeability | Negative log permeability | 516 | 72 |
| Efflux | Log basolateral-to-apical/apical-to-basolateral ratio | 341 | 54 |

Human, rat and mouse measurements were retained for clearance and binding. The curated permeability and efflux pools also include dog-derived assay systems. The protein-binding quantity is an apparent bound/free ratio. Without protein concentration and a binding model it is not an identified dimensional association constant. Efflux direction follows the curated row annotation. [Data contract](data.md).

The primary acquisition metric became **additional purchases to reach any top-1, top-2, top-3 or top-4 compound**, including ties. It does not mean buying every member of the top four, nor success within four purchases. The initial hit can already satisfy a relaxed target, giving zero purchases. Top-4 is consequently trivial in pools of size three or four. Small pools still provide training signal and meaningful top-1 comparisons, but not every top-k statistic is informative for them.

For one free nonoptimal hit and one unique optimum in a pool of size \(n\), uniform random acquisition needs \(n/2\) purchases in expectation, including the successful purchase. With \(g\) acceptable unmeasured compounds, the expectation is \(n/(g+1)\). [Metric study](../results/analysis_history/nap_acquisition_metrics/protocol_report.md).

Prediction diagnostics use R², within-series Spearman correlation and negative log likelihood, abbreviated NLL. Spearman measures the ranking of hidden compounds within a series. Subtracting a shared reference does not change that ranking. R² also measures magnitude and offset accuracy, so a model can rank moderately well while making large numerical errors. A frozen predictor can improve after new observations because its context-dependent calculation changes even when its learned parameters do not.

NLL evaluates predictive density and penalizes both unwarranted confidence and excessive diffuseness. It is not a pure calibration measure independent of mean accuracy. Coverage must be interpreted with interval width and density scores. Likelihoods computed in different endpoint units or with different standardization scales are not directly comparable. [Methods](methods.md).

## Initial delta predictor and NAP development

The first delta predictor concatenated two ordered MiniMol embeddings and predicted their transformed property difference.  At acquisition time, measured anchors supplied query estimates consisting of the observed anchor outcome plus the predicted query-minus-anchor delta. Their mean and spread became dynamic features. A singleton spread of zero meant only one anchor estimate, not zero predictive uncertainty.

The delta study evaluates ranking, uncertainty, pool-size strata, and acquisition with predictor-matched controls ([delta study](../results/analysis_history/delta_acquisition_experiment/report_report.md)).

“Old NAP,” “New NAP,” and the current reference are different architectures. Old NAP used a compact Transformer-based predictive distribution and acquisition head. New NAP used frozen, group-cross-fitted forecasters with a small controller mixing expert acquisition ranks. Its acquisition inputs included GP and neural predictions. The later residual-kernel neural predictor followed a separate development path.

Multitask studies evaluated task conditioning, gradient interactions, private components, ordinal objectives, and expert mixtures. New NAP used cross-fitted teachers that excluded controller-training-group labels. Predictor-screen and expert-distribution pilot results are recorded separately ([multitask study](../results/analysis_history/nap_multitask_recovery/protocol_report.md), [cross-fitting](../results/analysis_history/nap_multitask_crossfit/protocol_report.md), [pilot](../results/analysis_history/nap_multitask_expert_distribution/protocol_pilot_result.json)).

## Five-fold evaluation and interpretation of decisions

Experiments progressed from development splits to grouped five-fold evaluation. Relevant molecule, species, source-document, and cross-endpoint relationships were grouped by the recorded split generation. Earlier experiments separated delta-training and acquisition-training roles; later meta-learning comparisons used full outer-training data for each predictor.

In the earlier large-pool six-endpoint benchmark, mean top-1 purchases were approximately 10.42 for random, 7.69 for delta greedy, 7.30 for GP + EI, 7.89 for Old NAP and 7.20 for New NAP. In vivo clearance had 20 large pools, compared with 311 microsomal pools. [Earlier synthesis](../results/analysis_history/project_summary/protocol_project_summary.md).

The New NAP decision audit replayed 148,476 actions exactly. In about 90–94% of disagreements with delta greedy in large pools, the GP mean preferred the NAP choice over the delta choice. All six first-disagreement override intervals included zero. [Decision audit](../results/analysis_history/new_nap_greedy_diagnostics/report_findings.md).

## Starting conditions, augmentation and value learning

The initial-hit study retrained for the worst 10, 20, 30 and 40 percent and compared with the existing 50-percent condition. It separated a change in test-start difficulty from a change in training. At small pool sizes, several percentages can select the same finite set, so fractional labels are not always distinct experimental conditions.

Multi-hit augmentation supplied combinations of two through five lower-half compounds during training, retaining one-hit validation and testing. Cumulative top-removal augmentation removed one through five best compounds during training and left test pools intact ([initial hits](../results/analysis_history/acquisition_fivefold_initial_hit_sensitivity/report_report.md), [multi-hit augmentation](../results/analysis_history/acquisition_fivefold_lower_half_multihit_augmentation/report_report.md), [top removal](../results/analysis_history/top_removal_augmentation/report_results.md)).

Auxiliary top-2 through top-6 heads predicted remaining costs on sampled trajectories. [Auxiliary targets](../results/analysis_history/nap_topk_auxiliary/report_results.md).

Value learning used learned cost-to-go, Double-Q updates, compact prediction summaries, Deep Sets and attention variants. Planning used hypothetical GP outcomes, short lookahead and Monte Carlo tree search. These experiments were expanded from an initial screen to all endpoints and then all tested families. [All value methods](../results/analysis_history/value_all_methods/report_results.md).

## Species heads, EI inputs and assay overlap

The first species-head experiment is recorded as a three-input ablation. The subsequent feature-preserving experiment retained the other feature paths and used GP mean, standard deviation, and incumbent.

A four-cell factorial then separated species treatment from EI replacement. Large-pool top-1 means were 7.200 for the original, 7.262 for species heads only, 7.487 for EI inputs only, and 7.278 for both. The main contrasts and interaction had intervals crossing zero. This did not support attributing the combined change to either modification alone. [Factorial results](../results/analysis_history/nap_species_ei_factorial/report_findings.md).

Exact shared standardized structures linked 3,644 endpoint-local series into 2,245 inferred overlap groups. Of these, 676 spanned at least two assays and 237 at least three. Split generation uses its separately recorded grouping metadata ([overlap table](../results/analysis_history/assay_overlap/overlap_summary.csv)).

## Learning an unfamiliar series and useful unsuccessful experiments

The local-learning experiment held a common hidden query panel fixed while revealing nested contexts. This prevents an apparent improvement that merely removes hard compounds from evaluation. GP ranking improved as local measurements arrived, whereas the frozen neural forecaster improved much less. The shape and size of the improvement varied by series.

Retrospective counterfactual reveals evaluate how individual measurements change predictions for the remaining hidden compounds.

Expected-outcome controls separate changes due to molecular location from changes due to the observed label ([local-learning findings](../results/analysis_history/local_series_learning/report_findings.md)).

## External memory, GP means and molecular kernels

The external-memory model encoded historical molecular pairs into keys and values. A query pair retrieved an attention-weighted vector which a downstream network used to predict a delta. Historical memory and local measured context were distinct information sources. Full MiniMol and principal-component inputs, embedding dimensions and decoder capacities were tuned. [Memory findings](../results/analysis_history/pair_memory_benchmark/report_findings.md).

The GP work separated expected signed differences from covariance. A learned mean can predict which molecule is higher or lower; a symmetric positive-semidefinite covariance models how residual deviations co-vary. Deep mean and deep kernel variants were compared with tuned conventional kernels. A neural mean plus a conventional kernel became the preferred GP comparator in this study. [GP comparison](../results/analysis_history/pair_memory_benchmark_deep_gp/report_findings.md).

Tanimoto, covariance remapping and multiple Morgan-fingerprint similarities were tested. The radial-only comparison was followed by a direct-covariance extension. These studies compare geometry together with its representation, covariance mapping, noise treatment and tuning budget. An arbitrary distance-to-covariance conversion need not be positive semidefinite, and a single metric is not universally optimal. The direct extension was exploratory because it followed inspection of the earlier results. [Remapping](../results/analysis_history/pair_memory_benchmark_kernel_remapping/report_findings.md), [Morgan metrics](../results/analysis_history/pair_memory_benchmark_morgan_metrics/report_findings.md), [direct extension](../results/analysis_history/pair_memory_benchmark_morgan_metrics_direct_extension/report_findings.md).

## Acquisition features, optimizers and auxiliary prediction

With the neural-mean GP fixed, a broad search tested incumbent and delta features, molecular coordinates, Deep Sets, cross-attention, full and compact Set Transformers, and state statistics. In that study, mean/SD NAP averaged 5.695 large-pool top-1 purchases, compact Set Transformer 5.877, full Set Transformer 6.173 and GP + EI 5.570. These figures belong to that study's aggregation and predictor allocation. [Set-context study](../results/analysis_history/nap_set_context/report_results.md).

The distance-context study evaluated Tanimoto and MiniMol distances to acquired molecules ([distance study](../results/analysis_history/nap_distance_context/report_results.md)).

The optimizer comparison tested proximal policy optimization (PPO), trust region policy optimization (TRPO) and direct preference optimization (DPO) with matched actors and detached critic features. The seven primary Holm-adjusted contrasts were nonsignificant. [Optimizer results](../results/analysis_history/nap_policy_optimization/report_results.md).

Random-pair auxiliary supervision selected a series in proportion to its compound count and then a uniform pair. Thus total pair samples grew linearly with series size rather than quadratically. True trajectory-dependent predictor updates were examined later in joint GP/PPO training. [Weight search](../results/analysis_history/gp_auxiliary_weight_search/report_results.md).

## Selecting batches and learning the EI transformation

Batch selectors chose all members before revealing their outcomes. Deep Sets and pair-aware Transformers scored subsets followed by search; batch PPO constructed pending selections autoregressively; Gumbel top-k used a differentiable training relaxation with hard distinct selections at evaluation. Their original inputs included GP predictions and other engineered features, so these were not structure-only comparisons.

GP controls included joint batch EI and mean-fantasy EI. A mean fantasy uses a hypothetical measurement equal to the current mean to reduce redundancy through covariance updates. In the historical large-pool comparison, Deep Sets needed 3.189 versus 3.091 rounds for joint EI at batch size two, and 1.673 versus 1.659 at batch size five. Every compound in the successful final batch counted toward purchases. [Batch report](../results/analysis_history/batch_subset_selection/report_results.md).

Further experiments removed node embeddings and introduced pairwise distances or GP covariance into attention, including batch sizes one, two and five. They used supervised subset losses, which must not be mistaken for direct optimization of purchase counts.

Providing EI ingredients or the normal density and cumulative probability did not guarantee that a learned scorer would reproduce EI. The loss, initialization, amount of data and available state information still matter. Early ingredient studies used supervised scores; later ones used PPO and separately tested EI-imitation initialization. Joint GP/PPO experiments removed the two-stage training assumption. None of these interventions should be described as the same comparison merely because their input lists overlap. [Input study](../results/analysis_history/nap_ei_inputs_k1/protocol_readme.md), [PPO study](../results/analysis_history/nap_phi_ppo_k1/protocol_readme.md), [joint training](../results/analysis_history/joint_gp_ppo/protocol_readme.md).

## Neural uncertainty and residual-kernel adaptation

The neural uncertainty work compared heteroscedastic networks, variational Bayesian neural networks, evidential regression, conditional models and ensembles. Continuous deltas used Gaussian or Student-t predictive distributions. A Dirichlet output would describe category probabilities rather than directly model a continuous clearance value.

The distance-aware neural ensemble supplied a learned pair baseline and adapted using residuals at measured molecules. Later iterations explored context encoders, residual-graph correction and alternative uncertainty models. Three-member mixture uncertainty included both member variance and disagreement between member means. Density evaluation used the actual mixture; acquisition using Gaussian EI used its marginal mean and variance.

The residual iteration approximately solves a regularized kernel system. Its coefficients weight measured residuals, accounting for overlap in their kernel influence. Kernel structure then informed variance as well as mean.

The option-2 variance study used matched checkpoint continuation. At ten measurements, calibrated NLL was 0.580 versus 0.583 for the control; top-1 costs were 5.500 versus 5.509, with a paired interval including zero. Validation selected initialization for 64 of 90 option-2 members ([uncertainty benchmark](../results/analysis_history/neural_uncertainty/report_results.md), [option-2 results](../results/analysis_history/kernel_variance_option2/report_results.md)).

## Noisy references, averaging and fresh retraining

Subtracting the initial hit removes a shared additive offset on the transformed scale, but it also shares that hit's measurement noise across all differences. Estimates derived from the same neural predictor or common anchors are not generally independent. Equal or inverse-variance averaging therefore requires assumptions that cannot be inferred merely from independent laboratory errors.

The `checkpoint_1` architecture served as the starting point for average pair baselines, consistent residual definitions, average-reference covariance, and kernel-softmax weighting. Archived tables identify checkpoint-continuation and fresh-training protocols.

Fresh-training comparisons informed selection of the average-mean, average-reference-kernel model ([fresh results](../results/analysis_history/from_scratch_mean_kernel/report_results.md), [weighting](../results/analysis_history/kernel_weighted_mean/report_results.md)).

For measured context count \(n\), unmeasured candidate count \(p\), and \(t\) dense residual iterations, mean-correction cost is \(O(tn^2+pn)\), aside from neural feature evaluation. The conditional-variance solve adds \(O(n^3+pn^2)\). Dense working memory includes \(O(n^2)\) context and \(O(pn)\) cross terms; chunking reduces the latter.

## Task combinations, latent acquisition features and the current standard

The later multitask search evaluated every nonempty subset of the six endpoints, giving 63 task combinations. Gains depended on endpoint and metric. Likelihood improvement was more consistent than uniform improvement in R² and rank correlation. Validation-selected combinations and their uncertainty are more meaningful than choosing the best test-table cell. [Task combinations](../results/analysis_history/multitask_mean_kernel_search/report_results.md).

The latent-feature study compared two, four, eight, and sixteen additional features. The EI comparison gave large-pool top-1 costs of 6.325 for mean/SD, 6.289 for mean/SD/EI, and 6.176 for direct EI, with paired intervals crossing zero. Direct EI was selected as the standard rule ([latent features](../results/analysis_history/neural_latent_acquisition/report_results.md), [direct EI](../results/analysis_history/neural_ei_acquisition/report_results.md)).

## Standard meta-learning and ALPaCA comparisons

The final broad comparator set included frozen transfer, fine-tuning, model-agnostic meta-learning, head-only adaptation, conditional and attentive neural processes, a Transformer neural process, deep-kernel transfer, adaptive deep-kernel fitting, neural-mean GP, and adaptive learning for probabilistic connectionist architectures (ALPaCA). The comparison used common modern folds and equal predictor label access.

For pools with at least 15 compounds, the latest equal-assay prediction summary at five measured compounds is below. Purchase counts describe a separate sequential-acquisition evaluation.

| Method | R² | Spearman ρ | Mixture NLL | Purchases to top-1 |
|---|---:|---:|---:|---:|
| Current neural/kernel reference | 0.3436 | 0.3762 | 0.9325 | 5.9072 |
| Neural mean + conventional GP | 0.3225 | 0.3711 | 1.0195 | 5.7212 |
| ALPaCA | 0.2675 | 0.3454 | 1.0497 | 5.8690 |
| ALPaCA without extra offset | 0.2646 | 0.3304 | 1.0391 | 5.8092 |

The main benchmark completed 353 of 360 fold-level evaluations; three MAML endpoint conditions lacked all five successful folds and were excluded from the complete-assay aggregate. The no-offset ALPaCA ablation completed all 30 endpoint/fold evaluations. [Complete-assay results](../results/analysis_history/meta_learning_benchmark/report_overall_results.md), [ALPaCA ablation](../results/analysis_history/alpaca_offset_ablation/report_results.md).

ALPaCA learns a neural basis and a prior over linear coefficients, then updates those coefficients analytically from the measured context. The added unknown series offset allows a common local level to move without forcing the basis weights to explain it; its uncertainty also contributes to the predictive variance. The no-offset ablation fixed that additional term to zero while keeping matched selected settings and fresh initialization.

## What remains unestablished

These retrospective benchmarks evaluate recorded experimental outcomes.

Confidence intervals resample linked groups conditional on fitted models. Each comparison records its cohort, target, multiplicity adjustment, uncertainty convention, and comparator access.

## Reproduction added to the repository

The [reproduction guide](reproduction_guide.md) distinguishes three operations. Historical evidence and graphs can be regenerated from bundled tables. Current-model diagnostics can be rerun from explicitly checked saved checkpoints. Fresh model/policy comparisons can be trained using editable recipes with their own provenance and output directories.

The new recipes cover starting-hit sensitivity, multi-hit context augmentation, cumulative best-compound removal, fixed-query local-learning curves, counterfactual experiment value, and conventional versus molecular-fingerprint GP kernels. Existing recipes cover optimizer comparisons, acquisition features, mean/kernel ablations, batch selection and the broad meta-learning comparison. Newly trained results will be separate experiments under the common repository protocol; they will not silently replace the archived numbers described here.
