# Simple kernel-softmax weighting

This experiment adds RBF-softmax weighting to the current multi-reference mean.
The existing centered covariance and uncertainty calculation are retained.

Three fixed temperatures (0.1, 0.3, 1.0) are selected by validation ensemble NLL.
All five folds, six endpoints and three seeds are included. Weighted candidates
start from checkpoint_1 and use the same 1200-update training streams as the
previous combined mean/kernel control. The control and GP results are reused.

Run or resume from any working directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/kernel_weighted_mean/benchmark_weighted.py
```

Numerical checks:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/kernel_weighted_mean/test_weighted.py
```

No GPU is required. Source, models, choices, predictions, reports and input hashes
are saved in this directory. Prior results and checkpoint_1 are left intact.

See protocol.json for the exact coordinate transformations, selection rules and
exploratory limitations. The PDF is reports/kernel_softmax_weighting_report.pdf.
