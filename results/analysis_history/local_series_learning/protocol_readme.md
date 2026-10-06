# Local learning and the value of unsuccessful experiments

Completed retrospective diagnostics using frozen five-fold predictors. The main report is [local_series_learning.pdf](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/local_series_learning.pdf), with an [eight-page summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/results_summary.pdf) and [written findings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning/reports/findings.md).

No forecasting or policy weights were fitted in this study. The preceding [NAP factorial experiment](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_species_ei_factorial/reports/nap_factorial_results.pdf) independently separates the species-conditioned pipeline and the replacement of the Gaussian expected-improvement feature.

## Predictors and held-out data

Three predictors are evaluated under both the pooled-species and species-specific pipelines: anchored delta means, Gaussian-process posterior means, and neural histogram means. The neural forecaster is the frozen predictor used by the NAP acquisition controller, not the controller's acquisition score. Predictions use only current-series measured outcomes. No outcome information from the held-out source group is available in forecasting training or validation. Each pool is tested exactly once per pipeline across the five folds. Training and validation scales, embeddings, outcome transformations, and checkpoints are unchanged.

All existing endpoints and species strata are retained. Lower oriented outcomes are better. Clearance uses log10, permeability uses negative log10, protein binding uses log10((1−fu)/fu), and efflux uses the existing log10 BA/AB orientation. Values supplied to models are relative to the initial measured reference. Thus one observation supplies a reference structure and zero relative outcome; numerical local outcome differences begin with the second measurement.

## Three experiments

- Fixed-query learning curves use 580 pools of size ≥15 with five hidden queries and 1–10 measurements, 880 pools of size 8–14 with three hidden queries and 1–5 measurements, and 1,041 pools of size 5–7 with three hidden queries and 1–2 measurements. Ten random partitions and nested reveal sequences per pool are matched across predictors. The cohort and query compounds remain fixed within each curve. Reveals, including the first, are uniformly random for this prediction diagnostic.
- Counterfactual experimental-value analysis uses four initial contexts per large pool. The initial reference is drawn from the worst half, consistent with the acquisition benchmark. Five other compounds remain hidden. Every remaining candidate is revealed separately from the same one-hit context. In total there are 42,536 distinct alternative reveals, scored by six predictors. Immediate property gain, hidden-query ranking gain, and the quality of the next predicted-best hidden compound are saved.
- Chemical-change transfer uses two disjoint matched pairs with the same oriented single-cut substitution. Structural cases are selected without outcomes, at most 24 per pool. A shared core contains ≥60% of each molecule's heavy atoms and variable fragments contain ≤12 heavy atoms. One pair is measured and the other remains hidden. Historical effects use training source groups only, within endpoint and species. Direction evaluation requires a hidden effect magnitude ≥0.10 oriented log units. A model-near-null, surprising subset uses |predicted hidden effect|≤0.10 and |diagnostic residual|≥0.20. A historical-near-null subset requires at least three training groups and |historical mean|≤0.10.

## Outcome controls and statistics

Each actual reveal is compared with the same molecular structure given its expected outcome. For learning curves, expected outcomes come from the initial one-hit prediction and stay fixed. For counterfactual and pair-transfer experiments, the newly revealed value is replaced with its pre-reveal predicted mean. This separates the response to unexpected outcomes from changes caused by context structures and measured status. Delta-mean rankings are mathematically invariant to anchor outcomes. Gaussian means remain unchanged under their self-consistent expected-outcome observations. Both properties are numerically verified.

Ranking uses Spearman correlation and pairwise concordance. Constant hidden outcomes are unscorable and excluded consistently across conditions. Constant predictions against varying truth receive rho zero. Concordance omits true ties and gives predicted ties half credit. Candidate reveals are averaged within context, then contexts within pool. Curves average random draws within pool. Pool means are averaged within endpoint, then endpoints receive equal weight.

Intervals use 2,000 paired source-group bootstrap resamples, with shared group draws across endpoints and trained checkpoints held fixed.

## Artifacts and reproducibility

- `engine.py` explicitly separates supplied measured values from hidden labels.
- `worker.py` defines all three experiments; `config.py` fixes draw counts and absolute paths.
- `fragment_pairs.py` creates the structure-only matched-pair catalog using the separate existing RDKit environment.
- `run_analysis.py` runs isolated CPU inference jobs so historical module globals do not mix across folds or pipelines.
- `analyze.py` computes paired summaries; `analysis_tests.py` checks ties, group resampling, fold coverage, molecule ordering, and disjoint pairs.
- `draw_examples.py` renders real chemical structures; `report.py` builds figures and PDFs.
- `jobs/` contains all per-fold raw results. `reports/` contains pool and aggregate CSV tables, example details, chemical images, and verification records.
- `source_lock.json` and per-job checkpoint hashes preserve the inference definition. Reporting-only edits do not change models or inference outputs.

All products are written under `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/local_series_learning`. No GPU or manual execution is required for the completed analysis.
