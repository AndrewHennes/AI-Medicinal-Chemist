# When the new NAP differs from delta greedy

The analysis uses the existing unaugmented new NAP. No models were retrained. Each comparison gives NAP and delta greedy the identical measured context. The recorded NAP action is compared against the full set of delta-mean minimizers, so arbitrary tie-breaking is not counted as a disagreement.

All 148,476 replayed actions before top-1 success matched their saved trajectories, and every score was reconstructed from its five weighted ranks. All 4,625 held-out pools, five folds, three seeds and four starts were included. Primary results below use the 580 pools with at least 15 compounds. Forced last-candidate choices are excluded from decision summaries.

| Endpoint | First purchase differs (%) | All decisions differ (%) | Same as GP+EI (%) | Same as GP mean greedy (%) |
| --- | --- | --- | --- | --- |
| Microsomal clearance | 64.881 | 70.089 | 44.242 | 41.267 |
| In vivo clearance | 78.750 | 86.553 | 45.523 | 38.537 |
| Protein binding | 55.303 | 60.514 | 24.809 | 25.185 |
| Cellular clearance | 74.684 | 78.843 | 41.644 | 36.491 |
| Permeability | 68.866 | 73.791 | 36.809 | 36.952 |
| Efflux | 57.716 | 67.652 | 34.192 | 31.985 |

The acquisition score is

$$s(a\mid S)=T(S)\sum_j w_j(S)r_j(a\mid S),$$

where the five ranks correspond to GP expected improvement, GP mean, delta mean, neural expected improvement and GP standard deviation multiplied by average absolute posterior correlation with other candidates. The positive temperature does not change deterministic ranking. The context-dependent weights use observed progress, incumbent, pool size, spreads, disagreement and endpoint identity. There is no explicit tree search.

Largest positive rank contribution supporting the NAP action over the greedy representative, among disagreements:

| Endpoint | GP expected improvement | GP predicted mean | Delta predicted mean | Neural expected improvement | GP information heuristic |
| --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 94.344 | 0.175 | 0.000 | 2.386 | 3.095 |
| In vivo clearance | 80.193 | 0.037 | 0.000 | 4.884 | 14.886 |
| Protein binding | 78.100 | 0.200 | 0.000 | 9.191 | 12.508 |
| Cellular clearance | 73.110 | 0.000 | 0.000 | 12.519 | 14.371 |
| Permeability | 89.039 | 0.000 | 0.000 | 3.227 | 7.735 |
| Efflux | 81.103 | 0.079 | 0.000 | 10.333 | 8.485 |

Additional same-state diagnostics among disagreements:

| Endpoint | gp_prefers_nap_to_delta | GP_uncertainty_tradeoff | nap_more_GP_uncertain | farther_from_observed | delta_top3 |
| --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 93.502 | 40.077 | 53.837 | 55.358 | 40.145 |
| In vivo clearance | 90.003 | 35.912 | 51.042 | 51.758 | 38.444 |
| Protein binding | 92.699 | 33.704 | 46.843 | 47.372 | 43.233 |
| Cellular clearance | 90.705 | 44.526 | 53.217 | 50.932 | 31.816 |
| Permeability | 93.067 | 38.703 | 55.975 | 55.403 | 46.475 |
| Efflux | 89.804 | 34.072 | 59.066 | 62.212 | 48.201 |

The GP uncertainty tradeoff compares the NAP action with the GP-mean-minimizing candidate, using predicted mean and standard deviation. The information score is a posterior-correlation heuristic. Embedding distance is reported descriptively.

Purchase-count comparisons for pools with at least 15 compounds:

| endpoint | pools | greedy_tau | nap_tau | policy_savings_vs_greedy | policy_savings_vs_greedy_low | policy_savings_vs_greedy_high | override_effect | override_effect_low | override_effect_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 311 | 5.695 | 5.400 | 0.296 | -0.305 | 0.838 | -0.100 | -0.326 | 0.089 |
| In vivo clearance | 20 | 9.762 | 9.600 | 0.163 | -2.792 | 2.820 | -0.958 | -2.795 | 0.644 |
| Protein binding | 44 | 6.909 | 6.716 | 0.193 | -1.295 | 1.896 | -0.616 | -1.684 | 0.093 |
| Cellular clearance | 79 | 6.826 | 6.500 | 0.326 | -0.815 | 1.675 | 0.044 | -0.254 | 0.351 |
| Permeability | 72 | 9.802 | 8.127 | 1.675 | 0.442 | 2.987 | 0.166 | -0.162 | 0.417 |
| Efflux | 54 | 7.116 | 6.858 | 0.258 | -0.855 | 1.403 | -0.398 | -1.088 | 0.187 |

The override replaces the first strict disagreement with a delta-greedy action and then resumes NAP. Positive effects indicate more purchases under the override. Cases without disagreements have effect zero. Starting-hit and outcome conventions are fixed.

Decision summaries weight pools equally, then starts and seeds within pool, then eligible states within trajectory. Conditional summaries restrict those weights to disagreements. Paired source-group intervals use 5,000 draws, conditional on fitted models and without multiplicity adjustment.

Replay uses the historical case bank and analyzes its worst-half subset. Counterfactual branches use isolated copies of prediction caches.
