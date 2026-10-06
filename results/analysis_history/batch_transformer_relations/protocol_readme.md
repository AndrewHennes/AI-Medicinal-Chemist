# GP-summary Transformer with pair relations

This experiment tests five matched batch subset scorers. The first four encode each unmeasured molecule using only its current Gaussian process posterior mean and standard deviation, both relative to the original starting hit and in the existing endpoint training scale.

| Arm | Node features | Pair features inside attention |
| --- | --- | --- |
| `summary` | Mean, SD | None |
| `distance` | Mean, SD | MiniMol PCA32 distance |
| `covariance` | Mean, SD | GP posterior covariance |
| `both` | Mean, SD | Distance and covariance |
| `coordinates_both` | Mean, SD, hit-relative PCA32 coordinates, hit PCA32 coordinates | Distance and covariance |

For each candidate pair, the available relation features are

\[
r_{ij}^{\mathrm{distance}}=\log\left(1+\frac{\|z_i-z_j\|^2}{32}\right),\qquad
r_{ij}^{\mathrm{covariance}}=\operatorname{sign}(C_{ij})\log(1+|C_{ij}|).
\]

Here \(z_i\) uses the saved PCA32 transform and scale fitted on predictor-training molecules. \(C\) is the calibrated conditional covariance of relative utilities after the already purchased molecules have been revealed. It is not the raw prior kernel and is not a correlation matrix. Its diagonal agrees with the squared SD node features. A covariance between negative objectives equals the covariance between objectives, so the endpoint direction reversal does not change this matrix.

For attention head \(h\), a small feedforward network maps active relation features to a logit bias. Another network maps them to a value message:

\[
\alpha_{ij}^{h}=\operatorname{softmax}_{j}\left(
\frac{q_i^{h\mathsf T}k_j^h}{\sqrt{d_h}}+b_h(r_{ij})\right),\qquad
o_i^h=\sum_j\alpha_{ij}^h\left(v_j^h+t_h(r_{ij})\right).
\]

Unused relation channels are masked to zero. The four lean arms have identical parameter counts at a fixed width and depth. Attention is self-attention within a proposed subset. Other remaining candidates supply pooled mean/max summaries; the measured context influences the selector through GP conditioning and its observation count. There is no direct attention to a separate sequence of measured compounds. All pooling and attention are permutation invariant or equivariant as appropriate.

The final network predicts whether the subset contains any globally optimal molecule and predicts the best utility within the subset as an auxiliary target. Training minimizes binary cross entropy plus 0.1 times a Huber loss. The success logit ranks subsets during greedy, beam, or swap search. This is supervised subset-value learning, not an additional PPO run.

Neither explicit expected improvement nor neural-delta summaries enter these models. EI still supplies one of the three training subset-proposal distributions, matched across arms. Global inputs contain only cardinality information. The full successful batch is charged before any measurement can guide another choice.

## Protocol and outputs

- [Protocol](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_transformer_relations/protocol.json)
- [PDF report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_transformer_relations/reports/transformer_relational_features_report.pdf)
- [Acquisition summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_transformer_relations/reports/summary.csv)
- [Paired comparisons](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_transformer_relations/reports/paired_comparisons.csv)
- [Prediction diagnostics](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_transformer_relations/reports/prediction_summary.csv)
- [Saved-model inference interface](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/batch_transformer_relations/relation_api.py)

There are six endpoints, five grouped outer folds, four matched initial hits, and three selector seeds. The GP and PCA transforms are frozen. Hyperparameters, checkpoint steps, and search settings are selected only on validation.

The distance ablation uses PCA32. Evaluation uses batch sizes 1, 2, 3, 4, 5, 7, 8, and 10; the implementation accepts any positive integer K. The maximum requested training size is 8.

Feature-isolation tests ensure that lean models ignore direct coordinates, inactive relations do not affect predictions, active relations can affect predictions, permutations preserve scores, hidden outcomes and delta predictions do not enter states, and batch selections contain distinct unmeasured indices. The public interface is checked against the internal state and selection code.
