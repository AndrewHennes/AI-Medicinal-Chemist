# Chemical-series adaptation benchmark

This directory implements the internally trained comparator suite proposed in the [benchmark framework](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark_design/benchmark_framework.md). The designated reference remains the single-endpoint average-mean and average-reference-kernel neural ensemble, followed by directly calculated expected improvement (EI). There is no learned acquisition network in this benchmark.

The code is implemented and has a separate integration pilot. Pilot results are not comparative performance results. The full five-fold experiment is a separate, resumable run. Its final report refuses to build until every specified condition has completed. Existing historical checkpoints and reports are unchanged.

## Implemented conditions

| Identifier | Architecture and defining training behavior | Adaptation at inference |
|---|---|---|
| reference | Existing pair-delta mean, centered residual kernel, 24 learned iterative correction steps, learned kernel-based variance; existing endpoint-specific Gaussian or Student likelihood | Conditions on all acquired observations with frozen network weights |
| transfer | Feedforward molecular mean and observation variance, trained on historical within-series prediction episodes | Anchors predictions with the mean measured residual; weights stay frozen |
| finetune | Exactly the selected transfer checkpoints | Regularized gradient steps on measured contrasts; no update from hidden targets |
| neural_mean_gp | Learned pointwise neural mean with a conventional Matérn-5/2 or radial basis function covariance on PCA32 | Gaussian conditioning with an unknown constant series offset |
| alpaca | Adaptive Learning for Probabilistic Connectionist Architectures (ALPaCA); learned features, full Gaussian linear-head prior, conditional query likelihood | Analytic Bayesian linear regression, evaluated through equivalent function-space covariance algebra |
| maml | Model-Agnostic Meta-Learning (MAML); full second-order differentiation through support updates | Updates all trainable predictor parameters from support contrasts |
| anil | Almost No Inner Loop (ANIL); meta-trained body and head | Updates only the final mean/variance head |
| cnp | Conditional Neural Process (CNP); pooled measured-pair encoding and Gaussian decoder | Direct context-conditioned prediction |
| anp | Attentive Neural Process (ANP); context self-attention, query cross-attention, latent task variable, variational objective | Marginalizes 32 reproducible latent samples per ensemble member |
| tnp_d | Deterministic Transformer Neural Process (TNP-D); masked transformer and marginal Gaussian decoder | Context-conditioned attention, with no query-to-query information flow |
| dkt | Deep Kernel Transfer (DKT); learned feature adapter plus shared GP hyperparameters, trained with per-task marginal evidence | Exact GP conditioning, without local hyperparameter fitting |
| adkf_ift | Adaptive Deep Kernel Fitting with the Implicit Function Theorem (ADKF-IFT); support evidence optimization and implicit outer gradients | Fits three task-specific GP hyperparameters, then conditions the GP |
| random | Acquisition-only analytical expectation | No predictor or uncertainty metrics |

The algorithm families are implemented for this regression benchmark using frozen MiniMol principal components. External pretraining, including TabPFN, is a separate track. This suite requires no external model weights.

## Protocol and fairness

There are five existing global linked folds and six separate endpoint benchmarks. Species remain pooled within each endpoint, including the species labels already present in the source metadata. There is one trained ensemble per endpoint, fold and method. The three member seeds are 11, 29 and 47. Ensemble members are not independent experimental replicates.

The former predictor-training and policy-training roles are reunited within the outer-training split. Direct EI needs no held-out policy-training labels. Every method, including a freshly fitted reference, gets this same expanded training set. Validation and test groups remain excluded from training. PCA fitting indices are checked against outer-training molecular indices. Linked groups and molecular feature identities are checked for overlap across partitions.

Training samples series with a mixture of equal-pool sampling and extra emphasis on pools with at least 15 compounds. Context and query sets are disjoint. Contexts can contain one initial observation and up to 24 additional observations. A mixture of random and chemically clustered supports follows the earlier reference protocol. No sign-consistency, cycle-consistency or ranking auxiliary loss has been added.

