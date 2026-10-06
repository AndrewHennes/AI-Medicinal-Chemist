## Scope and provenance

This package contains the most recent single-endpoint conditional-prediction comparison and ALPaCA offset ablation. It preserves the numerical definitions from the completed benchmark while consolidating modules and eliminating imports through earlier experiments. Methods are local implementations of published families, with project-specific handling of relative labels, nuisance offsets, noise, and ensemble predictions.

Thirteen model configurations and random acquisition are available. The standard is the average-mean plus average-reference-kernel ensemble with directly calculated expected improvement. No reinforcement-learning actor is trained in this particular benchmark.

## Data partitions and information access

Five outer folds group related series across endpoints using the saved shared-molecule, source-document, and prior-group connections. A held-out group cannot appear in training or validation for its test fold. The intended train/validation/test proportions are approximately 64/16/20 percent; actual counts follow linked-group assignment and are provided in `results/published/realized_modern_splits.csv`.

The supplied 512-dimensional MiniMol embeddings are fixed. Principal component analysis, abbreviated PCA, uses unique molecules from outer training groups across endpoints. Models share this structural preprocessing, but a single-endpoint model sees only that endpoint's training labels. The selected representation keeps 32 components and divides them by one common root-mean-square eigenvalue scale, rather than whitening every component separately.

For endpoint-transformed outcomes \(y\), the scale is fitted with equal training-pool weight,

\[
s_e=\max\left(0.05,\sqrt{\frac1S\sum_{s=1}^S\frac{2m_s}{m_s-1}\operatorname{Var}_0(y_s)}\right).
\]

Model-visible observations are \(z_i=(y_i-y_r)/s_e\), where \(r\) is the initial hit. All objectives are oriented to minimize. This full-training allocation differs from earlier studies that separated predictor and policy training groups.

Training draws a large series with probability one half when available and otherwise samples from all training series. It combines random and worse-half references, contexts with no additional measurement and contexts up to 24 additional compounds, and random or spatially clustered context draws. Query labels are used only in training loss or held-out evaluation. The model prediction API accepts measured features/outcomes and unmeasured query features, not hidden outcomes.

## Current reference architecture

An ordered pair network maps concatenated projected embeddings through two width-64 Gaussian error linear unit layers to a delta.  For measured set \(C\), with \(n=|C|\),

\[
a_q=\frac1n\sum_{j\in C}\delta_\theta(x_q,x_j),\qquad
\bar a=\frac1n\sum_{i\in C}a_i,\qquad
m_q^0=a_q-\bar a+\bar z.
\]

Self-pair terms in measured averages are exactly zero. The covariance is a radial basis kernel on PCA coordinates with learned coordinate scales and bandwidth,

\[
k(x_i,x_j)=\exp\left[-\frac1{db}\sum_{\ell=1}^d
\left(\frac{x_{i\ell}-x_{j\ell}}{s_\ell}\right)^2\right].
\]

Let \(H=I-\mathbf1\mathbf1^\top/n\), \(G=\mathbf1\mathbf1^\top/n\), and \(\omega=\mathbf1/n\). The centered residual is \(e=H(z-a)\), and

\[
A=HK_{CC}H+\lambda H+G,
\quad c_q=(k_{qC}-\omega^\top K_{CC})H,
\quad a_q^{\mathrm{ker}}=1-2k_{qC}\omega+\omega^\top K_{CC}\omega.
\]

The \(G\) term fixes an unused constant direction and is not additional measurement noise. Twenty-four learned Richardson steps start from zero,

\[
\alpha_{t+1}=\alpha_t+\eta_t(e-A\alpha_t),\qquad
\eta_t=\frac{1.8\,\operatorname{sigmoid}(\ell_t)}
{\max(1,\max_i\sum_j|A_{ij}|)}.
\]

