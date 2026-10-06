# From-scratch architecture comparison

All task-specific models are newly initialized. Training does not load historical
predictor weights. The existing MiniMol representations, training-only PCA,
linked-group splits and architecture configurations are retained.

The main report compares the GP, original neural architecture, average mean only,
average-reference covariance only, both changes, and RBF-softmax weighted averaging.
There are five folds, six endpoints, three seeds and three weighting temperatures.
The 720 fresh fits include three new GP members per fold and endpoint. Single-seed
GP results are also reported for comparison with the older table convention.

Each fit runs at least 4,000 and at most 16,000 updates with validation-based
learning-rate reduction and stopping. Every run records its initial-state hash,
training history, stop reason and final-state hash. Partial runs can resume only
from this experiment's own optimizer/model/RNG checkpoints.

Validation selects the lowest-NLL checkpoint, including initialization. All jobs
still execute at least 4,000 updates; selection of initialization is counted
explicitly in the report. Architecture hyperparameters are retained from the
earlier experiments rather than retuned in this run.

Run or resume from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/from_scratch_mean_kernel/run_experiment.py
```

Numerical and initialization checks:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/from_scratch_mean_kernel/test_scratch.py
```

The run is CPU-only. Model checkpoints, validation choices, test predictions and
reports are saved here. The final PDF is
reports/from_scratch_architecture_comparison.pdf. Earlier fine-tuning artifacts
and checkpoint_1 are preserved.
