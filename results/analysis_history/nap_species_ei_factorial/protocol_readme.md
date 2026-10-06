# Separating species heads from EI replacement

This is a matched two-by-two factorial experiment on the New Neural Acquisition Process (NAP). It separates the two changes introduced in the preceding run and measures whether they interact.

| Cell | Species-specific pipeline | GP EI replaced with its three inputs | Source |
| --- | --- | --- | --- |
| A, original NAP | No | No | Frozen original five-fold controls |
| B, species heads only | Yes | No | Newly trained policy |
| C, EI inputs only | No | Yes | Newly trained policy |
| D, both changes | Yes | Yes | Frozen corrected species-NAP experiment |

The species factor includes the existing species-conditioned delta predictor, GP prior, neural forecaster, acquisition gate and critic. It is a pipeline-level factor, not an ablation of one output matrix. Sharing remains within each endpoint. Human, rat, mouse and dog are represented where present, with shared fallback predictions for species absent from training.

The EI factor replaces only the Gaussian-process expected-improvement (EI) rank with the already-implemented learned function of GP mean, GP standard deviation and the best measured relative outcome. Its learned output lies between zero and one. The other four experts and all context features remain available, including the separate neural-predictor EI. Any effect of this factor concerns the acquisition representation and its learned scoring rule, since these three values are sufficient to calculate Gaussian EI.

Within each species setting, both EI variants use the exact same frozen delta, GP and neural forecasting checkpoints. Shared gate and critic initialization is also preserved across that EI intervention. Behavioral checks reproduce both existing comparator forward passes from saved checkpoints and verify feature preservation, hidden-label exclusion and gradient routing. The pooled family retains its original endpoint identity input; it does not receive species identity.

The two new cells use five grouped outer folds, six endpoints, seeds 11/29/47, 800 supervised warm-start updates and 500 clipped Proximal Policy Optimization (PPO) iterations per endpoint/fold/seed. Forecasters are frozen and reused. Evaluation uses all 4,625 eligible pools, four identical worst-half initial-hit draws per pool, and complete acquisition orders. Models lock before full held-out scoring. There is no architecture or hyperparameter search in this experiment.

## Planned contrasts

Write A, B, C and D for mean additional purchases under each cell. Lower values are better.

- Species effect with analytic EI is B minus A.
- Species effect with learned EI inputs is D minus C.
- EI replacement with pooled predictors is C minus A.
- EI replacement with species heads is D minus B.
- The interaction is D minus B minus C plus A.
- The observed combined change is D minus A, equal to the two individual changes plus the interaction.

In equations, the interaction and decomposition are

\[
I = D-B-C+A,\qquad D-A=(B-A)+(C-A)+I.
\]

A negative interaction means that the combined change costs fewer purchases than an additive prediction based on the individual changes. A positive interaction means that the combination costs more. Neither sign alone establishes that the combined model is better than the original model.

Primary evaluation is purchases to any top-1, top-2, top-3 or top-4 compound in pools of at least 15 compounds. Pools of at least three are also summarized, along with endpoint, species and minimum-size cutoff breakdowns. The initial hit is free and boundary ties qualify.

Paired intervals resample source groups jointly across endpoints with all four cells retained. Each replicate weights pools within endpoint and endpoint means equally. Intervals are conditional on fitted models and unadjusted for multiple comparisons.

Outputs remain in `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_species_ei_factorial`. The CPU runner is `run_benchmark.py`. `progress.json`, `runner.log` and `jobs` record execution; `completed.json` records successful evaluation and report generation. No manual command is needed for the active run.
