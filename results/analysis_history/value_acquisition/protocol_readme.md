# Value learning for molecular acquisition

This completed experiment implements action-value learning, shallow outcome-sampled lookahead, and value-guided Monte Carlo tree search for microsomal stability. It reuses the existing five grouped outer folds and frozen predictors. All outputs are stored in this directory. Other endpoints have not been retrained for this experiment.

## Objective and observations

Lower microsomal clearance is better. Outcomes use the existing log10 transformation and training-fold scale, then subtract the initial hit's transformed value. Every policy receives the measured set, measured relative outcomes, remaining candidates, species, and pool size. Hidden outcomes are kept in separate simulator objects.

The free initial hit is sampled from the metabolically least stable half of the pool. Four test starts per pool match the completed 50% starting-hit benchmark exactly. Human, rat and mouse pools remain distinct tasks within this single-endpoint model, with species indicators in the state.

The main action-value output estimates expected additional purchases to reach any top-1 compound. Three auxiliary outputs are trained in one refinement to predict purchases to any top-2, top-3 and top-4 compound under the same top-1 policy. Auxiliary targets do not create four separately optimized policies.

Simulated step cost is one until a target-rank compound is acquired and zero afterward. Trajectories continue through pool exhaustion, so cumulative cost equals the retrospective first-hit purchase count. The deployed policy supplies an acquisition ordering.

Rank-boundary ties qualify. An already qualifying initial hit gives zero purchases. With a pool of size n and g acceptable remaining items, random sampling takes n/(g+1) purchases in expectation when the initial hit does not qualify. The exact expectation is used for the random baseline.

## Implemented models

| Method | Representation or search |
| --- | --- |
| Q statistics | Candidate prediction summaries, observed mask and outcomes, pooled statistics, and state context |
| Q deep_sets | Learned MiniMol projections plus prediction summaries; mean/max pooling over observed and available sets |
| Q attention | The same inputs with two layers of attention over the pool |
| Q selected | A recipe selected separately within each outer fold using only that fold's validation data |
| Value lookahead | Selected Q model plus Gaussian-process outcome branches and one- or two-purchase lookahead |
| Value MCTS | Selected Q model plus depth-limited chance-node Monte Carlo tree search |

Prediction summaries include conditional Gaussian-process (GP) means and standard deviations, expected improvement, and the mean and sample standard deviation of observed-reference delta predictions. Delta estimates are measured relative to the initial hit by adding each observed molecule's relative value. A singleton delta estimate has standard deviation zero. No sign-consistency loss is added.

Networks use a shared state-cost term and centered candidate advantages, with remaining-purchase normalization. Double-Q updates choose the next action with the online network and evaluate its cost using a target network. Warm-up targets are exact costs for buying the candidate and then sampling randomly. They are not clairvoyant optimal-action labels.

The training bank contains 40 transitions per training pool with varied observed sets. Smaller pools provide training signal. The large-balanced refinement samples half its transitions from pools with at least 15 compounds. Other refinements test additional updates, a 25% random-return anchor, and auxiliary rank-2/3/4 costs with that anchor.

## Planning

Hypothetical observations are Gaussian quantiles from the current GP belief. Each hypothetical purchase updates the entire conditional covariance. Learned values estimate costs beyond the search horizon. Search uses a small shortlist containing Q-preferred, expected-improvement-preferred and high-variance candidates.

Immediate expected cost is estimated from correlated Gaussian draws as the probability that the unmeasured set contains a better item than the incumbent.

Lookahead and tree search are blended with direct Q costs; the blend and search settings are chosen on validation data. A shared offset correction aligns searched and unsearched candidate cost scales. Search runs only for the first eight actual acquisitions, then direct Q is used. This cap depends only on acquisition count, never on hidden success. Monte Carlo tree search uses 32 or 64 simulations and depth three; this is a bounded search experiment rather than exhaustive planning.

## Development and evaluation protocol

1. Audit the existing role and fold partitions. Delta training retains its disjoint half. GP summaries for acquisition-training pools come from group-excluded teacher models; validation and test use GP fits on the full acquisition-training partition.
2. Compare three Q architectures within each outer fold, using seed 11 and up to 1,800 updates each.
3. Refine the two best architectures in each fold with four predefined follow-ups, each allowing 1,800 additional updates. This produces 55 architecture-development trials across the five folds.
4. Select a recipe independently within each fold. The validation criterion weights normalized top-1 purchase counts 75% for pools of at least 15 compounds and 25% for all pools.
5. Repeat the three baseline Q architectures and the selected recipe with seeds 11, 29 and 47, allowing up to 1,800 plus 1,800 updates. Retain the better validation checkpoint across phases.
6. Compare four planning configurations and refine the best lookahead and tree-search configuration in each fold at two additional blend weights, for 40 planning trials.
7. Lock model and selection hashes before running all outer-test evaluations. No outer-test results guide this experiment's architecture or search selection.
8. Compare against the existing random, delta greedy, GP plus expected improvement, original neural acquisition process (NAP), and revised cross-fitted NAP trajectories on identical starts.

The outer test covers 1,827 pools once each, including 311 pools with at least 15 compounds. Starts are averaged within seed and pool, then seeds, then pools. Related species pools remain grouped. Baseline delta and GP methods have one fitted predictor per fold; neural acquisition methods have three seeds.

Recipe selection uses 12 large validation pools per fold. Bootstrap intervals resample source groups conditional on fitted models and without multiplicity adjustment. Training budgets are recorded for each method.

## Files

- `data.py` defines the public/private boundary, belief updates, observations, costs and targets.
- `networks.py` implements the three value architectures.
- `learning.py` builds transition banks, trains models and evaluates direct acquisition.
- `planning.py` implements lookahead and tree search.
- `experiment.py` runs resumable development, model locking and final evaluation.
- `audit.py` checks partition separation and records original artifact hashes.
- `tests.py` checks cost/metric alignment, exact random returns, hidden-outcome isolation, GP conditioning, set permutation behavior and planner isolation.
- `report.py` creates the PDF, charts, metric CSVs, paired differences and validation-development tables.
- `progress.json`, `jobs/`, and `runner.log` contain execution status and logs.
- `completed.json` exists only after evaluation and reporting finish successfully.
- `reports/value_learning_comparison.pdf` is the final four-page comparison report.

The experiment has completed. No manual command is required. For reproducibility, these commands work from any current directory and use the existing CPU environment:

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_acquisition/tests.py
```

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_acquisition/experiment.py
```

The runner has an exclusive lock and resumes successful jobs rather than retraining them. Changed model configurations should be run as a separate experiment so that cached results and locked checkpoints retain their meaning.
