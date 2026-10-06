# ALPaCA series-offset ablation

The offset is analytically inferred with a flat prior, not a separate neural network. The ablation fixes that additional intercept to zero, removing its mean and uncertainty contributions. The learned neural basis, Gaussian weight prior and observation-noise scalar remain.

Ninety no-offset members were trained from scratch across six endpoints, five linked folds and three seeds. Original offset models were reused. Architecture sizes, seeds, episodes, learning rates, 4000 updates and validation checkpoint selection are matched. The ablation uses the original offset model's selected hyperparameters.

Labels remain relative to the initial hit. The no-offset model loses guaranteed invariance to shifting those labels. Its neural basis biases can still represent a constant with a finite learned prior. This is a whole offset-treatment ablation, not a claim that all capacity for constant shifts was removed.

## Equal assay averages, series size ≥15

| Context | Model | R² | Spearman ρ | NLL | 90% coverage | 90% width |
|---:|---|---:|---:|---:|---:|---:|
| 1 | ALPaCA with series offset | -0.2010 | 0.3083 | 1.2978 | 0.8756 | 2.8059 |
| 1 | ALPaCA without series offset | -0.1353 | 0.2971 | 1.2648 | 0.8703 | 2.6566 |
| 2 | ALPaCA with series offset | 0.0596 | 0.2884 | 1.1486 | 0.8581 | 2.2783 |
| 2 | ALPaCA without series offset | 0.0756 | 0.2831 | 1.1377 | 0.8590 | 2.2126 |
| 3 | ALPaCA with series offset | 0.1817 | 0.3108 | 1.0763 | 0.8517 | 2.0586 |
| 3 | ALPaCA without series offset | 0.2077 | 0.3066 | 1.0610 | 0.8645 | 2.0250 |
| 5 | ALPaCA with series offset | 0.2675 | 0.3454 | 1.0497 | 0.8439 | 1.8082 |
| 5 | ALPaCA without series offset | 0.2646 | 0.3304 | 1.0391 | 0.8454 | 1.7992 |
| 10 | ALPaCA with series offset | 0.3986 | 0.4101 | 0.9863 | 0.8321 | 1.5599 |
| 10 | ALPaCA without series offset | 0.3938 | 0.4246 | 0.9914 | 0.8347 | 1.5679 |

## Assays at five measured compounds, series size ≥15

| Assay | Model | R² | Spearman ρ | NLL |
|---|---|---:|---:|---:|
| Microsomal clearance | ALPaCA with series offset | 0.3335 | 0.3791 | 0.9671 |
| Microsomal clearance | ALPaCA without series offset | 0.3316 | 0.3670 | 0.9653 |
| In vivo clearance | ALPaCA with series offset | 0.0630 | 0.1832 | 1.2700 |
| In vivo clearance | ALPaCA without series offset | 0.0391 | 0.0682 | 1.2812 |
| Protein binding | ALPaCA with series offset | 0.3826 | 0.5126 | 0.7286 |
| Protein binding | ALPaCA without series offset | 0.3285 | 0.5123 | 0.6854 |
| Cellular clearance | ALPaCA with series offset | 0.2949 | 0.3633 | 0.9216 |
| Cellular clearance | ALPaCA without series offset | 0.3077 | 0.3847 | 0.9216 |
| Permeability | ALPaCA with series offset | 0.2853 | 0.3525 | 1.2119 |
| Permeability | ALPaCA without series offset | 0.2843 | 0.3552 | 1.2130 |
| Efflux | ALPaCA with series offset | 0.2459 | 0.2817 | 1.1991 |
| Efflux | ALPaCA without series offset | 0.2964 | 0.2951 | 1.1681 |

## Acquisition, series size ≥15

| Model | Top-1 | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| ALPaCA with series offset | 5.8690 | 3.7252 | 3.0452 | 2.5066 |
| ALPaCA without series offset | 5.8092 | 3.8270 | 3.0919 | 2.4132 |

Initial hit is free. Acquisition starts with one hit and updates after every purchase, separately from fixed-query prediction evaluation.

Paired confidence intervals in paired_differences.csv resample linked groups across assays, using 4000 replicates. Differences are without offset minus with offset. Intervals condition on the fitted models and development folds.
