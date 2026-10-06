# Equal-weight multi-reference baseline

For each query, replace the first-hit-only baseline by the arithmetic mean of
`observed_delta_to_hit(anchor) + predicted_delta(query, anchor)` across every
measured anchor, including the first hit. The offset is necessary before averaging.

This is an isolated query-baseline change. First-hit context representations and
local residuals, the iterative correction, and option-2 variance are retained.
Joint fine-tuning allows their weights to adjust. No independent-anchor variance
reduction, new sign-consistency penalty, centered-reference kernel, or extra
correction model is introduced.

Four comparisons use the same existing five folds and fixed hidden query panels:
the frozen checkpoint, inference-only averaging, original-model continuation,
and average-model continuation. The continued models receive identical training
episodes and 1200 updates, with validation-only checkpoint selection. Evaluation
focuses on R², within-series Spearman rho and raw/calibrated mixture NLL.

Run or resume from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_reference_mean/benchmark.py
```

Outputs, fitted weights, reports, and progress are written to this absolute
experiment directory. The saved original architecture is in
`/Users/asselism/Documents/Codex/2026-09-23/i-h/checkpoint_1`.

The targeted follow-up also recomputes each measured compound's residual against
the averaged predictor. It leaves that compound's own measurement out of its
baseline and retains the existing correction and variance architecture.

To run or resume that follow-up and its combined report:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_reference_mean/consistent_benchmark.py
```

The combined PDF, including the earlier comparisons, is written to the absolute
path `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_reference_mean/consistent_residuals/reports/multi_reference_mean_report.pdf`.
