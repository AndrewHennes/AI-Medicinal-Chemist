# NAP multitask recovery experiments

Candidate development uses only the existing globally separated acquisition-training and validation pools. No sign consistency or oracle information was added to policy inputs. All observed outcomes and frozen delta-anchor estimates remain relative to the initial hit.

## What the diagnostics support

The original acquisition head sees the histogram prediction, a raw feature projection, and three state summaries. It does not directly receive the context-encoded query token. The recovery models test that additional connection, private task heads, task adapters, selective sharing, private experts, and separate policy adaptation after shared prediction pretraining. Other controlled variants test full candidate-pool attention, reference-centered embeddings, prediction distributions, initial acquisition priors, sampling emphasis, and reinforcement-learning updates.

PCGrad is applied only during supervised prediction pretraining, and only to shared parameters. It projects conflicting task gradients and leaves private heads untouched, following Yu et al. ([paper](https://arxiv.org/abs/2001.06782)). Its results do not test gradient projection during PPO.

GP-conditioned hybrids use a frozen GP posterior and acquisition prior. Comparators include GP-only acquisition and the corresponding single-task hybrid.

## Validation and selection

Architecture screening uses validation data and repeats candidate seeds before test selection. The ≥15 validation cohort has 13 pools, with endpoint counts of 0 in vivo clearance, 1 binding, 1 cellular clearance, 6 permeability, and 5 efflux.

Each ordinary candidate receives 800 prediction updates and 500 PPO iterations per task. A shared model receives the sum of those task budgets. Matched single-task controls use the same revised architecture and per-task exposure. The shared-pretraining/private-RL model reuses shared prediction pretraining and allocates the same PPO budget independently to each task. Larger-pool sampling changes the distribution of episodes, not the split or nominal update budget.

Checkpoint selection uses all validation pools, with equal endpoint weights after normalization by the exact random expectation. Revised single-task and multitask models share this selection rule.

| architecture | regime | cutoff | mean | std | count |
| --- | --- | --- | --- | --- | --- |
| adapter_rank | multitask | 3 | 0.898 | nan | 1 |
| adapter_rank | multitask | 15 | 0.563 | nan | 1 |
| centered_context | multitask | 3 | 0.848 | nan | 1 |
| centered_context | multitask | 15 | 0.521 | nan | 1 |
| context_heads | multitask | 3 | 0.859 | 0.039 | 3 |
| context_heads | multitask | 15 | 0.520 | 0.065 | 3 |
| context_heads | single_task | 3 | 0.814 | 0.008 | 3 |
| context_heads | single_task | 15 | 0.564 | 0.055 | 3 |
| context_rank | multitask | 3 | 0.908 | nan | 1 |
| context_rank | multitask | 15 | 0.564 | nan | 1 |
| delta_prior_context | multitask | 3 | 0.872 | nan | 1 |
| delta_prior_context | multitask | 15 | 0.692 | nan | 1 |
| dual_prior_context | multitask | 3 | 0.811 | nan | 1 |
| dual_prior_context | multitask | 15 | 0.782 | nan | 1 |
| frozen_adapter_rank | multitask | 3 | 0.970 | nan | 1 |
| frozen_adapter_rank | multitask | 15 | 0.937 | nan | 1 |
| frozen_context_rank | multitask | 3 | 0.977 | nan | 1 |
| frozen_context_rank | multitask | 15 | 1.168 | nan | 1 |
| gaussian_context | multitask | 3 | 0.889 | nan | 1 |
| gaussian_context | multitask | 15 | 0.660 | nan | 1 |
| gp_context_rank | multitask | 3 | 0.808 | nan | 1 |
| gp_context_rank | multitask | 15 | 0.929 | nan | 1 |
| gp_frozen_context_rank | multitask | 3 | 0.829 | 0.025 | 3 |
| gp_frozen_context_rank | multitask | 15 | 0.819 | 0.026 | 3 |
| gp_frozen_context_rank | single_task | 3 | 0.803 | 0.005 | 2 |
| gp_frozen_context_rank | single_task | 15 | 0.761 | 0.155 | 2 |
| gp_statistical | multitask | 3 | 0.847 | nan | 1 |
| gp_statistical | multitask | 15 | 0.694 | nan | 1 |
| hitting_time_context | multitask | 3 | 0.884 | nan | 1 |
| hitting_time_context | multitask | 15 | 0.529 | nan | 1 |
| hitting_time_frozen | multitask | 3 | 0.865 | nan | 1 |
| hitting_time_frozen | multitask | 15 | 0.523 | nan | 1 |
| hitting_time_shaped | multitask | 3 | 0.834 | nan | 1 |
| hitting_time_shaped | multitask | 15 | 0.588 | nan | 1 |
| large_pool_context | multitask | 3 | 0.814 | nan | 1 |
| large_pool_context | multitask | 15 | 0.543 | nan | 1 |
| mixed_adapter_rank | multitask | 3 | 0.947 | nan | 1 |
| mixed_adapter_rank | multitask | 15 | 0.735 | nan | 1 |
| original | multitask | 3 | 0.881 | 0.041 | 3 |
| original | multitask | 15 | 0.602 | 0.179 | 3 |
| original | single_task | 3 | 0.838 | 0.014 | 3 |
| original | single_task | 15 | 0.779 | 0.156 | 3 |
| pcgrad_context | multitask | 3 | 0.880 | nan | 1 |
| pcgrad_context | multitask | 15 | 0.486 | nan | 1 |
| pcgrad_frozen_context | multitask | 3 | 0.853 | nan | 1 |
| pcgrad_frozen_context | multitask | 15 | 0.589 | nan | 1 |
| pool_context | multitask | 3 | 0.863 | 0.080 | 3 |
| pool_context | multitask | 15 | 0.641 | 0.051 | 3 |
| pool_context | single_task | 3 | 0.851 | 0.003 | 2 |
| pool_context | single_task | 15 | 0.731 | 0.078 | 2 |
| private_heads | multitask | 3 | 0.855 | nan | 1 |
| private_heads | multitask | 15 | 0.746 | nan | 1 |
| related_task_experts | multitask | 3 | 0.849 | 0.031 | 3 |
| related_task_experts | multitask | 15 | 0.732 | 0.228 | 3 |
| relative_context | multitask | 3 | 0.861 | 0.056 | 3 |
| relative_context | multitask | 15 | 0.551 | 0.152 | 3 |
| relative_gaussian_context | multitask | 3 | 0.923 | nan | 1 |
| relative_gaussian_context | multitask | 15 | 0.741 | nan | 1 |
| relative_pool_context | multitask | 3 | 0.837 | nan | 1 |
| relative_pool_context | multitask | 15 | 0.503 | nan | 1 |
| shared_pretrain_private_rl | multitask | 3 | 0.824 | 0.005 | 3 |
| shared_pretrain_private_rl | multitask | 15 | 0.467 | 0.035 | 3 |
| shared_private_experts | multitask | 3 | 0.882 | nan | 1 |
| shared_private_experts | multitask | 15 | 0.630 | nan | 1 |

![Validation diagnostics](validation_diagnostics.png)

## Locked acquisition-test comparison

The primary population is pools with at least 15 compounds. The primary metric averages, equally across endpoints, each endpoint’s mean number of additional purchases divided by its exact random expectation. Lower is better. The initial hit is free. For a unique remaining optimum in a pool of size n, random acquisition needs n/2 additional purchases in expectation; ties and an already optimal initial hit are handled exactly.

Uncertainty uses 10,000 paired bootstrap draws over global provenance groups and matched training seeds. Starts, species pools, and cross-endpoint links remain grouped during resampling.

| candidate | comparator | cutoff | pools | groups | endpoints | candidate_score | comparator_score | improvement | ci_low | ci_high | percent_improvement | percent_ci_low | percent_ci_high | conditional_ci_low | conditional_ci_high | draws | seeds | seed_resampling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Adapted multitask NAP ensemble | Matched single-task NAP ensemble | 15 | 56 | 38 | 5 | 0.970 | 1.042 | 0.072 | -0.236 | 0.157 | 6.955 | -26.796 | 14.956 | -0.072 | 0.174 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Original single-task NAP ensemble | 15 | 56 | 38 | 5 | 0.970 | 0.950 | -0.020 | -0.260 | 0.200 | -2.091 | -29.397 | 19.057 | -0.152 | 0.151 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Single-task NAP with shared inputs ensemble | 15 | 56 | 38 | 5 | 0.970 | 1.014 | 0.044 | -0.250 | 0.175 | 4.367 | -28.239 | 16.575 | -0.106 | 0.157 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Joint multitask NAP ensemble | 15 | 56 | 38 | 5 | 0.970 | 1.069 | 0.099 | -0.207 | 0.312 | 9.232 | -22.534 | 27.282 | -0.057 | 0.291 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | single_task_NAP | 15 | 56 | 38 | 5 | 0.970 | 0.928 | -0.042 | -0.264 | 0.149 | -4.545 | -30.087 | 15.204 | -0.158 | 0.098 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | multitask_NAP | 15 | 56 | 38 | 5 | 0.970 | 1.099 | 0.129 | -0.119 | 0.374 | 11.750 | -11.737 | 31.669 | -0.028 | 0.323 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | single_task_GP + EI | 15 | 56 | 38 | 5 | 0.970 | 0.800 | -0.170 | -0.413 | 0.048 | -21.230 | -55.036 | 5.627 | -0.333 | 0.015 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | multitask_GP + EI | 15 | 56 | 38 | 5 | 0.970 | 0.734 | -0.236 | -0.496 | 0.014 | -32.142 | -72.481 | 1.718 | -0.424 | -0.012 | 10000 | 3 | Recompute policy for all ten seed multisets |

Candidate selection was locked before evaluation on the existing acquisition-test cohort.

## Supporting hybrid comparisons

| candidate | comparator | cutoff | pools | groups | endpoints | candidate_score | comparator_score | improvement | ci_low | ci_high | percent_improvement | percent_ci_low | percent_ci_high | draws | seeds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Adapted multitask NAP ensemble individual members | Matched single-task NAP ensemble individual members | 15 | 56 | 38 | 5 | 0.969 | 0.992 | 0.022 | -0.158 | 0.132 | 2.245 | -17.001 | 13.061 | 10000 | 3 |
| GP-conditioned multitask NAP | GP-conditioned single-task NAP | 15 | 56 | 38 | 5 | 0.759 | 0.777 | 0.018 | -0.117 | 0.112 | 2.333 | -15.580 | 14.248 | 10000 | 3 |
| GP-conditioned multitask NAP | single_task_NAP | 15 | 56 | 38 | 5 | 0.759 | 0.928 | 0.169 | 0.014 | 0.280 | 18.231 | 1.600 | 29.152 | 10000 | 3 |
## Reserved delta-test acquisition check

The reserved cohort contains 106 pools, including 11 large pools from seven global provenance groups. Uncertainty includes member-seed variation.

| candidate | comparator | cutoff | pools | groups | endpoints | candidate_score | comparator_score | improvement | ci_low | ci_high | percent_improvement | percent_ci_low | percent_ci_high | conditional_ci_low | conditional_ci_high | draws | seeds | seed_resampling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Adapted multitask NAP ensemble | Matched single-task NAP ensemble | 3 | 106 | 54 | 5 | 0.897 | 0.932 | 0.035 | -0.112 | 0.136 | 3.753 | -13.445 | 13.582 | -0.063 | 0.113 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Single-task NAP with shared inputs ensemble | 3 | 106 | 54 | 5 | 0.897 | 0.908 | 0.011 | -0.113 | 0.106 | 1.158 | -13.235 | 10.877 | -0.085 | 0.094 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Original single-task NAP ensemble | 3 | 106 | 54 | 5 | 0.897 | 0.832 | -0.065 | -0.213 | 0.060 | -7.833 | -27.487 | 6.732 | -0.169 | 0.024 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Matched single-task NAP ensemble | 15 | 11 | 7 | 5 | 0.653 | 0.832 | 0.179 | -0.099 | 0.399 | 21.521 | -16.629 | 44.633 | 0.091 | 0.226 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Single-task NAP with shared inputs ensemble | 15 | 11 | 7 | 5 | 0.653 | 0.785 | 0.133 | -0.184 | 0.283 | 16.896 | -33.189 | 33.396 | 0.016 | 0.211 | 10000 | 3 | Recompute policy for all ten seed multisets |
| Adapted multitask NAP ensemble | Original single-task NAP ensemble | 15 | 11 | 7 | 5 | 0.653 | 0.712 | 0.059 | -0.284 | 0.219 | 8.342 | -53.270 | 28.508 | 0.005 | 0.148 | 10000 | 3 | Recompute policy for all ten seed multisets |

| candidate | comparator | cutoff | pools | groups | endpoints | candidate_score | comparator_score | improvement | ci_low | ci_high | percent_improvement | percent_ci_low | percent_ci_high | draws | seeds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GP-conditioned multitask NAP | GP-conditioned single-task NAP | 3 | 106 | 54 | 5 | 0.832 | 0.899 | 0.067 | -0.040 | 0.159 | 7.435 | -4.583 | 17.113 | 10000 | 3 |
| GP-conditioned multitask NAP | single_task_NAP | 3 | 106 | 54 | 5 | 0.832 | 0.832 | -0.001 | -0.123 | 0.122 | -0.101 | -16.291 | 13.513 | 10000 | 3 |
| GP-conditioned multitask NAP | GP-conditioned single-task NAP | 15 | 11 | 7 | 5 | 0.683 | 0.845 | 0.162 | -0.035 | 0.267 | 19.174 | -4.184 | 33.042 | 10000 | 3 |
| GP-conditioned multitask NAP | single_task_NAP | 15 | 11 | 7 | 5 | 0.683 | 0.654 | -0.029 | -0.274 | 0.137 | -4.459 | -56.248 | 16.859 | 10000 | 3 |

![Performance by pool-size cutoff](test_performance_by_cutoff.png)

The ≥15 comparison is primary. Cutoff curves include endpoint and source-group counts in `locked_test_summary.csv`.

## Reproducibility
All checkpoints, configurations, training logs, complete validation purchase sequences, unsuccessful screens, and the evaluation plan are retained in this directory. The source datasets and preceding experiment outputs are unchanged. Unit checks cover masking, task routing, initial-function preservation where intended, permutation equivariance, hidden-label exclusion, training-return construction, continuous prediction gradients, conflict projection, and clustered comparison arithmetic.
