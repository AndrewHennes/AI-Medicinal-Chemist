# Full value-learning comparison across six datasets

Completed comparison of compact, set-pooling and attention value models, within-fold validation-selected recipes, shallow lookahead and Monte Carlo tree search. All six endpoints use five grouped outer folds, three neural seeds and four matched worst-half starts per pool. Microsomal results and the completed compact fits are reused unchanged.

## Mean purchases to top-1, pools of at least 3 compounds

| Endpoint | Random | Delta greedy | GP + EI | Original NAP | Revised NAP | Compact value | Set-pooling value | Attention value | Selected value | Value + lookahead | Value + tree search |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 3.526 | 2.719 | 2.698 | 2.753 | 2.598 | 2.608 | 2.915 | 2.799 | 2.661 | 2.671 | 2.642 |
| In vivo clearance | 2.745 | 2.615 | 2.626 | 2.543 | 2.593 | 2.595 | 2.680 | 2.693 | 2.710 | 2.688 | 2.660 |
| Plasma protein binding | 2.981 | 2.202 | 2.432 | 2.290 | 2.260 | 2.222 | 2.511 | 2.472 | 2.438 | 2.398 | 2.418 |
| Cellular clearance | 3.576 | 2.895 | 2.950 | 3.031 | 2.778 | 2.891 | 3.270 | 3.336 | 2.970 | 2.998 | 2.938 |
| A→B permeability | 4.266 | 3.494 | 3.354 | 3.561 | 3.325 | 3.302 | 3.661 | 3.638 | 3.583 | 3.596 | 3.478 |
| Efflux ratio | 4.125 | 3.147 | 3.272 | 3.563 | 3.148 | 3.276 | 3.766 | 3.685 | 3.323 | 3.403 | 3.326 |

## Mean purchases to top-1, pools of at least 15 compounds

| Endpoint | Random | Delta greedy | GP + EI | Original NAP | Revised NAP | Compact value | Set-pooling value | Attention value | Selected value | Value + lookahead | Value + tree search |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 8.621 | 5.695 | 5.835 | 6.111 | 5.400 | 5.348 | 6.622 | 6.159 | 5.669 | 5.695 | 5.653 |
| In vivo clearance | 10.650 | 9.762 | 9.375 | 8.838 | 9.600 | 8.787 | 11.017 | 10.867 | 11.067 | 10.617 | 9.371 |
| Plasma protein binding | 12.205 | 6.909 | 7.716 | 7.438 | 6.716 | 7.403 | 8.892 | 8.803 | 8.947 | 8.331 | 8.759 |
| Cellular clearance | 9.453 | 6.826 | 6.997 | 7.301 | 6.500 | 6.912 | 8.014 | 8.781 | 7.167 | 7.407 | 7.111 |
| A→B permeability | 11.921 | 9.802 | 7.465 | 9.122 | 8.127 | 8.610 | 9.491 | 9.690 | 9.492 | 9.493 | 8.854 |
| Efflux ratio | 9.694 | 7.116 | 6.394 | 8.523 | 6.858 | 7.148 | 9.559 | 9.113 | 6.995 | 7.153 | 6.938 |

## All four purchase counts by endpoint

### Microsomal clearance

Lower log10 clearance.

Pools ≥15: 311 pools from 183 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 8.621 | 6.140 | 4.918 | 4.136 |
| Delta greedy | 5.695 | 3.761 | 3.031 | 2.459 |
| GP + EI | 5.835 | 3.932 | 3.140 | 2.709 |
| Original NAP | 6.111 | 3.989 | 3.130 | 2.626 |
| Revised NAP | 5.400 | 3.610 | 2.881 | 2.506 |
| Compact value | 5.348 | 3.587 | 2.924 | 2.474 |
| Set-pooling value | 6.622 | 4.585 | 3.601 | 3.066 |
| Attention value | 6.159 | 4.072 | 3.236 | 2.753 |
| Selected value | 5.669 | 3.893 | 3.076 | 2.612 |
| Value + lookahead | 5.695 | 3.922 | 3.080 | 2.622 |
| Value + tree search | 5.653 | 3.818 | 2.986 | 2.543 |

