# Controlled NAP feature and set-encoder benchmark

This experiment keeps the selected **neural pair mean plus conventional covariance kernel** fixed while changing the acquisition policy inputs. Existing predictor checkpoints are read without modification. It is an acquisition benchmark, not a refit of the Gaussian process predictor.

Nine policy families compare Gaussian posterior mean/standard deviation alone, the best measured relative utility, anchored neural-delta summaries, molecular coordinates, Deep Sets, cross-attention, and Set Transformers. No learned policy receives an explicit expected-improvement feature. Separate GP expected improvement, GP greedy, delta greedy, and analytic random baselines are included.

Two further policy families were specified before outer test evaluation to control for simple state statistics. They add measurement count, pool size, progress, mean measured utility, and sample standard deviation of measured utility, with and without molecular coordinates. This makes eleven policy families, 55 screened configurations per endpoint/fold, 2,670 training runs, and 990 final policy checkpoints. The additional entry point is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_set_context/nap_summary_controls.py`; it waits for the core experiment and then incorporates the controls into the same report.

The compact-Set-Transformer follow-up evaluates eight configurations. It tests 4/8/16/32 PCA coordinates, widths 16/32, dropout 0.1/0.3 and weight decay 0.01/0.1. These coordinates truncate the existing PCA32 transform without refitting or whitening. Its entry point is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_set_context/nap_compact_followup.py`, which waits for the summary controls. The complete experiment comprises twelve policy families, 63 configurations, 3,030 training runs and 1,080 final checkpoints.

Each endpoint is fitted separately with the existing species pools and five grouped outer folds. Predictor-role series remain disjoint from acquisition-policy training and validation series. The existing predictor-training PCA and outcome scaling are reused. All outcomes supplied to a policy are measured, centered on the starting hit, and oriented so larger utility is better. The protein-binding and permeability transformations are inherited from the prepared datasets.

The primary population contains at least 15 molecules per pool. Secondary results include all pools of at least 3 molecules and curves over minimum pool size. Metrics are purchases to **any** top-1, top-2, top-3, or top-4 molecule, with ties accepted and zero purchases if the initial hit qualifies. Four identical starting hits per test pool are shared by all methods. Starts are uniform within the worst `floor(n/2)` members, after randomized tie breaking.

Forty-eight configurations are screened independently in each endpoint/fold combination, including twenty Set Transformer configurations. The best two Set Transformers and best model in each other family are refined. The chosen architecture in each family is then fitted using two additional seeds. Hyperparameters and checkpoints are selected only from acquisition-policy validation outcomes. The test data are accessed by evaluation after checkpoint hashes have been locked.

Training uses an oracle-best classification warm start followed by clipped proximal policy optimization (PPO) with a purchase cost of one until a best molecule is acquired. Validation chooses among the initial GP-greedy policy, warm-start checkpoints, and PPO checkpoints.

Exploratory paired intervals resample linked series groups conditional on fitted models. Primary top-1 feature comparisons use Holm adjustment.

The absolute entry point is `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_set_context/nap_run.py`. It resumes completed jobs and needs no command-line arguments. Its Python environment is `/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python`. Products are written under this experiment directory, including checkpoints, training histories, individual trajectories, CSV tables and a PDF report.

Architecture references: [Set Transformer, Lee et al. (2019)](https://proceedings.mlr.press/v97/lee19d.html) and [Deep Sets, Zaheer et al. (2017)](https://papers.nips.cc/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html).
