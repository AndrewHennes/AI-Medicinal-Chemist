# Purchases to reach top-ranked compounds

[All endpoint charts](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/five_fold_acquisition_comparison.pdf) contain only purchases to reach any top-1, top-2, top-3 or top-4 compound. Lower is better. Each of the 2,798 pools is held out exactly once across five source-group folds. The comparison includes 13 methods, with the same four initial-hit draws per pool.

## Definition and weighting

The initial hit is free and counts as zero purchases if it already qualifies. Every molecule tied at the kth-best value qualifies. If a pool has fewer than k molecules, every molecule qualifies. This makes top-4 automatically zero for pools with three or four molecules. These trivial tasks are included in the primary curves; the supporting CSV contains the same counts restricted to nontrivial cases.

Random is its exact expectation for the same starting hit. If the hit does not qualify and g acceptable molecules remain in a pool of n molecules, its expected purchase count is n/(g+1). Starts are averaged within each seed and pool, then seeds, then pools within each endpoint. Overall means give equal weight to all five endpoints. Overall curve points missing an endpoint are omitted. Hollow markers indicate fewer than five source groups in a contributing endpoint.

## New delta + expected improvement baseline

The single-task and multitask delta predictors are the existing outer-fold, validation-selected checkpoints. No predictor was retrained, and no sign-consistency constraint was introduced. Each baseline uses every unique molecule from its predictor’s delta-training partition. The single-task reference set contains its endpoint’s training molecules; the multitask reference set contains training molecules from all five endpoints. Both predictions use the query endpoint’s output head. Validation and test molecules are excluded. No training-anchor outcome labels enter acquisition.

For candidate $q$, currently best measured molecule $b$, and training anchor $a$, form $d_a(q,b)=\widehat{\Delta}(q,a)-\widehat{\Delta}(b,a)$. Compute $\mu_q=\operatorname{mean}_a d_a(q,b)$ and $\sigma_q=\operatorname{SD}_a d_a(q,b)$, using sample standard deviation and zero for a singleton. The two predictions share the same anchor before subtraction, removing its common offset. This preserves the current series’ relative scale.

For the lower-is-better objective, $\mathrm{EI}(q)=(-\mu_q)\Phi(-\mu_q/\sigma_q)+\sigma_q\phi(-\mu_q/\sigma_q)$. If $\sigma_q=0$, use $\max(-\mu_q,0)$. Stable log-EI is used for numerical ranking. Only purchased outcomes identify the current best molecule; the full purchase order is generated before scoring any target rank. The incumbent updates after each purchase.

