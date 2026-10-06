## Environment

The scripts can run directly with the existing analysis environment. Its captured versions are in `results/published/documentation_environment.json`. For a separate environment, install this repository in editable mode with the chosen Python interpreter. Keep the interpreter and repository paths absolute.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python -m pip install --no-deps -e /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization
```

The command above uses already installed scientific dependencies. On another machine, install the dependencies declared in `pyproject.toml` and update `config/paths.json`. CPU is the validated execution mode; this package does not silently change the numerical recipe to use GPU-specific kernels.

The entrypoint scripts themselves do not need an editable install. They locate `src` from their own absolute file path. Editable installation is useful for importing the API in notebooks or other Python code. Configuration and result assets live in the source tree, so a standalone wheel without those assets is not the supported distribution route.

## Existing checkpoints

`scripts/predict_example.py` loads the selected original reference ensemble and a held-out microsomal series. It uses five measured compounds to predict a fixed set of remaining molecules, writes a small JSON example into the new artifact root, and selects the next compound with EI. It reads the original data and checkpoint files but never edits them.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/predict_example.py
```

For your own measured context, construct `predictor` with absolute checkpoint and feature-file paths. The three checkpoint files must belong to the same selected endpoint/fold. The target scale is fitted from that fold's training labels. `features.npz` must belong to the same fold. `configuration` is normally omitted, except for the fine-tuning control that intentionally loads transfer weights with its selected adaptation rule.

```python
from pathlib import Path as path_type
import numpy as np
from hit_to_lead.inference import predictor

benchmark = path_type('/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark')
features = path_type('/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/repository_benchmark/data/fold_0/features.npz')
checkpoints = [benchmark / 'runs/fold_0/microsomal_clearance/reference/final' / f'seed_{seed}/best.pt'
               for seed in (11, 29, 47)]

# Obtain this scale from the same endpoint/fold's training data.
from hit_to_lead.data import series_dataset
scale = series_dataset(0, 'microsomal_clearance').scale
predictor = predictor(checkpoints, features, scale)

# The first measured molecule is the designated initial hit.
posterior = predictor.predict(measured_embeddings, measured_log_clearance, query_embeddings)
index, log_ei_scores = predictor.select_next(
    measured_embeddings, measured_log_clearance, query_embeddings)
```

The example's three arrays are application-provided variables, not paths to bundled private data. Returned means, standard deviations, and intervals are in transformed assay units relative to the observed first hit. Add the first measured transformed value if an absolute transformed mean is needed. Do not exponentiate a standard deviation as though it were a measurement. No hidden query outcomes are passed to the API.

For inference in already projected and standardized coordinates, use `models.build` or `training.load`, construct a `measured_context`, and call `model.predict(context, queries)`. That lower-level API returns a marginal mixture representation whose `moments`, `log_prob`, and `interval` methods expose the distribution. `torch.no_grad()` is supported even for models with inner adaptation because their implementation explicitly enables the required local gradients.

## Training and reporting

`config/benchmark.json` specifies endpoint, method, fold, seed, and update budgets. Defaults match the completed main study. Fine-tuning depends on transfer; the no-offset ablation depends on ALPaCA. The runner enforces those dependencies and writes fitting, recovery, and evaluation records separately.

Use a new `artifacts_root` when changing configuration, data, or implementation. Matching interrupted runs resume from optimizer and random-number states. The file lock prevents two runners from writing the same run simultaneously. Numerical failures are recorded; a failed test condition is not replaced by a model selected using the test outcome.

To regenerate reports for a newly completed run without fitting again,

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/report_run.py
```

`scripts/make_figures.py` instead regenerates the repository's historical published figures from the included summary tables. The two operations have separate input and output locations.

## Verification

`scripts/run_tests.py` uses only synthetic data. It checks Bayesian conditioning, marginal mixture calculations, implicit and second-order gradients, context order, query isolation, random acquisition with ties, coverage handling, and exact interrupted-run recovery.

`docs/migration_verification.json` records implementation comparisons. `docs/checkpoint_verification.json` records saved-checkpoint compatibility across available model families and endpoints. Original source hashes are in `docs/source_provenance.json`.
