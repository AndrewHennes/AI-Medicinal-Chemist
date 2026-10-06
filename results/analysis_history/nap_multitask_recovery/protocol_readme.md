# Multitask NAP recovery

This project extends the preceding acquisition experiments without modifying their data or checkpoints. The task is to minimize additional purchases until an optimum is first encountered. Model inputs never include an unrevealed outcome or an optimum-found flag.

The current experiment narrative is in [report.md](report.md). The complete development ledger is in `experiment_ledger.csv`, and each candidate directory retains its configuration, checkpoints, training log, and full validation purchase orders.

## Running from any directory

The interpreter and all data/output locations are absolute. No command-line options are required.

Run the implementation checks with:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_recovery/test_recovery.py
```

Refresh the validation summary with:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_recovery/validation_summary.py
```

Refresh the report and figures with:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_recovery/report_recovery.py
```

`train.train(variant, seed, endpoint)` is the Python entry point for a candidate. It skips completed runs and restarts incomplete runs. Shared models use `endpoint=None`; single-task controls use an endpoint name. Candidate settings are defined in `architectures.py`. Prediction and PPO budgets are matched per endpoint, with special handling documented for reused shared pretraining.

## Separation of development and evaluation

`common.load_data()` defaults to acquisition training and validation only. Candidate training does not load acquisition-test pools. A `selection_lock.json` containing checkpoint hashes is required by the final evaluation scripts. Selection is based on validation; final test output must not be used to revise that locked choice.

`final_evaluation.py` evaluates individual policies. `ensemble_evaluation.py` evaluates every multiset of three trained ensemble members, enabling paired bootstrap resampling of source groups and member seeds while recomputing actual purchase sequences. Ordinary averages of three individual hitting times are not treated as an ensemble policy.

This recovery round uses the existing acquisition-test cohort. Fitting and architecture selection use the development partitions.
