# Continued multitask NAP experiments

Exploratory comparisons on the existing main and reserved evaluation cohorts are reported below, with endpoint-balanced, random-normalized purchase counts.

This follow-up retains every screen and adds 68 completed policy fits to the 130 earlier recovery fits. Eighteen cross-fit teacher sets contain both a GP and a neural forecaster. Six additional delta-mean GP fits were screened. Counts exclude the original baseline training.

## New diagnosis and architecture changes

Cross-fit teachers exclude their held source groups from supervised losses across endpoints and species. Delta inputs use the separate delta training role. Input and outcome scalers are fitted to the acquisition-training split and shared across teacher folds.

The compact neural acquisition controller learns a mixture of GP expected improvement, GP mean, delta mean, neural expected improvement, and GP information scores. The GP information score is uncertainty times mean absolute posterior correlation with other unmeasured candidates. Warm starts use training-only labels to teach selection of the optimum in nonterminal acquisition states. Neural and GP forecasters are frozen while reinforcement learning updates the controller.

The shared controller's seed-11 initial expert weights were quite similar across endpoints, with roughly 37–39% delta weight and 19–26% GP-EI weight. This motivated a predeclared supporting architecture that retains shared forecasters and the shared controller warm start, then gives each endpoint its own 500 PPO iterations. It preserves the per-endpoint prediction and reinforcement-learning budgets. Its selection plan was recorded before evaluation. This additional comparison does not replace the previously specified shared-controller primary comparison.

A seed-11 validation-only swap separated the fixed forecaster source from the acquisition controller source. Using multitask forecasters, the shared versus separate controllers have almost identical focused scores, 0.8254 and 0.8241. With single-task forecasters, the separate controller scores 0.8091 versus 0.8886 for the shared controller. These conditional swaps suggest that simply changing the controller cannot explain all transfer behavior. Forecaster swaps also shift the controller's input distribution, so this is a sensitivity analysis rather than a clean causal estimate. Full results are in `validation_component_swap_summary.csv`. Checkpoint selection uses the saved training-time validation trace.

Other screens add query-specific mixture weights, larger-pool sampling, correlated GP probability of being the best remaining candidate, and species indicators in the acquisition gate. The species variant does not add species conditioning to the frozen forecasters. The probability expert uses 512 fixed quasi-Monte Carlo draws and canonical molecule ordering. A separate ordinal NAP predicts within-pool rank bins rather than physical value bins, with frozen versus joint surrogate updates.

A separate validation-only GP diagnostic conditions posterior draws on the known worse-half starting-hit rule. It also distinguishes the best remaining candidate from the global optimum, counting posterior worlds in which the optimum is already observed as zero mass for unmeasured candidates. Global-optimum probability improves on remaining-candidate probability, but still trails expected improvement for the multitask GP. Conditioning on starting-hit selection gives only a modest gain. These acquisition diagnostics were not promoted into additional NAP fits. Their full results are in `outputs/nap_selection_prior/combined_validation_summary.csv`.

## Validation screens

Scores divide purchases by the exact random expectation and average endpoints equally. Lower is better. Selection uses ≥15 pools when an endpoint has at least five such pools from three source groups; otherwise it uses that endpoint's full validation cohort. Three controller seeds share frozen forecasters.

