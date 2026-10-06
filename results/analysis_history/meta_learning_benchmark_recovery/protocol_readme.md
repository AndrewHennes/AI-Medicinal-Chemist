# Recovery of the first full benchmark

The recovery runner preserves the original model, data, training and evaluation source files and their hashes. It adds numerical-failure handling around the existing training functions. A failure rejects the entire hyperparameter configuration. Search settings are selected using seed-11 validation NLL and must complete all three final member fits. Rejected artifacts are retained, and the next predeclared setting is considered when necessary. Fine-tuning settings also require finite validation predictions from all three transfer members.

Eligibility uses training and validation results. A test-time failure is recorded with the selected setting held fixed. Reports include endpoint/method comparisons when all five folds complete and list remaining conditions in the coverage file.

Start or resume recovery from any working directory with

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/recovery/run_recovery.py
```

The original runner remains unchanged for provenance. Use this recovery entrypoint for the ongoing run. Progress remains in the main benchmark directory. Model-level recovery states and failure explanations are stored in this directory and beside the affected fit artifacts.
