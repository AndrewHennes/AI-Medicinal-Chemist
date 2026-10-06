# Distance-aware neural acquisition, K=1

Frozen models, five held-out folds, four worse-half starting hits per pool. No new PPO training or test-set tuning.

| Primary comparison, 580 pools with at least 15 compounds | Purchases to top-1 |
| --- | ---: |
| Neural mixture EI | 6.09784 |
| GP EI | 5.52457 |

Neural mixture EI minus GP EI is +0.57328 purchases, with a linked-group bootstrap 95% interval of [+0.18784, +0.95279].
Neural EI versus greedy delta: 9.29% fewer purchases. Versus random: 36.40% fewer.
Neural EI minus neural greedy is -0.05431 purchases, with a linked-group bootstrap 95% interval of [-0.17287, +0.07537].

Primary aggregation averages starting hits within pools and then pools equally. Endpoint-macro results are separately saved.
Uncalibrated EI, single-model EI and GP greedy are ablations, not alternative winners selected on test results.
The acquisition code receives only candidate features and previously revealed labels. Ground truth is used by the retrospective environment to reveal a purchased outcome and stop at a true optimum.

See distance_aware_neural_K1_report.pdf, summary.csv, paired_comparisons.csv, pool_metrics.csv.gz and context_extrapolation.csv. Saved per-start trajectories are in the evaluation directory.
