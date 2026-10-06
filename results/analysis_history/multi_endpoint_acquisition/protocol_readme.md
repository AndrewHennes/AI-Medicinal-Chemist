# Five independent acquisition experiments

The [results report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/report.md) compares random, delta-greedy, Gaussian-process expected improvement, and NAP with frozen delta features on five supplied endpoint datasets. The primary reporting population has at least 15 retained molecules per pool. No sign consistency is enforced. Endpoints are modeled on log10 scales, with the bound/free logK transformation for protein binding.

Configuration is in `settings.py`, with absolute source and output paths and no command-line options. Products are written into this workspace. Training uses the CPU and requires no GPU.

Run the completed experiments or resume unfinished endpoints from any directory:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/run_experiments.py
```

Completed endpoints are preserved. For a fresh run with changed training settings, set `PROJECT` to a new absolute directory inside this workspace. The runner checks final training-log events for the delta and Gaussian-process stages and the final policy checkpoint for NAP. An interrupted stage restarts its training budget from its configured seed; this does not resume optimizer state. If endpoint definitions or input data change, use a new project directory so cached labels and predictions cannot be reused accidentally.

Behavioral checks:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/test_experiment.py
```

Regenerate reports and figures from completed endpoint results:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/report_all.py
```

The source tables are read only. Endpoint-specific exclusions, binding-percent repairs, data splits, and assay selection are saved beside each prepared dataset.

`verify_completed.py` verifies original-file hashes, completed training budgets, matched test starts, exact random expectations, complete purchase trajectories, and consistency between frozen delta checkpoints and their cached predictions. Its result is saved in `verification.json`.
