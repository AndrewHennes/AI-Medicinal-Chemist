# Findings from the earlier acquisition studies

These findings summarize saved experiments under their recorded models, splits, training budgets, and evaluation conventions. Early studies used a single split; later studies used five folds. Results are exploratory internal evaluations.

## Initial microsomal delta model and NAP

The first plain delta predictor concatenated two 512-dimensional MiniMol representations, giving 1,024 input coordinates. A feedforward network with hidden widths 256, 128, and 64 predicted the signed difference in log10 clearance. No sign-consistency, reversed-pair averaging, cycle, or self-zero constraint was imposed. The frozen predictor supplied a mean and sample standard deviation over currently measured anchors to the acquisition policy. The singleton standard deviation was zero by convention; this represented missing disagreement information and did not imply certain prediction. ([Original report](../results/analysis_history/delta_acquisition_experiment/report_report.md))

On the independent 77-pool predictor test set, root mean squared error was 0.571 log10 units, versus 0.607 for the zero-delta baseline; mean absolute error was 0.446 and directional accuracy was 62.9%. On a separate 244-pool acquisition test set, mean purchases to the optimum were 3.177 for random, 2.316 for delta greedy, 2.326 for NAP control, and 2.311 for NAP with delta summaries. The augmented policy saved 0.015 purchases over its matched control, with a 95% source-group bootstrap interval from −0.030 to 0.058. ([Original report](../results/analysis_history/delta_acquisition_experiment/report_report.md))

Among 27 test pools with at least 15 compounds, greedy needed 3.731 purchases and the augmented NAP 3.917, compared with 8.387 for random. Among the 14 pools with at least 25 molecules, the augmented NAP had a lower mean than greedy, 4.720 versus 5.821. The latter comparison had a wide group-bootstrap interval. 311 of the 1,827 curated microsomal pools contained at least 15 molecules, and large pools were scarce in the early validation split. ([Pool-size analysis](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/size_analysis/report.md))

The interpretation study compared a trained policy with greedy and EI computed from that same policy's conditional predictions, and with its fixed initial ranking. ([Policy interpretation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/policy_interpretation/report.md))

## Early multitask regression and recovery

The first shared model combined five endpoints, excluding microsomal clearance at that stage. On the held-out large-pool cohorts, shared GP plus EI improved its point estimate on four of five endpoints, delta greedy improved on two, and the original shared NAP improved on none. The test cohorts contained 7 to 18 large pools per endpoint. Cellular-clearance GP plus EI improved from 7.806 to 5.722 purchases. ([Multitask comparison](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/report.md))

Recovery experiments tested shared/private heads, adapters, private experts, a context-token connection to the acquisition head, gradient projection during prediction pretraining, alternative rewards, changed sampling, and GP-conditioned controllers. Cross-task gradient misalignment supported interference as one possible contributor. A second diagnosis found that training-group GP predictions were more optimistic than group-excluded predictions, supporting a reason to train controllers using cross-fitted forecasters. Neither diagnostic isolated a unique cause. ([Recovery report](../results/analysis_history/nap_multitask_recovery/protocol_report.md), [cross-fitting report](../results/analysis_history/nap_multitask_crossfit/protocol_report.md))

The revised warm-started, cross-fitted multitask controller improved the endpoint-balanced, random-normalized purchase metric over the *original* single-task NAP by 20.1% on the main large-pool cohort and 34.8% on a reserved cohort. Improvement over the *identically revised* single-task controller was 3.2% and 29.9%, with both intervals including no improvement. The reinforcement-learning stage itself added about 1.1% and 0.5% over the supervised warm start, also with intervals crossing zero. Two of three shared-controller seeds selected the iteration-zero checkpoint. These comparisons use the development cohorts. ([Cross-fitting report](../results/analysis_history/nap_multitask_crossfit/protocol_report.md))

## Five-fold acquisition benchmark and metric changes

The project moved from one small split to five grouped outer folds. Within each fold, model and checkpoint selection used its training and validation data. Outcomes remained relative to a free starting hit; related species and provenance groups stayed together. The final acquisition metrics became purchases to reach any top-1, top-2, top-3, or top-4 molecule, with rank-boundary ties accepted. Already qualifying starting hits cost zero. Top-4 is automatically zero in pools of three or four molecules, so all-pool curves and large-pool curves answer different questions. ([Five-fold report](../results/analysis_history/acquisition_fivefold/report_report.md))

The five-endpoint report used 2,798 pools. Its macro-average large-pool top-1 counts were 7.609 for revised single-task NAP, 7.972 for revised multitask NAP, 7.577 for single-task GP plus EI, 8.059 for single-task delta greedy, and 10.786 for random. Microsomal clearance was subsequently added as a sixth endpoint, bringing the studies below to 4,625 pools, including 580 with at least 15 compounds. ([Five-fold report](../results/analysis_history/acquisition_fivefold/report_report.md), [six-endpoint removal report](../results/analysis_history/top_removal_augmentation/report_results.md))

A delta-plus-EI experiment used the variation of pairwise predictions over historical training anchors as a Gaussian uncertainty surrogate. In the five-endpoint large-pool comparison, single-task delta plus EI required 8.836 top-1 purchases versus 7.577 for its matched GP plus EI, a difference of 1.259 with a nominal interval from 0.085 to 2.470. ([Five-fold report](../results/analysis_history/acquisition_fivefold/report_report.md))

## Initial-hit sensitivity

