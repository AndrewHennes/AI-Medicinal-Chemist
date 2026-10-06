# Acquisition performance under three metric families

All results below re-score frozen acquisition sequences. No model was retrained or reselected using these metrics. The main cohort contains 507 pools, including 296 with 3–5 compounds and 56 with at least 15. The reserved cohort contains 106 pools, including 63 with 3–5 compounds and 11 with at least 15.

## Findings

On the main cohort across all series sizes, revised multitask NAP has discovery efficiency 0.232, regret area 0.171, one-purchase success 37.5%, and two-purchase success 56.4%. Its matched single-task version scores 0.219, 0.178, 36.2%, and 50.8%. Random scores 0, 0.233, 28.2%, and 40.7%. Success rates are opportunity-conditioned as defined below, so the two budget columns use different eligible cases.

The revised multitask model's two-purchase gain over its matched single-task control is 5.7 percentage points on the main cohort, with a nominal 95% interval of 1.5 to 9.9 points. The corresponding reserved-cohort gain is 6.3 points, with an interval of −3.2 to 16.5 points. When each size band receives equal weight within each endpoint, gains are 5.9 points on the main cohort and 11.9 points on the reserved cohort. These are useful signals for a fixed-budget objective, not independent confirmation after the preceding architecture search.

For 3–5 compounds on the main cohort, single-task delta greedy has regret area 0.196 versus random 0.260 and revised multitask NAP 0.207. The matched single-task NAP also has higher discovery efficiency than revised multitask NAP in this band, 0.203 versus 0.171.

For pools of at least 15 compounds, revised multitask NAP has regret area 0.103 versus 0.119 for multitask GP with expected improvement and 0.128 for single-task delta greedy. Conversely, single-task delta greedy has better first-purchase and two-purchase success than revised multitask NAP, 17.2% versus 14.2% and 24.9% versus 23.3%. The acquisition objectives measure different useful behaviors.

The supervised warm start and final revised multitask NAP remain very close across metrics. On the main all-size cohort, warm-start scores are 0.233 efficiency, 0.172 regret area, and 56.7% two-purchase success.

## Metric definitions and inclusion rules

Let n be the pool size, m=n−1 the unmeasured candidates after the free hit, and k the number of exact optima remaining. All objectives are already transformed and oriented for minimization, with outcomes supplied to policies only relative to the initial hit.

1. Discovery efficiency is (E_random[T]−T)/(E_random[T]−1), with E_random[T]=n/(k+1) for a nonoptimal start. It equals 0 for random on average and 1 for immediate discovery. It is undefined when the start is already optimal or every remaining candidate is optimal. With k tied optima its lower bound is −k, not always −1.
2. Normalized incumbent regret after purchase t is (best_observed_t−pool_optimum)/(starting_outcome−pool_optimum). Regret area averages that quantity at t=1,…,m−1; the last forced-completion purchase is excluded. It lies in [0,1], with 0 best. Zero initial gap makes it undefined. Positive-gap cases where every remaining candidate is optimal have valid area 0 and remain included. Fixed-budget regrets after purchases 1 and 2 are exported as supplements.
3. Success@1 and Success@2 record whether the exact optimum has been acquired by those budgets. Primary rates exclude initially optimal starts and budgets for which random already succeeds with probability 1. This avoids rewarding automatic outcomes, such as two purchases in a three-compound pool. Inclusive success rates are retained in the episode and supplementary exports.

Random success is exactly 1−C(m−k,t)/C(m,t), with automatic cases handled separately. Random regret is calculated analytically from the minimum of a uniform subset of the remaining candidates, including the known hit. No sampled random permutations are needed. These formulas were checked against exhaustive enumeration of small pools with and without ties.

The main cohort has 8 initially optimal starts and 30 additional starts with every remaining candidate optimal. The reserved cohort has 6 of each. All counts and per-metric eligibility are in [eligibility_counts.csv](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/eligibility_counts.csv). Normalized regret uses the exact positive starting gap.

## Aggregation and uncertainty

We retain the original four sampled starts per pool for matched comparisons. These can repeat references and are not an exhaustive evaluation of every eligible starting hit. Starts are averaged within each seed and pool, then seeds are averaged, pools are averaged within endpoint, and endpoints are weighted equally. “All ≥3” therefore gives each pool equal weight within its endpoint. “Size-balanced” first weights the four represented size bands equally within each endpoint, then endpoints equally. This differs intentionally from the older ratio of mean purchase counts to mean random counts.

