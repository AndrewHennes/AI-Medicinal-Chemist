# Policy optimizers and auxiliary GP pair supervision

This is a two-by-three experiment. The GP is either the preceding frozen neural-mean/conventional-kernel model, or the same architecture retrained with an auxiliary Gaussian pair likelihood. The acquisition policy uses PPO, TRPO, or a trajectory-preference DPO adaptation. Six endpoints, five existing grouped folds, three policy seeds, and the same held-out starting hits are retained. GP seed 11 is fixed to isolate policy optimization.

A pool with n compounds is selected with probability proportional to n; an unordered pair is then uniform within that pool, with a random orientation. Thus per-pair sampling mass is proportional to n / binom(n,2). Total auxiliary supervision grows linearly, rather than quadratically, with series size. Sampling units are the existing endpoint/species series pools. No additional importance weight is applied after this sampling, because doing so would double-correct the distribution.

The GP auxiliary loss is marginal Gaussian negative log likelihood of the transformed, scaled within-series difference. Its mean is the original concatenated-pair neural network and its variance is K_ii + K_jj - 2 K_ij, including the molecule-level nugget. Both mean and covariance parameters receive gradients. This loss is added to the original conditional Gaussian likelihood with validation-selected weight 0.1, 0.3, or 1.0, using 64 additional pairs per step. The original mean warm-up and 2400 training steps remain fixed, and the main sampler's random stream is unchanged. Only predictor-role training pools supply pairs. No sign-consistency or cycle-consistency loss is added.

Each GP/endpoint/fold/seed shares a supervised starting policy and fixed actor architecture. PPO and TRPO use the same actor and critic forward maps with detached actor features during critic training. Historical PPO is reported separately.

TRPO uses conjugate gradients, exact autograd KL Hessian-vector products, damping, and backtracking constrained by empirical mean KL and surrogate improvement. DPO uses complete acquisition trajectories from a frozen warm policy, pairing rollouts from the same initial context and preferring fewer purchases to the first optimum. Tied pairs are discarded. Standard reference-relative logistic DPO uses summed action log probabilities without length normalization. A temperature of 1.5 generates diverse offline rollouts; reference probabilities use the original temperature. Policy labels and DPO preferences come only from policy-role training series.

Four configurations per optimizer receive 60 screening iterations. Two finalists per GP/optimizer/endpoint/fold receive 400 iterations, then validation selects a configuration for two additional seeds. Budget iterations generate eight rollouts; DPO caches preferences and performs two minibatch updates. Compute and transition counts are recorded by method.

Acquisition results report purchases to top-1 through top-4, with a ≥15-compound primary population and size-cutoff curves. GP diagnostics cover prediction, context learning, and calibration. Linked-group intervals average seeds and starting hits. Holm adjustment covers seven primary exploratory comparisons.

The absolute entry point needs no command-line options:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_policy_optimization/run_experiment.py
```

All products are written under `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_policy_optimization`. CPU execution uses eight worker processes. `progress.json` records the policy stage; `gp_progress.json` records GP training. Completed jobs are reused. Models and sources are hashed before final test evaluation. The final PDF is `reports/policy_optimization_and_gp_auxiliary.pdf`.

References: Schulman et al., *Trust Region Policy Optimization* ([paper](https://proceedings.mlr.press/v37/schulman15.html)); Rafailov et al., *Direct Preference Optimization* ([paper](https://arxiv.org/abs/2305.18290)).
