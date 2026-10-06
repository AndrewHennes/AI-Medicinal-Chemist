Mean purchases to reach any top-k compound. Pools with at least 15 molecules; five grouped folds; three policy seeds. Lower is better. Best mean in each column is bold.

**Microsomal Clearance — 311 pools (183 linked groups)**

| Acquisition model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.028 | 3.613 | 2.845 | 2.475 |
| + best observed value | 5.014 | 3.577 | 2.819 | 2.445 |
| + delta summaries | 4.844 | 3.429 | 2.708 | 2.362 |
| + both scalar additions | **4.807** | 3.418 | 2.722 | 2.362 |
| GP + Set Transformer, without delta summaries | 5.215 | 3.582 | 2.803 | 2.457 |
| Full Set Transformer | 5.335 | 3.679 | 2.960 | 2.545 |
| Compact, regularized Set Transformer | 5.051 | 3.528 | 2.805 | 2.433 |
| Deep Sets | 5.444 | 3.822 | 3.039 | 2.632 |
| Cross-attention | 5.115 | 3.592 | 2.845 | 2.467 |
| GP + expected improvement | 4.934 | **3.402** | **2.643** | **2.332** |

**In Vivo Clearance — 20 pools (16 linked groups)**

| Acquisition model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | **6.929** | 4.779 | 4.071 | 3.133 |
| + best observed value | 7.496 | **4.650** | 4.037 | **2.987** |
| + delta summaries | 7.746 | 4.850 | 4.100 | 3.158 |
| + both scalar additions | 9.175 | 6.188 | 4.675 | 3.708 |
| GP + Set Transformer, without delta summaries | 7.500 | 5.633 | 4.242 | 3.192 |
| Full Set Transformer | 8.483 | 6.383 | 4.404 | 3.058 |
| Compact, regularized Set Transformer | 8.254 | 6.213 | 4.763 | 3.638 |
| Deep Sets | 8.192 | 6.133 | 4.442 | 3.425 |
| Cross-attention | 9.650 | 6.779 | 5.242 | 3.967 |
| GP + expected improvement | 7.075 | 4.900 | **3.800** | 3.013 |

**Protein Binding — 44 pools (29 linked groups)**

| Acquisition model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.890 | 3.250 | 2.398 | 1.811 |
| + best observed value | 5.752 | 3.193 | 2.369 | 1.801 |
| + delta summaries | 5.722 | 3.102 | 2.420 | 1.909 |
| + both scalar additions | 5.674 | **3.002** | 2.347 | 1.816 |
| GP + Set Transformer, without delta summaries | 5.943 | 3.750 | 2.769 | 2.231 |
| Full Set Transformer | 6.409 | 3.807 | 2.879 | 2.267 |
| Compact, regularized Set Transformer | 5.676 | 3.424 | 2.684 | 1.941 |
| Deep Sets | 6.850 | 4.140 | 3.053 | 2.583 |
| Cross-attention | 6.767 | 3.759 | 2.714 | 2.316 |
| GP + expected improvement | **5.489** | 3.011 | **2.239** | **1.636** |

**Cellular Clearance — 79 pools (53 linked groups)**

| Acquisition model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 6.236 | 3.945 | 3.480 | 2.839 |
| + best observed value | **6.066** | **3.850** | 3.453 | 2.809 |
| + delta summaries | 6.291 | 4.045 | **3.379** | **2.752** |
| + both scalar additions | 6.137 | 4.019 | 3.496 | 2.816 |
| GP + Set Transformer, without delta summaries | 6.597 | 4.808 | 4.074 | 3.540 |
| Full Set Transformer | 6.924 | 4.961 | 4.178 | 3.628 |
| Compact, regularized Set Transformer | 6.392 | 4.332 | 3.755 | 3.262 |
| Deep Sets | 7.058 | 5.153 | 4.256 | 3.525 |
| Cross-attention | 7.099 | 5.137 | 4.276 | 3.575 |
| GP + expected improvement | 6.073 | 3.886 | 3.456 | 2.892 |

**Permeability — 72 pools (62 linked groups)**

| Acquisition model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 7.646 | 4.745 | 3.706 | 2.905 |
| + best observed value | 7.578 | 4.728 | 3.630 | 2.825 |
| + delta summaries | 7.819 | 4.966 | 3.725 | 2.919 |
| + both scalar additions | 7.917 | 4.977 | 3.760 | 2.983 |
| GP + Set Transformer, without delta summaries | 8.546 | 5.929 | 4.168 | 3.495 |
| Full Set Transformer | 8.154 | 5.740 | 4.281 | 3.531 |
| Compact, regularized Set Transformer | 8.439 | 5.185 | 4.171 | 3.307 |
| Deep Sets | 8.647 | 5.836 | 4.459 | 3.877 |
| Cross-attention | 8.751 | 5.994 | 4.779 | 4.052 |
| GP + expected improvement | **7.392** | **4.597** | **3.562** | **2.771** |

**Efflux — 54 pools (49 linked groups)**

| Acquisition model | Top 1 | Top 2 | Top 3 | Top 4 |
|---|---:|---:|---:|---:|
| NAP: GP mean + SD | 5.526 | 3.903 | 3.199 | 2.353 |
| + best observed value | **5.407** | 3.789 | 3.059 | 2.285 |
| + delta summaries | 5.878 | 3.869 | 3.125 | 2.335 |
| + both scalar additions | 5.892 | 3.972 | 3.116 | 2.230 |
| GP + Set Transformer, without delta summaries | 6.153 | 4.412 | 3.531 | 2.554 |
| Full Set Transformer | 6.208 | 4.177 | 3.398 | 2.417 |
| Compact, regularized Set Transformer | 5.745 | 3.886 | 3.256 | 2.275 |
| Deep Sets | 5.827 | 4.111 | 3.182 | 2.335 |
| Cross-attention | 6.105 | 4.174 | 3.347 | 2.458 |
| GP + expected improvement | 5.574 | **3.630** | **3.009** | **2.222** |

