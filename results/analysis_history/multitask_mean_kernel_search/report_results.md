# Multitask task-subset benchmark

All 63 nonempty task combinations were trained from scratch. Two sharing designs were tested for all multitask combinations, with five global linked-group folds and three seeds. All 15 pairs and every larger subset were evaluated.

Primary tables use pools with at least 15 molecules and ten total measured compounds, including the initial hit. Query molecules remain fixed as context grows. NLL is validation-calibrated; raw NLL is also supplied. Subset selection uses validation only, independently in each outer fold.

These are matched new single-task controls. Cross-endpoint leakage checks required globally linked folds, and this prediction experiment uses all available training-fold pools rather than preserving the former predictor/RL role restriction. The older benchmark is not the control for this experiment.

At ten measurements in pools with at least 15 compounds, exhaustive NLL-based subset selection changes the equal-endpoint average R² from 0.5958 to 0.5972; Spearman rho from 0.4368 to 0.4377; NLL from 0.5489 to 0.5295.

Forward task addition has macro NLL 0.5345; exhaustive subset selection has 0.5295; forcing all six tasks has 0.5353. These are held-out evaluations of choices made on validation, not test-optimal choices.

A separately predeclared selection rule uses only validation pools with at least 15 compounds. Its macro R² is 0.5979; rho is 0.4353; NLL is 0.5302. This checks whether small-pool validation examples change the preferred partners. No extra training or test-driven selection is involved.

The next tables give fixed task combinations preferred by average validation performance for each metric. The held-out performance tables instead evaluate fold-specific selection, which may choose different combinations in different folds. Selection frequencies and every fold choice are provided so instability is visible.

The search covers every task subset under two sharing designs. It does not establish a universal optimum over all possible neural architectures, loss functions or future datasets. Matched controls, global grouping and fixed hidden queries isolate the comparison within the tested family.

The primary macro NLL improvement is 0.0194, with paired 95% interval [0.0117, 0.0264]. The R² interval is [-0.0020, +0.0042], and the Spearman interval is [-0.0104, +0.0092].

The likelihood benefit also exists before calibration: raw macro NLL changes from 0.5458 to 0.5247. After calibration, nominal 95% interval coverage changes from 95.03% to 95.26%. NLL measures the full predictive distribution, including its mean, spread and shape; this result should not be interpreted as a pure calibration improvement.

With only the initial measurement, macro Spearman rho changes from 0.2928 to 0.3090. This early-context ranking gain is larger than the ten-measurement change, but endpoint patterns differ and the exploratory interval is only narrowly above zero. The full learning curves are more informative than any single context size.

Removing the largest linked group leaves the main likelihood finding intact: macro NLL changes from 0.5501 to 0.5319. In vivo clearance has only 20 large test pools in 15 linked groups; 826 of its 945 trained endpoint checkpoints have worse checkpoint-validation NLL than initialization.

## Equal endpoint average

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.5958 | 0.4368 | 0.5489 |
| Best pair or single task | 0.5984 | 0.4366 | 0.5361 |
| Forward task addition | 0.5971 | 0.4339 | 0.5345 |
| Exhaustive selection by NLL | 0.5972 | 0.4377 | 0.5295 |
| All six tasks | 0.5959 | 0.4309 | 0.5353 |
| Exhaustive selection by R² | 0.5970 | 0.4370 | 0.5387 |
| Exhaustive selection by Spearman | 0.5961 | 0.4343 | 0.5356 |
| Large-pool selection by NLL | 0.5979 | 0.4353 | 0.5302 |
| Large-pool selection by R² | 0.5976 | 0.4361 | 0.5385 |
| Large-pool selection by Spearman | 0.5971 | 0.4343 | 0.5375 |

## Microsomal clearance

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.6131 | 0.4382 | 0.4854 |
| Best pair or single task | 0.6105 | 0.4397 | 0.4743 |
| Forward task addition | 0.6108 | 0.4387 | 0.4722 |
| Exhaustive selection by NLL | 0.6125 | 0.4402 | 0.4680 |
| All six tasks | 0.6090 | 0.4341 | 0.4772 |
| Exhaustive selection by R² | 0.6103 | 0.4392 | 0.4796 |
| Exhaustive selection by Spearman | 0.6112 | 0.4370 | 0.4745 |
| Large-pool selection by NLL | 0.6112 | 0.4376 | 0.4729 |
| Large-pool selection by R² | 0.6102 | 0.4317 | 0.4774 |
| Large-pool selection by Spearman | 0.6113 | 0.4406 | 0.4792 |

