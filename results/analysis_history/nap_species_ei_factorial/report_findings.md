# Separating species heads from EI replacement

Mean additional purchases for pools ≥15, with equal endpoint weights. Lower is better.

| Model | Top-1 | Top-2 | Top-3 | Top-4 |
| --- | ---: | ---: | ---: | ---: |
| Original NAP | 7.200 | 4.339 | 3.332 | 2.716 |
| Species heads only | 7.262 | 4.634 | 3.526 | 2.815 |
| EI inputs only | 7.487 | 4.648 | 3.471 | 2.785 |
| Both changes | 7.278 | 4.726 | 3.550 | 2.887 |

| Effect on top-1 purchases, pools ≥15 | Difference [95% interval] |
| --- | --- |
| Species heads with analytic EI | +0.06 [-0.43, +0.53] |
| Species heads with learned EI inputs | -0.21 [-0.61, +0.22] |
| EI replacement with pooled predictors | +0.29 [-0.11, +0.70] |
| EI replacement with species heads | +0.02 [-0.40, +0.47] |
| Interaction | -0.27 [-0.63, +0.11] |
| Both changes versus original | +0.08 [-0.49, +0.69] |

Intervals resample source groups with all four cells paired, conditional on trained models and without multiplicity adjustment. The species factor includes the prediction and policy pipeline.

[Full PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_species_ei_factorial/reports/nap_factorial_results.pdf) · [Summary PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_species_ei_factorial/reports/results_summary.pdf) · [All factorial effects](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_species_ei_factorial/reports/factorial_effects.csv) · [Cutoff results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_species_ei_factorial/reports/performance_by_cutoff_and_species.csv)
