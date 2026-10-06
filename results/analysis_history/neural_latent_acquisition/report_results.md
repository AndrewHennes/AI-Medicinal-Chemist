# Learned acquisition features

Single-task predictors; K=1; five linked-group folds; three PPO seeds; four matched worst-half starting hits.

| Actor inputs | Top-1 purchases, >=15 | Paired improvement over mean+SD (95% CI) |
|---|---:|---:|
| Mean + SD | 6.325 | Reference |
| + 2 features | 6.551 | -0.227 [-0.583, 0.214] |
| + 4 features | 6.523 | -0.198 [-0.560, 0.303] |
| + 8 features | 6.733 | -0.408 [-0.850, 0.141] |
| + 16 features | 6.748 | -0.423 [-0.841, 0.093] |

Random expectation is 10.423 purchases. Positive paired improvement means fewer purchases. Intervals resample linked source groups after averaging policy seeds and are unadjusted for multiple comparisons.

The actor is a pointwise feedforward network with two 64-unit tanh hidden layers and one scalar output. Inputs are exactly mean and standard deviation, plus the optional learned vector. Softmax converts the scores to PPO action probabilities; evaluation selects the maximum score.

Each extra vector is a learned projection of the frozen neural baseline hidden features. Pair embeddings are averaged over acquired references separately within each of three ensemble members. Their 64-dimensional summaries are concatenated, normalized, projected to 2/4/8/16 dimensions, and passed through tanh. Projection weights are learned with PPO. No raw MiniMol vectors, EI, incumbent, or candidate-set pooling enter the actor.

The predictor uses the average mean and average-reference kernel architecture. It was retrained from scratch on approximately half of the outer-training linked groups. The other half trains PPO. Predictor weights remain fixed throughout PPO. Three predictor members and three independent policy seeds are used per fold and endpoint. The validation set selects trained predictor and policy checkpoints; test outcomes never select checkpoints or dimensions.

All models receive 400 PPO updates with 8 complete on-policy episodes each, three update epochs, learning rate 0.0003, clipping 0.2 and entropy coefficient 0.01. The reward is -1 per purchase until any tied best compound is found. The separate critic is identical across feature dimensions and uses no latent features. No imitation initialization is used.

Prediction mean and uncertainty are identical across arms on the same measured context. This experiment therefore tests acquisition, not an improvement to R-squared, Spearman correlation, or predictive NLL. Different selected compounds can lead to different subsequent contexts.

The feature ablation uses fixed hyperparameters and a fixed ensemble of three predictor seeds. Species are pooled within each endpoint.

[PDF](latent_acquisition_comparison.pdf)

Audit: 4625 held-out pools, 580 with >=15 compounds; 277500 acquisition trajectories independently checked.

| Endpoint (>=15 compounds) | Mean+SD | +2 | +4 | +8 | +16 |
|---|---:|---:|---:|---:|---:|
| Microsomal clearance | 5.147 | 5.281 | 5.364 | 5.510 | 5.613 |
| In vivo clearance | 9.458 | 9.054 | 8.412 | 9.025 | 8.871 |
| Protein binding | 4.845 | 5.208 | 5.233 | 5.627 | 5.674 |
| Cellular clearance | 5.267 | 5.834 | 6.137 | 6.138 | 6.127 |
| Permeability | 7.933 | 7.910 | 7.947 | 8.019 | 8.081 |
| Efflux ratio | 5.299 | 6.022 | 6.043 | 6.079 | 6.123 |

These are mean purchases to reach any top-1 compound. Full top-2/3/4 results and pool-size curves are in the PDF and CSV files.
