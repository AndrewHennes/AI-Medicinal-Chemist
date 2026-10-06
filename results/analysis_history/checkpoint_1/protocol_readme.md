# checkpoint_1

This preserves the current model before the multi-reference baseline experiment.
Its baseline predicts the query's delta relative to the original initial hit.
The final mean adds the gated iterative residual correction and neural offset.
The variance uses option 2, a scaled conditional kernel variance plus positive
neural extra variance. Three independently seeded members form a predictive mixture.

The directory contains 90 fitted members across six endpoints and five folds,
their configurations, validation calibration, copied prepared datasets and PCA
transforms, and both original and runnable copies of the Python sources.
`manifest.json` has SHA256 checksums. The runnable source changes only the absolute
workspace prefix so imports use the frozen snapshot. The original experiment is
not modified. This snapshot is about 1.2 GB and uses copies rather than symlinks.

All commands below work from any working directory.

To run a small inference example:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/checkpoint_1/inference.py
```

For new compounds, import `predict` from the absolute `inference.py` path. Supply
512-dimensional MiniMol vectors and only the observed transformed property values.
Values must follow the saved endpoint's log/logK and minimization convention.
The interface applies the saved training-only PCA and target scaling and returns
mean deltas relative to the initial hit, standard deviations, and mixture components.
The fold selects one three-member ensemble. It does not average across folds.

To continue training all saved members with the original architecture:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/checkpoint_1/train.py
```

This uses CPU, eight workers, 1200 additional updates and validation-only checkpoint
selection. Edit the constants in `train.py` if needed. Results go into the absolute
`checkpoint_1/runs/continued_training` directory and never replace the frozen
weights. `runtime.train_member` also supports fresh initialization when a job has
no `parent`. Continued training does not overwrite the original calibration;
new fitted ensembles require validation calibration before interpreting uncertainty.

The exact preceding experiment's sources and recipe are retained under
`original_source/outputs/kernel_variance_option2`. `train.py` is the supported
entry point for training this frozen architecture; historical source scripts are
archived for provenance and may refer to artifacts from earlier experiments.
The Python environment remains the shared workspace environment, with versions
recorded in `environment.json`.
