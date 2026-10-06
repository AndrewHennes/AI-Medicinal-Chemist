# Microsomal stability extension

[Updated simplified PDF](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/single_task_minimum_pool_cutoff.pdf) has seven pages, with the six endpoints and an equally weighted overall comparison. It contains only minimum pool-size cutoffs and purchases to any top-1, top-2, top-3 or top-4 compound.

Microsomal stability minimizes median log10 clearance. Human, rat and mouse are pooled for training and remain separate series/species acquisition pools. Every observed label is relative to the initial hit. The same existing curation supplies 1,827 pools, including 311 with at least 15 compounds.

Only single-task delta greedy, GP + EI, original NAP and revised single-task NAP were fitted; random is its exact expectation. The revised policy additionally requires three inner cross-fitted forecasters and one full forecaster per outer fold. No multitask or delta + EI model was trained. The original five endpoints reuse their frozen predictions, and their endpoint-specific plotted values are unchanged.

Five new microsomal outer source-group folds are independent of the previously fitted five-endpoint partitions. This is valid for the displayed single-task models because they do not share fitted parameters or training observations across endpoints. Series, related documents and molecules are kept together across species. Every microsomal pool is tested once, using four matched worse-half initial draws and three policy seeds. Predictor and policy roles remain disjoint. Inner target proportions are 45% delta training, 5% delta validation, 45% acquisition training and 5% acquisition validation within each outer non-test partition.

Architecture, per-endpoint training budgets, validation selection and exact-optimum policy rewards match the existing benchmark. The raw 512-dimensional Minimol features and transformed labels were reused, with all input and outcome scaling refitted on the respective training partitions. No sign-consistency constraint was added. Cross-fitted teachers exclude their held training groups from losses and retain outer-training scales, as in the existing revised NAP.

The initial hit is free, all rank-boundary ties qualify, and every molecule qualifies for top-k when k is at least the pool size. Curves include these trivial cases. Random is calculated analytically. Overall curves require all six endpoints at every cutoff and average endpoint means equally. Hollow markers identify sparse source-group support. This remains an exploratory internal comparison, and the outer training partitions overlap.

| Minimum pool size | Method | Top-1 | Top-2 | Top-3 | Top-4 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 3 | Cross-fitted single-task NAP | 2.608 | 1.855 | 1.179 | 0.883 |
| 3 | Random | 3.527 | 2.481 | 1.644 | 1.236 |
| 3 | single_task_Delta greedy | 2.731 | 1.904 | 1.225 | 0.894 |
| 3 | single_task_GP + EI | 2.703 | 1.927 | 1.240 | 0.928 |
| 3 | single_task_NAP | 2.751 | 1.911 | 1.214 | 0.905 |
| 15 | Cross-fitted single-task NAP | 5.433 | 3.625 | 2.884 | 2.517 |
| 15 | Random | 8.625 | 6.140 | 4.918 | 4.137 |
| 15 | single_task_Delta greedy | 5.701 | 3.758 | 3.037 | 2.477 |
| 15 | single_task_GP + EI | 5.844 | 3.953 | 3.151 | 2.715 |
| 15 | single_task_NAP | 6.109 | 3.988 | 3.134 | 2.627 |
