# Joint GP and PPO training

This experiment trains the neural pair-difference mean, conventional Gaussian process (GP) covariance parameters, and acquisition policy together. The new networks start with random weights. There is no predictor warm-up or expected-improvement (EI) imitation. Fixed MiniMol representations, training-fitted principal components, endpoint transforms, and outer grouped folds are retained.

The policy uses predicted utility mean, standard deviation, incumbent, normal cumulative probability, and normal density, with the previous pool summaries and count features. It selects one compound at a time. Each acquisition has reward minus one, including the successful acquisition. The initial hit is free. Training stops when any compound tied for the pool optimum is acquired.

Every PPO optimizer step recomputes GP predictions from raw molecular contexts. PPO gradients can update the mean network and kernel through differentiable conditioning. An on-policy Gaussian prediction loss supervises the outcome of each purchased compound using its pre-purchase context. An additional auxiliary loss supervises randomly sampled pair differences. Its tested relative weights are 0, 0.1, 0.3, 1, and 3. The critic is separate and receives detached features.

A training series is selected for an off-policy example with probability proportional to its number of compounds. A distinct pair is then selected uniformly with random orientation. Total pair exposure is therefore proportional to the number of compounds rather than the number of available pairs. No sign-consistency loss is used.

All new variants use the same existing selector-role training series for both trajectory and pair supervision. This makes the auxiliary-weight comparison controlled. The historical frozen-GP references used a predictor trained on the separate predictor-role series, so those pipeline comparisons also differ in allocation of training labels.

The benchmark covers all six endpoints, five grouped folds, three final model seeds, and four common initial hits. Primary evaluation uses deterministic actions and pools with at least 15 compounds. The report retains pools with at least three compounds and acquisition counts to any top-1 through top-4 compound. Analytic EI on each jointly trained GP separates predictor performance from learned acquisition behavior. A separate diagnostic uses sampled actions, as PPO does during training.

Predictive evaluation keeps a fixed query set hidden while increasing the number of local measurements. For every pool with at least 15 compounds, the same five targets are predicted with 1, 2, 3, 5, and 10 measured compounds. Metrics include relative-outcome R², within-pool Spearman correlation, Gaussian negative log likelihood, root mean squared error, and interval coverage. Joint models use raw uncertainty; the historical GP retains its previous validation-fitted variance factor. No calibration factor is fitted to the test set. Prediction references are sampled independently of outcomes, whereas acquisition starts come from the worse half of a pool.

The search is specified in `protocol.json`. Three coupled model/optimizer configurations are screened per auxiliary weight. Two finalists receive 600 PPO updates; the selected configuration repeats at two further seeds. Each weight is reported separately, along with a positive weight selected using validation results only. Initial checkpoints are excluded from PPO model selection.

The completed primary benchmark contains 580 pools with at least 15 compounds in 334 linked groups. Off-policy weights 0, 0.1, 0.3, 1, and 3 required 6.108, 6.109, 5.918, 5.810, and 5.693 purchases to the optimum, respectively. Weight3 reduced purchases by 6.80% versus zero weight, with a 95% interval of 3.64% to 9.98% and primary Holm-adjusted p=0.012. Weight1 also passed the primary correction. The validation-selected positive-weight pipeline required 5.888 purchases, and its improvement over zero did not pass that correction (p=0.075).

Analytic EI using the jointly trained weight3 GP required 5.391 purchases, compared with 5.693 for its learned policy and 5.525 for historical GP plus EI. The additional exploratory GP-versus-GP comparison had a 95% improvement interval from -2.22% to 7.05%. The prespecified validation-selected comparison favored analytic EI over PPO on the same joint GP (adjusted p=0.008).

With only the reference measured, adding weight3 changed prediction R² from -0.436 to -0.011 and 95% interval coverage from 81.4% to 90.1%. At ten measurements, R² changed from 0.565 to 0.580.

Main outputs:

- `reports/joint_GP_PPO_off_policy_delta_report.pdf` contains endpoint charts, paired acquisition effects, prediction learning curves, and calibration.
- `reports/summary.csv` contains acquisition outcomes by endpoint and pool cutoff.
- `reports/paired_comparisons.csv` contains paired group-bootstrap intervals and primary Holm-adjusted p values.
- `reports/prediction_summary.csv` contains predictive metrics by measured-context size.
- `reports/selected_auxiliary_weights.csv` contains validation-selected weights.
- `reports/pool_metrics_by_seed.csv.gz` preserves acquisition results by pool and model seed.
- `reports/audit.json` and `tests.json` record verification results.

The scripts have no command-line options and resolve paths absolutely. To resume training from any working directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/joint_gp_ppo/run_experiment.py
```

After evaluation completes, generate the report:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/joint_gp_ppo/joint_report.py
```