The input is fixed at PCA32 in this first suite. Each independently trained family receives three predeclared hyperparameter settings, 1,200 search updates per setting, and 4,000 updates per final member, all starting from fresh weights. The search varies applicable network widths, Bayesian feature dimensions, latent dimensions, transformer depth, kernel family, learning rate and gradient-update settings. The reference architecture stays fixed and searches its learning rate. Fine-tuning reuses the exact selected transfer ensemble and searches only three update rules. Different algorithms take different amounts of compute per update, which is recorded.

Selection uses validation marginal negative log-likelihood (NLL), with half the weight on equal-pool performance across all sizes and half on pools of at least 15 compounds. Checkpoint selection uses one fixed validation draw per pool, keeping all eligible large validation pools and a deterministic selection of smaller pools. All architecture and hyperparameter choices finish before full test evaluation starts. There are 990 search fits and 990 final member fits, excluding the fine-tuning condition, which shares transfer weights.

At prediction evaluation, one, two, three, five and ten measurements are revealed using nested supports and fixed hidden query sets. Small pools contribute at the context sizes they support. Pools of at least 15 support the entire curve with five common hidden queries. Pools with only one hidden query cannot contribute Spearman correlation; they still contribute NLL, squared error, calibration and acquisition measurements. Eligibility counts are reported.

All acquisition comparisons use one purchase at a time, the same four starting hits drawn from the worse half, and directly calculated Gaussian EI from the ensemble mean, total observation standard deviation and best measured value. Gaussian EI uses matched moments even for Student or latent mixtures. The initial measurement costs zero. Metrics are purchases to any top-1, top-2, top-3 or top-4 compound, including ties. Pool cutoffs are 3, 15, 20, 25 and 30. The random expectation is calculated exactly, including already-successful starting hits.

Prediction outputs include weighted pooled R² on relative targets, macro within-series Spearman correlation, native marginal mixture NLL, 90% interval coverage and interval width. Here native means that the density is scored as its actual Gaussian, Student or latent mixture, rather than replacing it with a moment-matched Gaussian. Labels and density units are standardized by the fold-training endpoint scale. Interval endpoints are numerical quantiles of the predictive mixture. No post-hoc uncertainty recalibration is applied. Acquisition intervals use paired bootstrap resampling of global linked groups, with equal pools within each endpoint and equal endpoints in the aggregate.

## Series offsets and measurement noise

Let the measured context be \(C=\{(x_i,y_i)\}_{i=1}^{n}\), and let \(q\) denote a hidden query. Only observed labels enter the inference interface. All outcomes are minimized after the existing endpoint transformation. The outcome scale is fitted from the outer-training pools alone.

Neural-process inputs use \(y_i-\bar y_C\), where \(\bar y_C\) is the mean of the measured labels. The predicted mean is shifted back by \(\bar y_C\). This makes the wrapper invariant to an arbitrary constant series offset. It does not assume that the centered measurement errors become independent.

For the pointwise transfer and gradient models, let \(m_\theta(x)\) and \(v_\theta(x)>0\) be the network outputs. The context-anchored prediction is

\[
\mu_q=m_\theta(x_q)+\frac1n\sum_{i\in C}\left(y_i-m_\theta(x_i)\right),\qquad
v_q=v_\theta(x_q)+\frac1{n^2}\sum_{i\in C}v_\theta(x_i).
\]

The second term accounts for uncertainty in the measured average under the independent observation-noise model. It is not a complete posterior over neural weights. Between-member disagreement supplies an additional ensemble contribution. Inner-loop updates use an orthonormal contrast basis \(U\), with \(U^\top\mathbf1=0\) and \(U^\top U=I\), and the likelihood

\[
U^\top y_C\sim\mathcal N\left(U^\top m_C,\ U^\top\operatorname{diag}(v_C)U\right).
\]

