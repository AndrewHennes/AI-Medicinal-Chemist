# Cumulative top-removal training augmentation

This study compares the original (old) and revised cross-fitted (new) single-task neural acquisition processes (NAPs), with and without cumulative top-removal training augmentation. Random expectation, single-task delta greedy, and Gaussian process (GP) plus expected improvement (EI) are shared unchanged baselines. All six endpoints use the same five grouped outer folds and three neural seeds.

One mixed augmentation condition is trained. Half of eligible training draws keep the original pool. The other half remove a uniformly sampled feasible count from one through five of its best compounds, leaving at least three. With distinct outcomes, removing the best k compounds makes the original rank k+1 the new target. Pools of three remain unchanged. Ties are broken randomly and exactly k molecules are removed, so tied best values can remain.

After removal, one initial hit is sampled from the worst half of the remaining pool. All outcomes remain relative to that hit. Surviving molecules retain their original order, and features and pairwise delta matrices are subset together. Removed molecules contribute neither observed anchors nor candidate/pool summaries. Gaussian-process caches are rebuilt for the reduced pool.

The augmentation is applied to original-NAP supervised contexts and policy rollouts, revised-NAP neural forecasters, controller warm starts and policy rollouts. Both NAP controllers retain clipped Proximal Policy Optimization (PPO). Frozen delta models, baseline GPs and group-excluded GP teachers are reused. No sign-consistency loss or additional multi-hit augmentation is introduced.

Supervised-step and episode budgets, validation pools, starting hits, contexts, and checkpoint-selection rules are fixed. Checkpoints are locked before scoring.

Evaluation uses original complete held-out pools and the same four worst-half single-hit starts as the controls. The 4,625 pools include 580 with at least 15 compounds. Only additional purchases to any top-1, top-2, top-3 or top-4 compound are reported. The initial hit is free and already qualifying starts score zero. Rank-boundary ties qualify; top-4 is necessarily zero in pools of three or four.

Charts use minimum pool sizes 3 and 15 and size-cutoff curves. Starts and seeds are averaged within pool, then pools within endpoint. Paired 95% intervals resample source groups conditional on fitted models and without multiplicity adjustment.

Endpoint transformations, species contexts, role allocations, and group-excluded teacher assignments are preserved.

## Mean top-1 purchases, pools ≥3

| Endpoint | Random | Delta greedy | GP + EI | Old NAP | New NAP | Old NAP + augmentation | New NAP + augmentation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal stability | 3.526 | 2.719 | 2.698 | 2.753 | 2.598 | 2.789 | 2.617 |
| In vivo clearance | 2.745 | 2.615 | 2.626 | 2.543 | 2.593 | 2.657 | 2.607 |
| Plasma protein binding | 2.981 | 2.202 | 2.432 | 2.290 | 2.260 | 2.264 | 2.302 |
| Cellular clearance | 3.576 | 2.895 | 2.950 | 3.031 | 2.778 | 3.041 | 2.811 |
| A to B permeability | 4.266 | 3.494 | 3.354 | 3.561 | 3.325 | 3.521 | 3.330 |
| Efflux ratio | 4.125 | 3.147 | 3.272 | 3.563 | 3.148 | 3.411 | 3.232 |

## Mean top-1 purchases, pools ≥15

| Endpoint | Random | Delta greedy | GP + EI | Old NAP | New NAP | Old NAP + augmentation | New NAP + augmentation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal stability | 8.621 | 5.695 | 5.835 | 6.111 | 5.400 | 6.221 | 5.419 |
| In vivo clearance | 10.650 | 9.762 | 9.375 | 8.838 | 9.600 | 9.754 | 9.671 |
| Plasma protein binding | 12.205 | 6.909 | 7.716 | 7.438 | 6.716 | 7.049 | 7.377 |
| Cellular clearance | 9.453 | 6.826 | 6.997 | 7.301 | 6.500 | 7.238 | 6.690 |
| A to B permeability | 11.921 | 9.802 | 7.465 | 9.122 | 8.127 | 8.986 | 8.015 |
| Efflux ratio | 9.694 | 7.116 | 6.394 | 8.523 | 6.858 | 7.701 | 7.194 |

## Paired top-1 differences for pools ≥15

Negative differences favor augmentation. Intervals hold fitted models fixed and are unadjusted.

