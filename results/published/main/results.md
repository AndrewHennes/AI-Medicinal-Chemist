# Five-fold benchmark results

Comparison tables require all five folds for each endpoint/method combination. The coverage file records availability and evaluation status. The recovery protocol defines training/validation eligibility while preserving the original architecture, completed fits, and test-independent hyperparameter selection.

## Microsomal Clearance

| Method | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Current reference + EI | 4.600 | 3.216 | 2.535 | 2.191 |
| Neural mean + conventional GP | 4.789 | 3.251 | 2.597 | 2.163 |
| ALPaCA | 4.887 | 3.170 | 2.466 | 2.160 |
| MAML | 5.162 | 3.584 | 2.830 | 2.411 |
| TNP-D | 5.406 | 3.452 | 2.633 | 2.299 |
| Ordinary fine-tuning | 5.477 | 3.622 | 2.722 | 2.333 |
| ANIL | 5.510 | 3.678 | 2.703 | 2.387 |
| ANP | 5.627 | 3.634 | 2.760 | 2.423 |
| Frozen neural ensemble | 5.652 | 3.693 | 2.793 | 2.398 |
| DKT | 5.656 | 4.094 | 3.265 | 2.817 |
| CNP | 5.663 | 3.638 | 2.732 | 2.406 |
| ADKF-IFT | 6.124 | 4.380 | 3.553 | 3.009 |
| Random expectation | 8.616 | 6.130 | 4.908 | 4.126 |

Pool size ≥15. Initial hit is free. Lower counts are better.

## In Vivo Clearance

| Method | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Neural mean + conventional GP | 7.362 | 5.388 | 4.463 | 3.562 |
| ALPaCA | 7.763 | 4.513 | 3.712 | 3.013 |
| Current reference + EI | 8.613 | 5.162 | 3.375 | 2.550 |
| CNP | 8.838 | 5.875 | 3.712 | 2.938 |
| TNP-D | 9.213 | 6.700 | 5.475 | 3.413 |
| DKT | 9.250 | 5.088 | 4.362 | 3.575 |
| ADKF-IFT | 9.650 | 5.388 | 4.375 | 3.163 |
| ANP | 9.738 | 5.438 | 4.400 | 3.312 |
| Frozen neural ensemble | 10.125 | 7.550 | 5.612 | 4.525 |
| ANIL | 10.150 | 7.537 | 5.638 | 4.625 |
| Ordinary fine-tuning | 10.175 | 7.525 | 5.625 | 4.575 |
| Random expectation | 10.650 | 6.904 | 5.275 | 4.146 |

Pool size ≥15. Initial hit is free. Lower counts are better.

## Protein Binding

| Method | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Current reference + EI | 4.443 | 2.892 | 2.267 | 1.881 |
| Neural mean + conventional GP | 4.523 | 2.818 | 2.347 | 1.847 |
| ALPaCA | 4.528 | 2.557 | 2.347 | 1.869 |
| TNP-D | 4.977 | 3.142 | 2.080 | 1.733 |
| Ordinary fine-tuning | 5.131 | 3.290 | 2.324 | 1.852 |
| Frozen neural ensemble | 5.170 | 3.330 | 2.369 | 1.835 |
| ADKF-IFT | 5.205 | 3.062 | 2.432 | 1.909 |
| CNP | 5.267 | 3.347 | 2.233 | 1.676 |
| ANIL | 5.284 | 3.483 | 2.511 | 2.023 |
| DKT | 5.318 | 3.080 | 2.778 | 2.068 |
| ANP | 5.881 | 3.381 | 2.295 | 1.773 |
| Random expectation | 12.205 | 7.598 | 5.828 | 4.727 |

Pool size ≥15. Initial hit is free. Lower counts are better.

## Cellular Clearance

| Method | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Neural mean + conventional GP | 5.421 | 3.089 | 2.782 | 2.361 |
| Current reference + EI | 5.478 | 3.709 | 3.396 | 2.854 |
| ALPaCA | 5.972 | 3.665 | 3.459 | 3.082 |
| DKT | 6.269 | 4.013 | 3.598 | 3.313 |
| TNP-D | 6.389 | 3.972 | 3.579 | 3.136 |
| ANIL | 6.449 | 4.177 | 3.601 | 3.051 |
| ANP | 6.566 | 4.297 | 3.943 | 3.196 |
| ADKF-IFT | 6.661 | 4.316 | 3.867 | 3.462 |
| CNP | 6.728 | 4.396 | 3.854 | 3.250 |
| Ordinary fine-tuning | 6.883 | 4.494 | 3.918 | 3.323 |
| Frozen neural ensemble | 7.323 | 4.589 | 3.968 | 3.370 |
| Random expectation | 9.453 | 6.637 | 5.262 | 4.367 |

Pool size ≥15. Initial hit is free. Lower counts are better.

## Permeability

| Method | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Current reference + EI | 6.865 | 4.486 | 3.406 | 2.729 |
| ALPaCA | 6.903 | 4.587 | 3.292 | 2.642 |
| MAML | 6.972 | 4.892 | 3.760 | 2.979 |
| Ordinary fine-tuning | 7.288 | 5.017 | 3.833 | 3.028 |
| Neural mean + conventional GP | 7.302 | 4.806 | 3.361 | 2.729 |
| ANIL | 7.510 | 5.090 | 3.944 | 3.299 |
| Frozen neural ensemble | 7.531 | 5.132 | 3.910 | 3.205 |
| ADKF-IFT | 7.771 | 5.174 | 4.056 | 3.597 |
| DKT | 7.965 | 5.205 | 4.097 | 3.476 |
| ANP | 8.288 | 5.010 | 3.347 | 2.771 |
| TNP-D | 8.337 | 5.146 | 3.781 | 3.184 |
| CNP | 8.653 | 5.347 | 3.951 | 3.319 |
| Random expectation | 11.921 | 8.005 | 5.922 | 4.809 |

Pool size ≥15. Initial hit is free. Lower counts are better.

## Efflux

| Method | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Neural mean + conventional GP | 4.931 | 3.519 | 2.718 | 2.144 |
| ALPaCA | 5.162 | 3.861 | 2.995 | 2.273 |
| MAML | 5.435 | 4.111 | 3.194 | 2.213 |
| Current reference + EI | 5.444 | 4.069 | 3.347 | 2.421 |
| DKT | 5.870 | 4.231 | 3.440 | 2.750 |
| ANIL | 5.898 | 4.426 | 3.537 | 2.319 |
| ADKF-IFT | 5.949 | 4.111 | 3.347 | 2.713 |
| ANP | 6.042 | 4.444 | 3.630 | 2.806 |
| CNP | 6.153 | 4.361 | 3.620 | 2.532 |
| TNP-D | 6.352 | 4.898 | 3.963 | 2.796 |
| Ordinary fine-tuning | 6.569 | 4.273 | 3.343 | 2.505 |
| Frozen neural ensemble | 6.764 | 4.486 | 3.653 | 2.639 |
| Random expectation | 9.694 | 6.367 | 4.946 | 3.932 |

Pool size ≥15. Initial hit is free. Lower counts are better.
