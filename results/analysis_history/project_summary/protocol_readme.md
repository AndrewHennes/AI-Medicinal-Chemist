# Molecular acquisition project summary

The completed 16-page PDF synthesizes the project through 26 September 2026. It includes the scientific objective, curation and transformations, model definitions, grouped evaluation, current six-endpoint results, earlier predictor and multitask diagnostics, augmentation, value learning, interpretation, limitations and proposed next experiments.

- `project_summary.pdf` is the shareable report with section bookmarks.
- `project_summary.md` is the editable narrative companion.
- `benchmark_summary.csv`, `coverage.csv` and `cutoff_curves.csv` hold the plotted benchmark values.
- `source_manifest.json` records source paths and hashes.
- `verification.json` records coverage, numerical reconciliation, document and molecular-viewer checks.
- `prepare_figures.py` and `build_summary.py` regenerate the figures and document using absolute paths. Neither trains models or adds command-line options.

The main numerical source is the later matched 50% initial-hit control bank. Earlier five-endpoint multitask results and single-split predictor diagnostics are labeled separately because their evaluation populations and/or starting draws differ.

The companion decision explorer at `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/new_nap_greedy_diagnostics/reports/decision_explorer.html` now embeds molecular SVG drawings for both choices in every example. Drawings are generated locally with the existing RDKit environment at `/Users/asselism/Documents/Codex/2026-09-14/the-x20/work/benchmark_venv/bin/python`; the finished HTML needs no Python environment or network connection. All 506 example selections were checked for matching drawing and SMILES identity.
