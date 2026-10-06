# Five-way mean and covariance benchmark

Compares the established GP, unchanged neural architecture, average mean only,
measured-set-centered kernel only, and both mean and kernel changes. The mean-only
model is the prior version with leave-one-out residuals. `checkpoint_1` stays intact.

The kernel-change arms consistently center outcomes, baseline means, covariance
and measurement noise. They restore the observed context mean when reporting on
the initial-hit scale. Therefore the kernel factor includes the coordinate/noise
changes required by centering, rather than an isolated covariance-array swap.

The unchanged and mean-only models reuse their existing matched1200-update fits.
The two kernel conditions get the same initial weights, episodes and update budget.
All five linked-group folds, six endpoints and three neural ensemble seeds are used.
GP retains the established frozen seed11 model and its validation calibration.

Run or resume, from any working directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/centered_kernel_factorial/benchmark_factorial.py
```

Run the centering and inference checks:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/centered_kernel_factorial/tests_factorial.py
```

Everything runs on CPU. This directory contains source, fitted models, validation
choices, locked inputs, evaluation predictions, and the report. The primary report
is `reports/five_way_mean_kernel_report.pdf`, with endpoint charts and CSV tables.
`protocol.json` records the exact definitions and exploratory limitations.
