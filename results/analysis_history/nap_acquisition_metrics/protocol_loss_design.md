# Acquisition objectives and training changes

The existing reinforcement-learning loss minimizes purchases to the exact optimum. This document defines alternative normalized discovery, regret-area, and fixed-budget success objectives.

No model was retrained for this analysis. Existing training sources and checkpoints are unchanged. The accompanying objective_rewards.py contains standalone, tested offline reward prototypes for a later controlled experiment.

## What the current code actually trains

The original and revised proximal policy optimization (PPO) implementations use undiscounted return

\[
G_t=-(T-t+1),\qquad t=1,\ldots,T.
\]

The code uses a zero-based index, so this appears as -max(tau-step,0). This correctly charges for the successful purchase. Original training includes the remaining post-optimum states with zero returns. Crossfit training masks these states with preopt_only=True, retaining the successful action. Acquisition rollouts still acquire the full pool and are scored afterward, so unknown optimum status is not supplied to the deployed policy.

The actor uses the clipped PPO surrogate, the critic fits returns, and prediction cross-entropy and entropy bonuses supplement some variants. The current crossfit controller freezes its forecasters and skips auxiliary prediction updates during PPO. Its supervised warm start has a best-query listwise cross-entropy term. Prediction cross-entropy is also numerically present, but contributes no gradient through those frozen forecasters. Its nonterminal state sampler excludes already measured global optima, making the best remaining candidate a global optimum in those warm-start states.

The actor reward is raw purchase count, while checkpoint selection uses an endpoint-averaged ratio to random. The listwise warm-start objective targets immediate optimum selection. The optional `reward_shaping` adjustment uses the normalized incumbent gap and preserves the undiscounted terminal objective.

