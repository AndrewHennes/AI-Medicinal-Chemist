# Simple kernel-softmax weighting of delta predictions

Five linked-group folds, six endpoints, three-member neural ensembles. Primary results use fixed hidden queries in pools with at least 15 compounds after ten total measurements. Equal endpoint averages. Lower NLL is better.

| Model | R² | Spearman ρ | Calibrated NLL |
|---|---:|---:|---:|
| Equal weights | 0.5837 | 0.4137 | 0.5723 |
| RBF + softmax (validation selected) | 0.5776 | 0.4106 | 0.5787 |
| GP reference | 0.5737 | 0.4030 | 0.6178 |

## Weighted model versus equal weighting

Positive improvement favors weighting. NLL improvement means equal-weight NLL minus weighted NLL. Paired 95% intervals use 5000 linked-group bootstrap draws.

| Metric | Improvement | Paired 95% interval |
|---|---:|---:|
| r2 | -0.00604 | [-0.01202, -0.00126] |
| rho | -0.00312 | [-0.00686, +0.00082] |
| nll | -0.00631 | [-0.01049, -0.00201] |

## Individual endpoints

| Endpoint | Equal R² | Weighted R² | Equal ρ | Weighted ρ | Equal NLL | Weighted NLL |
|---|---:|---:|---:|---:|---:|---:|
| Microsomal clearance | 0.6085 | 0.6070 | 0.4287 | 0.4288 | 0.5121 | 0.5161 |
| In vivo clearance | 0.5336 | 0.5328 | 0.2884 | 0.2924 | 0.4915 | 0.4913 |
| Protein binding | 0.5563 | 0.5541 | 0.5448 | 0.5321 | 0.6450 | 0.6576 |
| Cellular clearance | 0.5566 | 0.5542 | 0.3831 | 0.3803 | 0.5045 | 0.5074 |
| Permeability | 0.6425 | 0.6442 | 0.4271 | 0.4296 | 0.6563 | 0.6521 |
| Efflux ratio | 0.6045 | 0.5736 | 0.4102 | 0.4003 | 0.6248 | 0.6473 |

## Temperature sensitivity

The following fixed-temperature test results are descriptive. They did not choose the reported weighted model.

| Fixed temperature | R² | Spearman ρ | Calibrated NLL |
|---|---:|---:|---:|
| weighted_t010 | 0.5668 | 0.4099 | 0.5904 |
| weighted_t030 | 0.5811 | 0.4124 | 0.5748 |
| weighted_t100 | 0.5835 | 0.4135 | 0.5719 |

## Method and controls

The attention weights are w(q,i)=softmax_i(exp(-D(q,i)^2)/temperature), with temperatures 0.1, 0.3 and 1.0. D² is the mean squared distance in the existing PCA representation, using the existing learned diagonal metric and bandwidth. This is literal softmax over RBF values, rather than normalizing RBF values directly. No new neural embedding or covariance-aware correction of these weights was added.

Before coordinate centering, the query prior is sum_i w(q,i)delta(q,i)+sum_i(w(q,i)-1/n)z_i. This aligns each delta vote with its measured outcome. The measured-item raw prior excludes its own index, with weights summing to (n-1)/n and equal reference weights 1/n off diagonal. Subtracting the mean measured prior and adding the observed context mean produces the reporting baseline. Uniform attention exactly recovers the preceding combined mean/kernel architecture; perfect delta predictions give the correct centered property for every weighting.

The existing centered covariance, transformed noise, iterative residual correction and uncertainty-head formulas remain in place. Their parameters are jointly retrained, and the RBF weighting uses the existing learned distance parameters. Therefore numerical covariance values and predicted uncertainties may change during training, but the covariance architecture and calculation are not replaced. There is no assumption that reference prediction errors are independent and no division of final predictive variance by the reference count.

All three temperature conditions start from the same checkpoint_1 members and receive the same 1200-update, learning-rate0.0003 continuation as the reused equal-weight combined control. Episodes and member seeds11/29/47 match. No sign-consistency loss is added. The 270 weighted fits and 90 reused control fits have the same training budget per candidate.

Validation selects one temperature per endpoint/fold by raw ensemble NLL. Counts across 30 panels are {'weighted_t100': 21, 'weighted_t030': 6, 'weighted_t010': 3}. Each member checkpoint is selected at step 0 or every 100 updates; initialization selections are {'weighted_t010': 13, 'weighted_t030': 40, 'weighted_t100': 63}. Uncertainty scale calibration is fitted on validation only. Temperature selection is restricted to the weighted models.

The inherited validation criterion balances single-hit and additional-context cases. Where enough large validation pools exist, it combines all-pool weighting with extra emphasis on pools containing at least 15 compounds. It does not select temperature solely for the ten-measurement large-pool comparison.

Audit passed. All 4625 test pools in 2011 linked groups were evaluated. The primary >=15 group has 580 pools in 334 linked groups. Hidden query molecules stay fixed as measured context grows through1,2,3,5,10 compounds. Smaller-series results use the feasible context sizes and can change pool composition.

R² uses pooled target moments with equal pool weights within endpoint. Spearman averages within fixed query sets; singleton query sets have undefined correlation. NLL is the exact mixture density in transformed endpoint units. Raw and calibrated NLL and50/80/95% interval coverage are in the CSV. Effective reference count1/sum(w²) measures attention concentration, not the number of statistically independent observations.

The GP reference is the established single frozen neural-mean/conventional-kernel model, reused exactly. Neural methods use three-member ensembles. This is a prediction benchmark, not an acquisition experiment.