Pools ≥3: 1827 pools from 897 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 3.526 | 2.480 | 1.644 | 1.233 |
| Delta greedy | 2.719 | 1.895 | 1.216 | 0.882 |
| GP + EI | 2.698 | 1.920 | 1.234 | 0.921 |
| Original NAP | 2.753 | 1.910 | 1.213 | 0.902 |
| Revised NAP | 2.598 | 1.846 | 1.172 | 0.874 |
| Compact value | 2.608 | 1.856 | 1.187 | 0.871 |
| Set-pooling value | 2.915 | 2.064 | 1.334 | 1.004 |
| Attention value | 2.799 | 1.940 | 1.244 | 0.928 |
| Selected value | 2.661 | 1.896 | 1.206 | 0.887 |
| Value + lookahead | 2.671 | 1.908 | 1.221 | 0.899 |
| Value + tree search | 2.642 | 1.884 | 1.200 | 0.883 |

### In vivo clearance

Lower log10 clearance.

Pools ≥15: 20 pools from 16 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 10.650 | 6.904 | 5.275 | 4.146 |
| Delta greedy | 9.762 | 6.200 | 4.100 | 3.413 |
| GP + EI | 9.375 | 6.275 | 4.362 | 3.600 |
| Original NAP | 8.838 | 7.412 | 5.529 | 4.054 |
| Revised NAP | 9.600 | 4.800 | 3.321 | 2.750 |
| Compact value | 8.787 | 6.200 | 4.379 | 3.600 |
| Set-pooling value | 11.017 | 8.196 | 5.921 | 4.525 |
| Attention value | 10.867 | 6.908 | 4.517 | 3.700 |
| Selected value | 11.067 | 7.250 | 5.254 | 4.329 |
| Value + lookahead | 10.617 | 6.875 | 4.925 | 4.029 |
| Value + tree search | 9.371 | 6.304 | 4.783 | 3.892 |

Pools ≥3: 537 pools from 399 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 2.745 | 1.809 | 0.986 | 0.610 |
| Delta greedy | 2.615 | 1.734 | 0.913 | 0.549 |
| GP + EI | 2.626 | 1.742 | 0.951 | 0.598 |
| Original NAP | 2.543 | 1.739 | 0.951 | 0.592 |
| Revised NAP | 2.593 | 1.654 | 0.888 | 0.537 |
| Compact value | 2.595 | 1.773 | 0.944 | 0.589 |
| Set-pooling value | 2.680 | 1.833 | 1.001 | 0.608 |
| Attention value | 2.693 | 1.776 | 0.930 | 0.582 |
| Selected value | 2.710 | 1.814 | 0.982 | 0.609 |
| Value + lookahead | 2.688 | 1.804 | 0.969 | 0.593 |
| Value + tree search | 2.660 | 1.778 | 0.962 | 0.593 |

### Plasma protein binding

Lower logK = log10((1−fu)/fu), hence higher unbound fraction.

Pools ≥15: 44 pools from 29 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 12.205 | 7.598 | 5.828 | 4.727 |
| Delta greedy | 6.909 | 3.994 | 3.119 | 2.085 |
| GP + EI | 7.716 | 4.938 | 4.438 | 3.426 |
| Original NAP | 7.438 | 4.161 | 3.371 | 2.943 |
| Revised NAP | 6.716 | 3.852 | 3.394 | 2.447 |
| Compact value | 7.403 | 4.517 | 3.678 | 2.975 |
| Set-pooling value | 8.892 | 5.458 | 4.830 | 3.597 |
| Attention value | 8.803 | 4.920 | 4.297 | 3.286 |
| Selected value | 8.947 | 6.112 | 5.491 | 3.953 |
| Value + lookahead | 8.331 | 5.540 | 4.898 | 3.807 |
| Value + tree search | 8.759 | 5.606 | 4.922 | 3.801 |

