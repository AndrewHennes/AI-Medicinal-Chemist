# Morgan metric benchmark

Five folds, three seeds, six endpoints. Primary comparison uses 580 held-out pools with at least 15 compounds, ten total measurements, and five fixed hidden queries.

| Covariance / distance | Spearman ρ | R² | Raw NLL | Raw 95% coverage |
| --- | --- | --- | --- | --- |
| Tanimoto | 0.374 | 0.560 | 0.660 | 95.3% |
| Dice | 0.380 | 0.563 | 0.651 | 95.0% |
| Cosine | 0.380 | 0.563 | 0.652 | 95.0% |
| Braun–Blanquet | 0.380 | 0.565 | 0.647 | 95.1% |
| Sokal | 0.361 | 0.554 | 0.670 | 95.6% |
| Pearson | 0.380 | 0.563 | 0.652 | 95.0% |
| Hamming / Euclidean | 0.380 | 0.563 | 0.668 | 95.3% |
| Validation-selected metric | 0.380 | 0.563 | 0.653 | 95.0% |
| Direct Morgan Tanimoto | 0.382 | 0.564 | 0.659 | 94.9% |
| Existing MiniMol GP | 0.399 | 0.579 | 0.624 | 91.7% |
| Remapped MiniMol GP | 0.401 | 0.581 | 0.608 | 93.0% |

Every model uses the same frozen MiniMol linear mean. Metric selection is performed within each endpoint/fold using validation data. The PDF includes paired intervals, calibration, smaller series, and endpoint curves.
