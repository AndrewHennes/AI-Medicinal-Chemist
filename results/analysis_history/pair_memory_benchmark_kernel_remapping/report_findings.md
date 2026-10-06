# Tanimoto and covariance remapping

Five folds, three seeds, six endpoints, 580 held-out pools with at least 15 compounds. All 4625 pools are included in the numeric summaries.

| Model | 1 label: R² | 1 label: ρ | 10 labels: R² | 10 labels: ρ |
| --- | --- | --- | --- | --- |
| Existing tuned GP | 0.081 | 0.228 | 0.579 | 0.399 |
| Current kernel refit | 0.081 | 0.228 | 0.579 | 0.398 |
| Current kernel remapped | 0.081 | 0.228 | 0.581 | 0.401 |
| MiniMol Tanimoto | 0.081 | 0.228 | 0.581 | 0.398 |
| MiniMol Tanimoto remapped | 0.081 | 0.228 | 0.580 | 0.400 |
| Morgan Tanimoto | 0.081 | 0.228 | 0.564 | 0.382 |
| Morgan Tanimoto remapped | 0.081 | 0.228 | 0.555 | 0.366 |
| Joint fit: current kernel | 0.080 | 0.228 | 0.578 | 0.397 |
| Joint fit: selected alternative | 0.080 | 0.228 | 0.574 | 0.392 |
| Original delta + anchors | -0.033 | 0.217 | 0.416 | 0.221 |

One label is the reference only; ten labels includes nine additional outcomes. Primary GP means and geometries are frozen. Hyperparameters are selected on validation data. See the PDF for uncertainty, paired confidence intervals, endpoint curves, and limitations.