The potential-shaping interpretation follows from the usual telescoping construction in Ng, Harada, and Russell ([paper](https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf)). The clipped-surrogate framework comes from Schulman et al. ([PPO paper](https://arxiv.org/abs/1707.06347)). The proposed metric-specific rewards below are direct derivations for this dataset.

Audited locations

- [Crossfit returns and sampling](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/train.py:10)
- [Crossfit validation selection](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/train.py:96)
- [Crossfit PPO reduction and auxiliary terms](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/train.py:156)
- [Shared supervised objective](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_recovery/architectures.py:197)
- [Mixture-controller critic range](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_mixture/architectures.py:65)
- [Original PPO return construction](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multitask_acquisition/train_models.py:180)

## Candidate 1: normalized discovery cost

Let \(n\) include the initial hit, \(k\) be the number of tied global optima remaining, and \(\bar T_0=n/(k+1)\) the exact expected number of purchases for random sampling. On eligible starts,

\[
E=\frac{\bar T_0-T}{\bar T_0-1}.
\]

Use

\[
r_t=-\frac{1}{\bar T_0-1}\quad (t\leq T),
\qquad r_t=0\quad(t>T).
\]

The sum of rewards plus the initial-state constant \(\bar T_0/(\bar T_0-1)\) equals \(E\). That constant is unnecessary for the actor gradient. The successful purchase must receive its cost. Keep \(\gamma=1\); discounting costs would change the objective.

Exclude starts already at the optimum and cases with \(\bar T_0=1\) from this objective's target population. With a unique optimum, efficiency lies between -1 and 1. With tied optima the negative bound can extend below -1, so do not silently clip the metric or assume a universal bounded critic target.

This is the smallest conceptual change from the existing objective. It aligns the cross-series weighting with discovery efficiency. It does not make within-series stopping times more granular.

## Candidate 2: dense regret-area training

For \(m=n-1\) available purchases, let \(H=m-1=n-2\). With transformed outcomes oriented toward minimization,

\[
R_t=\frac{b_t-y_*}{y_{\mathrm{reference}}-y_*},
\qquad
A=\frac{1}{H}\sum_{t=1}^{H}R_t.
\]

Use the post-purchase reward

\[
r_t=-R_t/H,\quad 1\leq t\leq H.
\]

The undiscounted return at the initial state is exactly \(-A\). It credits useful improvements before finding the exact optimum. The final purchase carries no regret-area weight because it guarantees exhaustion. If the optimum is found earlier, subsequent regret is zero; the successful action remains in the training trajectory even when its immediate penalty is zero.

An equivalent positive-improvement formulation is

\[
\widetilde r_t=\frac{H-t+1}{H}(R_{t-1}-R_t),
\qquad
\sum_{t=1}^{H}\widetilde r_t=1-A.
\]

The time weights are essential. Unweighted improvements summed through exhaustion telescope to \(R_0-R_m=1\), providing no preference between orderings. Potential shaping alone also cannot turn a purchase-count objective into regret area.

Normalize by the gap to the initial hit, as in evaluation. Exclude zero-gap starts. If a minimum assay-relevant gap is later introduced, declare it before fitting and report how many series it removes. Do not silently substitute an epsilon denominator or clip targets and then claim exact alignment with the original metric. With positive gaps, \(R_t\in[0,1]\) algebraically; the concern in almost-flat series is sensitivity to measurement noise in the tiny observed differences.

For a one-step supervised warm start, an additional loss

\[
\mathcal L_{\mathrm{one\ step}}
=\sum_{a\in\mathcal U}\pi_\theta(a\mid s)
\frac{\min(b,y_a)-y_*}{y_{\mathrm{reference}}-y_*}
\]

gives each candidate credit proportional to its incumbent regret after purchase. This is an exact expected one-step regret objective in an offline labeled training state. It is still myopic. Follow it with the full regret-area PPO objective to train information-seeking choices whose benefits appear later. All action labels in this loss are training targets only.

This is the first alternative I would test because it adds feedback that the existing optimum-classification and hitting-time objectives omit.

## Candidate 3: success at one or two purchases

For a fixed budget \(B\), maximize

\[
S_B=\mathbf 1[T\leq B].
\]

Reward the first optimum purchase with 1 if it occurs by \(B\), otherwise give zero reward. Terminate the training objective after success or after \(B\) actions, with \(\gamma=1\). Giving the success reward early is equivalent to paying it at budget \(B\) only because it is undiscounted. Rewarding every post-success step would instead reward earlier discovery and change the objective.

For the informative comparison, exclude already-optimal starts and pools where random succeeds with probability 1. With \(m\) available molecules and \(k\) optima, random succeeds by \(B\) with probability

\[
1-\frac{\binom{m-k}{B}}{\binom mB},
\]

interpreting the numerator as zero when \(B>m-k\), and capping budget at pool exhaustion. In particular, success by purchase 2 is inevitable in a three-compound pool. Include those cases separately in descriptive inclusive rates, but they contribute no action-dependent signal for this objective.

At budget 1, the existing best-query cross-entropy can be made exactly tie-aware for the event of success by using

\[
\mathcal L_{\mathrm{hit}}
=-\log\sum_{a:y_a=y_*}\pi_\theta(a\mid s).
\]

Current cross-entropy against a uniform distribution over tied optima also encourages equal probability among equally successful actions. The event loss only rewards their total probability. Both coincide for a unique optimum. Train this on initial states for the hit-at-one objective; sampling arbitrary measured sets changes the training-state distribution.

This log loss is a classification surrogate, not an exact replacement for the aggregate mean success objective under a restricted model. An exact expected one-step success loss is \(-\sum_{a:y_a=y_*}\pi_\theta(a\mid s)\). The log form often gives a larger gradient when optimum probability is small; its usefulness must be checked on validation performance.

At budget 2, immediate optimum classification misses the possible value of measuring an informative compound first. A short-horizon PPO rollout can capture this tradeoff. If one shared policy is intended to handle different budgets, supply the remaining budget, and optionally an objective identifier, as an observed input. Otherwise train separate fixed-budget policies. Adding an unknown optimum or true regret to the policy inputs is not permissible.

## Required accompanying implementation changes

**Critic.** Use a scalar critic with a range appropriate to the selected objective. An unconstrained scalar supports the initial controlled ablation. A sigmoid output represents success probability, and a negative sigmoid can represent negative regret area. Reinitialize the critic when changing objectives.

**Sampling and actor reduction.** Sample endpoint, pool, and allowed starting hit in the same hierarchy as the reported metric aggregation. If reporting a size-balanced summary, explicitly sample size bins with those weights or use fixed importance weights. Source-group bootstrap units for uncertainty do not require equal-group training weights unless that is also the chosen target population.

For equally weighted sampled episodes, the actor surrogate is

\[
-\frac{1}{B_{\mathrm{episodes}}}
\sum_i\sum_{t\in\mathcal T_i}
\min\!\left(\rho_{it}\widehat A_{it},
\operatorname{clip}(\rho_{it},1-\epsilon,1+\epsilon)\widehat A_{it}\right).
\]

Sum action terms within each episode. For the controlled ablation, collect a fixed episode batch and accumulate the surrogate gradient over state chunks before one optimizer step per PPO epoch. Set critic and entropy weighting explicitly, for example using per-episode mean losses.

Use the chosen metric's eligible population for sampling and validation. Do not use one common exclusion mask for all three metric families. In particular, a positive-gap pool in which all remaining compounds are optimal has undefined normalized discovery efficiency but valid regret area zero.

**Magnitude and regularization.** Current advantages and critic returns use a batch standard deviation with a floor of 1. The critic and entropy coefficients are 0.25 and 0.01. Use one batch-level scale and choose coefficients using validation data. Inspect actor, critic and entropy gradient magnitudes and compare each change with the raw-count control.

**Horizon and checkpoint selection.** Keep undiscounted Monte Carlo targets for these short finite pools in the first ablation. Remove post-objective decisions from actor and critic updates, while retaining the successful purchase. Continue full evaluation rollouts independently of oracle success. Select checkpoints on the same validation metric and aggregation used for the training target. Freeze the metric and weights before comparisons. Report all three metrics for every checkpoint so improvements in early regret can be distinguished from losses in exact-optimum discovery. Existing reused test cohorts remain exploratory.

## Bounded next experiment

Use the existing frozen crossfit forecasters and the same supervised controller initialization. Compare raw purchase cost, normalized discovery cost, regret-area cost, and budget-2 success with matched single-task and multitask controllers, the same rollout data budget, and three seeds. Preserve greedy delta and Gaussian-process expected improvement baselines. Start with regret area versus raw count if computational scope needs limiting.

A later multiobjective extension could optimize \(\alpha E+(1-\alpha)(1-A)\), or condition a policy on the desired objective. Choose \(\alpha\) before test evaluation and show the tradeoff; a combined reward does not optimize every metric independently. More objective terms are not themselves evidence of improvement.

## Verification

The accompanying test_objective_rewards.py exhaustively enumerates small-pool purchase orders with and without tied optima. It verifies reward sums, exact random expectations, successful-purchase indexing, budget eligibility, already-optimal starts, zero headroom, affine outcome invariance, the weighted-improvement identity, and episode-sum reduction. Nine tests pass. These are mathematical and implementation checks of isolated reward functions, not training results.