Fixed combination recommended by mean validation NLL: **MIC+PPB**, Shared pair and context encoders. This fixed recommendation is distinct from the fold-wise selection procedure evaluated in the table.

- r2 improvement from exhaustive NLL selection: -0.0005; paired 95% interval [-0.0038, +0.0026].
- rho improvement from exhaustive NLL selection: +0.0020; paired 95% interval [-0.0075, +0.0101].
- nll improvement from exhaustive NLL selection: +0.0174; paired 95% interval [+0.0090, +0.0264].

## In vivo clearance

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.5346 | 0.2973 | 0.5216 |
| Best pair or single task | 0.5346 | 0.2978 | 0.5216 |
| Forward task addition | 0.5325 | 0.2898 | 0.5138 |
| Exhaustive selection by NLL | 0.5344 | 0.3016 | 0.5120 |
| All six tasks | 0.5352 | 0.2851 | 0.5183 |
| Exhaustive selection by R² | 0.5367 | 0.2981 | 0.5095 |
| Exhaustive selection by Spearman | 0.5368 | 0.2966 | 0.5078 |
| Large-pool selection by NLL | 0.5325 | 0.2898 | 0.5106 |
| Large-pool selection by R² | 0.5353 | 0.2931 | 0.5103 |
| Large-pool selection by Spearman | 0.5368 | 0.2966 | 0.5078 |

Fixed combination recommended by mean validation NLL: **IVC+PAP+EFF**, Shared pair and context encoders. This fixed recommendation is distinct from the fold-wise selection procedure evaluated in the table.

- r2 improvement from exhaustive NLL selection: -0.0002; paired 95% interval [-0.0056, +0.0049].
- rho improvement from exhaustive NLL selection: +0.0043; paired 95% interval [-0.0338, +0.0282].
- nll improvement from exhaustive NLL selection: +0.0095; paired 95% interval [-0.0053, +0.0270].

## Protein binding

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.5668 | 0.5722 | 0.6246 |
| Best pair or single task | 0.5718 | 0.5699 | 0.6074 |
| Forward task addition | 0.5727 | 0.5710 | 0.5989 |
| Exhaustive selection by NLL | 0.5682 | 0.5647 | 0.6022 |
| All six tasks | 0.5696 | 0.5578 | 0.6173 |
| Exhaustive selection by R² | 0.5636 | 0.5701 | 0.6189 |
| Exhaustive selection by Spearman | 0.5644 | 0.5744 | 0.6101 |
| Large-pool selection by NLL | 0.5728 | 0.5720 | 0.6005 |
| Large-pool selection by R² | 0.5670 | 0.5747 | 0.6231 |
| Large-pool selection by Spearman | 0.5666 | 0.5673 | 0.6191 |

Fixed combination recommended by mean validation NLL: **IVC+PPB**, Shared pair and context encoders. This fixed recommendation is distinct from the fold-wise selection procedure evaluated in the table.

- r2 improvement from exhaustive NLL selection: +0.0014; paired 95% interval [-0.0070, +0.0125].
- rho improvement from exhaustive NLL selection: -0.0075; paired 95% interval [-0.0285, +0.0103].
- nll improvement from exhaustive NLL selection: +0.0223; paired 95% interval [+0.0020, +0.0528].

## Cellular clearance

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.5796 | 0.4292 | 0.4857 |
| Best pair or single task | 0.5860 | 0.4271 | 0.4761 |
| Forward task addition | 0.5837 | 0.4224 | 0.4746 |
| Exhaustive selection by NLL | 0.5834 | 0.4229 | 0.4704 |
| All six tasks | 0.5795 | 0.4279 | 0.4712 |
| Exhaustive selection by R² | 0.5839 | 0.4214 | 0.4772 |
| Exhaustive selection by Spearman | 0.5823 | 0.4173 | 0.4837 |
| Large-pool selection by NLL | 0.5863 | 0.4253 | 0.4707 |
| Large-pool selection by R² | 0.5864 | 0.4207 | 0.4776 |
| Large-pool selection by Spearman | 0.5822 | 0.4144 | 0.4808 |

