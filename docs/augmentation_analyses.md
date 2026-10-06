# Initial-hit and training-context replications

The runner compares three interventions under the current architecture. It fits the average-mean, average-reference-kernel predictor from fresh initialization, freezes it, and trains a proximal policy optimization (PPO) acquisition network from predicted mean and standard deviation. It also evaluates direct expected improvement (EI) and exact random-search expectations. Current-protocol replications write separate result directories.

The current recipe varies policy-training contexts with one frozen predictor per outer fold and endpoint. Historical multi-hit and top-removal studies also augmented supervised predictor examples and, where applicable, cross-fitted forecasters.

## Experiments

| Family | Training intervention | Held-out evaluation |
| --- | --- | --- |
| Baseline | One hit from the worst 50% of each training pool | Original pools, one hit, each of the five fractions |
| Initial-hit sensitivity | One hit from the worst 10%, 20%, 30%, or 40% | Same fraction; also compare the 50%-trained baseline on the identical cases |
| Multi-hit augmentation | With probability 0.5, start with 2 through `context_max` free observations from the worst half | Original pools, one worst-half hit |
| Cumulative top removal | With probability 0.5, remove 1 through `remove_max` best compounds before sampling the hit | Original complete pools, one worst-half hit |

The default recipe tests `context_max` values 2, 3, 4, and 5, and `remove_max` values 1 through 5. Each maximum defines a mixture, not a condition in which exactly that many compounds are always added or removed. Counts are uniform over feasible values. Top removal leaves at least three molecules, samples ties randomly, and subsets molecular indices and outcomes together. Removed molecules cannot enter candidate or measured-context features. The remaining molecules retain their original order. A distinct reduced-pool identifier prevents cached predictions from being reused for another pool.

All objectives use the package's lower-is-better orientation. Thus the worst starting fraction comprises the *largest* transformed objective values. In a pool of size \(n\), a fraction \(p\) makes \(\max(1,\lfloor np\rfloor)\) compounds eligible. Ties are randomized. Different percentages can generate identical eligible sets in a small pool. A multi-hit context samples without replacement and uses its first molecule as the reference. All measurements shown to the predictor remain relative to that reference.

## Data and information flow

The existing five outer folds and validation subsets are retained. Globally linked training groups are divided into disjoint predictor and acquisition-policy roles using the package's existing role allocator. Predictor outcome scaling uses only its training role. Fold-level structure preprocessing follows the existing prepared dataset protocol. No test label selects a model, learning rate, checkpoint, or augmentation probability.

Predictors are fitted only once per endpoint and outer fold and are shared among augmentation arms. Each arm fits its policy from a new initialization using the same seed. The default includes predictor and policy seeds 11, 29, and 47. Two learning rates are compared on seed 11 using validation acquisition counts. The selected learning rate is then repeated with the other two seeds. Validation averages the all-pool and at-least-15-pool top-1 purchase means when a large-pool subset exists. Validation pools are intact and start with one hit. Initial-hit sensitivity uses the corresponding fraction; multi-hit and removal studies use 50%.

Defaults are 4,000 predictor updates and 400 PPO iterations per fit, with eight episodes per iteration. Half the sampling opportunities draw from pools with at least 15 molecules when available; half draw from all eligible policy-training pools. Augmentation fixes the episode budget and records resulting transitions and optimizer minibatches.

The policy receives candidate structures through the frozen predictor and measured outcomes through its current context. Hidden outcomes are used only by the retrospective environment to generate rewards and stopping conditions. The actor never receives an optimum-found flag, target rank, hidden response, or count of molecules tied at the optimum. The collected trajectory stops when the environment reaches the optimum; this is sufficient to score the first visits to top-1 through top-4. Unlike some historical artifacts, this runner does not save the irrelevant post-optimum remainder of the order.

## Matched cases and metrics

`test_cases.json` stores pool, source group, selected initial compound, and draw for every evaluated case. A deterministic random stream indexed by fold, endpoint, subset, pool, and draw is shared across fractions; the fraction itself is not part of the seed. All arms evaluated at the same fraction consequently use exactly the same original held-out pools and starts. Comparison between different starting fractions changes both training and task difficulty. The retrained and fixed-50% curves *at the same test fraction* estimate the effect of adapting both training and validation-based model selection to the changed starting distribution. The retrained arms select their learning rates and checkpoints using that fraction, while the baseline uses 50% validation starts.

Metrics count additional purchases to any compound tied at or above the desired top rank. An already qualifying free context costs zero. In a pool with \(n\) molecules, \(c\) initially measured molecules, and \(g\) acceptable unmeasured molecules, random ordering has expected first-success cost

\[
\mathbb{E}[T]=\frac{n-c+1}{g+1},
\]

provided the initial context has not already qualified. With one free hit and a unique optimum this is \(n/2\), not \((n-1)/2\). Top-4 is zero for pools containing only three or four molecules. These conventions match the purchase-count semantics of the historical reports.

Tables average starts and seeds within pools, then pools within endpoints. The `all` endpoint weights available endpoints equally. The CSV records contributing pools at cutoffs 3, 15, 20, 25, and 30. Curves are descriptive.

## Running and outputs

Edit [augmentation_analyses.json](../config/augmentation_analyses.json), then run this command from any working directory after completing the main package's data preparation and environment setup.

```bash
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Desktop/Collins_Lab/Repositories/learning_hit_to_lead_optimization/scripts/run_augmentation_analyses.py
```

The configured experiment writes beneath the absolute package artifact root, normally `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/repository_benchmark/augmentation_analyses`. It writes predictor checkpoints, policy checkpoints, optimizer and random-generator restart state, validation histories, role assignments, test cases, per-case acquisition orders, summary CSVs, and a PDF with three study pages per endpoint plus the overall pages. No command-line flags are needed.

Each run records configuration, source hashes, dataset hashes, checkpoint hashes, roles, and exact validation cases. Matching completed fits are reused; changed source or settings require a new output directory and fresh initialization. Synthetic tests cover fitting, restart, information boundaries, rank formulas, and reporting.

See [the early analysis findings](early_analysis_findings.md) for the conclusions supported by the original experiments.