Intervals use 5,000 paired bootstrap draws of global source groups and matched training seeds, conditional on fitted forecasting artifacts. Draws must represent every observed endpoint/size stratum. Approximately 85% of attempted draws omit at least one stratum and are rejected for the reserved size-balanced summaries. The reserved large-pool stratum contains 11 pools from 7 source groups.

### All ≥3

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.232 | 0.171 | 37.5% | 56.4% |
| Revised single-task NAP | 0.219 | 0.178 | 36.2% | 50.8% |
| Multitask NAP + private adaptation | 0.230 | 0.170 | 37.8% | 56.2% |
| Multitask supervised warm start | 0.233 | 0.172 | 37.6% | 56.7% |
| Original single-task NAP | 0.150 | 0.197 | 34.2% | 50.0% |
| Original multitask NAP | 0.069 | 0.213 | 32.4% | 46.8% |
| Single-task GP + EI | 0.135 | 0.198 | 30.9% | 45.6% |
| Multitask GP + EI | 0.171 | 0.191 | 33.9% | 51.0% |
| Single-task delta greedy | 0.199 | 0.177 | 37.0% | 51.6% |
| Multitask delta greedy | 0.165 | 0.185 | 34.9% | 53.4% |
| Random expectation | 0.000 | 0.233 | 28.2% | 40.7% |

### Size-balanced

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.262 | 0.148 | 29.0% | 48.5% |
| Revised single-task NAP | 0.236 | 0.157 | 25.0% | 42.6% |
| Multitask NAP + private adaptation | 0.264 | 0.145 | 29.9% | 48.4% |
| Multitask supervised warm start | 0.260 | 0.148 | 29.2% | 48.7% |
| Original single-task NAP | 0.153 | 0.175 | 25.7% | 42.1% |
| Original multitask NAP | 0.044 | 0.190 | 23.6% | 39.1% |
| Single-task GP + EI | 0.118 | 0.177 | 19.5% | 36.0% |
| Multitask GP + EI | 0.199 | 0.164 | 24.7% | 43.3% |
| Single-task delta greedy | 0.226 | 0.159 | 28.5% | 43.9% |
| Multitask delta greedy | 0.213 | 0.161 | 28.3% | 46.9% |
| Random expectation | 0.000 | 0.211 | 19.3% | 33.3% |

### 3–5

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.171 | 0.207 | 48.0% | 74.7% |
| Revised single-task NAP | 0.203 | 0.202 | 50.0% | 71.7% |
| Multitask NAP + private adaptation | 0.161 | 0.207 | 47.8% | 73.6% |
| Multitask supervised warm start | 0.171 | 0.207 | 47.9% | 75.0% |
| Original single-task NAP | 0.115 | 0.231 | 44.9% | 69.9% |
| Original multitask NAP | 0.084 | 0.244 | 44.1% | 68.3% |
| Single-task GP + EI | 0.133 | 0.224 | 46.1% | 67.7% |
| Multitask GP + EI | 0.125 | 0.224 | 45.9% | 71.1% |
| Single-task delta greedy | 0.180 | 0.196 | 49.2% | 72.0% |
| Multitask delta greedy | 0.077 | 0.216 | 44.0% | 72.4% |
| Random expectation | 0.000 | 0.260 | 40.0% | 61.5% |

### ≥15

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.304 | 0.103 | 14.2% | 23.3% |
| Revised single-task NAP | 0.289 | 0.118 | 11.4% | 19.7% |
| Multitask NAP + private adaptation | 0.293 | 0.106 | 14.6% | 22.3% |
| Multitask supervised warm start | 0.293 | 0.105 | 14.7% | 24.4% |
| Original single-task NAP | 0.063 | 0.160 | 9.1% | 15.5% |
| Original multitask NAP | -0.049 | 0.152 | 9.9% | 14.5% |
| Single-task GP + EI | 0.223 | 0.125 | 3.3% | 12.4% |
| Multitask GP + EI | 0.301 | 0.119 | 12.2% | 17.4% |
| Single-task delta greedy | 0.196 | 0.128 | 17.2% | 24.9% |
| Multitask delta greedy | 0.193 | 0.123 | 16.3% | 24.2% |
| Random expectation | 0.000 | 0.166 | 7.0% | 13.6% |

