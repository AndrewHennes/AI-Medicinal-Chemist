# Top-k auxiliary acquisition tasks

This study adds five auxiliary acquisition-cost heads to the original (old) and revised cross-fitted (new) single-task neural acquisition processes (NAPs). Controls are the same two NAPs without these tasks, random expectation, single-task delta greedy, and Gaussian process (GP) plus expected improvement (EI). All six endpoints retain five grouped outer folds and three neural seeds.

Each auxiliary head estimates the additional purchases needed to reach any top-k compound for k = 2, 3, 4, 5 or 6, conditional on the sampled next action and subsequent behavior of the current top-1 policy. These are Monte Carlo continuation-cost targets, not optimal action values or separately optimized top-k policies. The principal top-1 acquisition policy still uses clipped Proximal Policy Optimization (PPO).

From a complete training rollout, the target at state t is $\max(\tau_k-t,0)/(n-1-t)$. Here t is purchases already made, $\tau_k$ is the first qualifying purchase, and n includes the free initial hit. Only the action actually sampled receives a target. Threshold ties qualify. Heads with k at least n are excluded from the loss; zero targets after success in other pools remain valid.

The old NAP shares its 96-dimensional acquisition hidden representation with five sigmoid cost heads. The new NAP shares its 32-dimensional mixture-gate hidden representation, combined with five candidate expert ranks, with a small five-output cost predictor. Auxiliary gradients therefore update the actor representation in both models. Frozen revised-NAP forecasters remain frozen.

The added loss is squared error in normalized cost, averaged within each represented head and then across heads, with fixed coefficient 1.0. There is no tuning of that coefficient against held-out results. The original top-1 actor alone chooses purchases during evaluation. Adding heads preserves the original parameter initialization, primary forward outputs, and random-number stream before auxiliary training begins.

All training pools remain intact with one initial hit from the worst half. No top-removal or multi-hit augmentation is combined with this experiment. Relative outcomes, measured-anchor delta features, species, transformations, data-role splits and teacher assignments are unchanged. Delta models, GPs and cross-fitted neural forecasters are reused; both NAP policies retain their original pretraining/warmstart and PPO budgets.

Validation criteria and checkpoint-selection rules are unchanged. All 180 newly fitted policies are locked before test scoring. Evaluation uses complete held-out pools and four matched worst-half starting hits. The 4,625 pools include 580 with at least 15 compounds. Reported metrics remain additional purchases to any top-1, top-2, top-3 or top-4 compound. Already qualifying initial hits score zero.

Charts show minimum pool sizes 3 and 15 and cutoff curves. Starts and seeds are averaged within pool, then pools within endpoint. Paired 95% intervals resample source groups conditional on fitted models and without multiplicity adjustment.

## Mean top-1 purchases, pools ≥3

| Endpoint | Random | Delta greedy | GP + EI | Old NAP | New NAP | Old NAP + auxiliary | New NAP + auxiliary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal stability | 3.526 | 2.719 | 2.698 | 2.753 | 2.598 | 2.755 | 2.602 |
| In vivo clearance | 2.745 | 2.615 | 2.626 | 2.543 | 2.593 | 2.542 | 2.595 |
| Plasma protein binding | 2.981 | 2.202 | 2.432 | 2.290 | 2.260 | 2.307 | 2.263 |
| Cellular clearance | 3.576 | 2.895 | 2.950 | 3.031 | 2.778 | 3.070 | 2.767 |
| A to B permeability | 4.266 | 3.494 | 3.354 | 3.561 | 3.325 | 3.511 | 3.315 |
| Efflux ratio | 4.125 | 3.147 | 3.272 | 3.563 | 3.148 | 3.536 | 3.134 |

## Mean top-1 purchases, pools ≥15

| Endpoint | Random | Delta greedy | GP + EI | Old NAP | New NAP | Old NAP + auxiliary | New NAP + auxiliary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal stability | 8.621 | 5.695 | 5.835 | 6.111 | 5.400 | 6.197 | 5.415 |
| In vivo clearance | 10.650 | 9.762 | 9.375 | 8.838 | 9.600 | 8.571 | 9.588 |
| Plasma protein binding | 12.205 | 6.909 | 7.716 | 7.438 | 6.716 | 7.206 | 6.703 |
| Cellular clearance | 9.453 | 6.826 | 6.997 | 7.301 | 6.500 | 7.686 | 6.482 |
| A to B permeability | 11.921 | 9.802 | 7.465 | 9.122 | 8.127 | 8.987 | 8.025 |
| Efflux ratio | 9.694 | 7.116 | 6.394 | 8.523 | 6.858 | 8.410 | 6.770 |