Pools ≥3: 880 pools from 355 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 2.981 | 1.920 | 1.090 | 0.714 |
| Delta greedy | 2.202 | 1.428 | 0.762 | 0.467 |
| GP + EI | 2.432 | 1.661 | 0.939 | 0.616 |
| Original NAP | 2.290 | 1.521 | 0.845 | 0.564 |
| Revised NAP | 2.260 | 1.478 | 0.813 | 0.510 |
| Compact value | 2.222 | 1.500 | 0.818 | 0.536 |
| Set-pooling value | 2.511 | 1.677 | 0.962 | 0.624 |
| Attention value | 2.472 | 1.633 | 0.929 | 0.595 |
| Selected value | 2.438 | 1.683 | 0.973 | 0.634 |
| Value + lookahead | 2.398 | 1.650 | 0.945 | 0.632 |
| Value + tree search | 2.418 | 1.645 | 0.936 | 0.624 |

### Cellular clearance

Lower log10 clearance.

Pools ≥15: 79 pools from 53 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 9.453 | 6.637 | 5.262 | 4.367 |
| Delta greedy | 6.826 | 4.785 | 3.481 | 2.902 |
| GP + EI | 6.997 | 4.573 | 3.930 | 3.509 |
| Original NAP | 7.301 | 4.964 | 4.186 | 3.598 |
| Revised NAP | 6.500 | 4.162 | 3.525 | 3.055 |
| Compact value | 6.912 | 4.674 | 3.718 | 3.318 |
| Set-pooling value | 8.014 | 5.776 | 4.989 | 4.176 |
| Attention value | 8.781 | 6.222 | 5.059 | 4.195 |
| Selected value | 7.167 | 4.931 | 4.059 | 3.409 |
| Value + lookahead | 7.407 | 5.108 | 4.159 | 3.448 |
| Value + tree search | 7.111 | 4.807 | 4.056 | 3.400 |

Pools ≥3: 524 pools from 222 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 3.576 | 2.483 | 1.647 | 1.221 |
| Delta greedy | 2.895 | 2.042 | 1.251 | 0.916 |
| GP + EI | 2.950 | 1.992 | 1.351 | 1.048 |
| Original NAP | 3.031 | 2.123 | 1.406 | 1.059 |
| Revised NAP | 2.778 | 1.869 | 1.250 | 0.950 |
| Compact value | 2.891 | 1.988 | 1.293 | 1.005 |
| Set-pooling value | 3.270 | 2.328 | 1.555 | 1.177 |
| Attention value | 3.336 | 2.324 | 1.550 | 1.160 |
| Selected value | 2.970 | 2.077 | 1.360 | 1.021 |
| Value + lookahead | 2.998 | 2.095 | 1.380 | 1.029 |
| Value + tree search | 2.938 | 2.039 | 1.365 | 1.022 |

### A→B permeability

Higher log10 A→B permeability.

Pools ≥15: 72 pools from 62 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 11.921 | 8.005 | 5.922 | 4.809 |
| Delta greedy | 9.802 | 6.076 | 4.875 | 4.135 |
| GP + EI | 7.465 | 5.583 | 4.108 | 3.493 |
| Original NAP | 9.122 | 6.310 | 4.616 | 3.763 |
| Revised NAP | 8.127 | 4.897 | 3.610 | 2.882 |
| Compact value | 8.610 | 5.714 | 4.021 | 3.455 |
| Set-pooling value | 9.491 | 7.025 | 5.278 | 4.492 |
| Attention value | 9.690 | 6.887 | 5.397 | 4.655 |
| Selected value | 9.492 | 6.273 | 4.738 | 4.086 |
| Value + lookahead | 9.493 | 6.237 | 4.693 | 4.015 |
| Value + tree search | 8.854 | 6.062 | 4.461 | 3.795 |