![Main cohort scores](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/acquisition_test_all_pools.png)

![Scores by series size](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/acquisition_test_by_size.png)

### All ≥3

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.266 | 0.135 | 37.8% | 58.2% |
| Revised single-task NAP | 0.195 | 0.155 | 35.1% | 51.9% |
| Multitask NAP + private adaptation | 0.295 | 0.125 | 39.1% | 59.4% |
| Multitask supervised warm start | 0.268 | 0.134 | 37.3% | 58.2% |
| Original single-task NAP | 0.211 | 0.156 | 40.5% | 48.1% |
| Original multitask NAP | 0.071 | 0.189 | 33.3% | 41.7% |
| Single-task GP + EI | 0.133 | 0.192 | 28.3% | 47.1% |
| Multitask GP + EI | 0.105 | 0.178 | 32.3% | 41.2% |
| Single-task delta greedy | 0.251 | 0.155 | 43.1% | 57.6% |
| Multitask delta greedy | 0.289 | 0.137 | 41.7% | 55.7% |
| Random expectation | 0.000 | 0.217 | 28.3% | 40.9% |

### Size-balanced

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.370 | 0.101 | 28.5% | 53.5% |
| Revised single-task NAP | 0.241 | 0.122 | 23.1% | 41.6% |
| Multitask NAP + private adaptation | 0.377 | 0.097 | 28.7% | 52.5% |
| Multitask supervised warm start | 0.369 | 0.100 | 28.6% | 53.5% |
| Original single-task NAP | 0.186 | 0.134 | 31.1% | 38.8% |
| Original multitask NAP | 0.072 | 0.165 | 24.8% | 35.7% |
| Single-task GP + EI | 0.123 | 0.173 | 15.5% | 33.5% |
| Multitask GP + EI | 0.161 | 0.147 | 18.7% | 32.9% |
| Single-task delta greedy | 0.263 | 0.125 | 32.2% | 52.4% |
| Multitask delta greedy | 0.302 | 0.117 | 28.6% | 42.3% |
| Random expectation | 0.000 | 0.191 | 18.6% | 32.2% |

### 3–5

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.200 | 0.160 | 52.1% | 75.5% |
| Revised single-task NAP | 0.216 | 0.174 | 52.4% | 81.2% |
| Multitask NAP + private adaptation | 0.263 | 0.142 | 54.8% | 80.9% |
| Multitask supervised warm start | 0.207 | 0.158 | 51.6% | 75.5% |
| Original single-task NAP | 0.227 | 0.169 | 52.6% | 64.3% |
| Original multitask NAP | 0.114 | 0.201 | 47.9% | 60.7% |
| Single-task GP + EI | 0.155 | 0.194 | 44.0% | 77.9% |
| Multitask GP + EI | 0.040 | 0.198 | 46.7% | 54.7% |
| Single-task delta greedy | 0.249 | 0.180 | 56.7% | 83.4% |
| Multitask delta greedy | 0.268 | 0.156 | 55.0% | 87.5% |
| Random expectation | 0.000 | 0.240 | 40.1% | 61.0% |

### ≥15

| Model | Efficiency ↑ | Regret area ↓ | Success@1 ↑ | Success@2 ↑ |
| --- | --- | --- | --- | --- |
| Revised multitask NAP | 0.603 | 0.039 | 28.9% | 44.7% |
| Revised single-task NAP | 0.439 | 0.048 | 14.2% | 28.1% |
| Multitask NAP + private adaptation | 0.588 | 0.044 | 27.8% | 33.9% |
| Multitask supervised warm start | 0.600 | 0.039 | 32.8% | 44.4% |
| Original single-task NAP | 0.385 | 0.062 | 34.4% | 39.4% |
| Original multitask NAP | -0.149 | 0.136 | 2.2% | 2.8% |
| Single-task GP + EI | 0.292 | 0.098 | 0.0% | 2.5% |
| Multitask GP + EI | 0.326 | 0.056 | 0.0% | 22.5% |
| Single-task delta greedy | 0.405 | 0.046 | 25.0% | 40.0% |
| Multitask delta greedy | 0.383 | 0.047 | 11.7% | 13.3% |
| Random expectation | 0.000 | 0.121 | 4.9% | 9.8% |

![Reserved cohort scores](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/reserved_delta_test_all_pools.png)

![Reserved scores by size](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/reserved_delta_test_by_size.png)

