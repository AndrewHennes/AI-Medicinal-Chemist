# Species prediction heads and a three-input NAP

This directory contains the three-input New NAP ablation. The EI-feature replacement study is in [species_nap_ei_inputs](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_nap_ei_inputs/README.md). Both studies use the same species delta, GP plus EI, and Old NAP baselines.

This implements the requested change to the current five-model comparison. It shares parameters across species **within each endpoint**, with separate human, rat, mouse and dog residual heads where those species are present. Permeability and efflux retain their dog-derived data. No value-based models or joint endpoint-sharing models are added in this study.

The revised Neural Acquisition Process (NAP) candidate scorer receives exactly three numerical values:

1. Gaussian process (GP) predicted relative mean for the candidate.
2. GP predicted standard deviation for the candidate.
3. Best measured reference-relative outcome so far.

A shared 3 → 32 → 32 network with hyperbolic tangent activations learns an acquisition score. A species-specific residual adjusts the shared score. It does not receive expected improvement (EI), EI ranks, embeddings, delta estimates, neural forecasts, or the old information heuristic. Species identity routes the output head; it is not a fourth numerical input. The critic pools the same encoded three-value inputs and uses the available-candidate count to scale its predicted remaining cost.

This replaces the earlier five-expert rank mixture with a directly learned scoring function. The revised policy retains group-cross-fitted GP predictions, a supervised optimum-selection warm start, and clipped Proximal Policy Optimization (PPO). There are no unused neural forecaster fits because this scorer only needs GP predictions. No EI is computed in the new policy's state construction or forward pass. GP + EI remains a separate benchmark and continues to use EI.

## Species-aware models

- **Delta greedy:** shared ordered-pair MiniMol network plus a shared output and species-specific residual outputs. No sign-consistency constraint.
- **GP + EI:** shared Matérn-5/2 feature lengthscales and linear mean, with species-specific residual means, amplitude adjustments and nugget adjustments. This transfers through shared hyperparameters; it does not estimate cross-species correlations or use other species' held-out outcomes at test time.
- **Old NAP:** shared transformer and prediction head with species-specific residual prediction heads. The acquisition and critic networks retain their previous form and can use species through the input representation. Species-input columns start at zero, ensuring that an absent species does not inherit an untrained random embedding contribution.
- **Three-input NAP:** the shared scorer and critic have species-specific residual outputs, with a species-aware GP supplying the predictive inputs.
- **Random:** unchanged analytical expectation.

Residual heads initialize to zero. Species absent from a training partition use the learned shared prediction.

## Matched design

The study preserves all 4,625 pools, five outer group folds, delta/acquisition role separation, three inner GP teacher folds, outcome transformations, training-only feature and outcome scales, and four matched worst-half initial-hit draws per pool. Neural seeds remain 11, 29 and 47. All outcomes remain relative to the original hit. Only measured anchors contribute to delta features, and a singleton anchor has spread zero.

Species does not change the original per-endpoint training budgets or uniform pool sampling. Each endpoint/fold uses 3,000 delta updates, 700 GP updates, three additional group-excluded GP fits, 800 old-NAP prediction or new-NAP warm-start updates, and 500 PPO iterations per policy seed. GP species residuals receive fixed regularization. Species are not rebalanced in this first comparison.

The existing unmodified 50%-start models remain read-only comparators. New trained checkpoints lock before the full held-out evaluation. No model selection uses the outer-test comparison. The short integration smoke test checks implementation on a few previously used test cases; its results do not select an architecture or training recipe.

Reports include purchases to top-1 through top-4, endpoint/species strata, and size cutoffs. The initial hit is free and rank-boundary ties qualify. Intervals resample source groups conditional on fitted models and without multiplicity adjustment.

The study combines species heads and the New NAP scorer changes.

## Execution and outputs

The runner is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_multitask_nap/experiment.py`. It requires no command-line arguments, uses absolute paths and writes all checkpoints and results under this directory. It runs on CPU; no manual GPU job is needed.

`runner_pid.json`, `runner.log`, `progress.json` and the `jobs` directory record actual process/job status. `benchmark_completed.json` appears only after fitting and full evaluation complete. `completed.json` appears after reports are also built. `failed.json`, if present, records a runner failure. Consult those files for current status rather than treating this README as a completion claim.

The final PDF will be `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_multitask_nap/reports/species_multitask_comparison.pdf`. Numerical outputs include complete trajectories, pool metrics, species coverage, cutoff curves and paired differences. Previously completed experiment files are not overwritten.

Behavioral checks in `tests.py` cover species gradient routing, unseen-species shared fallback, hidden-label exclusion, reference-offset invariance, action masking, permutation equivariance, the three-input restriction and absence of direct EI computation. `smoke_verification.json` records the short end-to-end fitting/evaluation check.
