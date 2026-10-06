# Corrected New NAP results

All other New NAP feature paths are retained. Only the GP-EI branch is replaced with its mean, standard deviation and incumbent inputs. Species-specific heads are retained. The earlier three-input-only run is excluded.

| Endpoint, pools ≥15 | Original New NAP | Corrected species NAP | Change [95% interval] |
| --- | ---: | ---: | --- |
| Microsomal clearance | 5.40 | 5.43 | +0.03 [-0.57, +0.56] |
| In vivo clearance | 9.60 | 8.17 | -1.43 [-3.70, +1.14] |
| Protein binding | 6.72 | 6.80 | +0.08 [-0.88, +1.41] |
| Cellular clearance | 6.50 | 6.41 | -0.09 [-1.03, +0.72] |
| Permeability | 8.13 | 9.73 | +1.60 [+0.28, +2.99] |
| Efflux ratio | 6.86 | 7.14 | +0.29 [-0.95, +1.58] |

Lower is better. Paired intervals are conditional on fitted models and unadjusted for multiple comparisons. This comparison changes species handling and the EI branch together.

[Full results PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_nap_ei_inputs/reports/species_nap_ei_inputs.pdf) · [Four-page summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_nap_ei_inputs/reports/results_summary.pdf) · [All cutoff data](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_nap_ei_inputs/reports/performance_by_cutoff_and_species.csv) · [Paired differences](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_nap_ei_inputs/reports/paired_differences.csv)

# Species heads and EI-input replacement

All six endpoints use the existing five grouped folds, four matched worst-half starts and three policy seeds. Species heads and the GP-EI branch are changed; all other New NAP signals are retained. Models share across species within each endpoint; human, rat, mouse and dog are routed separately where present.

Only the GP-EI branch is replaced by a learned function of GP mean, GP standard deviation and best observed relative outcome. The GP is fitted on acquisition-training labels, with group-excluded teachers for policy-training states. Species heads are zero-initialized residuals around shared predictions, allowing a shared fallback when a species is absent from training. MiniMol-based neural forecasts, delta summaries, neural EI, GP information and pool context remain available. No precomputed Gaussian EI enters the revised controller.

Pools, labels, transforms, role splits, and outcome scales are fixed. Training samples pools uniformly at the existing per-endpoint budgets. Paired intervals resample source groups conditional on fitted models and without multiplicity adjustment. This comparison changes species conditioning and the acquisition feature branch together.

## Top-1 purchases for pools ≥3

| Endpoint | Random | Pooled delta greedy | Species delta greedy | Pooled GP + EI | Species GP + EI | Pooled Old NAP | Species Old NAP | Original New NAP | Species NAP with EI inputs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 3.526 | 2.719 | 2.680 | 2.698 | 2.907 | 2.753 | 2.758 | 2.598 | 2.604 |
| In vivo clearance | 2.745 | 2.615 | 2.613 | 2.626 | 2.598 | 2.543 | 2.611 | 2.593 | 2.565 |
| Protein binding | 2.981 | 2.202 | 2.195 | 2.432 | 2.619 | 2.290 | 2.277 | 2.260 | 2.258 |
| Cellular clearance | 3.576 | 2.895 | 2.822 | 2.950 | 3.010 | 3.031 | 2.954 | 2.778 | 2.814 |
| A→B permeability | 4.266 | 3.494 | 3.625 | 3.354 | 3.578 | 3.561 | 3.429 | 3.325 | 3.564 |
| Efflux ratio | 4.125 | 3.147 | 3.120 | 3.272 | 3.520 | 3.563 | 3.606 | 3.148 | 3.249 |

## Top-1 purchases for pools ≥15

| Endpoint | Random | Pooled delta greedy | Species delta greedy | Pooled GP + EI | Species GP + EI | Pooled Old NAP | Species Old NAP | Original New NAP | Species NAP with EI inputs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 8.621 | 5.695 | 5.660 | 5.835 | 6.306 | 6.111 | 6.135 | 5.400 | 5.427 |
| In vivo clearance | 10.650 | 9.762 | 9.588 | 9.375 | 8.113 | 8.838 | 10.338 | 9.600 | 8.167 |
| Protein binding | 12.205 | 6.909 | 6.585 | 7.716 | 9.040 | 7.438 | 7.028 | 6.716 | 6.795 |
| Cellular clearance | 9.453 | 6.826 | 6.294 | 6.997 | 6.994 | 7.301 | 6.851 | 6.500 | 6.407 |
| A→B permeability | 11.921 | 9.802 | 10.510 | 7.465 | 8.552 | 9.122 | 8.569 | 8.127 | 9.728 |
| Efflux ratio | 9.694 | 7.116 | 6.787 | 6.394 | 7.681 | 8.523 | 8.705 | 6.858 | 7.144 |

## Paired interpretation

The accompanying paired_differences.csv reports each new model minus its historical comparator for every endpoint/species, top-k target and pool cutoff. Negative values favor the new model. Species absent from the corresponding training role are flagged in test_species_coverage.csv. No model or recipe is selected using these results.
