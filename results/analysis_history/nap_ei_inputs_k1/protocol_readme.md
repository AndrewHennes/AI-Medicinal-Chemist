# EI ingredients at K=1

The models receive posterior mean, posterior standard deviation, and (optionally) the best measured utility relative to the original hit. They never receive EI as an input. The matched mean/SD model has the third input slot fixed to zero. All three arms have identical parameter counts at a given configuration.

For a maximization problem with incumbent \(u^*\),

\[
z=\frac{\mu-u^*}{\sigma},\qquad
\operatorname{EI}=(\mu-u^*)\Phi(z)+\sigma\phi(z).
\]

At zero uncertainty, EI is \(\max(\mu-u^*,0)\). The implementation evaluates EI in log space for numerical stability. Analytic EI and the teacher use exactly the same float32 inputs given to the neural models.

Two arms train with the existing optimum-membership binary cross entropy plus 0.1 Huber utility-regression objective, restricted to singleton acquisitions. The third arm trains with Kullback–Leibler divergence from normalized EI weights to the network's predicted candidate probabilities. EI is a teacher target for that arm, rather than an input or analytic layer in the neural model.

The network architecture is the previous lean subset scorer evaluated at K=1. Its singleton attention blocks become pointwise transformations. Mean/max summaries of the remaining pool and cardinality inputs are retained. There are no MiniMol coordinates, pair relations, or delta predictions in these models. This experiment does not add a PPO training stage.

All six endpoints and five existing grouped folds are included. The GP is fixed, and predictor-versus-selector training roles remain separated. Each arm gets four hyperparameter configurations, two refined finalists, and three final seeds. The held-out evaluation uses four matched initial hits per pool. Models and hyperparameters are selected only with training and validation data.

For the 580 held-out pools with at least 15 molecules, mean purchases to the best compound were 5.690 for mean/SD, 5.709 for mean/SD/incumbent, 5.498 for EI imitation, and 5.525 for analytic EI. The EI imitation network agreed with the teacher on 98.1% of shared held-out contexts. No primary acquisition comparison was significant after Holm correction.

- [Endpoint report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_ei_inputs_k1/reports/ei_ingredients_K1_report.pdf)
- [Acquisition summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_ei_inputs_k1/reports/summary.csv)
- [Paired comparisons](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_ei_inputs_k1/reports/paired_comparisons.csv)
- [Teacher agreement](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_ei_inputs_k1/reports/teacher_summary.csv)
- [Protocol](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_ei_inputs_k1/protocol.json)

Checkpoints, test results, and all analysis outputs are saved under this experiment's absolute workspace directory. The matched K=1 models are newly trained; the earlier mixed-batch models are retained unchanged in their original directory.