Pools ≥3: 516 pools from 376 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 4.266 | 2.804 | 1.853 | 1.333 |
| Delta greedy | 3.494 | 2.321 | 1.559 | 1.148 |
| GP + EI | 3.354 | 2.321 | 1.513 | 1.075 |
| Original NAP | 3.561 | 2.396 | 1.584 | 1.124 |
| Revised NAP | 3.325 | 2.136 | 1.378 | 0.975 |
| Compact value | 3.302 | 2.225 | 1.415 | 1.049 |
| Set-pooling value | 3.661 | 2.540 | 1.713 | 1.238 |
| Attention value | 3.638 | 2.452 | 1.664 | 1.228 |
| Selected value | 3.583 | 2.380 | 1.583 | 1.157 |
| Value + lookahead | 3.596 | 2.367 | 1.569 | 1.144 |
| Value + tree search | 3.478 | 2.350 | 1.543 | 1.110 |

### Efflux ratio

Lower log10 B→A/A→B efflux ratio, following the curated direction annotation.

Pools ≥15: 54 pools from 49 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 9.694 | 6.367 | 4.946 | 3.932 |
| Delta greedy | 7.116 | 5.546 | 4.412 | 3.144 |
| GP + EI | 6.394 | 4.176 | 3.324 | 2.880 |
| Original NAP | 8.523 | 5.853 | 4.628 | 3.552 |
| Revised NAP | 6.858 | 4.715 | 3.261 | 2.657 |
| Compact value | 7.148 | 5.335 | 3.813 | 2.920 |
| Set-pooling value | 9.559 | 6.199 | 4.651 | 3.596 |
| Attention value | 9.113 | 6.031 | 4.548 | 3.535 |
| Selected value | 6.995 | 4.872 | 3.403 | 2.665 |
| Value + lookahead | 7.153 | 4.938 | 3.471 | 2.755 |
| Value + tree search | 6.938 | 4.880 | 3.418 | 2.713 |

Pools ≥3: 341 pools from 251 source groups.

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | --- | --- | --- | --- |
| Random | 4.125 | 2.708 | 1.860 | 1.356 |
| Delta greedy | 3.147 | 2.270 | 1.589 | 1.104 |
| GP + EI | 3.272 | 2.186 | 1.478 | 1.111 |
| Original NAP | 3.563 | 2.425 | 1.663 | 1.217 |
| Revised NAP | 3.148 | 2.163 | 1.418 | 1.038 |
| Compact value | 3.276 | 2.284 | 1.508 | 1.081 |
| Set-pooling value | 3.766 | 2.539 | 1.720 | 1.240 |
| Attention value | 3.685 | 2.471 | 1.673 | 1.222 |
| Selected value | 3.323 | 2.219 | 1.458 | 1.052 |
| Value + lookahead | 3.403 | 2.280 | 1.499 | 1.078 |
| Value + tree search | 3.326 | 2.248 | 1.469 | 1.083 |

## Paired top-1 differences versus revised NAP in large pools

Negative is better. Intervals resample source groups with fitted models fixed and are unadjusted for multiple comparisons.

