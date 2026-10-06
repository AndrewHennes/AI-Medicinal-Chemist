# Local adaptation and the value of an experiment

This recipe evaluates prediction improvement with local measurements and the value of individual reveals using the current saved model families. The archived `local_series_learning` experiment retains its recorded forecasters, reference selection, draws, and fitted weights.

## Run and inputs

The default recipe is [local_adaptation.json](../config/local_adaptation.json). It evaluates the current reference architecture, the neural-mean Gaussian process, and the frozen transfer predictor. Each ensemble contains seeds 11, 29, and 47, across five held-out folds and six endpoints. All 270 configured checkpoint paths existed when this recipe was added. The code imports the exact curated fold data through the existing hash-audited data importer. It does not fit models, choose hyperparameters, or select a best method using test outcomes.

Run from any directory with the existing environment.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_local_adaptation.py
```

Each model entry specifies an absolute `checkpoint_template`. The fold, endpoint, and seed placeholders expand before loading. To evaluate newly trained versions, replace those templates with paths to the new `best.pt` files. The adjacent `specification.json` must match the exact data and feature hashes, training scale, fold, endpoint, seed, model configuration, and training role. The loader expects the full outer training split used by the standard predictor benchmark. It rejects predictors trained with a separately normalized policy-role split.

The default output directory is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/repository_benchmark/local_adaptation`. It must remain beneath the configured artifact root. Changing scientific settings or source code requires a fresh output directory. Completed fold/endpoint/model cases can be resumed only when provenance and checkpoint hashes match.

## Reference and outcome conventions

The fold data already contain the endpoint transformations and orientation, with lower values always preferred. For each pool, one initial hit is sampled uniformly from the worse half, with seeded tie resolution. This retrospective condition deliberately uses labels to define the starting population, as in the acquisition benchmark. The subsequent reveal order and query selection use random permutations rather than candidate outcomes.

Let \(t_i\) be the transformed, minimization-oriented outcome, \(s\) the training-derived scale, and \(r\) the initial hit. The model receives measured features and \(y_i=(t_i-t_r)/s\). The first hit stays first in the context at every step. No hidden outcome is supplied to the model. Evaluation targets are \((t_q-t_r)/s\), so reference normalization remains consistent across context sizes and counterfactual experiments.

## Fixed-query learning curves

For a pool containing \(n\) compounds, the hidden query count is \(\min(5,\max(1,\lfloor n/3\rfloor))\). Those compounds remain hidden throughout one draw. The other compounds form a single random reveal order. Contexts contain the initial hit and prefixes of that order, producing nested measurement counts 1, 2, 3, 5, and 10 whenever feasible. The default uses three draws per pool.

The primary `complete` cohort requires five hidden queries and sufficient remaining compounds for every requested context size, requiring at least 15 compounds by default. Its pools are fixed across measurement counts. The secondary `available` cohort uses all feasible counts from pools of size at least three, so membership varies with context size. Spearman averages include cases with at least two queries and defined correlations.

The `expected_initial` control adds the same structures as the real context, substituting each added measurement with its prediction from the initial-hit-only context. This deterministic control separates adaptation to observed values from changes in context geometry.

## Counterfactual experiment value

The default initial context contains two measured compounds, including the original hit. The hidden query set remains fixed. Each candidate is then revealed in a separate experiment from that same context. Other candidate outcomes never accumulate. To bound evaluation cost, the default considers at most 12 candidates from the seeded random order and uses two draws per pool. Set `maximum_candidates` to `null` to evaluate every eligible candidate.

Let \(b=\min_{i\in C}y_i\) denote the current best measured outcome and \(y_a\) the candidate outcome. Signed immediate improvement is \(b-y_a\), and positive improvement is \(\max(0,b-y_a)\). A nonpositive signed improvement is labeled `disappointing`. Prediction usefulness is measured on the same hidden compounds before and after the reveal.

\[
U_{\rho}(a)=\rho_{\mathrm{after}}-\rho_{\mathrm{before}},\qquad
U_{\mathrm{mse}}(a)=\mathrm{MSE}_{\mathrm{before}}-\mathrm{MSE}_{\mathrm{after}},\qquad
U_{\mathrm{nll}}(a)=\mathrm{NLL}_{\mathrm{before}}-\mathrm{NLL}_{\mathrm{after}}.
\]

Positive values indicate improved hidden-query predictions. A second control reveals the same candidate structure with its current predicted mean. The `outcome_*_gain` fields compare actual-outcome adaptation with this control. Scatter plots show immediate improvement against retrospective prediction gain.

## Prediction and uncertainty metrics

The predictive distribution remains the native equal-weight Gaussian or Student mixture returned by the ensemble. The mean is the mixture mean, and its variance includes within-component and between-component variance. Negative log likelihood is evaluated using the mixture density, not a moment-matched Gaussian. The 90% interval uses numerical mixture quantiles.

`nll` is measured in standardized relative-outcome units. `nll_transformed = nll + log(s)` is the corresponding density score in the transformed assay units. The latter can be reproduced exactly because the scale is saved with every case. Spearman is computed over the fixed hidden compounds within one series/draw. It is a ranking metric for relative outcomes against the same initial hit, not a correlation pooled over all ordered molecular pairs.

Cases are averaged over draws within pools and equally over pools within each endpoint. The `macro` row weights endpoints equally. Endpoint series-balanced \(R^2\) uses mean squared error and target moments under the same pool weights; macro \(R^2\) averages those endpoint values. Experiment summaries average eligible reveals within pool and outcome category, then across pools. Bootstrap inference should cluster on the saved linked source-group identifier.

## Outputs and verification

Outputs include `learning_summary.csv`, `experiment_summary.csv`, compressed case tables, per-assay PNG figures, and `local_adaptation.pdf`. Each case records the hidden indices, measured indices, candidate where applicable, group, fold, draw, and scale. JSON case files preserve detailed before/after/control metrics. Provenance records all scientific source hashes, configuration, data hashes, checkpoint hashes, and training-specification hashes.

Synthetic tests check nested contexts, fixed hidden-query sets, complete-cohort consistency, invariance to hidden labels and common outcome offsets, independent counterfactual reveals, mixture likelihoods, training provenance, report generation, and restart.
