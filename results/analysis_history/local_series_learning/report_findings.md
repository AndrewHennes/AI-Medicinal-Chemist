# Local series learning and useful experiments

## Fixed-query learning curves

580 held-out pools with ≥15 compounds, ten random reveal orders per pool, five compounds held hidden throughout, existing five grouped folds. No new fitting. Equal weighting of endpoint means.

| Pipeline | Predictor | 1 measured | 2 | 3 | 5 | 10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Pooled species | Delta mean | 0.217 | 0.223 | 0.223 | 0.222 | 0.224 |
| Pooled species | Gaussian process | 0.122 | 0.147 | 0.168 | 0.193 | 0.254 |
| Pooled species | Neural forecaster | 0.083 | 0.099 | 0.100 | 0.104 | 0.106 |
| Species-specific heads | Delta mean | 0.228 | 0.229 | 0.228 | 0.227 | 0.229 |
| Species-specific heads | Gaussian process | 0.106 | 0.118 | 0.140 | 0.176 | 0.229 |
| Species-specific heads | Neural forecaster | 0.083 | 0.089 | 0.091 | 0.091 | 0.094 |

The pooled Gaussian-process gain from one to ten measurements is +0.133 Spearman rho [0.106, 0.160]. The pooled neural forecaster gains +0.024 [0.001, 0.047], but its actual-minus-expected-outcome contribution is −0.004 [−0.015, 0.005]. The delta mean cannot alter rankings in response to numerical anchor values because their average is a common offset for every query.

## Can an unsuccessful molecule be useful?

Among disappointing reveals, 15.6% [13.7%, 17.4%] meet the informative-reveal criterion for the pooled Gaussian process, versus 7.9% [6.4%, 9.5%] for the pooled neural forecaster. The criterion requires at least +0.10 concordance versus both the original context and the expected-outcome control.

In the retrospectively selected rat microsomal series 1593 example, the initial hit has clearance 88 µL/min/mg. A revealed compound measures 690 despite a prediction near 43.5. The pooled neural forecaster's hidden-set rho increases from 0.00 to 0.90, and the next choice changes from clearance 72 to 19. Adding the same structure with its expected outcome leaves rho at 0.00. A separate compound with clearance 15 is excellent but leaves the hidden-set ranking unchanged.

## Does a locally observed chemical effect transfer?

Across 934 pools containing eligible disjoint repeated-substitution pairs, pooled Gaussian-process direction accuracy improves from 54.5% to 60.7%. The outcome contribution is +6.25 percentage points [4.52, 8.28]. Pooled neural accuracy changes from 54.5% to 54.7%, with outcome contribution +0.86 points [−0.06, 1.81].

In the model-dependent subset with an initially near-null predicted effect and a surprising measured pair, pooled GP accuracy increases from 52.3% to 68.3% across 392 pools.

An illustrative human microsomal series has methyl-to-chlorine substitutions. Historical mean effect across 34 training source groups is +0.030 log10 clearance. Measuring one local pair reveals a −0.640 effect. The GP changes its prediction for a disjoint hidden pair from +0.005 to −0.203; the true hidden effect is −1.033. It learns the favorable direction while underestimating its magnitude.

## Scope

These diagnostics evaluate frozen prediction means. The NAP policy also uses GP and delta experts. Confidence intervals use 2,000 source-group resamples shared across endpoints, conditional on fitted models. Structures alone select matched-pair cases, and historical effects use training labels. Smaller fixed-cohort panels contain 1,041 pools of size 5–7 and 880 pools of size 8–14.