| Endpoint | Method | Difference | 95% lower | 95% upper |
| --- | --- | --- | --- | --- |
| Microsomal clearance | Compact value | -0.052 | -0.392 | 0.287 |
| Microsomal clearance | Set-pooling value | 1.223 | 0.596 | 1.865 |
| Microsomal clearance | Attention value | 0.759 | 0.290 | 1.228 |
| Microsomal clearance | Selected value | 0.269 | -0.171 | 0.695 |
| Microsomal clearance | Value + lookahead | 0.296 | -0.109 | 0.720 |
| Microsomal clearance | Value + tree search | 0.253 | -0.118 | 0.625 |
| In vivo clearance | Compact value | -0.812 | -3.236 | 1.491 |
| In vivo clearance | Set-pooling value | 1.417 | -2.047 | 4.205 |
| In vivo clearance | Attention value | 1.267 | -1.375 | 3.364 |
| In vivo clearance | Selected value | 1.467 | -1.177 | 3.496 |
| In vivo clearance | Value + lookahead | 1.017 | -1.922 | 3.179 |
| In vivo clearance | Value + tree search | -0.229 | -2.174 | 1.764 |
| Plasma protein binding | Compact value | 0.688 | -1.081 | 2.428 |
| Plasma protein binding | Set-pooling value | 2.176 | 0.605 | 4.042 |
| Plasma protein binding | Attention value | 2.087 | 0.440 | 3.569 |
| Plasma protein binding | Selected value | 2.231 | 0.773 | 4.217 |
| Plasma protein binding | Value + lookahead | 1.616 | 0.338 | 3.237 |
| Plasma protein binding | Value + tree search | 2.044 | 0.752 | 3.537 |
| Cellular clearance | Compact value | 0.412 | -0.355 | 1.344 |
| Cellular clearance | Set-pooling value | 1.514 | -0.020 | 2.825 |
| Cellular clearance | Attention value | 2.281 | 0.997 | 3.406 |
| Cellular clearance | Selected value | 0.667 | -0.486 | 1.889 |
| Cellular clearance | Value + lookahead | 0.907 | -0.197 | 2.144 |
| Cellular clearance | Value + tree search | 0.611 | -0.411 | 1.754 |
| A→B permeability | Compact value | 0.483 | -0.485 | 1.374 |
| A→B permeability | Set-pooling value | 1.363 | -0.544 | 3.202 |
| A→B permeability | Attention value | 1.563 | -0.530 | 3.895 |
| A→B permeability | Selected value | 1.365 | -0.088 | 2.712 |
| A→B permeability | Value + lookahead | 1.366 | -0.109 | 2.733 |
| A→B permeability | Value + tree search | 0.727 | -0.546 | 1.852 |
| Efflux ratio | Compact value | 0.290 | -0.621 | 1.180 |
| Efflux ratio | Set-pooling value | 2.701 | 1.428 | 3.906 |
| Efflux ratio | Attention value | 2.255 | 0.805 | 3.588 |
| Efflux ratio | Selected value | 0.137 | -0.800 | 1.051 |
| Efflux ratio | Value + lookahead | 0.295 | -0.699 | 1.225 |
| Efflux ratio | Value + tree search | 0.080 | -0.844 | 0.914 |

## Protocol and interpretation

Each endpoint and outer fold independently compares three base architectures and then four refinements of its two strongest architectures. The selected recipe uses that fold's validation data only. Three seeds are used for each final comparison. Search settings are selected using seed 11 validation trajectories and applied to all three final seeds.

Shallow lookahead and tree search use the selected value model, so their matched parent is the "Selected value" method. Search uses hypothetical Gaussian observations, a candidate shortlist and at most the first eight real purchases, then direct Q. It never receives a true optimum-found signal. Predicted relative delta means and sample standard deviations update using measured anchors, with zero standard deviation for one anchor. No sign-consistency loss is used.

Model and search choices were fixed before this extension's evaluation. The original microsomal search space is retained. Bootstrap intervals are conditional on fitted models; compute budgets are recorded by method.

The initial hit is free; already qualifying starts cost zero. Rank-boundary ties qualify, so top-4 is necessarily zero for pools of three or four. Every pool has equal weight after averaging its starts and neural seeds. Human/rat/mouse and human/dog assay contexts retain their existing separate pools. Existing transformed outcomes and their directions are unchanged.

## Selected architecture counts across five outer folds

| Endpoint | attention | deep_sets | statistics |
| --- | --- | --- | --- |
| Microsomal clearance | 0 | 1 | 4 |
| In vivo clearance | 2 | 2 | 1 |
| Plasma protein binding | 1 | 2 | 2 |
| Cellular clearance | 0 | 1 | 4 |
| A→B permeability | 4 | 0 | 1 |
| Efflux ratio | 0 | 1 | 4 |

The combined PDF contains a methods page, a top-1 overview, and three pages per endpoint covering all four acquisition-count metrics. Separate endpoint PDFs, matched trajectories, source coverage, paired intervals, validation trials, selected recipes and runtimes are also provided.