| architecture | regime | seeds | all_pools | large_pools | selection_score |
| --- | --- | --- | --- | --- | --- |
| convex_mixture | multitask | 1 | 0.855 | 1.019 | 0.833 |
| crossfit_mixture | multitask | 1 | 0.851 | 0.819 | 0.853 |
| crossfit_mixture | single_task | 1 | 0.826 | 0.744 | 0.839 |
| expert_distribution | multitask | 1 | 0.876 | 0.632 | 0.884 |
| expert_distribution | single_task | 1 | 0.778 | 0.529 | 0.773 |
| large_convex_mixture | multitask | 1 | 0.831 | 0.949 | 0.814 |
| large_crossfit_mixture | multitask | 1 | 0.884 | 0.914 | 0.882 |
| large_crossfit_mixture | single_task | 1 | 0.868 | 0.772 | 0.881 |
| ordinal_frozen | multitask | 1 | 0.915 | 0.676 | 0.910 |
| ordinal_frozen | single_task | 1 | 0.827 | 0.542 | 0.824 |
| ordinal_joint | multitask | 1 | 0.870 | 0.655 | 0.860 |
| ordinal_joint | single_task | 1 | 0.847 | 0.729 | 0.837 |
| private_gate | multitask | 3 | 0.799 | 0.791 | 0.803 |
| probability_crossfit | multitask | 1 | 0.844 | 0.873 | 0.856 |
| species_probability_crossfit | multitask | 1 | 0.830 | 0.794 | 0.841 |
| warm_crossfit_mixture | multitask | 3 | 0.817 | 0.823 | 0.826 |
| warm_crossfit_mixture | single_task | 3 | 0.792 | 0.823 | 0.808 |
| warm_query_crossfit_mixture | multitask | 1 | 0.816 | 0.839 | 0.832 |

The ≥15 validation cohort contains 13 pools distributed across the endpoints as 0 in vivo, 1 protein binding, 1 cellular clearance, 6 permeability, and 5 efflux.

![Diagnosis and validation screens](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/followup_diagnostics.png)

## Exploratory acquisition evaluation

Controller and control models were specified in `exploratory_evaluation_plan.json`. Validation selects checkpoints, which are hashed before evaluation. Exploratory intervals resample global provenance groups and matched controller seeds, conditional on frozen forecasters.

The reserved baseline uses direct replay from frozen checkpoints. `reserved_baseline_reconciliation.json` records the replay check.

The acquisition charts and purchase tables also include simple greedy acquisition using the existing single-task and multitask delta predictors. At every step, the candidate score is the mean of the observed relative outcome plus the predicted ordered delta from each measured anchor to that candidate. The lowest predicted transformed objective is purchased next. Only measured anchors contribute, including the initial hit, and scores update after each purchase. There is no uncertainty bonus or reinforcement-learning policy in these baselines. The main-cohort trajectories are reused from the original benchmark; reserved-cohort trajectories use the same frozen predictors and evaluation starts. No model was refitted to add these curves.

### acquisition_test

| comparator | pools | groups | percent_improvement | percent_ci_low | percent_ci_high |
| --- | --- | --- | --- | --- | --- |
| Cross-fitted single-task NAP | 56 | 38 | 3.186 | -12.265 | 14.172 |
| single_task_NAP | 56 | 38 | 20.088 | 1.806 | 34.921 |
| multitask_NAP | 56 | 38 | 32.543 | 20.006 | 42.851 |
| single_task_GP + EI | 56 | 38 | 7.334 | -12.489 | 20.773 |
| multitask_GP + EI | 56 | 38 | -1.007 | -13.437 | 10.630 |
| Cross-fitted multitask warm start | 56 | 38 | 1.056 | -0.531 | 5.088 |

Mean additional purchases

| endpoint | Cross-fitted NAP with private adaptation | Cross-fitted multitask NAP | Cross-fitted single-task NAP | multitask_Delta greedy | multitask_GP + EI | single_task_Delta greedy | single_task_NAP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cellular_clearance | 9.310 | 8.750 | 10.171 | 10.556 | 5.722 | 9.819 | 7.958 |
| efflux | 5.719 | 5.781 | 6.750 | 4.625 | 8.906 | 5.125 | 8.906 |
| in_vivo_clearance | 10.869 | 10.893 | 9.595 | 14.536 | 7.036 | 14.429 | 12.845 |
| permeability | 6.215 | 6.319 | 5.396 | 6.208 | 7.125 | 6.125 | 8.590 |
| protein_binding | 6.462 | 6.561 | 7.644 | 6.773 | 9.750 | 8.114 | 10.091 |

