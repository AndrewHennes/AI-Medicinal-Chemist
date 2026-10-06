# Distance features for the GP mean + SD NAP

Five grouped folds; three policy seeds; four matched starts. Mean purchases to any top-k compound. Lower is better.

**All endpoints — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.695 | 3.838 | 3.080 | 2.539 |
| + Tanimoto distances | 5.702 | 3.794 | 3.055 | 2.492 |
| + Minimol distances | 5.714 | 3.795 | 3.075 | 2.537 |
| + both distances | 5.814 | 3.902 | 3.102 | 2.538 |
| GP + expected improvement | 5.570 | 3.659 | 2.911 | 2.423 |
| Random | 9.588 | 6.598 | 5.174 | 4.278 |

**Microsomal Clearance — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.028 | 3.613 | 2.845 | 2.475 |
| + Tanimoto distances | 4.962 | 3.517 | 2.766 | 2.395 |
| + Minimol distances | 4.982 | 3.497 | 2.790 | 2.427 |
| + both distances | 4.987 | 3.559 | 2.770 | 2.400 |
| GP + expected improvement | 4.934 | 3.402 | 2.643 | 2.332 |
| Random | 8.625 | 6.141 | 4.919 | 4.137 |

**In Vivo Clearance — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 6.929 | 4.779 | 4.071 | 3.133 |
| + Tanimoto distances | 7.371 | 4.992 | 4.167 | 3.271 |
| + Minimol distances | 6.367 | 4.425 | 4.175 | 3.371 |
| + both distances | 8.762 | 5.379 | 4.629 | 3.554 |
| GP + expected improvement | 7.075 | 4.900 | 3.800 | 3.013 |
| Random | 10.650 | 6.904 | 5.275 | 4.146 |

**Protein Binding — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.890 | 3.250 | 2.398 | 1.811 |
| + Tanimoto distances | 5.830 | 3.246 | 2.367 | 1.771 |
| + Minimol distances | 5.792 | 3.214 | 2.352 | 1.831 |
| + both distances | 5.864 | 3.133 | 2.326 | 1.811 |
| GP + expected improvement | 5.489 | 3.011 | 2.239 | 1.636 |
| Random | 12.205 | 7.598 | 5.828 | 4.727 |

**Cellular Clearance — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 6.236 | 3.945 | 3.480 | 2.839 |
| + Tanimoto distances | 6.211 | 3.902 | 3.449 | 2.809 |
| + Minimol distances | 6.546 | 4.011 | 3.526 | 2.876 |
| + both distances | 6.649 | 4.295 | 3.618 | 2.872 |
| GP + expected improvement | 6.073 | 3.886 | 3.456 | 2.892 |
| Random | 9.453 | 6.637 | 5.262 | 4.367 |

**Permeability — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 7.646 | 4.745 | 3.706 | 2.905 |
| + Tanimoto distances | 7.785 | 4.706 | 3.735 | 2.824 |
| + Minimol distances | 7.709 | 4.897 | 3.804 | 2.946 |
| + both distances | 7.851 | 4.977 | 3.889 | 3.006 |
| GP + expected improvement | 7.392 | 4.597 | 3.562 | 2.771 |
| Random | 11.921 | 8.005 | 5.922 | 4.809 |

**Efflux — pools ≥15**

| Model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.526 | 3.903 | 3.199 | 2.353 |
| + Tanimoto distances | 5.716 | 4.020 | 3.381 | 2.437 |
| + Minimol distances | 5.753 | 3.965 | 3.272 | 2.392 |
| + both distances | 5.502 | 3.954 | 3.281 | 2.438 |
| GP + expected improvement | 5.574 | 3.630 | 3.009 | 2.222 |
| Random | 9.694 | 6.367 | 4.946 | 3.932 |

**Primary top-1 comparison to GP-only NAP**

- + Tanimoto distances: -0.12% fewer purchases; 95% interval [-1.98, 1.70]%; Holm-adjusted bootstrap p = 1.0000.
- + Minimol distances: -0.34% fewer purchases; 95% interval [-2.34, 1.57]%; Holm-adjusted bootstrap p = 1.0000.
- + both distances: -2.08% fewer purchases; 95% interval [-4.28, -0.04]%; Holm-adjusted bootstrap p = 0.1380.
