# Overall benchmark results

[All-assay overview figure](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/reports/all_assays_overview.pdf)

These are equally weighted averages of six endpoint means, with equal pool weights within each endpoint. All listed methods completed five folds for every endpoint. Pools contain at least 15 compounds. Prediction metrics use five measured compounds and fixed hidden queries. Acquisition starts from one free measured hit in the worse half and uses K=1 direct EI until a target is found.

| Method | R² | Spearman ρ | NLL | Top-1 purchases | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Neural mean + conventional GP | 0.322 | 0.371 | 1.019 | 5.721 | 3.812 | 3.044 | 2.468 |
| ALPaCA | 0.268 | 0.345 | 1.050 | 5.869 | 3.725 | 3.045 | 2.507 |
| Current reference + EI | 0.344 | 0.376 | 0.933 | 5.907 | 3.923 | 3.054 | 2.438 |
| DKT | 0.240 | 0.281 | 1.044 | 6.721 | 4.285 | 3.590 | 3.000 |
| TNP-D | 0.264 | 0.281 | 1.019 | 6.779 | 4.552 | 3.585 | 2.760 |
| ANIL | 0.286 | 0.291 | 0.994 | 6.800 | 4.732 | 3.656 | 2.951 |
| CNP | 0.264 | 0.295 | 1.021 | 6.884 | 4.494 | 3.351 | 2.687 |
| ADKF-IFT | 0.225 | 0.246 | 1.053 | 6.893 | 4.405 | 3.605 | 2.975 |
| Ordinary fine-tuning | 0.291 | 0.294 | 0.994 | 6.921 | 4.704 | 3.627 | 2.936 |
| ANP | 0.269 | 0.277 | 1.015 | 7.024 | 4.367 | 3.396 | 2.713 |
| Frozen neural ensemble | 0.271 | 0.279 | 1.039 | 7.094 | 4.797 | 3.718 | 2.995 |
| Random expectation | — | — | — | 10.423 | 6.940 | 5.357 | 4.351 |

The current reference has the highest average R² and within-series Spearman, and the lowest average marginal NLL in this comparison. The 90% interval coverage is 87.4%. Prediction metrics are reported as point estimates.

The neural-mean conventional GP averages 0.186 fewer top-1 purchases than the reference, with paired 95% linked-group bootstrap interval [−0.576, +0.277]. ALPaCA averages 0.038 fewer purchases, with interval [−0.385, +0.414]. These are exploratory, unadjusted intervals.

The six-endpoint aggregate requires complete five-fold results. MAML is reported separately for microsomal clearance, permeability, and efflux. Six configurations were unavailable after training and one failed numerically during test evaluation; the selected hyperparameters were retained.

The current reference and comparators use full outer-training data. Earlier runs used half-training allocations. Results summarize development folds.
