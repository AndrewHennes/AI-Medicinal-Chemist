# Learned features for a feedforward acquisition score

This experiment compares five single-task acquisition policies. Each policy receives the same frozen predictor's mean and standard deviation. Four policies additionally receive a learned vector of dimension 2, 4, 8, or 16.

For each candidate molecule q and measured reference i, let h(q,i) denote the 64-dimensional hidden output of the predictor's neural pair encoder. Each of the three predictor ensemble members averages h(q,i) over the currently measured references. We concatenate these three summaries, rather than averaging their unrelated coordinate systems. The acquisition policy learns a projection from that 192-dimensional vector to its extra d-dimensional representation.

The actor is strictly pointwise: `[mean, SD, optional learned vector] -> Linear64 -> tanh -> Linear64 -> tanh -> Linear1`. The scalar output is the acquisition score. PPO samples from a softmax over the unmeasured candidates' scores. Test inference selects the maximum score. No candidate-set pooling, attention, incumbent, EI, or acquisition-progress features enter the actor. A separate critic is used during training and discarded for inference.

Predictors use the selected average-mean and average-reference-kernel architecture. They are retrained from scratch using half of the outer-training linked groups and then frozen. The other half provides PPO training episodes. The existing global five-fold test split and validation split are preserved. All six endpoints are trained separately, with species pooled within each endpoint. PCA uses the existing outer-training-only molecular structures; outcome scales use only predictor-training labels.

There are 90 predictor fits and 450 PPO fits. All actor and projection parameters are initialized freshly, with no EI imitation. Every policy receives the same 400-update budget, eight on-policy episodes per update, three optimization epochs, and the same checkpoint-selection rule. The objective is minus the number of purchases needed to find any tied optimum. Training samples initial hits from the worst half; half of episodes are sampled from series with at least 15 molecules when available.

Evaluation reports purchases to reach any top-1, top-2, top-3, or top-4 compound, with a free initial hit, four matched starting draws per series, and three policy seeds. Lower is better. The primary panel is series of size at least 15. All eligible series of size at least 3 are also included in the report. Additional latent features change the acquisition policy; they do not change predictor means or variances on identical measured contexts.

The experiment runs on CPU. All paths are absolute internally. Entry files are `run_experiment.py` and `report.py`; neither requires command-line arguments. `test_protocol.py` checks original/cached predictor agreement, latent gradients, pointwise actor inputs, masking, tied-target counts, and split separation.

Protocol details and exact hyperparameters are saved in `protocol.json`. Progress is saved in `progress.json`, per-fit progress files, and `run.log`. Final artifacts are written under `reports/`.
