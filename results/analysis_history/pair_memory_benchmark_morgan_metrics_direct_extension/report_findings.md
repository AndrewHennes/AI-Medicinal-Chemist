# Morgan metric benchmark

Five folds, three seeds, six endpoints. Primary comparison uses 580 held-out pools with at least 15 compounds, ten total measurements, and five fixed hidden queries.

| Covariance / distance | Spearman ρ | R² | Raw NLL | Raw 95% coverage |
| --- | --- | --- | --- | --- |
| Tanimoto | 0.378 | 0.561 | 0.659 | 95.1% |
| Dice | 0.381 | 0.564 | 0.649 | 94.7% |
| Cosine | 0.381 | 0.563 | 0.650 | 94.7% |
| Braun–Blanquet | 0.381 | 0.564 | 0.646 | 94.8% |
| Sokal | 0.371 | 0.557 | 0.670 | 95.5% |
| Pearson | 0.382 | 0.563 | 0.650 | 94.7% |
| Hamming / Euclidean | 0.381 | 0.564 | 0.668 | 95.2% |
| Validation-selected metric | 0.383 | 0.562 | 0.656 | 94.8% |
| Direct Morgan Tanimoto | 0.382 | 0.564 | 0.659 | 94.9% |
| Existing MiniMol GP | 0.399 | 0.579 | 0.624 | 91.7% |
| Remapped MiniMol GP | 0.401 | 0.581 | 0.608 | 93.0% |

Every model uses the same frozen MiniMol linear mean. Metric selection is performed within each endpoint/fold using validation data. The PDF includes paired intervals, calibration, smaller series, and endpoint curves.
