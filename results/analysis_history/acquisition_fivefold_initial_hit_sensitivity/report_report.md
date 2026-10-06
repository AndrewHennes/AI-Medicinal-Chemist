# Initial-hit sensitivity

Single-task comparison on all six endpoints. All 4,625 pools are evaluated once across five grouped outer folds, with four starting-hit draws per pool. The two neural acquisition processes (NAPs) each average three training seeds. Delta greedy and Gaussian process expected improvement (GP + EI) use one fit per fold.

The initial hit is selected uniformly from max(1, floor(n*p/100)) of the worst compounds in a pool of n. Ties in this eligible set are randomized. Percentages can give the same eligible set for small pools. The same latent random draws are used across percentages and all methods; a new evaluation bank is also used for the existing 50% models, so their values may differ slightly from the earlier PDF.

Solid curves use models trained at the test starting-hit fraction. Dashed curves keep the existing 50%-trained model fixed while changing only the test initial-hit distribution. Comparing solid and dashed curves at the same percentage isolates the retraining effect on identical starts. Comparing different percentages also changes the difficulty of the task.

Training budgets, architectures, preprocessing, outer/inner splits and model-selection rules are unchanged. Sampling-dependent fits are repeated for 10, 20, 30 and 40%; the pairwise delta predictor is reused. Checkpoints are locked before outer-test scoring. Endpoints retain their existing transformed, oriented outcomes and all observations are relative to the initial hit.

Only additional purchases to reach any top-1, top-2, top-3 or top-4 compound are shown. The initial hit is free; an already qualifying hit gives zero. Boundary ties qualify. Top-4 is necessarily zero for pools of three or four. Random is the exact expectation, not a simulated trajectory. Lower is better.

Starts are averaged within pool and seed, then seeds, then pools within endpoint; overall curves weight endpoints equally. These are descriptive internal cross-validation results. Outer training sets overlap, and related experimental conditions are compared on the same held-out pools. No architecture is chosen using these test results.

Files: starting_hit_sensitivity.pdf; all_fractions_minimum_pool_cutoff.pdf; pool_metrics.csv; paired_retraining_purchase_differences.csv.