Fixed combination recommended by mean validation NLL: **MIC+IVC+CLC+PAP**, Shared pair and context encoders. This fixed recommendation is distinct from the fold-wise selection procedure evaluated in the table.

- r2 improvement from exhaustive NLL selection: +0.0037; paired 95% interval [-0.0034, +0.0108].
- rho improvement from exhaustive NLL selection: -0.0063; paired 95% interval [-0.0228, +0.0081].
- nll improvement from exhaustive NLL selection: +0.0153; paired 95% interval [-0.0022, +0.0300].

## Permeability

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.6558 | 0.4439 | 0.6151 |
| Best pair or single task | 0.6606 | 0.4441 | 0.5869 |
| Forward task addition | 0.6562 | 0.4391 | 0.5940 |
| Exhaustive selection by NLL | 0.6575 | 0.4528 | 0.5744 |
| All six tasks | 0.6602 | 0.4527 | 0.5771 |
| Exhaustive selection by R² | 0.6629 | 0.4466 | 0.5947 |
| Exhaustive selection by Spearman | 0.6591 | 0.4483 | 0.5879 |
| Large-pool selection by NLL | 0.6573 | 0.4457 | 0.5748 |
| Large-pool selection by R² | 0.6583 | 0.4448 | 0.6017 |
| Large-pool selection by Spearman | 0.6611 | 0.4532 | 0.5899 |

Fixed combination recommended by mean validation NLL: **MIC+PPB+CLC+PAP+EFF**, Shared pair and context encoders. This fixed recommendation is distinct from the fold-wise selection procedure evaluated in the table.

- r2 improvement from exhaustive NLL selection: +0.0017; paired 95% interval [-0.0082, +0.0099].
- rho improvement from exhaustive NLL selection: +0.0089; paired 95% interval [-0.0139, +0.0298].
- nll improvement from exhaustive NLL selection: +0.0408; paired 95% interval [+0.0096, +0.0699].

## Efflux ratio

| Selection procedure | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| Single task | 0.6251 | 0.4399 | 0.5609 |
| Best pair or single task | 0.6270 | 0.4412 | 0.5503 |
| Forward task addition | 0.6268 | 0.4424 | 0.5535 |
| Exhaustive selection by NLL | 0.6272 | 0.4439 | 0.5497 |
| All six tasks | 0.6217 | 0.4280 | 0.5509 |
| Exhaustive selection by R² | 0.6248 | 0.4464 | 0.5525 |
| Exhaustive selection by Spearman | 0.6225 | 0.4323 | 0.5497 |
| Large-pool selection by NLL | 0.6273 | 0.4411 | 0.5517 |
| Large-pool selection by R² | 0.6287 | 0.4514 | 0.5410 |
| Large-pool selection by Spearman | 0.6245 | 0.4336 | 0.5482 |

Fixed combination recommended by mean validation NLL: **IVC+PPB+PAP+EFF**, Shared pair encoder. This fixed recommendation is distinct from the fold-wise selection procedure evaluated in the table.

- r2 improvement from exhaustive NLL selection: +0.0021; paired 95% interval [-0.0053, +0.0098].
- rho improvement from exhaustive NLL selection: +0.0041; paired 95% interval [-0.0192, +0.0278].
- nll improvement from exhaustive NLL selection: +0.0112; paired 95% interval [-0.0032, +0.0240].

## Methods and interpretation

There are 4625 pools in 1724 global connected components. Molecules, source documents and previous series groups define connections across all endpoints. The primary >=15 panel contains 580 pools in 283 components. A component with 891 pools is kept intact; its exclusion is supplied as a sensitivity analysis.

The current outer fold is test data. A balanced component sample from the other four folds supplies validation, targeting 20% of remaining pool, large-pool and group counts. The rest is training. A cap prevents a giant component from filling one endpoint's whole validation panel. Every test component occurs in only one outer fold. Exact split sizes are in split_summary.csv.