## Paired top-1 differences for pools ≥15

Negative differences favor auxiliary tasks. Intervals hold fitted models fixed and are unadjusted.

| endpoint | model | baseline_purchases | auxiliary_purchases | difference | bootstrap_low | bootstrap_high | pools |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal stability | Old NAP | 6.111 | 6.197 | 0.086 | -0.106 | 0.292 | 311 |
| Microsomal stability | New NAP | 5.400 | 5.415 | 0.016 | -0.014 | 0.046 | 311 |
| In vivo clearance | Old NAP | 8.837 | 8.571 | -0.267 | -0.906 | 0.411 | 20 |
| In vivo clearance | New NAP | 9.600 | 9.588 | -0.013 | -0.028 | 0.000 | 20 |
| Plasma protein binding | Old NAP | 7.437 | 7.206 | -0.231 | -0.632 | 0.265 | 44 |
| Plasma protein binding | New NAP | 6.716 | 6.703 | -0.013 | -0.051 | 0.016 | 44 |
| Cellular clearance | Old NAP | 7.301 | 7.686 | 0.385 | -0.028 | 0.835 | 79 |
| Cellular clearance | New NAP | 6.500 | 6.482 | -0.018 | -0.154 | 0.095 | 79 |
| A to B permeability | Old NAP | 9.122 | 8.987 | -0.134 | -0.813 | 0.607 | 72 |
| A to B permeability | New NAP | 8.127 | 8.025 | -0.102 | -0.242 | 0.007 | 72 |
| Efflux ratio | Old NAP | 8.523 | 8.410 | -0.113 | -0.585 | 0.345 | 54 |
| Efflux ratio | New NAP | 6.858 | 6.770 | -0.088 | -0.245 | 0.053 | 54 |

## Microsomal stability

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 8.621 | 6.140 | 4.918 | 4.136 |
| Delta greedy | 5.695 | 3.761 | 3.031 | 2.459 |
| GP + EI | 5.835 | 3.932 | 3.140 | 2.709 |
| Old NAP | 6.111 | 3.989 | 3.130 | 2.626 |
| New NAP | 5.400 | 3.610 | 2.881 | 2.506 |
| Old NAP + auxiliary | 6.197 | 3.998 | 3.100 | 2.600 |
| New NAP + auxiliary | 5.415 | 3.631 | 2.898 | 2.516 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 3.526 | 2.480 | 1.644 | 1.233 |
| Delta greedy | 2.719 | 1.895 | 1.216 | 0.882 |
| GP + EI | 2.698 | 1.920 | 1.234 | 0.921 |
| Old NAP | 2.753 | 1.910 | 1.213 | 0.902 |
| New NAP | 2.598 | 1.846 | 1.172 | 0.874 |
| Old NAP + auxiliary | 2.755 | 1.912 | 1.214 | 0.896 |
| New NAP + auxiliary | 2.602 | 1.852 | 1.175 | 0.878 |

## In vivo clearance

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 10.650 | 6.904 | 5.275 | 4.146 |
| Delta greedy | 9.762 | 6.200 | 4.100 | 3.413 |
| GP + EI | 9.375 | 6.275 | 4.362 | 3.600 |
| Old NAP | 8.838 | 7.412 | 5.529 | 4.054 |
| New NAP | 9.600 | 4.800 | 3.321 | 2.750 |
| Old NAP + auxiliary | 8.571 | 7.192 | 5.442 | 4.117 |
| New NAP + auxiliary | 9.588 | 4.817 | 3.333 | 2.763 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 2.745 | 1.809 | 0.986 | 0.610 |
| Delta greedy | 2.615 | 1.734 | 0.913 | 0.549 |
| GP + EI | 2.626 | 1.742 | 0.951 | 0.598 |
| Old NAP | 2.543 | 1.739 | 0.951 | 0.592 |
| New NAP | 2.593 | 1.654 | 0.888 | 0.537 |
| Old NAP + auxiliary | 2.542 | 1.736 | 0.956 | 0.599 |
| New NAP + auxiliary | 2.595 | 1.656 | 0.890 | 0.539 |

