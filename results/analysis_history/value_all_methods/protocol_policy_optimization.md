# Policy optimization in the acquisition benchmark

The original and revised neural acquisition process (NAP) policies use clipped Proximal Policy Optimization (PPO), with a learned critic. The model architecture specifies how observations become purchase scores. PPO specifies how sampled acquisition outcomes change those scores through weight updates.

For a trajectory that reaches a best compound after \(\tau\) purchases, the return at the state after \(t\) purchases is

\[
G_t=-\max(\tau-t,0).
\]

The policy receives measured outcomes during a rollout. Complete training-series labels are used afterward to compute this return. Hidden success is not an input to the acquisition policy. The advantage is \(A_t=G_t-V_{\mathrm{old}}(s_t)\), followed by batch scaling and, for configured revised variants, centering. These are undiscounted Monte Carlo returns, without generalized advantage estimation.

With \(r_t=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)\), the core policy loss is

\[
\mathcal{L}_{\mathrm{policy}}=-\mathbb{E}\left[\min\left(r_tA_t,\operatorname{clip}(r_t,0.8,1.2)A_t\right)\right].
\]

The implementation also scales this loss by the mean number of retained states per sampled episode. Clipping modifies the optimization objective; it is not a hard guarantee that every probability ratio remains inside those bounds. The loss includes a critic regression term with weight 0.25 and an entropy bonus with weight 0.01. AdamW performs the weight updates, with a policy learning rate of 0.0001 and gradient norm clipping at 1. Each iteration collects eight episodes and runs three optimization epochs with state minibatches of up to 64. Single-endpoint training uses 500 policy iterations. Validation selects the saved checkpoint.

The original NAP first learns to predict outcomes and retains an auxiliary prediction loss during PPO. The revised cross-fitted NAP freezes its forecasters, warm-starts its acquisition controller where configured, and uses PPO to update its controller and critic without the auxiliary forecaster loss. Some revised configurations retain only states before the first optimal acquisition for optimization, after generating the full trajectory.

The PPO critic predicts the return of the current policy to provide a training baseline. At evaluation, NAP uses its policy head to choose purchases. The new value models instead learn action costs through Double-Q updates and use those costs directly for selection or as continuation estimates in planning. Delta greedy uses supervised difference prediction, and Gaussian process plus expected improvement uses a fitted predictive distribution and a fixed acquisition formula. Neither baseline has a policy-gradient update.

Group Relative Policy Optimization (GRPO), Trust Region Policy Optimization (TRPO), and Direct Preference Optimization (DPO) have not been used in these comparisons. GRPO uses groups of sampled outcomes for the same problem to form its baseline. TRPO uses a constrained policy update. DPO uses preferred and dispreferred outcomes rather than the actor–critic update above. Applying any of these here would be a separate experiment, with architecture, reward, data splits and rollout budget controlled.

The PPO algorithm is described by Schulman and colleagues ([paper](https://arxiv.org/abs/1707.06347)). GRPO is introduced in DeepSeekMath ([paper](https://arxiv.org/abs/2402.03300)). The other algorithms are described in Trust Region Policy Optimization ([paper](https://arxiv.org/abs/1502.05477)) and Direct Preference Optimization ([paper](https://arxiv.org/abs/2305.18290)).

Implementation references are the [original NAP updates](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/initial_hit_sensitivity/worst_50/fold_0/in_vivo_clearance/outputs/multitask_acquisition/train_models.py:180), [revised NAP updates](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/initial_hit_sensitivity/worst_50/fold_0/in_vivo_clearance/outputs/nap_multitask_crossfit/train.py:168), and [training settings](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/initial_hit_sensitivity/worst_50/fold_0/in_vivo_clearance/outputs/multitask_acquisition/settings.py:26).