| endpoint | model | baseline_purchases | augmented_purchases | difference | bootstrap_low | bootstrap_high | pools |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal stability | Old NAP | 6.111 | 6.221 | 0.110 | -0.242 | 0.440 | 311 |
| Microsomal stability | New NAP | 5.400 | 5.419 | 0.019 | -0.053 | 0.092 | 311 |
| In vivo clearance | Old NAP | 8.837 | 9.754 | 0.917 | -0.764 | 2.625 | 20 |
| In vivo clearance | New NAP | 9.600 | 9.671 | 0.071 | -0.308 | 0.677 | 20 |
| Plasma protein binding | Old NAP | 7.437 | 7.049 | -0.388 | -1.272 | 0.338 | 44 |
| Plasma protein binding | New NAP | 6.716 | 7.377 | 0.661 | -0.042 | 1.770 | 44 |
| Cellular clearance | Old NAP | 7.301 | 7.238 | -0.062 | -1.055 | 0.880 | 79 |
| Cellular clearance | New NAP | 6.500 | 6.690 | 0.190 | -0.169 | 0.565 | 79 |
| A to B permeability | Old NAP | 9.122 | 8.986 | -0.135 | -1.127 | 0.892 | 72 |
| A to B permeability | New NAP | 8.127 | 8.015 | -0.112 | -0.628 | 0.339 | 72 |
| Efflux ratio | Old NAP | 8.523 | 7.701 | -0.823 | -1.635 | -0.042 | 54 |
| Efflux ratio | New NAP | 6.858 | 7.194 | 0.336 | -0.044 | 0.800 | 54 |

## Microsomal stability

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 8.621 | 6.140 | 4.918 | 4.136 |
| Delta greedy | 5.695 | 3.761 | 3.031 | 2.459 |
| GP + EI | 5.835 | 3.932 | 3.140 | 2.709 |
| Old NAP | 6.111 | 3.989 | 3.130 | 2.626 |
| New NAP | 5.400 | 3.610 | 2.881 | 2.506 |
| Old NAP + augmentation | 6.221 | 4.118 | 3.248 | 2.697 |
| New NAP + augmentation | 5.419 | 3.610 | 2.901 | 2.534 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 3.526 | 2.480 | 1.644 | 1.233 |
| Delta greedy | 2.719 | 1.895 | 1.216 | 0.882 |
| GP + EI | 2.698 | 1.920 | 1.234 | 0.921 |
| Old NAP | 2.753 | 1.910 | 1.213 | 0.902 |
| New NAP | 2.598 | 1.846 | 1.172 | 0.874 |
| Old NAP + augmentation | 2.789 | 1.944 | 1.244 | 0.917 |
| New NAP + augmentation | 2.617 | 1.862 | 1.184 | 0.886 |

## In vivo clearance

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 10.650 | 6.904 | 5.275 | 4.146 |
| Delta greedy | 9.762 | 6.200 | 4.100 | 3.413 |
| GP + EI | 9.375 | 6.275 | 4.362 | 3.600 |
| Old NAP | 8.838 | 7.412 | 5.529 | 4.054 |
| New NAP | 9.600 | 4.800 | 3.321 | 2.750 |
| Old NAP + augmentation | 9.754 | 6.487 | 5.300 | 4.117 |
| New NAP + augmentation | 9.671 | 4.408 | 3.333 | 2.775 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 2.745 | 1.809 | 0.986 | 0.610 |
| Delta greedy | 2.615 | 1.734 | 0.913 | 0.549 |
| GP + EI | 2.626 | 1.742 | 0.951 | 0.598 |
| Old NAP | 2.543 | 1.739 | 0.951 | 0.592 |
| New NAP | 2.593 | 1.654 | 0.888 | 0.537 |
| Old NAP + augmentation | 2.657 | 1.778 | 0.981 | 0.612 |
| New NAP + augmentation | 2.607 | 1.641 | 0.877 | 0.536 |