A context encoder averages per-observation vectors. A final network combines the pair representation, context vector, residual statistics, distance summaries, and the correction \(u_q=c_q\alpha_{24}\). It emits a correction gate, bias, positive variance multiplier, and positive additional variance,

\[
\mu_q=m_q^0+2\operatorname{sigmoid}(o_1)u_q+\mathbf1_{n>1}o_2,
\qquad \kappa_q=a_q^{\mathrm{ker}}-c_qA^{-1}c_q^\top.
\]

The conditional variance uses a double-precision Cholesky solve. It does not use an explicitly formed inverse. The predictive mean combines neural and kernel components with a learned multiple of \(\kappa_q\). Microsomal and in vivo clearance use Gaussian members. The other endpoints use Student-t members with learned degrees of freedom above 2.1. The Student-t scale is converted correctly to predictive variance.

`pair_backbone` retains checkpoint-compatible projection parameters and their initialization order. The active reference forward pass uses the documented pair/context encoders.

## Published baseline families

The transfer model learns a pointwise neural mean and variance, then aligns a new series using mean measured residual. Fine-tuning uses the corresponding selected transfer weights and adapts on support contrasts. Model-agnostic meta-learning, abbreviated MAML, differentiates through support updates to all network weights. Almost No Inner Loop, abbreviated ANIL, updates only the final head. The implementations retain second-order gradients where required (https://proceedings.mlr.press/v70/finn17a.html; https://arxiv.org/abs/1909.09157).

A conditional neural process uses a mean-pooled set representation. The attentive neural process includes both deterministic attention and a latent variable trained with a variational objective. Its prediction-time latent distribution reads context only. The diagonal Transformer neural process masks query-to-query attention and has no positional encoding. Chunking the queries therefore does not change other predictions (https://proceedings.mlr.press/v80/garnelo18a.html; https://arxiv.org/abs/1901.05761; https://proceedings.mlr.press/v162/nguyen22b.html).

ALPaCA learns a neural feature map \(\phi\) and a full Gaussian prior over linear weights. The induced prior mean and covariance are \(m(x)=\phi(x)^\top w_0\) and \(k(x,x')=\phi(x)^\top\Sigma_0\phi(x')\). Historical training learns the basis, prior, and positive observation-noise scalar. New measured compounds update its posterior analytically (https://arxiv.org/abs/1807.08912).

The neural-mean conventional GP uses a pointwise mean network and an RBF or Matérn-5/2 covariance. Deep-kernel transfer learns a representation and shared kernel parameters. Adaptive deep-kernel fitting with implicit function differentiation optimizes three support-specific kernel/noise parameters with BFGS and differentiates the outer query loss through the stationary inner optimum. Inner-solver tolerance, iteration budget, parameter bounds, prior penalty, and Hessian damping are recorded in the configuration (https://proceedings.mlr.press/v51/wilson16.html; https://arxiv.org/abs/1910.05199; https://arxiv.org/abs/2205.02708).

## Offset-enabled Gaussian posterior and ablation

The GP-family and standard ALPaCA implementations account for a flat-prior unknown series intercept. Define \(A=K_{CC}+\tau^2I\), \(h=A^{-1}\mathbf1\), \(p_b=\mathbf1^\top h\), and

\[
\hat b=\frac{\mathbf1^\top A^{-1}(y_C-m_C)}{p_b}.
\]

Then

\[
\mu_q=m_q+\hat b+k_{qC}A^{-1}(y_C-m_C-\hat b\mathbf1),
\]

\[
V_q=k_{qq}+\tau^2-k_{qC}A^{-1}k_{Cq}
+\frac{(1-k_{qC}h)^2}{p_b}.
\]

The no-offset ablation fixes the additional intercept to zero and removes its variance correction while retaining neural biases. It uses the offset model's validation-selected hyperparameters and fresh weights. Both the historical ablation and packaged runner use this matching rule.

## Training, selection, and numerical recovery

Each main family has three predeclared trials, 1,200 search updates with seed 11, and 4,000 fresh final updates with seeds 11, 29, and 47. AdamW uses the configured learning rate, weight decay 0.001, clipping at gradient norm five, and a cosine schedule with a ten-percent floor. Each update averages eight episodes. Validation occurs after the first update, every 200 updates, and at the final update. Its score averages equal-pool NLL over all eligible pools and over pools of at least fifteen compounds with equal weight for these two strata.

Fine-tuning reuses the selected transfer ensemble and searches only its adaptation settings. ALPaCA without offset reuses the selected ALPaCA settings but trains afresh. Other final fits do not continue their search checkpoint.

The runner rejects an entire configuration when fitting or validation is numerically invalid. All three required final members must succeed. If they do not, the next predeclared validation-ranked configuration is considered and rejected artifacts remain on disk. Programming and provenance errors are fatal. A held-out evaluation failure is recorded without selecting replacement hyperparameters using test outcomes.

Protocol fingerprints include configuration, data hashes, code hashes, and validation episode identities. Resumption saves model, optimizer, NumPy generator state, PyTorch generator state, progress, and best validation score. A changed implementation or protocol requires a new output root.

## Prediction and uncertainty evaluation

For each held-out series, fixed query molecules remain hidden as nested measured contexts grow through one, two, three, five, and ten compounds. Larger pools reserve five query molecules. Smaller pools use the recorded feasible query/context sizes. The same episode identities are shared by all models.

R² is computed from pooled squared errors with equal total weight per series. Spearman correlation is computed within each query set, then averaged across draws and series. Constant target or prediction vectors have undefined rank correlation and are counted separately. The code does not treat an undefined correlation as zero.

An ensemble has three independently trained members. Its density is an equal-weight mixture, with nested latent samples for ANP. Negative log likelihood, abbreviated NLL, evaluates that mixture directly. Its moments satisfy

\[
\bar\mu=\frac1M\sum_m\mu_m,\qquad
\bar V=\frac1M\sum_m(V_m+\mu_m^2)-\bar\mu^2.
\]

The 90-percent intervals use marginal mixture quantiles rather than a Gaussian approximation. No post-hoc calibration is applied in this latest suite. NLL and widths are in training-standardized endpoint units; they are not directly raw clearance units.

## Acquisition and relative performance

With current best value \(b\), mean \(\mu_q\), and standard deviation \(\sigma_q\), the directly calculated minimization EI is

\[
z_q=\frac{b-\mu_q}{\sigma_q},\qquad
\mathrm{EI}(q)=(b-\mu_q)\Phi(z_q)+\sigma_q\phi(z_q).
\]

The implementation evaluates Gaussian expected improvement from mixture moments using a stable log-EI calculation, including extreme tails.

The initial hit is sampled from the worst half and is free. Four deterministic starts per pool are evaluated. Metrics count purchases to any compound in the top one, two, three, or four, including threshold ties and zero purchases when the initial hit already qualifies. For a pool of total size \(P\) with \(g\) acceptable unmeasured compounds and a nonqualifying hit, random acquisition takes \(P/(g+1)\) purchases in expectation.

Relative plots compare matched panels. Percent fewer purchases than random is \(100[1-\overline{\tau}_{\mathrm{model}}/\overline{\tau}_{\mathrm{random}}]\), using the displayed equal-assay averages. The NLL difference subtracts the current reference at five measured compounds. Group bootstrap intervals condition on fitted models. Summaries use exploratory development-fold evaluations.

## Validation of this extraction

The migration checks compare the original and packaged models on exact seeded parameter initialization, one- and four-observation predictions, losses, and gradients for both Gaussian and Student-t endpoints. Additional tests check Gaussian posterior identities, ALPaCA weight-space equivalence, MAML second-order derivatives, implicit hypergradients, query isolation, measured-set order, mixture moments, exact random expectation with ties, and uninterrupted versus resumed training. Saved-checkpoint verification and a real-data inference example are recorded separately.
