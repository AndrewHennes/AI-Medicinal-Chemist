# Continued NAP development

Read [report.md](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/report.md) for results from both evaluation cohorts.

`run_followup.py` reproduces the follow-up with no command-line options. It uses the absolute interpreter and output paths in the script and runs correctly from another working directory. Completed training fits are reused. It requires the existing `multitask_acquisition` data/model artifacts and `nap_multitask_recovery` prediction checkpoints. It does not rebuild those earlier datasets or Minimol representations.

All results remain beneath `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs`.

The main files are

- `teachers.py` for source-group cross-fitting of Gaussian-process and neural forecasters
- `architectures.py` for the frozen-forecaster acquisition controllers
- `train.py` for supervised warm starts and proximal policy optimization
- `exploratory_evaluation_plan.json` for the comparison fixed before the repeated fits finished
- `exploratory_checkpoint_lock.json` for the evaluated checkpoint hashes
- `evaluate_followup.py` for matched evaluation and paired source-group/controller-seed intervals
- `report_followup.py` for the consolidated report, tables, and figures
- `verification.json` for final source, checkpoint, split, and trajectory checks

The private-policy adaptation variant is in `nap_multitask_private_gate`. Although its checkpoint directories begin with `single_` to indicate separate policy fitting, its forecasters and initial controller were trained jointly across endpoints. `shared_forecasters: true` and the associated source checkpoint record this explicitly. The matched single-task control remains in this directory under `candidates/warm_crossfit_mixture/single_*`.

The compact controller is a GP-conditioned neural acquisition policy. The neural forecaster, Gaussian process, and delta predictor are frozen during its reinforcement-learning stage. Seeds 11, 29, and 47 repeat controller training only. Confidence intervals are conditional on those fixed forecasting artifacts.

Additional screens are preserved in `nap_multitask_mixture`, `nap_multitask_delta_gp`, `nap_multitask_ordinal`, and `nap_selection_prior`. The delta-mean GP screen covers a predictor/acquisition baseline.

The validation pilot in `nap_multitask_expert_distribution` contains six controllers that mix sharper expert action distributions.

`evaluate_reserved_original.py` replays the original single-task comparator from its locked checkpoints. `restore_reserved_baseline.py` reconciles that baseline with the earlier ensemble cache. Candidate predictions are unchanged.
