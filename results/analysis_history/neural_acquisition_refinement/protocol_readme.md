# Neural architecture refinement

This extends the frozen distance-aware neural ensemble benchmark, with two rounds of validation-driven design changes. All products remain beneath `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_acquisition_refinement`.

The first round tests expanded-context training of the prior architecture, a set-attention model, and a finite-depth residual graph model. Six configurations per family explore Gaussian versus Student-t predictive distributions, principal component counts, widths, ranking loss, and group bootstrap sampling. The second round tests deeper graph propagation and Matern-5/2 similarity against a continued-training control. The graph model is an unrolled kernel-regression mean correction with a neural uncertainty head. It is GP-inspired, but does not invert covariance matrices or compute an analytic GP posterior. These are custom architectures.

Predictor gradients use only the historical predictor-role training series. Predictor-role validation selects checkpoints and architecture hyperparameters and fits ensemble scale calibration. A fixed panel of disjoint RL-role validation series selects EI uncertainty weights and the overall pipeline. The old neural model receives the same EI-weight search and is an allowed fallback. Test folds remain unopened until these choices are locked.

Each ensemble contains three independently seeded fits. Reported predictive uncertainty uses validation likelihood calibration. EI-specific uncertainty multipliers are separate decision parameters and are not used to report predictive interval calibration.

Evaluation covers the existing five held-out folds and six endpoints. Acquisition uses K=1, four matched worse-half starting hits, and purchases to any top-1/2/3/4 compound. Prediction uses exactly the prior fixed hidden-query panels, so additional context never removes difficult query molecules. Original endpoint transformations and initial-hit-relative outcomes are retained. No sign-consistency penalty or new PPO training is added.

All entry points use absolute workspace paths, independent of the shell working directory, and require the existing Python runtime at `/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python`.

- `refinement_core.py` defines models, distribution calculations, training and measured-only inference.
- `refinement_run.py` performs the first validation round.
- `iteration2.py` performs the second validation round and evaluates the previous-model control on validation pools.
- `evaluate_refinement.py` locks final choices and evaluates held-out acquisition and prediction panels.
- `refinement_report.py` audits outputs and generates the combined PDF and CSV reports.
- `tests.py` checks masking, order invariance, label isolation, finite gradients, Student-t expected improvement, mixture quantiles, and context sampling.

Resumable runners retain intermediate choices, training histories, checkpoint identities, per-start trajectories, and per-pool prediction statistics.
