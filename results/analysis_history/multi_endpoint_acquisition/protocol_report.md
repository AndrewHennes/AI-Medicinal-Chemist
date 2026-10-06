# Five-endpoint acquisition comparison

Five independent CPU experiments compare exact random-search expectations, greedy selection from a frozen pairwise delta predictor, a reference-relative Gaussian process with expected improvement (GP-EI), and a compact Neural Acquisition Process (NAP) adaptation with the frozen delta mean and standard deviation features. No microsomal checkpoint was reused. All three learned methods use full 512-dimensional Minimol representations, with training-only scaling and no principal-component projection.

## Primary results on pools with at least 15 molecules

Entries are mean additional purchases to the first recorded optimum. Lower is better. Pools have equal weight after averaging four starting draws and three NAP training seeds. Endpoint reports provide group-bootstrap intervals and seed results.

| endpoint | pools | groups | Random | Delta greedy | GP + EI | NAP + delta features |
| --- | --- | --- | --- | --- | --- | --- |
| in_vivo_clearance | 4 | 4 | 8.500 | 6.000 | 6.188 | 5.625 |
| protein_binding | 7 | 7 | 12.286 | 10.571 | 11.464 | 11.476 |
| cellular_clearance | 11 | 7 | 11.394 | 8.045 | 7.159 | 9.000 |
| permeability | 14 | 11 | 11.238 | 8.554 | 10.107 | 10.810 |
| efflux | 9 | 8 | 9.389 | 8.389 | 6.833 | 10.500 |

## Delta-predictor performance on the same larger test pools

Errors are in the endpoint's transformed units, log10 for clearance, permeability, and efflux, and logK for protein binding. R-squared weights each pool equally. Ranking correlations compare candidates against a fixed anchor and average across anchors and pools. Negative R-squared means the model's squared error exceeds always predicting zero difference; a positive ranking correlation can still coexist with that numerical error.

| endpoint | pools | groups | rmse | zero_rmse | r2 | mean_fixed_anchor_rho |
| --- | --- | --- | --- | --- | --- | --- |
| in_vivo_clearance | 4 | 4 | 0.679 | 0.671 | -0.025 | 0.135 |
| protein_binding | 7 | 7 | 1.531 | 1.510 | -0.028 | 0.442 |
| cellular_clearance | 11 | 7 | 0.579 | 0.611 | 0.102 | 0.362 |
| permeability | 14 | 11 | 0.781 | 0.773 | -0.020 | 0.251 |
| efflux | 9 | 8 | 0.601 | 0.571 | -0.108 | 0.077 |

## All eligible pools

| endpoint | pools | groups | Random | Delta greedy | GP + EI | NAP + delta features |
| --- | --- | --- | --- | --- | --- | --- |
| in_vivo_clearance | 101 | 90 | 2.703 | 2.468 | 2.498 | 2.717 |
| protein_binding | 169 | 100 | 2.851 | 2.419 | 2.540 | 2.406 |
| cellular_clearance | 92 | 56 | 3.765 | 3.016 | 2.954 | 3.436 |
| permeability | 100 | 77 | 4.213 | 3.553 | 3.688 | 3.817 |
| efflux | 64 | 51 | 4.333 | 3.414 | 3.484 | 4.020 |

![Performance by cumulative minimum pool size](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/comparison.png)

## Endpoint definitions

| Endpoint | Transformation | Preferred direction |
|---|---|---|
| In vivo clearance | log10(clearance) | Lower |
| Cellular clearance | log10(clearance) | Lower |
| A→B permeability | log10(permeability) | Higher |
| Plasma protein binding | log10(PPB/(100−PPB)) = log10((1−fu)/fu) | Lower logK, hence higher fu |
| Efflux ratio | log10(B→A/A→B) using the supplied direction annotation | Lower |