## Paired revised multitask versus revised single-task effects

Positive improvement always favors multitask. Success effects are in probability units; multiply by 100 for percentage points. Regret effects are comparator minus candidate.

| cohort | scope | metric | improvement | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- |
| acquisition_test | All ≥3 | efficiency | 0.0131 | -0.0584 | 0.0819 |
| acquisition_test | All ≥3 | regret_area | 0.0061 | -0.0126 | 0.0252 |
| acquisition_test | All ≥3 | success_1 | 0.0136 | -0.0238 | 0.0506 |
| acquisition_test | All ≥3 | success_2 | 0.0568 | 0.0146 | 0.0993 |
| acquisition_test | ≥15 | efficiency | 0.0155 | -0.0994 | 0.1056 |
| acquisition_test | ≥15 | regret_area | 0.0148 | -0.0052 | 0.0391 |
| acquisition_test | ≥15 | success_1 | 0.0272 | -0.0226 | 0.0784 |
| acquisition_test | ≥15 | success_2 | 0.0358 | -0.0439 | 0.1197 |
| acquisition_test | Size-balanced | efficiency | 0.0255 | -0.0442 | 0.0874 |
| acquisition_test | Size-balanced | regret_area | 0.0097 | -0.0063 | 0.0252 |
| acquisition_test | Size-balanced | success_1 | 0.0399 | -0.0006 | 0.0833 |
| acquisition_test | Size-balanced | success_2 | 0.0593 | 0.0122 | 0.1071 |
| reserved_delta_test | All ≥3 | efficiency | 0.0707 | -0.0878 | 0.2309 |
| reserved_delta_test | All ≥3 | regret_area | 0.0203 | -0.0142 | 0.0599 |
| reserved_delta_test | All ≥3 | success_1 | 0.0266 | -0.0558 | 0.1134 |
| reserved_delta_test | All ≥3 | success_2 | 0.0630 | -0.0317 | 0.1652 |
| reserved_delta_test | ≥15 | efficiency | 0.1643 | -0.0712 | 0.3920 |
| reserved_delta_test | ≥15 | regret_area | 0.0085 | -0.0091 | 0.0279 |
| reserved_delta_test | ≥15 | success_1 | 0.1472 | 0.0083 | 0.3167 |
| reserved_delta_test | ≥15 | success_2 | 0.1667 | 0.1000 | 0.2722 |
| reserved_delta_test | Size-balanced | efficiency | 0.1283 | -0.0036 | 0.2330 |
| reserved_delta_test | Size-balanced | regret_area | 0.0212 | -0.0017 | 0.0400 |
| reserved_delta_test | Size-balanced | success_1 | 0.0535 | -0.0132 | 0.1240 |
| reserved_delta_test | Size-balanced | success_2 | 0.1186 | 0.0510 | 0.1917 |

## Training implications and reproducibility

The proposed metric-aligned reward implementations and loss audit are in [loss_design.md](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/loss_design.md) and [objective_rewards.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/objective_rewards.py). They are standalone prototypes with mathematical tests. They have not been used to fit a new model or alter any locked training run. All 13 metric/reward tests passed, and [reward_metric_consistency.json](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/reward_metric_consistency.json) records 1,600 additional reward-to-metric checks. An independent audit reproduced all 53,944 saved policy sequences, 2,452 exact random expectations, 528 summary estimates, and 480 paired effects within floating-point precision, as recorded in [final_audit.json](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/final_audit.json).

Run [evaluate_metrics.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/evaluate_metrics.py) with the existing analysis interpreter to reproduce the metric tables, and [report_metrics.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/report_metrics.py) to reproduce this report and figures. Both scripts use absolute data/output paths and accept no CLI options. [replay_reserved_baselines.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/replay_reserved_baselines.py) supplies the missing frozen original multitask NAP and GP baselines for the reserved cohort. All original checkpoints and order caches remain unchanged.

Detailed results are in [metric_summary.csv](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/metric_summary.csv), [paired_comparisons.csv](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/paired_comparisons.csv), [endpoint_metric_summary.csv](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/endpoint_metric_summary.csv), and [supplementary_metric_summary.csv](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/supplementary_metric_summary.csv). The latter includes unconditional success rates and fixed-budget regret. [evaluation_plan.json](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/evaluation_plan.json) records the definitions and input hashes, while [verification.json](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_acquisition_metrics/verification.json) records order checks and absence of training.
