# PPO acquisition benchmark, one compound per batch

This experiment trains the acquisition policy using proximal policy optimization (PPO) on complete retrospective searches. It reuses the frozen neural-mean Gaussian process (GP), molecular data, transforms, and grouped folds from the existing project. GP posterior predictions update after every revealed measurement; GP network and kernel parameters are not retrained here.

The candidate inputs are GP mean, GP standard deviation, best measured utility, the normal cumulative distribution function, and the normal density. Utility is relative to the original hit, with larger values preferable. The standardized gap is the mean minus incumbent divided by the standard deviation. A matched three-input control masks the last two feature channels. The existing invariant pool summaries and count inputs remain available.

Four arms cross these feature sets with two initializations. The first starts from a policy that ranks compounds by GP mean. The second starts from an actor pretrained to imitate normalized expected improvement (EI) scores. Each selected PPO model is compared with its exact initial weights. An initial checkpoint cannot be selected or labeled as a PPO result.

During PPO, actions are sampled from the current policy. Each purchase receives reward minus one, including the successful purchase. An episode ends when it finds any compound tied for the pool optimum. The initial hit is free. A transition's return is the negative number of purchases remaining in its sampled trajectory. These returns train a separate critic and drive the clipped likelihood-ratio actor loss. The critic cannot update actor weights directly. No EI imitation, optimum-membership classification, utility regression, or off-policy pair loss is used during PPO.

The primary evaluation uses deterministic highest-score actions, four common initial hits, three model seeds, and all six endpoints across five linked-series folds. Purchases to any top-1, top-2, top-3, or top-4 compound are reported; top-1 is the training objective. The main analysis emphasizes pools with at least 15 compounds. A separate diagnostic measures sampled-policy performance before and after PPO.

Six paired contrasts compare five versus three inputs within each initialization, each five-input PPO arm versus analytic EI, and each five-input arm versus initialization. Intervals resample linked groups after averaging starts and seeds. Holm adjustment covers the six pooled top-1 comparisons on this exploratory benchmark.

The algorithm follows Schulman et al., *Proximal Policy Optimization Algorithms* ([paper](https://arxiv.org/abs/1707.06347)). The full implementation and search settings are in `ppo_core.py` and `protocol.json`.

The sampled-policy diagnostic uses sampled actions and the first common hit. The primary benchmark uses deterministic actions and four starting hits.

Files produced by the experiment:

- `tests.json` records trajectory, loss, masking, gradient, and evaluator checks.
- `source_lock.json`, `reference_lock.json`, and checkpoint locks record artifact hashes.
- `selected.json` records validation-selected hyperparameters.
- `training_completed.json` records all 360 final PPO fits.
- `evaluation/` contains measured acquisition counts and diagnostics per fold, endpoint, arm, and seed.
- `reports/PPO_normal_CDF_density_K1_report.pdf` contains the results and endpoint charts once evaluation and reporting finish.
- `reports/summary.csv` and `reports/paired_comparisons.csv` contain the aggregate results and paired statistics.
- `reports/pool_metrics_by_seed.csv.gz` preserves pool-level results by model seed.
- `reports/selected_training.csv` includes selected checkpoint steps and actual trajectory counts.
- `reports/audit.json` verifies coverage, matched starts, frozen artifacts, and that every reported PPO checkpoint received PPO updates.

The scripts have no command-line options and resolve data and output paths absolutely. To resume the experiment from any working directory:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_ppo_k1/run_experiment.py
```

After evaluation completes, generate the report:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_ppo_k1/ppo_report.py
```
