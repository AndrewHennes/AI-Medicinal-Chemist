# PPO, TRPO, DPO, and GP auxiliary pair supervision

Five grouped folds, six endpoints, three policy seeds. Mean purchases to any top-k compound; lower is better.

**All endpoints — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 5.695 | 3.838 | 3.080 | 2.539 |
| Original GP: warm start | 5.664 | 3.818 | 3.041 | 2.510 |
| Original GP + PPO | 5.714 | 3.853 | 3.079 | 2.543 |
| Original GP + TRPO | 5.701 | 3.828 | 3.059 | 2.539 |
| Original GP + DPO | 5.686 | 3.833 | 3.059 | 2.519 |
| Auxiliary GP: warm start | 5.632 | 3.799 | 3.036 | 2.503 |
| Auxiliary GP + PPO | 5.611 | 3.808 | 3.040 | 2.501 |
| Auxiliary GP + TRPO | 5.633 | 3.796 | 3.038 | 2.501 |
| Auxiliary GP + DPO | 5.636 | 3.822 | 3.068 | 2.540 |
| Original GP + EI | 5.570 | 3.659 | 2.911 | 2.423 |
| Auxiliary GP + EI | 5.525 | 3.662 | 2.907 | 2.411 |
| Random | 9.588 | 6.598 | 5.174 | 4.278 |

**Microsomal Clearance — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 5.028 | 3.613 | 2.845 | 2.475 |
| Original GP: warm start | 4.977 | 3.548 | 2.794 | 2.425 |
| Original GP + PPO | 5.048 | 3.620 | 2.842 | 2.467 |
| Original GP + TRPO | 5.008 | 3.604 | 2.839 | 2.471 |
| Original GP + DPO | 5.005 | 3.564 | 2.807 | 2.437 |
| Auxiliary GP: warm start | 5.009 | 3.569 | 2.799 | 2.438 |
| Auxiliary GP + PPO | 5.004 | 3.594 | 2.797 | 2.431 |
| Auxiliary GP + TRPO | 4.994 | 3.582 | 2.793 | 2.421 |
| Auxiliary GP + DPO | 5.012 | 3.590 | 2.822 | 2.473 |
| Original GP + EI | 4.934 | 3.402 | 2.643 | 2.332 |
| Auxiliary GP + EI | 4.988 | 3.494 | 2.660 | 2.322 |
| Random | 8.625 | 6.141 | 4.919 | 4.137 |

**In Vivo Clearance — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 6.929 | 4.779 | 4.071 | 3.133 |
| Original GP: warm start | 7.017 | 4.771 | 3.958 | 3.100 |
| Original GP + PPO | 6.875 | 4.783 | 3.979 | 3.108 |
| Original GP + TRPO | 7.088 | 4.754 | 3.962 | 3.029 |
| Original GP + DPO | 7.129 | 5.054 | 4.104 | 3.204 |
| Auxiliary GP: warm start | 6.996 | 5.042 | 4.121 | 3.175 |
| Auxiliary GP + PPO | 6.875 | 5.054 | 4.129 | 3.192 |
| Auxiliary GP + TRPO | 7.162 | 4.858 | 4.042 | 3.021 |
| Auxiliary GP + DPO | 6.879 | 5.008 | 4.104 | 3.167 |
| Original GP + EI | 7.075 | 4.900 | 3.800 | 3.013 |
| Auxiliary GP + EI | 6.925 | 4.900 | 3.825 | 3.013 |
| Random | 10.650 | 6.904 | 5.275 | 4.146 |

**Protein Binding — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 5.890 | 3.250 | 2.398 | 1.811 |
| Original GP: warm start | 5.792 | 3.195 | 2.333 | 1.826 |
| Original GP + PPO | 5.767 | 3.159 | 2.328 | 1.803 |
| Original GP + TRPO | 5.691 | 3.100 | 2.295 | 1.835 |
| Original GP + DPO | 5.750 | 3.208 | 2.373 | 1.818 |
| Auxiliary GP: warm start | 5.932 | 3.489 | 2.682 | 1.985 |
| Auxiliary GP + PPO | 5.871 | 3.373 | 2.570 | 1.883 |
| Auxiliary GP + TRPO | 5.807 | 3.356 | 2.610 | 1.939 |
| Auxiliary GP + DPO | 5.983 | 3.453 | 2.648 | 1.958 |
| Original GP + EI | 5.489 | 3.011 | 2.239 | 1.636 |
| Auxiliary GP + EI | 5.489 | 2.977 | 2.261 | 1.659 |
| Random | 12.205 | 7.598 | 5.828 | 4.727 |