## Plasma protein binding

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 12.205 | 7.598 | 5.828 | 4.727 |
| Delta greedy | 6.909 | 3.994 | 3.119 | 2.085 |
| GP + EI | 7.716 | 4.938 | 4.438 | 3.426 |
| Old NAP | 7.438 | 4.161 | 3.371 | 2.943 |
| New NAP | 6.716 | 3.852 | 3.394 | 2.447 |
| Old NAP + augmentation | 7.049 | 3.898 | 3.288 | 2.621 |
| New NAP + augmentation | 7.377 | 3.845 | 3.364 | 2.360 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 2.981 | 1.920 | 1.090 | 0.714 |
| Delta greedy | 2.202 | 1.428 | 0.762 | 0.467 |
| GP + EI | 2.432 | 1.661 | 0.939 | 0.616 |
| Old NAP | 2.290 | 1.521 | 0.845 | 0.564 |
| New NAP | 2.260 | 1.478 | 0.813 | 0.510 |
| Old NAP + augmentation | 2.264 | 1.512 | 0.847 | 0.539 |
| New NAP + augmentation | 2.302 | 1.484 | 0.808 | 0.503 |

## Cellular clearance

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 9.453 | 6.637 | 5.262 | 4.367 |
| Delta greedy | 6.826 | 4.785 | 3.481 | 2.902 |
| GP + EI | 6.997 | 4.573 | 3.930 | 3.509 |
| Old NAP | 7.301 | 4.964 | 4.186 | 3.598 |
| New NAP | 6.500 | 4.162 | 3.525 | 3.055 |
| Old NAP + augmentation | 7.238 | 4.859 | 4.234 | 3.621 |
| New NAP + augmentation | 6.690 | 4.313 | 3.664 | 3.109 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 3.576 | 2.483 | 1.647 | 1.221 |
| Delta greedy | 2.895 | 2.042 | 1.251 | 0.916 |
| GP + EI | 2.950 | 1.992 | 1.351 | 1.048 |
| Old NAP | 3.031 | 2.123 | 1.406 | 1.059 |
| New NAP | 2.778 | 1.869 | 1.250 | 0.950 |
| Old NAP + augmentation | 3.041 | 2.086 | 1.386 | 1.055 |
| New NAP + augmentation | 2.811 | 1.903 | 1.264 | 0.954 |

## A to B permeability

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 11.921 | 8.005 | 5.922 | 4.809 |
| Delta greedy | 9.802 | 6.076 | 4.875 | 4.135 |
| GP + EI | 7.465 | 5.583 | 4.108 | 3.493 |
| Old NAP | 9.122 | 6.310 | 4.616 | 3.763 |
| New NAP | 8.127 | 4.897 | 3.610 | 2.882 |
| Old NAP + augmentation | 8.986 | 6.233 | 4.576 | 3.806 |
| New NAP + augmentation | 8.015 | 5.179 | 3.794 | 3.135 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 4.266 | 2.804 | 1.853 | 1.333 |
| Delta greedy | 3.494 | 2.321 | 1.559 | 1.148 |
| GP + EI | 3.354 | 2.321 | 1.513 | 1.075 |
| Old NAP | 3.561 | 2.396 | 1.584 | 1.124 |
| New NAP | 3.325 | 2.136 | 1.378 | 0.975 |
| Old NAP + augmentation | 3.521 | 2.355 | 1.553 | 1.127 |
| New NAP + augmentation | 3.330 | 2.197 | 1.413 | 1.018 |

## Efflux ratio

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 9.694 | 6.367 | 4.946 | 3.932 |
| Delta greedy | 7.116 | 5.546 | 4.412 | 3.144 |
| GP + EI | 6.394 | 4.176 | 3.324 | 2.880 |
| Old NAP | 8.523 | 5.853 | 4.628 | 3.552 |
| New NAP | 6.858 | 4.715 | 3.261 | 2.657 |
| Old NAP + augmentation | 7.701 | 5.472 | 4.233 | 3.310 |
| New NAP + augmentation | 7.194 | 4.628 | 3.182 | 2.582 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 4.125 | 2.708 | 1.860 | 1.356 |
| Delta greedy | 3.147 | 2.270 | 1.589 | 1.104 |
| GP + EI | 3.272 | 2.186 | 1.478 | 1.111 |
| Old NAP | 3.563 | 2.425 | 1.663 | 1.217 |
| New NAP | 3.148 | 2.163 | 1.418 | 1.038 |
| Old NAP + augmentation | 3.411 | 2.319 | 1.616 | 1.189 |
| New NAP + augmentation | 3.232 | 2.141 | 1.403 | 1.021 |