There are \(n-1\) observed contrasts, rather than \(n(n-1)\) independent pair labels. A single observation supplies no contrast, so these models skip gradient adaptation in that case. They still use the observation as an anchor. Ordinary fine-tuning penalizes departure from pretrained weights. MAML and ANIL optimize the query loss through the complete inner update, including second-order terms.

The Bayesian models use an unknown constant offset with a flat prior. Write \(m_C\) for the prior mean, \(K_{CC}\) for latent covariance, and \(\tau^2\) for raw observation variance. Define

\[
A=K_{CC}+\tau^2I,\quad h=A^{-1}\mathbf1,\quad
\widehat b=\frac{\mathbf1^\top A^{-1}(y_C-m_C)}{\mathbf1^\top A^{-1}\mathbf1}.
\]

For a new observed outcome, the conditional mean and variance are

\[
\mu_q=m_q+\widehat b+k_{qC}A^{-1}(y_C-m_C-\widehat b\mathbf1),
\]

\[
v_q=k_{qq}+\tau^2-k_{qC}A^{-1}k_{Cq}
+\frac{(1-k_{qC}h)^2}{\mathbf1^\top h}.
\]

The final term represents uncertainty about the unknown offset. With one measured compound this reduces to

\[
\mu_q=y_1+m_q-m_1,\qquad
v_q=k_{qq}+k_{11}-2k_{q1}+2\tau^2.
\]

Thus the initial measurement is not silently treated as noise-free. If raw measurement noise is independent, contrasts that share a reference are still correlated. The implementation uses either orthonormal contrasts or the equivalent unknown-intercept conditioning equations to retain this relationship. Computation uses Cholesky solves in double precision.

DKT and the neural-mean conventional GP train with restricted marginal evidence of the observed contrasts within sampled training tasks. DKT has a zero shared mean apart from the unknown series offset. The conventional-GP comparator learns a pointwise neural mean. This is a newly fitted comparator with an explicit offset model, not a byte-for-byte reproduction of an earlier GP checkpoint. ALPaCA instead optimizes conditional query NLL, learns its basis and full Gaussian head prior, and conditions analytically. Its learned observation noise and unknown-intercept treatment are declared extensions of the original known-noise formulation.

## Latent and implicit-gradient details

ANP has both a deterministic attentive path and a latent Gaussian task distribution. During training its latent posterior encoder sees training support and query labels, as required for variational inference. Inference uses only the support-conditioned latent prior. The loss is the sum of query negative log-likelihood and the posterior-to-prior Kullback–Leibler divergence, divided by the number of queries. Inference uses 32 fixed antithetic normal draws per member for reproducible marginal predictions. These are latent integration draws, not separately trained ensemble members.

TNP-D has no positional embeddings. Both context and query rows may attend only to context columns. Query labels are replaced by zeros and an observed-status indicator distinguishes measured tokens. Context states cannot read queries, and queries cannot read one another. This mask preserves permutation equivariance and makes predictions independent of the size or ordering of an inference chunk.

ADKF-IFT adapts lengthscale, amplitude and observation noise using support-only restricted evidence with a weak quadratic hyperparameter prior. The prior regularizes the very small supports in this benchmark. It uses smooth physical bounds rather than clipped optimization coordinates. The feature adapter is trained by the conditional query objective. If \(\theta\) denotes the adapter weights and \(\phi\) the fitted GP hyperparameters, the implemented gradient is

\[
\frac{dL_Q}{d\theta}=\partial_\theta L_Q-
\partial^2_{\theta\phi}L_C\left(\partial^2_{\phi\phi}L_C\right)^{-1}\partial_\phi L_Q.
\]

The inner fit uses BFGS and records its stationarity residual. The Hessian solve uses small, logged damping. A materially nonstationary fit fails visibly instead of silently becoming an approximate update. This is implicit differentiation rather than a stop-gradient fit or an unrolled surrogate. The flat offset, contrast evidence, weak hyperparameter prior and damping are benchmark adaptations. ADKF and DKT share the same kernel family search and learned-adapter design, but differ in their local hyperparameter adaptation and outer objective.