The baseline approximates anchor disagreement with a normal distribution. Its reference changes when the best measured compound changes. The [BoTorch analytic acquisition documentation](https://botorch.org/docs/v0.16.0/acquisition) describes the normal expected-improvement formula.

## Mean purchases for pools with at least 3 molecules

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | ---: | ---: | ---: | ---: |
| Revised multitask NAP | 2.920 | 1.908 | 1.173 | 0.817 |
| Revised single-task NAP | 2.832 | 1.859 | 1.155 | 0.804 |
| Multitask NAP + private adaptation | 2.901 | 1.897 | 1.165 | 0.807 |
| Multitask supervised warm start | 2.912 | 1.887 | 1.157 | 0.807 |
| Original single-task NAP | 2.996 | 2.041 | 1.295 | 0.912 |
| Original multitask NAP | 3.245 | 2.202 | 1.432 | 1.008 |
| Single-task GP + EI | 2.933 | 1.980 | 1.250 | 0.890 |
| Multitask GP + EI | 3.017 | 2.018 | 1.289 | 0.921 |
| Single-task delta greedy | 2.869 | 1.956 | 1.217 | 0.837 |
| Multitask delta greedy | 2.922 | 1.952 | 1.215 | 0.835 |
| Single-task delta + EI (training anchors) | 2.984 | 2.002 | 1.228 | 0.842 |
| Multitask delta + EI (training anchors) | 3.016 | 1.997 | 1.219 | 0.832 |
| Random expectation | 3.539 | 2.346 | 1.492 | 1.049 |

## Mean purchases for pools with at least 15 molecules

| Method | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | ---: | ---: | ---: | ---: |
| Revised multitask NAP | 7.972 | 4.934 | 3.708 | 3.081 |
| Revised single-task NAP | 7.609 | 4.514 | 3.481 | 2.805 |
| Multitask NAP + private adaptation | 7.824 | 4.817 | 3.605 | 2.984 |
| Multitask supervised warm start | 7.897 | 4.827 | 3.563 | 2.987 |
| Original single-task NAP | 8.243 | 5.738 | 4.462 | 3.571 |
| Original multitask NAP | 9.997 | 6.932 | 5.400 | 4.399 |
| Single-task GP + EI | 7.577 | 5.067 | 4.023 | 3.364 |
| Multitask GP + EI | 8.067 | 5.216 | 4.223 | 3.562 |
| Single-task delta greedy | 8.059 | 5.312 | 3.979 | 3.114 |
| Multitask delta greedy | 8.118 | 5.163 | 4.127 | 3.222 |
| Single-task delta + EI (training anchors) | 8.836 | 5.716 | 4.177 | 3.281 |
| Multitask delta + EI (training anchors) | 8.786 | 5.596 | 4.273 | 3.356 |
| Random expectation | 10.786 | 7.103 | 5.447 | 4.397 |

## Comparison against the matching GP + EI

Values below are delta + EI minus GP + EI in mean purchases, with nominal 95% source-group bootstrap intervals. Negative values favor delta + EI.

| Pools | Delta model | Target | Purchase difference [95% interval] |
| --- | --- | --- | ---: |
| ≥3 | Single-task | Top-1 | +0.050 [-0.089, +0.179] |
| ≥3 | Single-task | Top-2 | +0.022 [-0.074, +0.122] |
| ≥3 | Single-task | Top-3 | -0.022 [-0.094, +0.045] |
| ≥3 | Single-task | Top-4 | -0.048 [-0.107, +0.006] |
| ≥3 | Multitask | Top-1 | -0.001 [-0.142, +0.151] |
| ≥3 | Multitask | Top-2 | -0.021 [-0.119, +0.092] |
| ≥3 | Multitask | Top-3 | -0.070 [-0.143, +0.003] |
| ≥3 | Multitask | Top-4 | -0.089 [-0.146, -0.031] |
| ≥15 | Single-task | Top-1 | +1.259 [+0.085, +2.470] |
| ≥15 | Single-task | Top-2 | +0.649 [-0.160, +1.529] |
| ≥15 | Single-task | Top-3 | +0.155 [-0.365, +0.701] |
| ≥15 | Single-task | Top-4 | -0.083 [-0.496, +0.343] |
| ≥15 | Multitask | Top-1 | +0.720 [-0.677, +2.055] |
| ≥15 | Multitask | Top-2 | +0.380 [-0.512, +1.313] |
| ≥15 | Multitask | Top-3 | +0.049 [-0.632, +0.696] |
| ≥15 | Multitask | Top-4 | -0.207 [-0.746, +0.305] |

## Files and limits

[Numerical size curves and coverage](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/topk_performance_by_pool_size.csv), [paired baseline comparisons](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/paired_baseline_purchase_counts.csv), and [per-fold count summaries](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/topk_per_fold_counts.csv).

Individual endpoint PDFs contain the same four count metrics. Policy rewards and validation checkpoint selection follow the original training protocol.

- [In vivo clearance](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/in_vivo_clearance.pdf)
- [Plasma protein binding](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/protein_binding.pdf)
- [Cellular clearance](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/cellular_clearance.pdf)
- [A→B cell permeability](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/permeability.pdf)
- [Efflux ratio](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/efflux.pdf)