**Cellular Clearance — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 6.236 | 3.945 | 3.480 | 2.839 |
| Original GP: warm start | 6.209 | 4.068 | 3.553 | 2.882 |
| Original GP + PPO | 6.205 | 3.938 | 3.439 | 2.809 |
| Original GP + TRPO | 6.233 | 3.931 | 3.474 | 2.847 |
| Original GP + DPO | 6.177 | 4.009 | 3.522 | 2.869 |
| Auxiliary GP: warm start | 6.018 | 3.868 | 3.411 | 2.726 |
| Auxiliary GP + PPO | 6.013 | 3.887 | 3.436 | 2.737 |
| Auxiliary GP + TRPO | 6.046 | 3.830 | 3.398 | 2.764 |
| Auxiliary GP + DPO | 6.019 | 3.891 | 3.429 | 2.748 |
| Original GP + EI | 6.073 | 3.886 | 3.456 | 2.892 |
| Auxiliary GP + EI | 5.832 | 3.741 | 3.424 | 2.867 |
| Random | 9.453 | 6.637 | 5.262 | 4.367 |

**Permeability — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 7.646 | 4.745 | 3.706 | 2.905 |
| Original GP: warm start | 7.672 | 4.751 | 3.704 | 2.905 |
| Original GP + PPO | 7.773 | 4.875 | 3.818 | 3.022 |
| Original GP + TRPO | 7.769 | 4.770 | 3.733 | 2.920 |
| Original GP + DPO | 7.704 | 4.775 | 3.752 | 2.924 |
| Auxiliary GP: warm start | 7.545 | 4.601 | 3.625 | 2.860 |
| Auxiliary GP + PPO | 7.557 | 4.642 | 3.676 | 2.895 |
| Auxiliary GP + TRPO | 7.595 | 4.641 | 3.691 | 2.911 |
| Auxiliary GP + DPO | 7.646 | 4.711 | 3.740 | 2.951 |
| Original GP + EI | 7.392 | 4.597 | 3.562 | 2.771 |
| Auxiliary GP + EI | 7.271 | 4.549 | 3.549 | 2.812 |
| Random | 11.921 | 8.005 | 5.922 | 4.809 |

**Efflux — pools ≥15**

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| Previous PPO NAP | 5.526 | 3.903 | 3.199 | 2.353 |
| Original GP: warm start | 5.537 | 3.918 | 3.063 | 2.264 |
| Original GP + PPO | 5.616 | 3.924 | 3.213 | 2.340 |
| Original GP + TRPO | 5.651 | 3.955 | 3.114 | 2.358 |
| Original GP + DPO | 5.616 | 3.918 | 3.082 | 2.256 |
| Auxiliary GP: warm start | 5.353 | 3.744 | 2.951 | 2.247 |
| Auxiliary GP + PPO | 5.245 | 3.704 | 2.988 | 2.289 |
| Auxiliary GP + TRPO | 5.384 | 3.821 | 3.022 | 2.299 |
| Auxiliary GP + DPO | 5.247 | 3.731 | 3.020 | 2.313 |
| Original GP + EI | 5.574 | 3.630 | 3.009 | 2.222 |
| Auxiliary GP + EI | 5.347 | 3.431 | 2.903 | 2.111 |
| Random | 9.694 | 6.367 | 4.946 | 3.932 |

**Primary top-1 contrasts**

- Original GP + TRPO versus Original GP + PPO: 0.23% fewer purchases; 95% interval [-1.21, 1.67]%; Holm p = 1.0000.
- Original GP + DPO versus Original GP + PPO: 0.49% fewer purchases; 95% interval [-0.53, 1.51]%; Holm p = 1.0000.
- Auxiliary GP + PPO versus Original GP + PPO: 1.81% fewer purchases; 95% interval [-0.62, 4.22]%; Holm p = 1.0000.
- Auxiliary GP + TRPO versus Original GP + TRPO: 1.19% fewer purchases; 95% interval [-1.09, 3.31]%; Holm p = 1.0000.
- Auxiliary GP + DPO versus Original GP + DPO: 0.89% fewer purchases; 95% interval [-1.70, 3.41]%; Holm p = 1.0000.
- Auxiliary GP + TRPO versus Auxiliary GP + PPO: -0.39% fewer purchases; 95% interval [-1.34, 0.51]%; Holm p = 1.0000.
- Auxiliary GP + DPO versus Auxiliary GP + PPO: -0.45% fewer purchases; 95% interval [-1.42, 0.49]%; Holm p = 1.0000.

The matched PPO critic is detached from actor features to match the TRPO setup. Historical PPO is reported separately. Results summarize the development-fold evaluation.
