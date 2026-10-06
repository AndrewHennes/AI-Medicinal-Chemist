## Exact replay of the published benchmark

`scripts/prepare_data.py` imports the verified five-fold prepared data named in `config/paths.json`. It checks SHA-256 hashes against the included prepared-data manifest, refuses conflicting destination files, and audits linked-group, molecule, and PCA-training isolation. Files are copied into the configured artifact root. This preserves the original split and feature coordinates exactly.

The import uses the historically curated tables. Curation includes assay selection, species scope, censoring detection, protein-binding percentage repair, and replicate aggregation. The extended project handbook records the procedure, and `results/published/input_manifest.json` records source hashes and columns. MiniMol embeddings are supplied 512-dimensional inputs.

## Endpoint transforms

All models minimize the transformed objective.

| Endpoint | Transformed objective | Retained species |
| --- | --- | --- |
| Microsomal clearance | \(\log_{10}(c)\) | Human, rat, mouse |
| In vivo clearance | \(\log_{10}(c)\) | Human, rat, mouse |
| Cellular clearance | \(\log_{10}(c)\) | Human, rat, mouse |
| Plasma protein binding | \(\log_{10}[(1-f_u)/f_u]\) | Human, rat, mouse |
| Permeability | \(-\log_{10}(p)\) | Human and dog-derived assays |
| Efflux ratio | \(\log_{10}(\mathrm{BA}/\mathrm{AB})\) | Human and dog-derived assays |

Here \(f_u\) is the unbound fraction, rather than percent. For percent bound \(B\), the binding transform is \(\log_{10}[B/(100-B)]\). It is a log bound/free ratio, not an identified dimensional association constant without a protein concentration and binding model. Clearance and permeability must be positive; binding must lie strictly between zero and one hundred percent. Efflux direction follows the BA/AB annotation in the curated rows.

Pools contain at least three unique compounds and nonconstant transformed outcomes. Repeated measurements are consolidated using the median on the transformed scale within a selected compatible assay context. Retaining a different assay, species, censoring rule, or aggregation method defines a different dataset.

## Prepared fold schema

Each `fold_0` through `fold_4` contains two files.

`dataset.json` contains a `pools` list. Each pool includes

- `pool_id`, `endpoint`, `species`, and `series_id`.
- `group`, the global leakage-control group.
- `subset`, one of `train`, `validation`, or `test`.
- `feature_indices`, row indices into the fold's feature arrays.
- `objective`, finite transformed measurements aligned to those indices.
- Molecular identifiers and source-document links retained for provenance.

`features.npz` contains

- `pca_32`, a float array of shape `[unique_molecules, 32]`.
- `center`, the training-only 512-dimensional embedding mean.
- `components`, principal directions as columns.
- `eigenvalues`, used for the common root-mean-square scaling.
- `training_indices`, exactly the union of all outer-training molecule indices.

The endpoint target scale is recomputed from full outer-training labels. The original metadata also retains additional PCA dimensions and an older stored outcome scale; the current loader intentionally uses the full-training formula in the methods document.

## New datasets

The public `predictor` API can score new molecular embeddings with measured context outcomes using a fitted checkpoint and its original preprocessing. It does not need the new pool's unmeasured labels.

To retrain on a genuinely different dataset, provide prepared folds following the same schema, fit PCA only on each fold's training molecules, and construct groups that keep shared molecules and related source records out of different roles. Point a new artifact root to those prepared folds rather than changing or bypassing the published import hashes. `series_dataset` checks group and molecule isolation using the supplied group metadata. The included import entrypoint is specifically for exact benchmark replay, not a general raw-data curation tool.

No source datasets, large prepared arrays, or learned checkpoints are included in the repository. Paths to their local locations are explicit in the configuration.
