# Kernel-informed uncertainty, option 2

Option 2 needs 5.500 purchases versus 5.509 for the control, 5.518 for the existing refined model and 5.525 for GP + EI.

Option 2 minus matched control is -0.009 purchases, linked-group bootstrap 95% interval [-0.072, +0.053]. Against the existing model it is -0.017 [-0.081, +0.049].

## Acquisition, pools ≥15

| Model | Top-1 | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Kernel variance + neural scaling | 5.500 | 3.684 | 2.979 | 2.487 |
| Matched continued-training control | 5.509 | 3.728 | 3.018 | 2.512 |
| Existing refined model | 5.518 | 3.711 | 2.993 | 2.499 |
| Current GP + EI | 5.525 | 3.661 | 2.906 | 2.410 |
| Greedy delta | 6.722 | 4.451 | 3.494 | 2.788 |
| Random | 9.588 | 6.598 | 5.174 | 4.278 |

## Prediction after ten total measurements

Equal endpoint averages on fixed hidden compounds from pools ≥15. Validation-calibrated uncertainty.

| Model | R² | Spearman ρ | NLL | 95% coverage | 95% width |
|---|---:|---:|---:|---:|---:|
| Kernel variance + neural scaling | 0.567 | 0.397 | 0.580 | 0.947 | 1.907 |
| Matched continued-training control | 0.567 | 0.397 | 0.583 | 0.948 | 1.920 |
| Existing refined model | 0.566 | 0.395 | 0.582 | 0.949 | 1.933 |
| Current GP | 0.574 | 0.403 | 0.618 | 0.940 | 1.811 |

All six endpoints and five linked-group folds completed. 180 new fits, three members per ensemble, 1,200 additional updates per arm. Both arms start from the same corresponding saved model and see identical new training episodes. Architecture hyperparameters are inherited; no new broad hyperparameter search. Checkpoints and calibration use validation only. All weights remain trainable, so uncertainty gradients can also change mean predictions.

Validation selected the initialization checkpoint for 64/90 option-2 members and 49/90 control members.

The variance branch uses an exact Cholesky solve. The existing iterative mean correction is retained.

Intervals use linked-group bootstrap resampling conditional on fitted models.

Variance foundation follows Gaussian conditioning ([Rasmussen and Williams, Chapter 2](https://gaussianprocess.org/gpml/chapters/RW2.pdf)). Learned query-dependent scaling and the extra variance term are custom extensions.
