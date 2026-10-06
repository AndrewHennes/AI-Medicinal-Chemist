# Compact value learning across all datasets

Completed endpoint-specific fits with five grouped outer folds, three neural seeds and four matched worst-half starting hits. Microsomal compact-model results are reused exactly. All other endpoints use the same architecture and training settings, with their own training data and validation-selected checkpoints.

## Pools with at least 3 compounds

Mean additional purchases; lower is better.

| Endpoint | Pools | Value top-1 | Value top-2 | Value top-3 | Value top-4 | NAP top-1 |
| --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 1827 | 2.608 | 1.856 | 1.187 | 0.871 | 2.598 |
| In vivo clearance | 537 | 2.595 | 1.773 | 0.944 | 0.589 | 2.593 |
| Plasma protein binding | 880 | 2.222 | 1.500 | 0.818 | 0.536 | 2.260 |
| Cellular clearance | 524 | 2.891 | 1.988 | 1.293 | 1.005 | 2.778 |
| A→B permeability | 516 | 3.302 | 2.225 | 1.415 | 1.049 | 3.325 |
| Efflux ratio | 341 | 3.276 | 2.284 | 1.508 | 1.081 | 3.148 |

## Pools with at least 15 compounds

Mean additional purchases; lower is better.

| Endpoint | Pools | Value top-1 | Value top-2 | Value top-3 | Value top-4 | NAP top-1 |
| --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 311 | 5.348 | 3.587 | 2.924 | 2.474 | 5.400 |
| In vivo clearance | 20 | 8.787 | 6.200 | 4.379 | 3.600 | 9.600 |
| Plasma protein binding | 44 | 7.403 | 4.517 | 3.678 | 2.975 | 6.716 |
| Cellular clearance | 79 | 6.912 | 4.674 | 3.718 | 3.318 | 6.500 |
| A→B permeability | 72 | 8.610 | 5.714 | 4.021 | 3.455 | 8.127 |
| Efflux ratio | 54 | 7.148 | 5.335 | 3.813 | 2.920 | 6.858 |

## Paired top-1 differences versus revised NAP in large pools

Negative differences favor the value model. Intervals are source-group bootstrap intervals with fixed models, unadjusted for multiple comparisons.

| Endpoint | Value − NAP | 95% lower | 95% upper | Groups |
| --- | --- | --- | --- | --- |
| Microsomal clearance | -0.052 | -0.406 | 0.287 | 183 |
| In vivo clearance | -0.812 | -3.208 | 1.519 | 16 |
| Plasma protein binding | 0.688 | -1.148 | 2.366 | 29 |
| Cellular clearance | 0.412 | -0.339 | 1.342 | 53 |
| A→B permeability | 0.483 | -0.467 | 1.407 | 62 |
| Efflux ratio | 0.290 | -0.573 | 1.198 | 49 |

## Model and evaluation

The compact model uses the same prediction summaries, pooling, Double-Q cost updates, 40 transitions per training pool, and 1,800 + 1,800 update budget as the microsomal compact baseline. It predicts remaining acquisition costs and selects the smallest top-1 estimate. No additional architecture or search sweep was performed for this extension. Full trajectories are scored retrospectively; hidden optimum-found information never enters the model.

Delta models use their original training allocation. Acquisition-training GP summaries use source-group-excluded teachers. Checkpoint selection uses fold-specific validation, weighting normalized large-pool top-1 counts 75% and all-pool counts 25%.

The model is trained independently for each endpoint. Human/rat/mouse clearance and binding pools and human/dog permeability and efflux pools retain their existing species/assay separation. Dog is the reference category of the existing three species indicators. Transformed outcomes remain relative to the initial hit; no sign-consistency regularization is introduced.

Initial hits are free, rank-boundary ties qualify, and top-4 is zero for pools of three or four. Counts average starts, then seeds, then pools. The bootstrap clusters related pools by source group and is conditional on fitted models.

## Endpoint objectives

| Endpoint | Objective |
| --- | --- |
| Microsomal clearance | Lower log10 clearance |
| In vivo clearance | Lower log10 clearance |
| Plasma protein binding | Lower logK = log10((1−fu)/fu), hence higher unbound fraction |
| Cellular clearance | Lower log10 clearance |
| A→B permeability | Higher log10 A→B permeability |
| Efflux ratio | Lower log10 B→A/A→B efflux ratio, following the curated direction annotation |

Efflux follows curated row annotations. Protein binding uses the existing log binding-odds transform. The combined PDF contains a summary and two chart pages per endpoint; individual endpoint PDFs are also provided.
