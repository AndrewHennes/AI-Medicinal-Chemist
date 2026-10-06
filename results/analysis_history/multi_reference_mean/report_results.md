# Equal-weight multi-reference mean

Current architecture saved in checkpoint_1, including 90 fitted members, configurations, validation calibration, original and runnable source, prepared folds and PCA transformations.

Five-fold matched comparison across six endpoints. Primary results use fixed hidden compounds in pools of at least 15 molecules, after ten total measurements. Endpoints have equal weight.

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Saved current model | 0.5668 | 0.3969 | 0.5801 |
| Average, inference change only | 0.1665 | 0.3978 | 0.9755 |
| Original baseline, retrained | 0.5665 | 0.3987 | 0.5798 |
| Average baseline, retrained | 0.4861 | 0.3658 | 0.6935 |

Matched retraining, average baseline minus original baseline, expressed as improvement. Positive values favor averaging. NLL improvement means control NLL minus averaging NLL.

| Metric | Improvement | Paired 95% interval |
|---|---:|---:|
| r2 | -0.0804 | [-0.0960, -0.0694] |
| rho | -0.0329 | [-0.0501, -0.0177] |
| nll | -0.1137 | [-0.1280, -0.0986] |

## Endpoints after ten measurements

| Endpoint | Original retrained R² | Average retrained R² | Original ρ | Average ρ | Original NLL | Average NLL |
|---|---:|---:|---:|---:|---:|---:|
| Microsomal clearance | 0.5992 | 0.5386 | 0.4199 | 0.3790 | 0.5194 | 0.5914 |
| In vivo clearance | 0.5098 | 0.3904 | 0.2573 | 0.2378 | 0.5069 | 0.6212 |
| Protein binding | 0.5229 | 0.4861 | 0.5232 | 0.5336 | 0.6472 | 0.7607 |
| Cellular clearance | 0.5447 | 0.4570 | 0.3808 | 0.3133 | 0.5103 | 0.6288 |
| Permeability | 0.6232 | 0.5396 | 0.4122 | 0.3709 | 0.6715 | 0.7951 |
| Efflux ratio | 0.5992 | 0.5050 | 0.3987 | 0.3604 | 0.6233 | 0.7639 |

## Design and interpretation

For each unmeasured query q, the new baseline averages z_i + delta(q,i) over the initial hit and all measured context compounds. The initial hit has z_i=0. Deltas are aligned before averaging. We do not divide predictive variance by the number of anchors or assume their errors are independent.

Only the query baseline construction changes. The original first-hit pair representation, local residual definitions, iterative correction, anchored kernel variance and uncertainty decoder are retained. Their weights can adapt during joint fine-tuning.

The frozen-average arm uses exactly the saved weights with a different inference baseline. Each retrained arm receives 1200 AdamW updates at initial learning rate 0.0003, identical episodes, inherited hyperparameters and three seeds. Checkpoint 0 and every 100 updates are eligible by validation NLL. Calibration temperatures are fit on validation. No test-driven model selection.

Validation chose initialization for 68/90 original-baseline members and 0/90 average-baseline members.

Reported NLL is exact ensemble-mixture NLL in transformed endpoint units. Both raw and calibrated NLL are in the CSV. R² uses equally weighted pool target moments within endpoints; Spearman is calculated within fixed hidden sets and then averaged over draws and pools. Tiny panels with one hidden compound have undefined Spearman and are excluded from that metric.

The primary >=15 panel contains 580 pools in 334 linked groups and keeps the same query compounds at every context size. All-pool charts are secondary; the eligible pool composition changes at larger context sizes. Full smaller-pool and additional-cutoff results are included in CSV.

Confidence intervals resample linked groups jointly across endpoints, with 5000 draws.

R² and rho of the uncorrected baselines are reported separately in baseline_summary.csv. NLL is only assigned to the full model whose uncertainty head was trained for that predictive distribution.

Inference in the averaging branch evaluates one neural pair per measured anchor and query. This adds O(P n) fixed-width neural work while leaving the existing kernel-variance solve unchanged.
