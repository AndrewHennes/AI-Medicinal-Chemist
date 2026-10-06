# Value learning and planning results

The experiment is complete. All comparisons use five grouped outer folds, 1,827 test pools exactly once, four matched worst-half starts per pool, and three seeds for every neural method. Primary large-pool results cover 311 pools from 183 source groups.

## Mean additional purchases in pools with at least 15 molecules

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random expectation | 8.621 | 6.140 | 4.918 | 4.136 |
| Single-task delta greedy | 5.695 | 3.761 | 3.031 | 2.459 |
| Single-task GP + EI | 5.835 | 3.932 | 3.140 | 2.709 |
| Original single-task NAP | 6.111 | 3.989 | 3.130 | 2.626 |
| Revised single-task NAP | 5.400 | 3.610 | 2.881 | 2.506 |
| Q-learning: prediction summaries | 5.348 | 3.587 | 2.924 | 2.474 |
| Q-learning: set pooling | 6.622 | 4.585 | 3.601 | 3.066 |
| Q-learning: attention | 6.159 | 4.072 | 3.236 | 2.753 |
| Q-learning: validation-selected recipe | 5.669 | 3.893 | 3.076 | 2.612 |
| Value + shallow lookahead | 5.695 | 3.922 | 3.080 | 2.622 |
| Value + Monte Carlo tree search | 5.653 | 3.818 | 2.986 | 2.543 |

## What the iterations showed

- The development phase tested three architectures, then refined each fold's two strongest architectures with additional training, large-pool balancing, random-return anchoring, and auxiliary top-2/3/4 costs. There were 55 architecture-development trials and 40 planning trials, followed by seed replication and locked outer-test evaluation.

- Search used Gaussian hypothetical outcomes, a candidate shortlist and at most eight real acquisition steps before reverting to direct Q. Search settings and model choices were fixed before outer-test scoring. The tested planners were bounded approximations, not exhaustive search.

## Results including all pools of at least three molecules

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random expectation | 3.526 | 2.480 | 1.644 | 1.233 |
| Single-task delta greedy | 2.719 | 1.895 | 1.216 | 0.882 |
| Single-task GP + EI | 2.698 | 1.920 | 1.234 | 0.921 |
| Original single-task NAP | 2.753 | 1.910 | 1.213 | 0.902 |
| Revised single-task NAP | 2.598 | 1.846 | 1.172 | 0.874 |
| Q-learning: prediction summaries | 2.608 | 1.856 | 1.187 | 0.871 |
| Q-learning: set pooling | 2.915 | 2.064 | 1.334 | 1.004 |
| Q-learning: attention | 2.799 | 1.940 | 1.244 | 0.928 |
| Q-learning: validation-selected recipe | 2.661 | 1.896 | 1.206 | 0.887 |
| Value + shallow lookahead | 2.671 | 1.908 | 1.221 | 0.899 |
| Value + Monte Carlo tree search | 2.642 | 1.884 | 1.200 | 0.883 |

## Within-fold selected recipes

| fold | architecture | refinement | trial |
| --- | --- | --- | --- |
| 0 | deep_sets | multi_target | deep_sets__multi_target |
| 1 | statistics | longer | statistics |
| 2 | statistics | large_balanced | statistics__large_balanced |
| 3 | statistics | large_balanced | statistics__large_balanced |
| 4 | statistics | longer | statistics |

## Interpretation limits

Bootstrap intervals are conditional on trained models and unadjusted for multiple comparisons. Training and inference budgets are recorded by method. Initial hits are free, rank-boundary ties qualify, and top-4 requires zero additional purchases in pools of three or four.

Full paired differences, pool-size curves, validation trials, coverage, and runtimes are in the accompanying CSV files. The PDF contains only top-1/2/3/4 purchase-count performance charts. Code and reproducibility details are in the parent README.
