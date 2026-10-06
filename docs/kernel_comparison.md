# Conventional covariance and neural-mean comparison

This recipe compares Gaussian process (GP) kernels under the current shared benchmark protocol. Archived pair-memory, Morgan-distance, and kernel-remapping studies use their recorded splits, targets, preprocessing, training budgets, and calibration. Regenerate archived figures from the corresponding numeric tables.

The code compares Matérn-5/2, radial basis function (RBF), rational-quadratic, and linear covariance on principal component analysis (PCA) projections of MiniMol representations. It also supports a genuine Morgan-fingerprint Tanimoto covariance. Fingerprints come from each prepared dataset's `molecules` SMILES, joined through its audited `feature_indices`. MiniMol coordinates are never treated as binary fingerprints. The default Morgan settings are radius 2, 2,048 bits, and chirality enabled. RDKit is an optional dependency required only when `tanimoto` remains in the configuration. A missing dependency or invalid molecule stops the run rather than substituting an unrelated descriptor.

Each kernel uses either a zero structural mean or a learned neural mean. The latter is a two-hidden-layer, 64-unit GELU network of selected MiniMol PCA coordinates. Its weights, covariance amplitude, observation noise, and applicable length scale are learned jointly from training episodes. Both conditions analytically adapt a free series intercept and initialize fresh parameters. Historical pairwise delta-mean studies use their recorded architectures.

## Covariance and observation model

Let `x` and `z` denote the selected PCA representations, `d` their dimension, `ell` the length scale, `a` the covariance amplitude, and `v` the observation-noise variance. Define `r2 = mean((x-z)^2)/ell^2`. The available covariances are

```text
rbf(x,z) = a * exp(-r2/2)
matern(x,z) = a * (1 + sqrt(5*r2) + 5*r2/3) * exp(-sqrt(5*r2))
rational_quadratic(x,z) = a * (1 + r2/(2*alpha))^(-alpha), alpha = 1
linear(x,z) = a * dot(x,z)/d
```

For Morgan bit vectors `b_x` and `b_z`, the Tanimoto covariance is

```text
tanimoto(x,z) = a * dot(b_x,b_z)
                 / (||b_x||^2 + ||b_z||^2 - dot(b_x,b_z))
```

Two empty bit vectors have similarity one; an empty and nonempty vector have similarity zero. All these covariance constructions are positive semidefinite on their stated representations. Linear covariance uses its actual query-specific diagonal, which is important when computing posterior variance. The code does not map an arbitrary distance to covariance without checking the mathematical construction.

For measured context `C` with outcomes `y_C`, let `m_C` and `m_q` be structural mean predictions, and define

```text
A = K_CC + v * I
one = vector of ones
beta = (one^T A^-1 (y_C-m_C)) / (one^T A^-1 one)
mu_q = m_q + beta + K_qC A^-1 (y_C-m_C-beta*one)
variance_q = K_qq + v - K_qC A^-1 K_Cq
             + (1-K_qC A^-1 one)^2 / (one^T A^-1 one)
```

The last variance term accounts for uncertainty in the unknown series intercept. The `v` term includes noise of a new measured outcome. All solves use Cholesky factorization. Both the mean and uncertainty are invariant to adding a constant to all context labels, apart from the corresponding shift of the predicted mean. The unit tests explicitly verify this property.

Training minimizes the existing restricted Gaussian evidence in within-episode contrasts. The free intercept is integrated out. Context and query measurements from training episodes contribute to that likelihood. Test query labels never update parameters. Inference uses only revealed context outcomes.

## Selection and evaluation

The default configuration uses all six endpoints, five globally linked folds, and final seeds 11, 29, and 47. Each kernel/mean family selects among 8 or 32 PCA components and learning rates 0.001 or 0.0003. Hyperparameters are selected by seed-11 validation negative log-likelihood (NLL) after 1,200 updates. The selected configuration is then trained from fresh weights for 4,000 updates per final seed. A neural mean on Tanimoto covariance still uses PCA inputs; a zero-mean Tanimoto model has no meaningful PCA hyperparameter, so that duplicate trial is omitted. This is a compact predeclared search, not exhaustive tuning of every possible kernel or network.

The prepared PCA fits and label scales use training data only. All families use the same context-sampling geometry, the first 32 PCA components, including when Morgan bits are present for covariance. This prevents fingerprints from silently changing which training contexts are sampled. Model fitting uses the full outer-training set, matching the current predictive benchmark. No predictor/policy role split is needed because acquisition is calculated directly by expected improvement (EI), without a learned acquisition actor.

Model selection uses the existing balanced validation weighting. Half the mass is spread across all eligible pools and half across pools with at least 15 compounds. Within each pool, cases are equally weighted. Best checkpoints use validation NLL; there is no test-based fallback or selection.

The runner evaluates a common hidden query set at context sizes 1, 2, 3, 5, and 10, subject to pool eligibility. It records R², within-query-set Spearman correlation, exact three-member Gaussian-mixture NLL, 90% coverage, and interval width in training-normalized target coordinates. NLL comparisons require consistent target units. R² uses equal pool weights within endpoints, and overview curves weight endpoints equally. Pool eligibility varies with context size; Spearman correlation requires at least two queries.

Acquisition uses Gaussian-moment EI from the same ensemble predictive mean and variance. It starts from a free worse-half hit and reveals one selected compound per step. The reported outcomes are purchases until any top-1, top-2, top-3, or top-4 compound is reached, with ties counted as success and zero if the initial hit already meets the target. An analytic random expectation is included. This intentionally separates prediction quality from acquisition efficiency.

Output includes per-fold selection records, all query predictions and acquisition trajectories, checkpoint hashes, validation histories, per-endpoint and equal-endpoint figures, and numeric summaries. Source, prepared feature, dataset, configuration, and fingerprint-cache hashes guard against silently mixing different runs. Each fitted model's resume signature binds the actual fingerprint artifact hash and the RDKit version that generated it, as well as the Morgan settings. Regenerating descriptors cannot silently reuse a fit from a different descriptor artifact. Interrupted training resumes optimizer and random-number-generator state. A changed code or configuration requires a new output directory.

## Running

Import the prepared data using the repository's standard setup first. Edit the absolute artifact path in `config/paths.json` if needed, and edit `config/kernel_comparison.json` to choose the experiment. Then execute the script by absolute path

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_kernel_comparison.py
```

The default destination is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/repository_benchmark/kernel_comparison`. Validation includes covariance/gradient tests, reference-shift invariance, Morgan bit generation, and a synthetic train/select/restart/evaluate/report workflow.
