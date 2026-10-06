# Normal CDF and density features at K=1

The new model receives

\[
[\mu,\sigma,u_{\mathrm{best}},\Phi(z),\phi(z)],\qquad
z=\frac{\mu-u_{\mathrm{best}}}{\max(\sigma,10^{-12})}.
\]

Here \(\Phi\) is the standard normal cumulative distribution function and \(\phi\) its density. Inputs are computed from the frozen GP posterior and the best outcome actually measured in the current series. Every outcome is expressed as a utility relative to the original starting hit. No unmeasured outcomes enter these features.

The directly matched control has the same five input slots, network parameters, initialization, and training schedule, but masks the last two channels to zero. Both models use the previous optimum-membership binary cross entropy plus 0.1 Huber utility-regression objective. Neither model is trained to imitate EI. The earlier three-input model, EI imitation network, analytic EI, and random selection remain historical references evaluated on the same folds and starting hits.

Explicit EI, the standardized gap, and the weighted EI summands are not inputs. The model still learns how to combine the five supplied quantities. At K=1, the previous subset attention layers operate on singleton sets; they do not supply cross-molecule attention. Existing whole-pool summaries and cardinality features remain present.

All six endpoints, five grouped folds, three neural-model seeds, and four common initial hits are included. The main comparison contains 580 held-out pools with at least 15 molecules. There are 4,625 held-out pools overall.

| Model | Mean purchases to the best compound, pools ≥15 |
| --- | ---: |
| Matched three-input control | 5.73290 |
| Added normal CDF and density | 5.73017 |
| Analytic EI | 5.52457 |
| Earlier EI imitation network | 5.49756 |

The matched five-slot control and engineered-feature model share their initialization scheme. The historical three-slot control is reported separately.

- [Endpoint report](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_features_k1/reports/normal_cdf_density_features_K1_report.pdf)
- [Acquisition results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_features_k1/reports/summary.csv)
- [Paired comparisons](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_features_k1/reports/paired_comparisons.csv)
- [EI agreement diagnostics](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_features_k1/reports/teacher_summary.csv)
- [Protocol](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_phi_features_k1/protocol.json)

All checkpoint and analysis products are saved under this workspace directory. Training runs through the absolute-path `run_experiment.py` script; report rendering is a separate `phi_report.py` script. Neither has command-line options. Both phases were completed for the reported results.
