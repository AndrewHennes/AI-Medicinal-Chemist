# Pure neural prediction and uncertainty

The current benchmark compares continuous within-series delta predictions from heteroscedastic Gaussian neural networks, variational Bayesian neural networks, Normal–Inverse-Gamma evidential regression, and an attentive conditional neural process variant. Three-member ensembles of the Gaussian and attentive models are also evaluated. All are pure neural predictors. They do not receive any GP output or use a GP for conditioning, training labels or calibration.

For continuous deltas, Normal–Inverse-Gamma evidence gives a Student-t predictive distribution. A Dirichlet is a distribution over class probabilities; this experiment does not discretize the continuous endpoint or describe a Student-t distribution as Dirichlet.

The existing neural-mean GP, tuned feed-forward delta model and original delta model provide reference comparisons. Existing five linked-group folds and predictor-only training/validation roles are preserved. Six endpoints are fitted separately, pooling species as in the historical prediction experiment. All endpoint transforms and training-only feature transforms are reused.

Inputs are a query/reference MiniMol pair and a variable set of measured reference-relative local outcomes. The first three neural families use permutation-invariant Deep Sets context pooling. The attentive model learns a pair prior and uses query-to-context attention over observed residuals. Neural context adaptation is amortized and has no test-time weight fitting. Variational Bayesian weight posteriors are diagonal Gaussian approximations over all linear layers, with tuned KL tempering; this is not exact Bayesian inference. The attentive model is inspired by conditional neural processes and is not an exact reproduction of the latent Attentive Neural Process paper.

Six configurations per family explore 32/64/128 principal components or raw 512-dimensional MiniMol representations, hidden widths, learning rates and uncertainty regularization. The initial screen uses 200 updates, then two candidates per family/fold/endpoint receive longer training. Architecture and checkpoint choices use validation negative log likelihood only. Three final seeds are retained. An initial coarse checkpoint schedule selected its earliest saved checkpoint in most attentive fits. Before inspecting test performance, the same two candidate configurations were refit for 2400 updates with validation every100 updates. `refine_checkpoints.py` records that validation-motivated refinement and preserves original fits and manifests.

Primary test results use pools with at least15 compounds. Each has five hidden query compounds, unchanged as local measurements increase from1 to2,3,5 and10 total measurements including the reference. Ten fixed random query/reference draws per test pool match the historical GP experiment exactly. Smaller pools are included with shorter curves. References are random, not chosen from the worse half.

Report R², within-query Spearman correlation, RMSE, predictive negative log likelihood, central interval coverage and width, probability integral transform histograms and uncertainty/error association. Raw uncertainty is primary. A single validation-fitted scale factor per model/fold/endpoint is reported separately. Mixture likelihoods and quantiles are used for ensembles and Bayesian predictions; Student-t quantiles are used for evidential regression. Original delta models have no learned predictive distribution and therefore have point metrics only.

Draws and training seeds are averaged within pool, pools within endpoint, and endpoints within macro summaries. Intervals use linked-group bootstrap weights shared across endpoints and describe uncertainty in stored measurement differences.

The follow-up adds molecular-distance attention with learned coordinate scales and compact 8/16-component inputs. Configurations and checkpoints use validation selection. The model and its three-member ensemble use neural predictions.

Outputs stay in this directory. `protocol.json` records the design; `reports/summary.csv` contains endpoint and pool-cutoff summaries; `reports/neural_prediction_uncertainty_report.pdf` contains figures and tables; `reports/audit.json` records split and evaluation checks. `evaluation_phase.json` identifies the final evaluated runs. Original first-pass results remain in `evaluation`; the refined evaluation is in `evaluation_early`, and the distance-attention follow-up is in `evaluation_metric`.

CPU entry points, independent of the shell working directory:

```
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty/run_experiment.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty/refine_checkpoints.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_uncertainty/metric_followup.py
```

`tests.py` checks order invariance, masking, hidden-target isolation, finite gradients, density/quantile calculations, scale calibration, group/document/molecule separation and unchanged hidden panels. Held-out GP arrays are reused only after case identities, reference/query/context indices, targets and masks match exactly.