The completed sensitivity study retrained sampling-dependent components for initial hits drawn from the worst 10%, 20%, 30%, and 40%, in addition to the existing worst-50% condition. It also evaluated the unchanged 50%-trained models on the same altered starts. All six endpoints, five outer folds, and three NAP seeds were included. The same latent random draws were used across fractions; small pools could have identical eligible starting sets. ([Sensitivity protocol](../results/analysis_history/acquisition_fivefold_initial_hit_sensitivity/report_report.md))

For pools of at least 15 compounds, the revised NAP's retrained-minus-fixed-50% top-1 purchase differences were −0.467 at 10%, −0.257 at 20%, +0.193 at 30%, and +0.249 at 40%, averaged equally across endpoints. The original NAP's corresponding differences were positive at all four percentages, from +0.164 to +0.469. Changing the percentage itself also changes task difficulty, so the matched-versus-fixed comparison at the *same* percentage is the relevant retraining contrast. These are descriptive cross-validation results. ([Paired numerical results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/initial_hit_sensitivity/reports/paired_retraining_purchase_differences.csv))

## Multi-hit training augmentation

Half of eligible training draws retained the original single-hit recipe, while the other half began with two through five free observations sampled from the worst half. The historical intervention affected supervised prediction contexts, policy warm starts, rollouts, and revised-NAP neural forecasters; validation and test remained single-hit. Budgets were fixed by updates and sampled episodes, so shorter augmented episodes could consume fewer transitions. ([Multi-hit protocol and findings](../results/analysis_history/acquisition_fivefold_lower_half_multihit_augmentation/report_report.md))

In the six-endpoint large-pool macro-average, original-NAP top-1 purchases rose from 7.889 to 8.055, a difference of +0.167 with a nominal 95% interval from −0.326 to +0.581. Revised NAP rose from 7.200 to 7.292, a difference of +0.092 with an interval from −0.058 to +0.282. The corresponding top-2, top-3, and top-4 intervals also crossed zero. ([Paired differences](../results/analysis_history/acquisition_fivefold_lower_half_multihit_augmentation/paired_purchase_differences.csv))

## Cumulative top-removal augmentation

The historical removal experiment mixed unchanged pools with pools missing a uniformly sampled feasible count of their best one through five molecules. The intervention left at least three compounds and sampled the initial hit from the worst half of the remaining pool. Evaluation always used the original complete held-out pools and identical starts. With tied outcomes, exactly the requested number of molecules was removed, so a tied optimum could remain. ([Removal report](../results/analysis_history/top_removal_augmentation/report_results.md))

For large pools, original NAP on efflux improved from 8.523 to 7.701 purchases, a difference of −0.823 with an unadjusted 95% interval from −1.635 to −0.042. The revised NAP's corresponding efflux result changed from 6.858 to 7.194. The revised model's removal-versus-control intervals crossed zero for all six large-pool top-1 endpoint comparisons. ([Paired removal results](../results/analysis_history/top_removal_augmentation/paired_purchase_differences.csv))

## Auxiliary top-k tasks

Five extra heads estimated continuation purchase costs for reaching any top-2 through top-6 molecule under the current top-1 policy. They were trained on Monte Carlo trajectory costs rather than optimal Q values, and the main acquisition policy still used PPO. The auxiliary loss coefficient was fixed at 1.0. All 180 new policy fits were locked before test scoring. ([Auxiliary-task report](../results/analysis_history/nap_topk_auxiliary/report_results.md))

The revised NAP's large-pool top-1 point estimate improved on five of six endpoints. Across both NAP variants, four target ranks, and both reported cutoffs, none of the paired 95% intervals lay wholly below zero. ([Auxiliary findings](../results/analysis_history/nap_topk_auxiliary/report_results.md))

## Value learning and search

The value-learning program evaluated compact prediction-summary models, Deep Sets pooling, attention-based value models, validation-selected refinements, shallow lookahead, and Monte Carlo tree search. Its six-endpoint expansion used five outer folds, three seeds, and four matched worst-half starts. Frozen delta predictions and group-excluded GP teachers supplied predictive features. The compact model used Double-Q cost learning and selected the action with the smallest estimated remaining top-1 purchase cost. ([Complete value-model report](../results/analysis_history/value_all_methods/report_results.md))

The table gives mean purchases for pools with at least 15 molecules from that study. Lower is better.

| Endpoint | Revised NAP | Compact value | Set-pooling value | Attention value | Selected value plus tree search |
| --- | ---: | ---: | ---: | ---: | ---: |
| Microsomal clearance | 5.400 | 5.348 | 6.622 | 6.159 | 5.653 |
| In vivo clearance | 9.600 | 8.787 | 11.017 | 10.867 | 9.371 |
| Plasma protein binding | 6.716 | 7.403 | 8.892 | 8.803 | 8.759 |
| Cellular clearance | 6.500 | 6.912 | 8.014 | 8.781 | 7.111 |
| Permeability | 8.127 | 8.610 | 9.491 | 9.690 | 8.854 |
| Efflux | 6.858 | 7.148 | 9.559 | 9.113 | 6.938 |

The compact value model's large-pool differences from revised NAP had intervals crossing zero on each endpoint. Search used the validation-selected value model, hypothetical GP observations, and a candidate shortlist during the first eight real purchases, followed by direct Q selection. Historical NAP training budgets were recorded separately ([complete report and paired intervals](../results/analysis_history/value_all_methods/report_results.md)).

## What these studies collectively support

These are conclusions about tested recipes. They are not proofs that reinforcement learning, multitask learning, or the alternative architectures cannot help. The new [augmentation replication code](augmentation_analyses.md) preserves the core comparisons under the current package APIs and records its changed protocol explicitly.