The protein-binding column contains percent bound. The transformation is a pseudo binding constant derived from the bound/free ratio, not a molar dissociation constant. It follows the definition in Toma et al., *QSAR Development for Plasma Protein Binding: Influence of the Ionization State* ([paper](https://doi.org/10.1007/s11095-018-2561-8)). The optimization direction is highest unbound fraction, the stated default for this experiment, and is not a universal claim about desirable clinical protein binding.

The efflux analysis uses the supplied `BA_div_AB_efflux_ratio` row annotation and excludes explicit description conflicts. Efflux ratio is basolateral-to-apical over apical-to-basolateral permeability ([primary experimental paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2628205/)).

Human, rat, and mouse pools are used for clearance and protein binding. Permeability and efflux use human and dog-derived assay pools, primarily Caco-2 and MDCK systems. Species and assay systems remain separate search pools. Endpoints are trained independently; this is not multitask learning.

## Experimental design

Each pool contains at least three distinct retained molecules and nonconstant transformed labels. The initial molecule is uniformly sampled from the worse half, with random tie breaking. It is provided without a purchase cost. For maximization endpoints, the transformed objective is negated internally so that every method minimizes. Measurements are revealed only after purchase. All trajectories are generated to pool exhaustion with no oracle-success flag, then scored retrospectively by the first optimum. Random expectation is exact and accounts for tied optima and initially optimal hits.

Series linked by any shared standardized molecule or known source document remain in one group, including species variants. Groups are assigned to six disjoint subsets, aiming for half the pools in the delta-model allocation and half in the acquisition allocation. Within the full dataset, target fractions are 40% delta training, 5% delta validation, 5% delta test, 24% acquisition training, 6% acquisition validation, and 20% acquisition test. Group sizes prevent exact fractions. The seeded allocation is balanced using pool counts and the number of large pools only, without looking at endpoint values or model performance. All six subsets have disjoint molecules and provenance groups. Different endpoints are independently split because no parameters or labels are transferred across endpoints.

The plain delta predictor uses ordered concatenation and mean squared error, without sign consistency, reversed-pair averaging, or self-zero constraints. It fits only delta-training pools and is frozen before NAP training. At every state, each measured anchor produces a query estimate by adding its observed relative outcome to the predicted query-minus-anchor difference. Greedy delta chooses the lowest average estimate. NAP appends the mean and sample standard deviation of those estimates to each embedding; the standard deviation is zero for one anchor.

GP-EI learns a shared Matérn-5/2 reference-relative prior from acquisition-training pools. NAP learns supervised conditional prediction and then an acquisition policy with Proximal Policy Optimization on the same acquisition-training pools. Both use validation purchases to choose checkpoints. The NAP reward penalizes each purchase through the first optimum; it receives no reward or termination information during test selection. Existing CPU budgets are retained: 3,000 delta steps, 700 GP steps, 800 NAP prediction steps, and 500 policy iterations for each of three seeds.

Training-label allocation differs by pipeline. Delta-only fits one allocation, GP-EI fits the other, and augmented NAP uses its own allocation plus the frozen predictor from the first. All methods share held-out pools and starting draws.

Training pools are sampled uniformly, so smaller pools remain the majority of training episodes. Checkpoint selection prioritizes ≥15 validation pools only when at least five such pools across at least three groups exist. Otherwise the full validation set is used. Large-pool performance is always reported separately, even where large-only checkpoint selection is unsupported.

## Curation and limits

Within each series-species pair, the largest assay-compatible source group is selected by distinct molecule count, with a deterministic lexical tie break. Assay descriptions, original type/units, cell/tissue fields, and source distinguish groups. Repeated measurements are aggregated by median on the transformed objective scale. Explicit nonintravenous in vivo clearance records are excluded to avoid combining clearance with apparent clearance. A small number of protein-binding percent/fraction discrepancies are corrected only when original percent values and bound-endpoint metadata support that correction. Nonpositive log inputs and binding percentages at or outside 0–100 are excluded rather than clipped. Numeric ties remain tied optima.

![Unique-optimum sensitivity](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/comparison_unique_optima.png)

The nine behavioral checks verify transformations, objective direction, worse-half starts, hidden-label exclusion, reference invariance, mean/sample-standard-deviation aggregation, no sign constraint, random expectations, GP conditioning, and split disjointness. Complete evaluated trajectories are checked for valid purchases without repeats.

## Endpoint reports and artifacts

- [In vivo clearance](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/in_vivo_clearance/results/report.md)
- [Protein binding](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/protein_binding/results/report.md)
- [Cellular clearance](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/cellular_clearance/results/report.md)
- [A→B permeability](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/permeability/results/report.md)
- [Efflux ratio (B→A/A→B)](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/efflux/results/report.md)

Each endpoint directory contains prepared data, exclusions and repairs, split manifests, input scalers, frozen delta predictions, checkpoints, validation logs, test trajectories, predictor metrics, and acquisition summaries. The absolute-path runner and dependencies are documented in the neighboring README. Source CSV files are not modified.
