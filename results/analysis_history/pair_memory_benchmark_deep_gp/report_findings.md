# Deep GP and memory benchmark

| Model | No context R² | No context ρ | +9 labels R² | +9 labels ρ |
| --- | --- | --- | --- | --- |
| Previous delta FNN | -0.033 | 0.217 | -0.033 | 0.217 |
| Tuned pair FNN | 0.037 | 0.216 | 0.037 | 0.216 |
| Previous delta + anchors | -0.033 | 0.217 | 0.416 | 0.221 |
| Tuned FNN + ridge | 0.037 | 0.216 | 0.468 | 0.218 |
| Key-value memory | 0.006 | 0.222 | 0.433 | 0.236 |
| Residual memory | 0.018 | 0.218 | 0.468 | 0.232 |
| Previous GP | -1.419 | 0.134 | 0.084 | 0.266 |
| Matched linear-mean GP | 0.081 | 0.228 | 0.579 | 0.399 |
| Neural mean GP | 0.027 | 0.237 | 0.572 | 0.401 |
| Deep kernel GP | 0.107 | 0.246 | 0.549 | 0.384 |
| Neural mean + deep kernel | 0.087 | 0.260 | 0.549 | 0.372 |

All figures use the same fixed queries in 580 held-out pools with at least 15 compounds. Five outer folds; three training seeds for new models.
