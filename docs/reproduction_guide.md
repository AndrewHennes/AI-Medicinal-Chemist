# Reproducing the project analyses

The [project summary](analysis_summary.md) explains the scientific findings. The [searchable catalog](../results/analysis_history/index.html) records 62 historical branches and labels validation pilots and incomplete benchmarks separately. This guide explains what the included code actually reproduces.

## Three different operations

**Historical evidence and figures.** Bundled tables and narratives are unchanged copies with SHA-256 hashes. Regenerating their index and figures recovers the recorded results without fitting models. Figures never combine scores from unrelated studies into a common leaderboard. Some archived narratives link to larger figures or source files in the original workspace. Their old job-status statements are historical, not current progress reports.

**Saved-model diagnostics.** The local-adaptation recipe uses the current reference, GP, and transfer checkpoints. It verifies their fold, endpoint, preprocessing, training role and source-data hashes. This reruns inference and counterfactual measurements under a newly documented diagnostic protocol.

**Fresh scientific replications.** Augmentation and kernel recipes retrain through the common package interfaces and write separate result directories. The coverage table identifies available implementations and historical source references for the 62 archived branches.

## Newly added recipes

| Recipe | Question and supported conditions | Detailed method |
|---|---|---|
| `augmentation_analyses.json` | Initial hits from the worst 10/20/30/40/50%; multi-hit caps 2/3/4/5; cumulative removal caps 1/2/3/4/5 | [Augmentation](augmentation_analyses.md) |
| `local_adaptation.json` | Nested measured contexts with fixed hidden queries; usefulness of separate counterfactual reveals; expected-outcome controls | [Local adaptation](local_adaptation.md) |
| `kernel_comparison.json` | Zero/neural mean with Matérn, RBF, rational-quadratic, linear, or real Morgan/Tanimoto covariance; PCA and learning-rate grid | [Kernel comparison](kernel_comparison.md) |

The augmentation recipe shares a newly fitted, frozen predictor while varying PPO training contexts. Historical NAP studies that also retrained forecasters are documented with their original protocol.

The kernel recipe uses a scalar structural mean and the common likelihood. Historical GP studies used their recorded pairwise or linear means. Molecular fingerprints are generated from structures using RDKit, available through the `chemistry` optional dependency.

Recipes are available for PPO/TRPO/GRPO/DPO, latent acquisition features, mean/kernel/weighting ablations, batch selection, and standard meta-learning/ALPaCA. See [the comparison guide](past_comparisons.md).

## Running from any directory

Scripts derive the repository root from their own absolute file location. They have no command-line options. Edit JSON recipes instead. External paths are absolute. Runtime products go beneath the configured artifact root, normally `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/repository_benchmark`.

Regenerate the historical catalog and the added starting-hit, multi-hit, top-removal, and auxiliary-target figures. This reads bundled tables only.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/make_analysis_history.py
```

The figures are [indexed here](../results/analysis_history_figures/augmentation_history_manifest.json). The four study reports contain 33 pages in total and preserve endpoint-specific results and original aggregates. Initial-hit charts distinguish matched fraction-specific training from the 50-percent-training control evaluated on those same starts. The other five historical comparisons remain available through `scripts/make_historical_figures.py`.

Prepare the exact frozen data once if it has not already been imported.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/prepare_data.py
```

Run the requested scientific recipe after reviewing its JSON settings. The full augmentation and kernel recipes are substantial training experiments. The local-adaptation recipe is inference-only, but its counterfactual branches can still be expensive.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_augmentation_analyses.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_local_adaptation.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_kernel_comparison.py
```

Do not launch concurrent writers against the same recipe output directory. Resume requires matching configuration, data and implementation hashes. If the protocol changes, use a new output directory. Fresh runs use validation to select hyperparameters/checkpoints before scoring test pools.

## Verification and interpretation

Meaningful synthetic tests cover all new workflows. They include hidden-label isolation, fixed hidden panels, independent counterfactual reveals, proper mixture likelihood, exact fingerprint indexing, valid covariance, reference-shift behavior, training-only removal, matched start construction, checkpoint resumption and provenance rejection. Synthetic values are never published as chemical performance.

Historical files are checked against their saved hashes when the catalog is rebuilt. Source-code locations and hashes identify the original implementation even where it has not been refactored into the clean package. No raw assay CSVs or large historical fitted weights are duplicated into the repository. The original methodology handbook remains linked from the main readme for full preparation and source lineage.
