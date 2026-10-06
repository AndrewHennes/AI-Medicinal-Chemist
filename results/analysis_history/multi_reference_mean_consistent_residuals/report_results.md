# Equal-weight multi-reference model comparison

The original model is preserved in checkpoint_1 with training/inference code, 90 fitted members, configurations, calibration, prepared data and PCA transforms. All runs completed on CPU.

Primary comparison: six endpoints, five linked-group folds, 580 pools with >=15 compounds, fixed hidden queries, ten measured compounds. Metrics average pools within endpoints, then endpoints equally. NLL uses validation-calibrated predictive mixtures.

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Saved current model | 0.5668 | 0.3969 | 0.5801 |
| Average, inference change only | 0.1665 | 0.3978 | 0.9755 |
| Original baseline, retrained | 0.5665 | 0.3987 | 0.5798 |
| Average baseline, retrained | 0.4861 | 0.3658 | 0.6935 |
| Average + updated residuals, retrained | 0.5605 | 0.3903 | 0.6150 |

Updated-residual averaging versus matched original-baseline retraining. Positive improvement favors averaging; NLL improvement is control minus averaging.

| Metric | Improvement | Paired 95% interval |
|---|---:|---:|
| r2 | -0.0060 | [-0.0157, +0.0004] |
| rho | -0.0084 | [-0.0200, +0.0036] |
| nll | -0.0352 | [-0.0447, -0.0252] |

## Endpoints after ten measurements

| Endpoint | Original R² | Average + updated residuals R² | Original ρ | Average ρ | Original NLL | Average NLL |
|---|---:|---:|---:|---:|---:|---:|
| Microsomal clearance | 0.5992 | 0.5888 | 0.4199 | 0.4039 | 0.5194 | 0.5400 |
| In vivo clearance | 0.5098 | 0.5096 | 0.2573 | 0.2557 | 0.5069 | 0.5221 |
| Protein binding | 0.5229 | 0.5400 | 0.5232 | 0.5360 | 0.6472 | 0.6930 |
| Cellular clearance | 0.5447 | 0.5277 | 0.3808 | 0.3524 | 0.5103 | 0.5525 |
| Permeability | 0.6232 | 0.6171 | 0.4122 | 0.4119 | 0.6715 | 0.7116 |
| Efflux ratio | 0.5992 | 0.5801 | 0.3987 | 0.3818 | 0.6233 | 0.6705 |

## What changed

Let z_i = y_i - y_hit and delta(q,i) be the trained neural pair prediction. The averaged query baseline is mean_i[z_i + delta(q,i)] over all measured compounds, including the initial hit. Simply averaging raw pair deltas would place estimates on different reference scales and is not what was implemented.

The first test changed only the query baseline and retained original context residuals. Both an inference-only swap and matched joint fine-tuning were tested. The targeted follow-up keeps the same averaged query mean but defines each additional measured compound's residual against an average of predictions anchored on the OTHER measured compounds. Its own measured value never contributes to its baseline. This updates the residual definition without introducing a new correction architecture.

The original initial-hit pair representation, learned kernel, finite iterative correction, mean gate/offset, and kernel-informed variance head remain. No sign-consistency penalty, independence-based division of variance, or full reference-centered covariance model was added.

The uncorrected frozen baseline R² rises from 0.0771 to 0.4744, while rho changes from 0.2783 to 0.2785. Averaging helps the baseline's overall offset accuracy far more than its within-series ordering.

About 99.8% of the frozen averaging change's mean squared magnitude is a common shift across each fixed hidden panel, averaged across endpoints. This explains why an inference swap can change R² substantially with little change in Spearman correlation. It supports, but does not prove, overlap between the averaged baseline and the original residual correction.

## Training and evidence limits

All three retrained arms start from the same saved member and receive the same 1200 AdamW updates, initial learning rate 0.0003, training episodes, inherited architecture hyperparameters, and three seeds per fold/endpoint. The follow-up adds 90 fits to the first 180. Step0 and every100 updates are eligible by validation NLL. Ensemble calibration uses validation only.

The follow-up uses warm starts. Validation retained initialization for 4/90 members.

Confidence intervals use 5,000 linked-group bootstrap draws conditional on fitted models.

R² is formed from pooled target moments with equal pool weights within each endpoint; rho is computed within fixed hidden query sets then averaged over draws/pools; NLL is the exact three-member mixture likelihood in transformed endpoint units. Raw and calibrated NLL, 50/80/95% coverage, baseline-only point metrics, smaller-series results and cutoffs >=20/25/30 are provided in CSV.

The >=15 panel keeps the same hidden compounds across all context sizes. Smaller-series charts have changing eligibility at larger context sizes; one-hidden-compound panels have undefined rho. No acquisition benchmark was run.

Additional checks confirm exact averaging/leave-one-out alignment, exclusion of own measurement from its local baseline, permutation/padding invariance, hidden-target isolation, finite gradients, original checkpoint reproduction, matched fixed queries, disjoint linked-group splits and frozen input/model hashes.
