# Five-way mean and covariance benchmark

Six endpoints, five linked-group folds, three-member neural ensembles. Primary table uses ten total measurements and fixed hidden queries in series pools with at least 15 compounds. Endpoint means receive equal weight. NLL is validation-calibrated and lower is better.

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5737 | 0.4030 | 0.6178 |
| Model without changes | 0.5665 | 0.3987 | 0.5798 |
| Average mean only | 0.5605 | 0.3903 | 0.6150 |
| Average-reference kernel only | 0.5823 | 0.4127 | 0.5728 |
| Average mean + average-reference kernel | 0.5837 | 0.4137 | 0.5723 |

## Changes relative to the unchanged architecture

Positive improvement favors the modified model. NLL improvement is baseline NLL minus modified NLL. Paired 95% intervals resample linked groups.

| Method | Metric | Improvement | Paired 95% interval |
|---|---|---:|---:|
| Average mean only | r2 | -0.0060 | [-0.0157, +0.0004] |
| Average mean only | rho | -0.0084 | [-0.0200, +0.0036] |
| Average mean only | nll | -0.0352 | [-0.0447, -0.0252] |
| Average-reference kernel only | r2 | +0.0158 | [+0.0094, +0.0198] |
| Average-reference kernel only | rho | +0.0140 | [+0.0090, +0.0202] |
| Average-reference kernel only | nll | +0.0070 | [+0.0034, +0.0110] |
| Average mean + average-reference kernel | r2 | +0.0172 | [+0.0104, +0.0215] |
| Average mean + average-reference kernel | rho | +0.0150 | [+0.0081, +0.0222] |
| Average mean + average-reference kernel | nll | +0.0074 | [+0.0036, +0.0114] |

## Microsomal clearance

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.6035 | 0.4240 | 0.5191 |
| Model without changes | 0.5992 | 0.4199 | 0.5194 |
| Average mean only | 0.5888 | 0.4039 | 0.5400 |
| Average-reference kernel only | 0.6074 | 0.4277 | 0.5129 |
| Average mean + average-reference kernel | 0.6085 | 0.4287 | 0.5121 |

## In vivo clearance

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5380 | 0.2853 | 0.5146 |
| Model without changes | 0.5098 | 0.2573 | 0.5069 |
| Average mean only | 0.5096 | 0.2557 | 0.5221 |
| Average-reference kernel only | 0.5310 | 0.2859 | 0.4934 |
| Average mean + average-reference kernel | 0.5336 | 0.2884 | 0.4915 |

## Protein binding

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5404 | 0.4863 | 0.8149 |
| Model without changes | 0.5229 | 0.5232 | 0.6472 |
| Average mean only | 0.5400 | 0.5360 | 0.6930 |
| Average-reference kernel only | 0.5530 | 0.5359 | 0.6471 |
| Average mean + average-reference kernel | 0.5563 | 0.5448 | 0.6450 |

## Cellular clearance

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5188 | 0.3772 | 0.5639 |
| Model without changes | 0.5447 | 0.3808 | 0.5103 |
| Average mean only | 0.5277 | 0.3524 | 0.5525 |
| Average-reference kernel only | 0.5565 | 0.3838 | 0.5019 |
| Average mean + average-reference kernel | 0.5566 | 0.3831 | 0.5045 |

## Permeability

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.6423 | 0.4615 | 0.6677 |
| Model without changes | 0.6232 | 0.4122 | 0.6715 |
| Average mean only | 0.6171 | 0.4119 | 0.7116 |
| Average-reference kernel only | 0.6413 | 0.4308 | 0.6573 |
| Average mean + average-reference kernel | 0.6425 | 0.4271 | 0.6563 |

## Efflux ratio

| Method | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5993 | 0.3839 | 0.6264 |
| Model without changes | 0.5992 | 0.3987 | 0.6233 |
| Average mean only | 0.5801 | 0.3818 | 0.6705 |
| Average-reference kernel only | 0.6044 | 0.4120 | 0.6240 |
| Average mean + average-reference kernel | 0.6045 | 0.4102 | 0.6248 |