Every condition uses three independent final fits. If member \(s\) returns mean \(\mu_s\) and observation variance \(v_s\), acquisition uses

\[
\mu=\frac1S\sum_s\mu_s,\qquad
v=\frac1S\sum_s v_s+\frac1S\sum_s(\mu_s-\mu)^2.
\]

The population denominator \(S\), rather than \(S-1\), gives the exact mixture variance. NLL uses log-sum-exp over actual component densities. The original reference retains its Student distributions for the endpoints that previously used them.

## Files and execution

All paths in the entrypoints are absolute. No working-directory change or command-line arguments are needed. The existing analysis environment is used. No package installation, GPU or new external dataset is required.

Run the full experiment with

```sh
/Users/asselism/Documents/Codex/2026-09-23/i-h/work/analysis_environment/bin/python /Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/run_benchmark.py
```

The same command resumes interrupted runs. Four CPU processes are used, each with one numerical thread. Changing worker count or experiment settings is done in [settings.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/settings.py). Checkpoints include optimizer state, NumPy and PyTorch random states, selected validation case identity, data hashes and source hashes. Resume refuses changed provenance rather than mixing incompatible experiments. A process lock prevents two full invocations from writing the same runs. A long benchmark requires the computer to remain awake.

Useful entrypoints are [benchmark_models.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/benchmark_models.py), [training.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/training.py), [evaluation.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/evaluation.py), and [run_smoke.py](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/run_smoke.py).

The integration pilot trains short models on fold 0 microsomal training series, reloads each saved model, evaluates held-out validation contexts, and completes EI trajectories on a three-compound and a 15-compound validation pool. It also executes a training loss and prediction for every family across all 30 endpoint/fold combinations. Test outcomes are not used in this pilot. The [test suite](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark/test_benchmark.py) additionally checks analytic posteriors, exact mixture variance, second-order and implicit gradients, initial-hit handling, random acquisition expectations, invariance properties, checkpoint resume equivalence, summary weighting, and agreement with archived reference inference.

Full outputs go to this directory. Runs and checkpoints are under runs, per-condition test predictions under evaluations, machine-readable status under progress, and the endpoint-separated PDF and CSV results under reports. Integration outputs are separately labeled under smoke and checks. There is no full benchmark leaderboard until the full run completes.

## Primary precedents

MAML follows Finn et al. ([paper](https://proceedings.mlr.press/v70/finn17a.html)). ANIL follows Raghu et al. ([paper](https://arxiv.org/abs/1909.09157)). The probabilistic Gaussian head, contrast likelihood, anchoring and ensemble evaluation are adaptations in this benchmark.

ALPaCA follows Harrison et al. ([paper](https://arxiv.org/abs/1807.08912)). Bayesian conditioning and the unknown-intercept construction use Gaussian linear-model algebra, with the related GP framework described by Rasmussen and Williams ([chapter](https://gaussianprocess.org/gpml/chapters/RW2.pdf)).

CNP follows Garnelo et al. ([paper](https://proceedings.mlr.press/v80/garnelo18a.html)). ANP follows Kim et al. ([paper](https://arxiv.org/abs/1901.05761)). TNP-D follows Nguyen and Grover ([paper](https://proceedings.mlr.press/v162/nguyen22b.html)). Input encoders, dimensions, observed-token flags and support-label centering are specified above so the precise benchmark variants are reproducible.

DKT follows Patacchiola et al. ([paper](https://arxiv.org/abs/1910.05199)). ADKF-IFT follows Chen et al. ([paper](https://arxiv.org/html/2205.02708v3)). The latter paper provides direct molecular-property precedent, although its original task definitions and support sizes differ from this benchmark.

Ensemble uncertainty follows the regression principle of independently trained probabilistic predictors described by Lakshminarayanan et al. ([paper](https://arxiv.org/abs/1612.01474)).
