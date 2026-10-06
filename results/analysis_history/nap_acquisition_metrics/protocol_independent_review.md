# Independent mathematical review

This review concerns evaluation of cached acquisition sequences. No models were trained or selected during this review.

## Setup and exact random expectations

Let the known reference have outcome \(y_r\), let \(y_*\) be the minimum in its pool, and let \(m=n-1\) unmeasured compounds remain. All endpoint outcomes are oriented so lower is better. Purchases are sampled without replacement under the random baseline. When the reference is not optimal and \(k\) remaining compounds achieve the exact minimum,

\[
\mathbb E[T_{\rm random}]=\frac{m+1}{k+1},\qquad
\Pr(T_{\rm random}\leq t)=1-\frac{\binom{m-k}{t}}{\binom mt}.
\]

Use zero for a binomial coefficient with an impossible upper/lower combination, and clamp the purchase budget to the available pool. If the reference is already optimal, the stopping time is zero and success at any nonnegative budget is one.

For an exact random regret baseline, sort the remaining outcomes as \(a_{(1)}\leq\cdots\leq a_{(m)}\). For \(1\leq t\leq m\),

\[
\mathbb E[b_t]=\sum_{j=1}^{m-t+1}
\min(y_r,a_{(j)})\frac{\binom{m-j}{t-1}}{\binom mt}.
\]

This formula remains correct with ties. For a positive reference gap \(g=y_r-y_*\),

\[
\mathbb E[R_t]=\frac{\mathbb E[b_t]-y_*}{g},\qquad
\mathbb E[A]=\frac{1}{m-1}\sum_{t=1}^{m-1}\mathbb E[R_t].
\]

The final exhausted-pool state is excluded because every method has zero regret there. A three-compound pool contributes one informative intermediate regret observation; it does not become devoid of signal.

## Eligibility and interpretation

- Discovery efficiency is undefined for an initially optimal reference or when every remaining compound is optimal. In the latter case, the random expectation equals one and its normalization denominator vanishes.
- With a unique optimum, discovery efficiency lies in \([-1,1]\). With \(k>1\) exact optima and a nondegenerate denominator, its minimum is \(-k\). Tied-optimum pools therefore have a potentially more asymmetric influence. Do not describe the metric as universally bounded by minus one.
- Normalized regret is undefined for an initially optimal reference. With any positive gap it lies in \([0,1]\). If all remaining compounds are optimal, its sequence average is validly zero for every policy; the case is nondiscriminating.
- Inclusive success at a fixed budget is valid even in guaranteed cases. For the primary opportunity-conditioned success result, additionally exclude initially optimal starts and cases whose random success probability is one. Explicitly label this conditioning and report its denominator. In particular, two purchases exhaust every three-compound pool.
- Retain exact outcome equality for identifying optima, matching the existing benchmark. A clinically or experimentally meaningful tolerance would be a new, separately specified metric.
- Small reference gaps make results sensitive to assay error. They do not make the bounded normalized regret numerically unbounded. No positive reference gap below 0.01 transformed units was present in the audited cached starts; six main-cohort starts had positive gaps below 0.05, and none in the reserved cohort did.

## Aggregation and uncertainty

Average repeated starts and available seeds within each pool before averaging pools within an endpoint. Macro-average endpoints so one endpoint's greater pool count does not set the objective implicitly. Report the size bins 3–5, 6–9, 10–14, and at least 15 separately. An additional summary can average size bins explicitly within endpoints, then average endpoints. State missing-bin handling.

All methods must use the same retained pool/start cases for a given metric and comparison. Eligibility follows the ground-truth pool and reference, never the policy's outcome. Exact random expectations eliminate simulation noise and should be aggregated over the identical retained cases.

Resample global source/provenance groups jointly across endpoints, maintaining the dependence between overlapping pools and repeated starts. Available training seeds can also be resampled, with matched seeds paired where appropriate.

The existing four sampled starts per pool should remain fixed for matched comparisons. They are not an exhaustive evaluation over all eligible starting molecules. Duplicate references in a small pool do not create independent observations.

## Independent examples

All examples below hold the first listed compound as the initial reference. Values were checked by enumerating all permutations of the remaining compounds.

| Outcomes | Random mean purchases | Random mean sequence regret | Success at 1 | Success at 2 |
|---|---:|---:|---:|---:|
| 5, 4, 3, 2, 1 | 2.5 | 0.2013888889 | 0.25 | 0.5 |
| 5, 1, 1, 4, 3 | 1.6666666667 | 0.1319444444 | 0.5 | 0.8333333333 |
| 2, 1, 1 | 1 | 0 | 1 | 1 |
| 1, 1, 2, 3 | 0 | Undefined | 1 | 1 |
| 5, 5, 1 | 1.5 | 0.5 | 0.5 | 1 |

For the first example, random normalized regrets after purchases one, two, and three are 0.375, 1/6, and 0.0625. For the second, they are 0.3125, 1/12, and zero. In the second example, first finding an optimum on purchase three gives discovery efficiency minus two, illustrating the tied-optimum bound.

## Audited cached case counts

The original shared-controller trajectory tables contain 2,028 distinct pool/start cases from 507 main-cohort pools, and 424 cases from 106 reserved-cohort pools.

| Case type | Main cohort | Reserved cohort |
|---|---:|---:|
| Initially optimal reference | 8 | 6 |
| Nonoptimal reference, all remaining candidates optimal | 30 | 6 |
| Starts in pools containing multiple exact optima | 144 | 32 |

These counts describe pool/start cases, not independent experimental units.
