# EI acquisition comparison

Five linked-group folds, six endpoints, three PPO seeds, four matched initial hits. Mean purchases, equally weighted across endpoints; lower is better. Primary panel has 580 series with at least 15 compounds.

| Acquisition rule | Top-1 | Top-2 | Top-3 | Top-4 |
|---|---:|---:|---:|---:|
| Mean + SD scorer | 6.325 | 4.255 | 3.407 | 2.768 |
| Mean + SD + EI scorer | 6.289 | 4.243 | 3.399 | 2.746 |
| Direct EI | 6.176 | 4.105 | 3.237 | 2.563 |
| Random | 10.423 | 6.940 | 5.357 | 4.351 |

| Top-1 comparison | Purchases saved (95% paired CI) |
|---|---:|
| Mean + SD + EI scorer vs Mean + SD scorer | 0.036 [-0.037, 0.125] |
| Direct EI vs Mean + SD scorer | 0.149 [-0.073, 0.316] |
| Mean + SD + EI scorer vs Direct EI | -0.113 [-0.256, 0.097] |

Both learned scorers have two64-unit tanh hidden layers and a scalar acquisition output. They use matched PPO training, with fresh random initialization and no EI imitation. The existing mean/SD scorer and predictors are reused unchanged; only the mean/SD/EI scorer is newly trained. Direct EI has no acquisition network or policy training.

For minimization, EI = (b-mu)*Phi(z) + sigma*phi(z), z=(b-mu)/sigma, where b is the best already measured value. Each endpoint has been transformed so lower is favorable. Mean and SD come from the same frozen neural ensemble. This is Gaussian EI from its marginal moments, not exact EI under its full mixture distribution.

The EI feature includes incumbent information. Direct EI uses log-EI for ranking, while the neural input uses raw EI.

Predictor and PPO training series are disjoint. Training settings, validation selection, and starts match the feature experiment. Exploratory intervals resample linked source groups after averaging policy seeds, conditional on frozen predictors.

| Endpoint, >=15 compounds | Mean+SD | Mean+SD+EI | Direct EI |
|---|---:|---:|---:|
| Microsomal clearance | 5.147 | 5.167 | 5.045 |
| In vivo clearance | 9.458 | 9.338 | 8.938 |
| Protein binding | 4.845 | 4.833 | 4.841 |
| Cellular clearance | 5.267 | 5.256 | 5.411 |
| Permeability | 7.933 | 7.888 | 7.448 |
| Efflux ratio | 5.299 | 5.250 | 5.370 |

Audit passed on 129500 saved trajectories. The mean/SD baseline exactly reproduces every previous acquisition count.

[PDF](ei_acquisition_comparison.pdf)
