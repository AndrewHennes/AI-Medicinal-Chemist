# Joint endpoint models and matched controls

This experiment trains a multitask delta predictor, a multitask Gaussian process with expected improvement, and a task-conditioned Neural Acquisition Process across the five previously curated endpoints. Five independent endpoint controls are retrained on a new global split. Random is evaluated exactly. The [report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/report.md) contains acquisition and predictor metrics, paired intervals, and size-cutoff plots.

All paths are absolute, all products stay in this workspace, and configuration is in `settings.py`. There are no command-line options. The CPU run works from any directory with the existing environment:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/run_experiments.py
```

Completed runs are preserved. A stage with a completion marker is skipped; an interrupted stage restarts from its configured seed rather than resuming optimizer state. For a new experiment or changed configuration, set `PROJECT` to a new absolute directory before running. The prepared dataset is reused when present, so changes to splitting or source preparation require a new project directory. Do not manually alter completion markers to mix settings.

Run the behavioral checks independently:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/test_experiment.py
```

Regenerate the report from saved results:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/report.py
```

Audit the completed results:

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/verify_completed.py
```

The runner records library versions in `environment.json`. It uses the dependencies already installed for the prior analysis, listed in `requirements.txt`.

The task identifier denotes endpoint; species remain separate pools. Initial-hit relative outcomes, log transformations, endpoint preferences, curation, and absence of sign consistency are preserved. The global split keeps linked molecules and source documents together across all endpoints. The new single-task controls, not the earlier independent-split results, provide the matched transfer comparison.

Task sampling is balanced and per-endpoint update budgets match the independent controls. Shared models therefore train for five times as many total steps as one control, equal to the sum of the five controls. GP training can include other endpoints from the same species/provenance group, up to 32 total points. NAP comparisons include the change in its frozen delta features as well as the shared policy.

The legacy `validation_tau` field in training logs and checkpoint metadata contains the endpoint-balanced ratio of mean purchases to the random expectation. It is a checkpoint-selection score, not an unnormalized purchase count. Test tables use actual additional purchase counts.

Primary results use pools with at least 15 molecules. Bootstrap intervals resample source groups conditional on fitted models and the selected split. The report also includes all-pool results, unique-optimum sensitivity, and NAP seed variation.
