# Earlier experiments and runnable comparisons

Five earlier studies are included with recorded numeric results, regenerated figures, and reusable implementations. New runners use the current data interface and editable configurations. Archived tables retain each study's sampling, split roles, calibration, initialization, and aggregation.

| Study | Archived results | Implementation and recipe |
| --- | --- | --- |
| Policy optimization and GP auxiliary supervision | PPO, TRPO, DPO, warm policies, direct EI and random, with original and auxiliary predictors | `policy/optimizers.py`, `models/pair_supervision.py`, `config/policy_comparison.json` |
| Learned acquisition features | Mean and standard deviation with 2, 4, 8 or 16 learned features | `policy/network.py`, `policy/episodes.py`, `config/acquisition_features.json` |
| Mean and kernel ablations | Original model, average mean, average-reference kernel, both changes, softmax weighting and GP | `models/reference_ablations.py`, `config/reference_ablations.json` |
| Batch subsets | Deep Sets, pair-aware Transformer, Gumbel top-k, batch PPO and joint-uncertainty GP methods | `batch/`, `config/batch_selection.json` |
| EI-input PPO | Mean, standard deviation, incumbent and Gaussian density/distribution features | Scalar feature arms in `config/acquisition_features.json` |

The current policy runner also includes group relative policy optimization (GRPO). [The historical manifest](../results/historical/manifest.json) records the archived methods and source hashes. Copied batch tables rename the `K` column to `batch_size` without changing scores.

## Optimization rules

Proximal policy optimization, abbreviated PPO, uses clipped probability ratios, complete-episode return-to-go and a learned critic. Trust region policy optimization, abbreviated TRPO, uses conjugate gradients with automatic-differentiation Hessian-vector products for empirical categorical Kullback–Leibler divergence. Accepted steps must satisfy the divergence limit and improve the surrogate. Critic inputs detach actor features, so critic updates cannot move the actor outside its accepted trust region. These rules are ported from the recorded optimizer study (https://arxiv.org/abs/1707.06347; https://proceedings.mlr.press/v37/schulman15.html).

Direct preference optimization, abbreviated DPO, compares complete trajectories from the same starting context. Fewer purchases are preferred, ties are discarded, and trajectory log probabilities sum action log probabilities without length normalization. A frozen initial actor generates the new runner's fixed offline preference dataset. This is a chemical-acquisition adaptation of the preference objective (https://arxiv.org/abs/2305.18290).

For GRPO, each group samples complete trajectories from an identical series and starting hit. If trajectory \(i\) takes \(T_i\) purchases, then \(R_i=-T_i\) and

\[
A_i=\frac{R_i-\operatorname{mean}_jR_j}{\max(\operatorname{std}_jR_j,\epsilon)}.
\]

The standard deviation is the population standard deviation. The same advantage applies at every action of a trajectory. Let \(r_{it}\) be its current-to-old action probability ratio, \(\eta\) the clipping range, \(\beta\) the divergence coefficient, \(B\) the number of starting contexts and \(G\) the trajectories per context. The loss is

\[
L=\frac1B\sum_b\frac1G\sum_i\frac1{T_i}\sum_t
\left[-\min\{r_{it}A_i,\operatorname{clip}(r_{it},1-\eta,1+\eta)A_i\}
+\beta\operatorname{KL}(\pi_\theta(\cdot\mid s_{it})\Vert\pi_{\mathrm{ref}}(\cdot\mid s_{it}))\right].
\]

GRPO has no critic update. Tied-reward groups have zero reward advantage. Exact categorical divergence replaces sampled divergence estimation because the action space is finite. Averaging within trajectories and then within groups follows outcome-supervised DeepSeekMath and differs from globally averaging every transition (https://arxiv.org/html/2402.03300v3#S4.SS1).

The PPO, TRPO, and GRPO arms share the actor, starting-context sampler, and trajectories per update. Transitions are recorded to quantify their computation. DPO uses a separate fixed offline preference budget. Settings are selected using seed 11 validation performance and repeated with additional seeds.

## Information separation and initialization

For the policy and batch recipes, outer training groups are split into disjoint predictor and policy roles, balancing pool counts and large-pool counts. Predictors train afresh on predictor-role measurements. Endpoint scaling uses those measurements. Existing principal components use outer-training structures, including unlabeled policy-role structures, and exclude validation/test structures.

Actor features use measured outcomes and candidate structures. Query outcomes enter the retrospective environment after acquisition and are used to determine termination. New actors initialize to a GP-mean rule plus a zero-initialized residual head; the historical optimizer study used a supervised warm policy.

Optional GP pair supervision uses `predictor_auxiliary_pair_weight`, defaulting to zero. A series is sampled proportional to its compound count, followed by a uniform distinct pair. Each unordered pair thus has sampling probability proportional to \(n/\binom n2\). The auxiliary objective is the Gaussian negative log likelihood of its signed difference, including both observation-noise terms. The configured weight multiplies this objective before adding it to the original predictor loss.

## Acquisition features

All values are normalized to the starting hit using a training-derived endpoint scale. Available feature sets are `mean_sd`, `mean_sd_best`, `mean_sd_phi` and `mean_sd_ei`. The `mean_sd_phi` condition includes \(\Phi(z)\) and \(\phi(z)\), where \(z=(\mu_{\mathrm{utility}}-b_{\mathrm{utility}})/\sigma\). The EI feature is calculated analytically. A separate `direct_ei` control directly uses EI for acquisition.

Optional learned vectors average frozen pair-network hidden features across measured references within each ensemble member. Member summaries are concatenated, normalized, projected to the configured dimension and transformed by tanh. Only the projection and actor learn during policy optimization. Predictors are shared across feature arms.

## Batch selection

The default batch sizes are 1, 2 and 5; any positive configured size is supported. The complete subset is selected before any of its outcomes are revealed. Deep Sets and pair-aware Transformers score subsets, followed by beam and swap search. Gumbel top-k trains with a relaxed objective and evaluates with hard distinct selections. Batch PPO constructs the subset autoregressively with pending selections and delayed feedback. Its return counts acquisition rounds.

Joint GP covariance includes independent observation noise and uncertainty in the unknown series offset. Its diagonal is tested against the ordinary marginal GP. Ensemble covariance includes between-member mean differences. Joint EI samples this covariance. Mean-fantasy EI conditions on hypothetical observations equal to their posterior means.

Batch inputs include projected query/reference embeddings, posterior utility mean, standard deviation, incumbent, GP prior mean difference, a zero-valued separate delta-uncertainty feature, and log EI. The historical study used recorded separate delta features. Setting `dimension` to zero removes direct embeddings while retaining structure-derived pair relations containing correlation, molecular distance, and mean difference.

Evaluation reports rounds and total purchased compounds to any top-1 through top-4 target. Every molecule in the successful final batch counts. Each evaluation records analytic random expectations. The current batch recipe trains each configured architecture with fixed settings and validates its checkpoint; historical recipes used screening and supervised warm starts.

## Running the comparisons

Edit the corresponding JSON recipe. Outputs go into separate directories under the configured workspace artifact root.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_policy_comparison.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_acquisition_feature_comparison.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_reference_ablations.py
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_batch_comparison.py
```

Recreate archived figures without training.

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/make_historical_figures.py
```

Compare performance within each study's target scaling, calibration, predictor training allocation, and selection protocol. Newly trained results use separate output directories.
