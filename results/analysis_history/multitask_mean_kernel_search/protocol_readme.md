# Multitask subset search for the average-mean / average-reference-kernel model

This experiment trains all 63 nonempty combinations of six assay endpoints.
All 15 pairs precede larger combinations. Both sharing designs are tested for
every multitask combination. Single-task controls are trained once because the
two designs are equivalent when only one task is trained. With five folds and
three seeds this gives 1,800 newly initialized fits.

The designs share either the pair encoder alone, or the pair encoder, measured
context encoder, and decoder hidden layer. Endpoint-specific delta heads,
output heads, distance scales, bandwidth, ridge, iterative step sizes and
likelihood parameters remain private. Species are pooled within endpoints as
in the preceding prediction benchmark. No sign-consistency loss is introduced.

Cross-endpoint connections through molecules, source documents, or existing
series groups define global components. Entire components stay in one outer
fold. Validation is a balanced component sample from the other four folds.
The former predictor/RL pool-role restriction is removed for this prediction
experiment. Matched single-task controls use exactly the same new splits,
representations, target scaling, architecture capacity and training schedule.
Consequently the previous benchmark's numbers are not the controls here.

MiniMol embeddings are fixed. A common PCA is fitted on unique training
molecules only. Its first 32 components are RMS-scaled. Per-endpoint target
normalization uses training-only within-series differences. Test query panels
remain fixed as 1, 2, 3, 5 and 10 measurements are revealed.

Endpoint values retain the preceding preprocessing: log10 clearance or efflux,
negative log10 permeability, and log10((1-fu)/fu) for protein binding, with fu
the unbound fraction. Lower modeled values are favorable for every endpoint.

Every included endpoint supplies 16 episodes per optimizer update. All fits
receive at least 4,000 updates, with validation-based stopping up to 16,000.
The validation-optimal trained checkpoint is saved independently for each
endpoint. Initialization is diagnostic only; early checkpoints at 25, 50 and
100 updates are evaluated before regular 250-update checks.

Subset and sharing choices use validation only, independently within each
outer fold and endpoint. Negative log-likelihood is the primary criterion;
separate choices optimize R² or within-series Spearman rho. The report compares
an exhaustive search, forward addition, pair-only selection, all-task training,
and matched single-task training. All candidate test scores are descriptive.

A predeclared sensitivity analysis selects partners using only validation pools
with at least 15 compounds. Its algorithm is SHA256-locked before test
predictions exist. This checks the effect of the validation population while
retaining the same training, checkpoints, candidate predictions and calibration.

Run or resume from any directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_mean_kernel_search/run_experiment.py
```

Numerical and split checks:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_mean_kernel_search/test_multitask.py
```

The active execution uses `train_multitask.py` and `finish_when_ready.py` in
separate processes to overlap validation with completed training tiers. Do not
start a duplicate run while those processes are active. All outputs remain in
this directory; earlier experiments are preserved.

`predict.py` provides a Python `Predictor` class for loading a selected fold
model and predicting means and standard deviations from new MiniMol vectors
and measured same-assay context. It applies the saved PCA, target scale and
validation calibration. It expects property values already transformed as
described above, not raw assay measurements.

Once evaluation completes, `reports/multitask_subset_comparison.pdf` contains
endpoint learning curves, pairwise transfer heatmaps, paired improvement
intervals, uncertainty tables, validation-preferred combinations, and training
diagnostics. `reports/results.md` provides the written findings.

`reports/combination_explorer.html` is a self-contained interactive table of all
candidate designs. It orders candidates by validation scores and displays
held-out results for each fixed candidate. Those fixed-candidate scores differ
from the report's primary evaluation of choosing a candidate independently
within each outer fold. The explorer needs no web server or network connection.

`reports/prediction_summary.csv`, `reports/candidate_summary.csv`, and
`reports/paired_comparisons.csv` contain the main quantitative results.
`reports/audit.json` records verification of initialization, source/checkpoint
hashes, split separation, and validation-only model selection.
