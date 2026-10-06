# ALPaCA series-offset ablation

This comparison removes the explicit flat-prior series intercept from the
ALPaCA implementation while retaining its neural basis, Gaussian prior over
linear weights, and learned observation-noise scalar. The labels stay relative
to the first measured molecule. This is an ablation of the entire offset
treatment, including its predictive variance correction.

The new models train from scratch with the original validation-selected
hyperparameters, random seeds, sampled episodes, five linked folds, 4000 AdamW
updates and three ensemble members. Only validation selects checkpoints. The
original offset-enabled models and their completed evaluations are reused.
Model sizes, checkpoints, and training duration are selected using training and validation data.

`matched_training.py` loads the frozen original trainer into a separate module
namespace and replaces only its model factory and provenance inventory. It
does not edit or monkey-patch the original imported training module. The
benchmark directory remains untouched.

## Mathematical change

Let m_C and m_q denote prior means at the measured context and query, and K
the covariance induced by neural features and the learned Gaussian weight
prior. Let A = K_CC + noise_variance * I. All values below are in the existing
standardized endpoint units.

With the offset fixed at zero, ordinary Gaussian conditioning gives

    mean_q = m_q + K_qC solve(A, y_C - m_C)
    variance_q = K_qq + noise_variance - K_qC solve(A, K_Cq)

The original model first computes

    precision = 1^T solve(A, 1)
    b_hat = [1^T solve(A, y_C - m_C)] / precision

and instead uses

    mean_q = m_q + b_hat + K_qC solve(A, y_C - m_C - b_hat * 1)
    variance_q = K_qq + noise_variance - K_qC solve(A, K_Cq)
                 + [1 - K_qC solve(A, 1)]^2 / precision

The ablation removes both uses of b_hat and the final variance term. Neural features retain their biases. The model continues to use reference-relative labels.

## Outputs

The reports directory contains a PDF with aggregate and assay-specific
learning curves, prediction and acquisition CSVs, paired group bootstrap
intervals, and a text results table. The aggregate weights each assay equally.
Fixed-query prediction uses 1, 2, 3, 5 and 10 measured context compounds. The
acquisition benchmark starts with one free initial hit and uses directly
calculated expected improvement after each additional purchase.

The bootstrap samples linked groups jointly across assays. It quantifies
variation from series sampling conditional on these fitted models, not
uncertainty from repeating the entire training procedure. Prediction scores
are pooled R² with equal series weighting and macro within-series Spearman
correlation, with marginal mixture negative log likelihood and 90% mixture
interval coverage and width.

## Reproduce or resume

No working-directory change is needed. The runner uses four CPU workers.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/alpaca_offset_ablation/run_ablation.py
```

Posterior algebra, initialization and differentiation checks can be rerun with

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/alpaca_offset_ablation/test_offset_model.py
```