The old predictor/RL role restriction is removed because this is a prediction experiment. No held-out labels are made available at inference except the explicitly revealed same-endpoint context. Shared training can transfer across assays; other-assay measurements of the held-out series are not supplied at inference. Human, rat and mouse remain pooled within each endpoint.

Raw MiniMol embeddings are common inputs. PCA is fitted on the union of unique training molecules from all six endpoints, without outcomes and without validation/test molecules, then the first 32 components are scaled by their RMS variance. Single-task controls use that same representation, isolating the effect of sharing labeled training signal. The historical arrays named raw were endpoint-standardized, so preprocessing returns to the original foundation embeddings.

The mathematical mean and variance architecture is the selected average-mean / average-reference-kernel model. It uses width 64, 24 residual iterations, a conventional RBF geometry, and endpoint-private distance scales, bandwidth, ridge, iteration step sizes and output heads. Normal likelihoods are used for microsomal and in vivo clearance, Student likelihoods for the other endpoints. All arms use these matched configurations.

The shared-mean design shares only the pair encoder. The broader design also shares the measured-context encoder and decoder hidden layer. Endpoint heads remain private in both designs. Single-task inference in the new batched implementation is numerically checked against the original architecture. No sign-consistency loss is used.

Every optimizer update contains 16 episodes from each included task, and the objective averages their negative log-likelihoods. This gives each target equal exposure per round, irrespective of dataset size or number of partners. Endpoint target scales are fitted from training-only within-series differences. Training retains random and chemically clustered contexts and the earlier mixture of random and unstable initial hits.

All 1,800 fits start from newly initialized weights and run at least 4,000 rounds. Actual rounds range to 6000, with no fit reaching the 16,000-round limit. Validation controls learning-rate reductions and plateau stopping. Trained checkpoints at 25, 50, 100 and every 250 updates are eligible, separately for each target. Initialization is diagnostic only. For 827 of 5670 selected endpoint checkpoints, validation NLL exceeded its initialization value.

Checkpoint validation uses all large pools plus a fixed small-pool sample up to 128 pools per endpoint, with three context draws. Final subset selection and scale calibration use every validation pool, with five draws. Validation gives half its weight to all pools and half to pools with at least 15 compounds, with equal context counts within each pool. Raw ensemble NLL is the primary subset criterion. Separate R² and rho selections choose among these same NLL-selected trained checkpoints.

The search is exhaustive rather than pruning after pairs, so it can detect a useful larger combination even if no immediate pair helps. A forward-addition path is also computed: start with the single task, consider every additional endpoint and sharing design, and advance only when validation NLL improves by at least 0.0001. Pair-only selection can retain the single-task control. All-six-task selection is forced to include all tasks.

Each test prediction uses a subset, sharing design and three-member ensemble selected solely inside its outer fold. A fixed recommended subset is additionally identified from mean validation scores across folds for future deployment; it is not what the fold-wise selection table estimates. All fixed-candidate test tables are descriptive, not a second model-selection step. Different metric-optimal subsets and validation Pareto sets are supplied.

An additional large-pool selection rule was written and SHA256-locked before any held-out predictions were generated. It chooses subsets by validation NLL, R² or rho using pools >=15 only. The original training, checkpoint and calibration rules are retained. The report computes these decisions exclusively from validation summaries and applies them to the saved candidate predictions. This isolates the choice of validation cohort.

R² pools query-error and target moments with equal pool weight within each endpoint. Spearman rho is computed within each fixed hidden query panel and then averaged. Exact Gaussian or Student ensemble-mixture NLL is reported in transformed endpoint units. Both raw and validation-calibrated uncertainty are included, along with 50%, 80% and 95% coverage. Calibration leaves the reported point means and ranks unchanged.

Test curves reveal 1, 2, 3, 5 or 10 total measurements while keeping the same hidden query compounds. The >=15 panels have a common cohort at every context size. Smaller-pool tables have changing eligibility, and one-query panels cannot support Spearman correlation. New global folds change the single-task reference compared with the earlier endpoint-specific benchmark.

Paired confidence intervals use 5,000 resamples of global linked groups, preserving cross-endpoint dependence. Predictions remain fixed during resampling.
