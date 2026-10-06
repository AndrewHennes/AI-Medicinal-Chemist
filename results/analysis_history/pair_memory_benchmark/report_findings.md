# Pairwise external memory benchmark

Five folds, three seeds, six endpoints; 4625 held-out pools, including 580 with at least 15 compounds.

| Model | No context: R² | No context: ρ | +9 labels: R² | +9 labels: ρ |
| --- | --- | --- | --- | --- |
| Pair FNN | 0.037 | 0.216 | 0.037 | 0.216 |
| FNN + anchor averaging | 0.037 | 0.216 | 0.453 | 0.218 |
| FNN + local ridge | 0.037 | 0.216 | 0.468 | 0.218 |
| Key-value memory | 0.006 | 0.222 | 0.433 | 0.236 |
| Residual memory | 0.018 | 0.218 | 0.468 | 0.232 |

Zero context means no local measured delta. The +9-label comparison holds the same five query compounds hidden. Each endpoint and pool receives equal weight; models are not ensembled.

Full results are in pair_memory_results.pdf. Numeric summaries, pool-level results, selected hyperparameters and paired group-bootstrap confidence intervals are included alongside it.