## Plasma protein binding

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 12.205 | 7.598 | 5.828 | 4.727 |
| Delta greedy | 6.909 | 3.994 | 3.119 | 2.085 |
| GP + EI | 7.716 | 4.938 | 4.438 | 3.426 |
| Old NAP | 7.438 | 4.161 | 3.371 | 2.943 |
| New NAP | 6.716 | 3.852 | 3.394 | 2.447 |
| Old NAP + auxiliary | 7.206 | 3.983 | 3.072 | 2.725 |
| New NAP + auxiliary | 6.703 | 3.862 | 3.369 | 2.438 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 2.981 | 1.920 | 1.090 | 0.714 |
| Delta greedy | 2.202 | 1.428 | 0.762 | 0.467 |
| GP + EI | 2.432 | 1.661 | 0.939 | 0.616 |
| Old NAP | 2.290 | 1.521 | 0.845 | 0.564 |
| New NAP | 2.260 | 1.478 | 0.813 | 0.510 |
| Old NAP + auxiliary | 2.307 | 1.530 | 0.838 | 0.550 |
| New NAP + auxiliary | 2.263 | 1.479 | 0.814 | 0.511 |

## Cellular clearance

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 9.453 | 6.637 | 5.262 | 4.367 |
| Delta greedy | 6.826 | 4.785 | 3.481 | 2.902 |
| GP + EI | 6.997 | 4.573 | 3.930 | 3.509 |
| Old NAP | 7.301 | 4.964 | 4.186 | 3.598 |
| New NAP | 6.500 | 4.162 | 3.525 | 3.055 |
| Old NAP + auxiliary | 7.686 | 5.370 | 4.468 | 3.713 |
| New NAP + auxiliary | 6.482 | 4.148 | 3.541 | 3.053 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 3.576 | 2.483 | 1.647 | 1.221 |
| Delta greedy | 2.895 | 2.042 | 1.251 | 0.916 |
| GP + EI | 2.950 | 1.992 | 1.351 | 1.048 |
| Old NAP | 3.031 | 2.123 | 1.406 | 1.059 |
| New NAP | 2.778 | 1.869 | 1.250 | 0.950 |
| Old NAP + auxiliary | 3.070 | 2.151 | 1.429 | 1.069 |
| New NAP + auxiliary | 2.767 | 1.863 | 1.252 | 0.948 |

## A to B permeability

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 11.921 | 8.005 | 5.922 | 4.809 |
| Delta greedy | 9.802 | 6.076 | 4.875 | 4.135 |
| GP + EI | 7.465 | 5.583 | 4.108 | 3.493 |
| Old NAP | 9.122 | 6.310 | 4.616 | 3.763 |
| New NAP | 8.127 | 4.897 | 3.610 | 2.882 |
| Old NAP + auxiliary | 8.987 | 6.053 | 4.369 | 3.672 |
| New NAP + auxiliary | 8.025 | 4.868 | 3.574 | 2.882 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 4.266 | 2.804 | 1.853 | 1.333 |
| Delta greedy | 3.494 | 2.321 | 1.559 | 1.148 |
| GP + EI | 3.354 | 2.321 | 1.513 | 1.075 |
| Old NAP | 3.561 | 2.396 | 1.584 | 1.124 |
| New NAP | 3.325 | 2.136 | 1.378 | 0.975 |
| Old NAP + auxiliary | 3.511 | 2.312 | 1.525 | 1.092 |
| New NAP + auxiliary | 3.315 | 2.133 | 1.380 | 0.975 |

## Efflux ratio

Pools ≥15

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 9.694 | 6.367 | 4.946 | 3.932 |
| Delta greedy | 7.116 | 5.546 | 4.412 | 3.144 |
| GP + EI | 6.394 | 4.176 | 3.324 | 2.880 |
| Old NAP | 8.523 | 5.853 | 4.628 | 3.552 |
| New NAP | 6.858 | 4.715 | 3.261 | 2.657 |
| Old NAP + auxiliary | 8.410 | 5.591 | 4.326 | 3.323 |
| New NAP + auxiliary | 6.770 | 4.690 | 3.267 | 2.636 |

Pools ≥3

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 4.125 | 2.708 | 1.860 | 1.356 |
| Delta greedy | 3.147 | 2.270 | 1.589 | 1.104 |
| GP + EI | 3.272 | 2.186 | 1.478 | 1.111 |
| Old NAP | 3.563 | 2.425 | 1.663 | 1.217 |
| New NAP | 3.148 | 2.163 | 1.418 | 1.038 |
| Old NAP + auxiliary | 3.536 | 2.398 | 1.641 | 1.189 |
| New NAP + auxiliary | 3.134 | 2.167 | 1.423 | 1.034 |