## What each comparison means

GP is the established frozen seed-11 neural-mean/conventional-kernel model with off-policy auxiliary delta supervision and its original predictor-validation variance multiplier. Its outputs reproduce the prior GP benchmark. It is a single GP, while the neural architecture uses three independent members. No new GP hyperparameter search was performed.

Model without changes retains the checkpoint_1 architecture and receives the same 1200-update continuation budget as each modified neural architecture. Its completed matched fit was reused. The untouched checkpoint_1 remains preserved; the main row is the fair continued-training control.

Mean-only retains the previous averaged query baseline and leave-one-out measured-compound residuals. The completed matched fit is reused. Its mean and calibration reproduce the preceding experiment.

Kernel-only retains the single-hit neural pair predictor but changes the covariance reference to the whole measured set. The combined arm also averages neural pair predictions over measured anchors. Both center the observed outcomes AND their neural baseline means before residual correction, then add back the observed mean to report deltas relative to the initial hit. Therefore kernel-only is a consistent reference/covariance/noise transformation, not merely replacing an array while keeping incompatible residual coordinates.

For n measured compounds including the hit, H=I-11^T/n and w=1/n. The context covariance is H K H; the query cross covariance is k_qC H - w^T K H; the diagonal is k_qq-2 k_qC w+w^T K w. The same centered kernel is used for iterative mean correction and conditional kernel variance.

Independent equal-variance raw measurement noise becomes lambda H, replacing the old diagonal ridge assumption in the kernel-change arms. H has a redundant common coordinate. Adding the unit projector 11^T/n fixes this unused coordinate; residuals and cross covariance lie in the orthogonal subspace. Tests agree with explicitly solving only n-1 independent contrasts.

The combined arm uses mean_j delta(q,j) for an unmeasured query and sum_{j!=i}delta(i,j)/n for a measured-point baseline. The latter is (n-1)/n times the leave-one-out delta mean, expressed in the common measured-set-mean coordinates. Diagonal self contrasts are known zero and not trained. No sign-consistency or cycle-consistency penalty is added.

Centering also adjusts baseline offsets. With the single-hit neural mean m, the baseline reported on the original-hit scale becomes m_q + mean_C(z_i-m_i). With the averaged pair mean, it becomes mean_C(z_i) + mean_i delta(q,i) minus the mean of the assigned measured-point delta baselines. These deterministic coordinate conversions are part of the kernel-reference change.

The original neural context input format, decoder, correction gate/offset, learned positive variance multiplier and extra variance are retained. First-hit embeddings remain in neural features.

## Training, evaluation and limitations

All neural conditions start from the same saved member and use identical newly sampled episodes, 1200 AdamW updates at initial learning rate0.0003, inherited architecture hyperparameters, and seeds11/29/47. Unchanged and mean-only reuse 180 previous matched fits; 180 new kernel-condition fits were completed on CPU. Step0 and every100 updates are eligible by validation NLL. Neural scale calibration uses validation only.

Validation selected initialization for 72/90 kernel-only and 67/90 combined members.

Audit passed for 4625 test pools in 2011 linked groups. The primary >=15 panel has 580 pools and 334 linked groups. Query molecules stay fixed as context grows. Smaller-series results and cutoffs>=20/25/30 are available in CSV; their feasible context sizes differ.

R² uses pooled target moments with equal pool weights inside endpoints; rho averages rank correlations within fixed hidden query sets; NLL uses exact mixture densities in transformed endpoint units. Tiny one-query panels cannot contribute rho. Both raw and calibrated NLL plus50/80/95% interval coverage are reported.

Paired confidence intervals use 5,000 linked-group bootstrap draws conditional on fitted models. The kernel factor combines reference centering with its residual and noise transformations.
