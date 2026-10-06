# Auxiliary top-k acquisition tasks

Completed and verified. All 180 policy fits, 150 jobs, five grouped folds, and six endpoints finished. All 180 prediction-pretraining or controller-warmstart checkpoints exactly matched their controls before auxiliary training, excluding the added heads. The original five methods' reported metrics are unchanged.

[Full PDF](</Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_topk_auxiliary/reports/topk_auxiliary_all_endpoints.pdf>) · [Detailed results](</Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_topk_auxiliary/reports/results.md>) · [Paired differences and intervals](</Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_topk_auxiliary/reports/paired_purchase_differences.csv>)

This experiment adds top-2, top-3, top-4, top-5, and top-6 action-cost prediction tasks to both single-task neural acquisition process (NAP) architectures. The primary policy continues to minimize purchases to any top-1 compound using clipped Proximal Policy Optimization (PPO).

For an observed state after \(t\) purchases and the next action actually sampled in its training rollout, the target for head \(k\) is

\[
c_{t,k}=\frac{\max(\tau_k-t,0)}{n-1-t},
\]

where \(n\) includes the free initial hit and \(\tau_k\) is the first purchase that reaches any top-\(k\) compound. Initial hits that already qualify have \(\tau_k=0\). Outcome ties at the rank threshold qualify. Heads with \(k\ge n\) are masked because the initial hit automatically solves those tasks. Success already achieved in larger pools remains a valid zero target. The auxiliary score in purchase units is the negative predicted fraction multiplied by the remaining candidate count.

These targets estimate continuation costs under the current top-1 behavior policy. They are not optimal action values for independently trained top-k policies. No target is assigned to an action that was not sampled. Full label vectors are used only to build training targets after the acquisition rollout, never as model inputs.

The old NAP adds five sigmoid outputs from its existing 96-dimensional acquisition hidden representation. The new NAP adds a small five-output network taking the existing 32-dimensional mixture-gate hidden representation and five candidate expert ranks. Both auxiliary losses therefore train the actor representation, rather than a disconnected critic. Existing revised-NAP forecasters remain frozen. Head initialization preserves the original random-number stream.

The added loss is squared error in normalized cost, averaged within each represented head and then across heads, with coefficient 1.0 fixed before evaluation. The original policy and prediction losses remain unchanged. Auxiliary heads are trained only during PPO, after the unchanged prediction pretraining or controller warm start. Only the main acquisition score chooses purchases at evaluation.

The study uses six endpoints, five existing grouped folds, three policy seeds, and the same four worst-half single-hit evaluation starts per pool. Both NAPs are refitted with the original training budgets and validation selection rules. Frozen delta models, Gaussian processes and group-excluded neural forecasters are reused. Training pools remain complete; this experiment does not add multi-hit or top-removal augmentation.

The report compares the original methods and auxiliary variants using purchases to top-1 through top-4, for all eligible pools, pools ≥15, and size-cutoff curves. Source-group bootstrap intervals are conditional on fitted models and unadjusted for multiple comparisons.

Code and outputs remain under `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_topk_auxiliary`. The experiment runner uses absolute paths and writes all artifacts here. `unit_verification.json` checks target semantics, ties, masking, action-specific supervision, shared gradients, frozen forecasters, and identical original forward outputs. `smoke_verification.json` records the separate two-iteration end-to-end check. `experiment_plan.json` fixes the experiment before test scoring. `completed.json` and `completion_audit.json` are written only after the benchmark and report checks finish.