Supporting private-adaptation comparison. Intervals use 97.5% coverage for the two controller-versus-matched-control comparisons.

| candidate | comparator | percent_improvement | percent_ci_low | percent_ci_high | adjusted_ci_low | adjusted_ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| Cross-fitted NAP with private adaptation | Cross-fitted single-task NAP | 2.350 | -12.074 | 12.824 | -13.657 | 14.173 |
| Cross-fitted NAP with private adaptation | Cross-fitted multitask NAP | -0.863 | -7.097 | 4.197 | -7.839 | 4.969 |
| Cross-fitted NAP with private adaptation | single_task_NAP | 19.398 | 0.050 | 33.757 | -3.721 | 35.823 |
| Cross-fitted multitask NAP | Cross-fitted single-task NAP | 3.186 | -12.265 | 14.172 | -14.477 | 15.838 |

### reserved_delta_test

| comparator | pools | groups | percent_improvement | percent_ci_low | percent_ci_high |
| --- | --- | --- | --- | --- | --- |
| Cross-fitted single-task NAP | 11 | 7 | 29.902 | -11.786 | 56.058 |
| single_task_NAP | 11 | 7 | 34.841 | 10.203 | 51.189 |
| Cross-fitted multitask warm start | 11 | 7 | 0.536 | -8.948 | 3.670 |

Mean additional purchases

| endpoint | Cross-fitted NAP with private adaptation | Cross-fitted multitask NAP | Cross-fitted single-task NAP | multitask_Delta greedy | single_task_Delta greedy | single_task_NAP |
| --- | --- | --- | --- | --- | --- | --- |
| cellular_clearance | 4.750 | 4.611 | 7.833 | 5.917 | 7.750 | 10.556 |
| efflux | 6.792 | 6.750 | 5.500 | 8.750 | 7.250 | 5.083 |
| in_vivo_clearance | 1.167 | 1.333 | 3.167 | 7.000 | 1.500 | 10.333 |
| permeability | 7.861 | 7.500 | 11.028 | 7.583 | 9.833 | 3.167 |
| protein_binding | 3.625 | 3.125 | 6.708 | 5.125 | 8.500 | 7.875 |

Supporting private-adaptation comparison. Intervals use 97.5% coverage for the two controller-versus-matched-control comparisons.

| candidate | comparator | percent_improvement | percent_ci_low | percent_ci_high | adjusted_ci_low | adjusted_ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| Cross-fitted NAP with private adaptation | Cross-fitted single-task NAP | 27.584 | -14.541 | 54.609 | -18.745 | 55.316 |
| Cross-fitted NAP with private adaptation | Cross-fitted multitask NAP | -3.306 | -10.596 | 6.840 | -12.627 | 8.149 |
| Cross-fitted NAP with private adaptation | single_task_NAP | 32.687 | 8.684 | 50.312 | 3.105 | 50.657 |
| Cross-fitted multitask NAP | Cross-fitted single-task NAP | 29.902 | -11.786 | 56.058 | -13.306 | 56.763 |

![Pool-size curves](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/followup_performance_by_cutoff.png)

![Reserved-cohort pool-size curves](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/reserved_performance_by_cutoff.png)

## Reproducibility and interpretation

The initial hit remains free and comes from the worse half of the series. Only purchased, transformed outcomes are supplied to the policy, always relative to that hit. The model never sees a success/stop signal while producing the complete sequence. The stopping time is calculated afterward against the stored optimum. For a unique remaining optimum, random purchase order takes n/2 additional purchases in expectation.

Tests cover hidden-label exclusion, permutation equivariance, probability normalization, teacher source-group separation, frozen-forecaster gradients, delta-prior gradients, ordinal-target invariance, and the inherited source-group bootstrap arithmetic. Scientific uncertainty remains separate from these implementation checks.
