# Corrected New NAP feature replacement

This study replaces Gaussian-process expected improvement with its mean, standard deviation, and incumbent inputs while retaining the other New NAP features.

This correction replaces only the **Gaussian-process expected-improvement (EI) branch** with a learned function of the predicted mean, predicted standard deviation, and best measured reference-relative outcome. It retains the original other four acquisition experts, their rank transforms, the contextual mixture and critic, MiniMol-based neural forecasts, delta mean and spread, Gaussian-process information, and pool context. The separate neural-predictor EI score is retained. Species-specific prediction, acquisition and value residual heads share parameters within each endpoint.

The original GP-EI expert supplied a rank between zero and one. Its replacement is a differentiable three-input network with a sigmoid output in that same range. This permits learning from the existing supervised warm start and clipped Proximal Policy Optimization (PPO) loss. The agreement statistic retains its previous purpose but compares the replacement branch's ordering with delta's ordering. No Gaussian EI value or Gaussian EI rank is computed or supplied to the corrected controller.

The completed species-specific delta, Gaussian-process plus EI, and Old NAP baselines are reused without changes. Their predictions and all reference draws remain fixed. Restoring the neural forecast feature requires training species-specific neural forecasters for each of the three inner group-excluded partitions and the full acquisition-training partition. This adds 120 supervised fits, followed by 90 corrected policy fits and 30 evaluation jobs across six endpoints and five outer folds. There are no new hyperparameter searches or changes to the original training budgets.

All 4,625 eligible pools, including 580 pools with at least 15 compounds, remain in the matched comparison. Four worst-half initial-hit draws and three neural policy seeds are retained. Evaluation reports additional purchases to any top-1, top-2, top-3 or top-4 compound. Source and checkpoint hashes lock before held-out evaluation.

The earlier three-input-only experiment remains intact at `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_multitask_nap` as a separate ablation. Its performance is not presented as the result of this corrected experiment.

The benchmark runs automatically on CPU. Progress is recorded in `progress.json`, `runner.log` and `jobs`. `benchmark_completed.json` records successful full evaluation; `completed.json` records successful report generation. Outputs remain under `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/species_nap_ei_inputs`.

Behavioral verification covers retention of the four other experts and context, absence of Gaussian EI calculation, hidden-label exclusion, reference-offset invariance, permutation equivariance, action masking, species gradient routing, shared fallback for unseen species, frozen neural forecasters, gradient flow into the replacement branch, supervised and policy updates, and complete acquisition trajectories.
