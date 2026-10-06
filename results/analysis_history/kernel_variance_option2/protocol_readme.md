# Kernel-informed uncertainty, option 2

All results and source code live under `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/kernel_variance_option2`.

The experiment preserves the refined residual model's mean architecture and changes its uncertainty to `variance = positive_neural_multiplier * conditional_kernel_variance + positive_extra_neural_variance`. The kernel is anchored to the initial hit. A differentiable Cholesky solve computes conditional kernel variance. Student-t variance is converted correctly into the distribution's scale. Three independently seeded members form an equal-weight predictive mixture.

The finite iterative mean update is unchanged, but computing exact conditional variance raises the per-pass cost to O(n^3 + P n^2 + T n^2), with n currently measured context molecules, P queries, and T fixed mean-update steps. Historical training examples are not involved in the inference solve.

The experiment uses the existing six endpoints and five linked-group folds. Both option 2 and its continued-training control start from the corresponding existing refined checkpoint and receive identical new episodes and 1,200 additional updates. Hyperparameters are inherited. Checkpoint selection includes the initialization. Validation data select checkpoints and ensemble scale calibration. Standard mixture expected improvement is used with K=1, without an extra acquisition-temperature search. Evaluation includes all pools of at least 3 compounds and emphasizes pools of at least 15.

Files:

- `model.py` implements the new variance branch and checkpoint transfer.
- `benchmark.py` runs paired training, validation calibration, locked evaluation, and the report. It is resumable and CPU-only.
- `tests.py` checks exact conditioning, gradients, monotonic kernel variance, Student-t scale, masking, order invariance, hidden-label isolation, and mean transfer.
- `make_report.py` audits stored trajectories and generates paired confidence intervals, endpoint charts, CSV files, and the PDF.
- `architecture_diagram.py` generates editable SVG, PDF, and PNG diagrams.
- `reports/results.md` and `reports/kernel_variance_option2_report.pdf` contain the results and limitations.

To reproduce or resume from any working directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/kernel_variance_option2/benchmark.py
```

To rerun the numerical checks:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/kernel_variance_option2/tests.py
```
