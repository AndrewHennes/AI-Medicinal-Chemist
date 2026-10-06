**A benchmark framework for adaptation to unfamiliar chemical series**

Prepared October 2, 2026. This document contains literature research and proposed experiments. No new models were implemented, trained, or evaluated for this report. Recommendations are hypotheses to test, not predictions that a published architecture will outperform the current model.

The reference is the existing **single-endpoint neural ensemble with the average pair-delta mean, average-reference kernel, and directly calculated expected improvement (EI)**. This is the `direct_ei` condition in [the completed comparison protocol](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_ei_acquisition/protocol.json). It is neither a conventional Gaussian process (GP) nor a learned acquisition network. A record of the designation is saved in [reference_model.json](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/meta_learning_benchmark_design/reference_model.json).

The reference uses MiniMol principal components, a pairwise neural baseline, context-dependent residual correction, kernel-derived variance with learned adjustments, and three trained ensemble members. The predictor is frozen during acquisition, but conditions on newly measured compounds. Each endpoint has its own predictor; the existing species treatment is retained. This is compatible with meta-learning across series. Here an endpoint is a separate benchmark, while a series/species measurement pool is an adaptation task. Linked groups that connect molecules, documents, or series remain the units for splitting and uncertainty estimates.

The current metadata contains Human, Rat, and Mouse pools, plus Dog-labeled permeability and efflux pools. These labels describe the existing dataset; no species filtering was changed in this review. Species are pooled during endpoint training, and the current predictor has no species-specific output heads.

**I recommend covering different adaptation mechanisms before adding many variants of the same mechanism.** A useful suite should tell us whether the current model benefits from its particular correction architecture, from learning an initialization, from learning a prior, or simply from pooling historical data. There is no single universally accepted list for our exact problem. Published molecular few-shot benchmarks often transfer across assays, whereas we transfer across series within an endpoint.

The closest direct molecular evidence I found is the regression extension used by Adaptive Deep Kernel Fitting with the Implicit Function Theorem (ADKF-IFT). It evaluates conditional neural processes, Deep Kernel Transfer, conventional GPs, and its adaptive kernel method on held-out assays. Its support sizes begin at 16 measurements, so this evidence does not establish performance in our one-to-ten-measurement regime ([Chen et al.](https://arxiv.org/html/2205.02708v3)). The original FS-Mol benchmark is chiefly classification; its classification leaderboard should not be presented as regression evidence ([FS-Mol paper](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/8d3bba7425e7c98c50f52ca1b52d3735-Paper-round2.pdf)). Graph neural processes also have molecular regression and optimization evidence, but on docking scores across protein targets rather than our experimental endpoints ([García-Ortegón et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11515514/)).

I used six selection criteria. A candidate should support continuous regression; produce a predictive distribution suitable for uncertainty evaluation; incorporate measurements from a new series; have a published algorithm whose identity survives our adaptation; support a comparison with the same molecular representation and historical labels; and test a mechanism not already represented by another comparator. Computational cost and reproducible author code determine implementation order, rather than substituting for these scientific criteria.

| Comparator | What changes after a measurement? | What the comparison would establish | Recommended placement |
|---|---|---|---|
| Pretrained neural ensemble, frozen | Only the explicitly specified series anchoring/conditioning | How much historical prediction alone achieves | Essential control |
| Same pretrained ensemble, fine-tuned | Selected weights updated using measured compounds | Whether ordinary transfer learning is sufficient | Essential control |
| Neural mean + conventional GP | GP posterior changes; feature map remains fixed | Whether standard residual conditioning matches the custom update | Essential control |
| ALPaCA | Posterior over a small linear prediction head | Whether a meta-learned prior plus an analytic update is enough | First wave |
| MAML | Neural weights take a few gradient steps | Whether training specifically for adaptation helps | First wave |
| CNP | Pooled representation of the measured set changes | What a simple established set-conditioned predictor achieves | First wave |
| ANP | Query-specific attention and latent task distribution change | Whether learned retrieval and function uncertainty help | First wave |
| TNP-D | Masked transformer conditions predictions on measurements | Stronger pure neural conditional prediction without a GP solve | First wave |
| DKT | GP posterior changes in a learned feature space | Whether meta-learned geometry is sufficient | First wave |
| ANIL | Only the neural output head takes inner-loop steps | Whether MAML needs representation adaptation | Paired extension |
| ADKF-IFT | Task-specific GP hyperparameters and posterior change | Whether adapting noise and lengthscales improves DKT | Priority extension |
| Pinned TabPFN regressor | Pretrained transformer conditions on a new table | What external synthetic pretraining adds | Separate external-pretraining track |

This is a suite of comparator conditions, not a claim that they are equally expensive or equally likely to succeed. The frozen and fine-tuned transfer models should share a backbone. CNP/ANP, MAML/ANIL, and DKT/ADKF-IFT are particularly informative paired comparisons. Random acquisition remains a cheap acquisition-only reference; it has no prediction or uncertainty scores.

**The common prediction interface is a distribution for each hidden molecule given the currently measured set.** Let \(x_i\) be the molecular representation, \(y_i\) the transformed property with lower values favorable, \(C=\{(x_i,y_i)\}_{i=1}^{n}\) the measured context, and \(q\) a hidden query. Each model supplies

\[
p_\theta(y_q\mid x_q,C),\qquad
\mu_q=\mathbb E[y_q\mid x_q,C],\qquad
v_q=\operatorname{Var}(y_q\mid x_q,C).
\]

Every primary acquisition comparison then uses the same rule, with \(b_C=\min_{i\in C}y_i\), \(\sigma_q=\sqrt{v_q}\), standard normal cumulative distribution \(\Phi\), and density \(\phi\):

\[
z_q=\frac{b_C-\mu_q}{\sigma_q},\qquad
\operatorname{EI}(q)=(b_C-\mu_q)\Phi(z_q)+\sigma_q\phi(z_q).
\]

At zero variance the limit is \(\max(b_C-\mu_q,0)\). Use the existing numerically stable implementation. For mixture or non-Gaussian predictors this is Gaussian EI applied to matched moments, as in the reference. Exact distribution-specific EI would be a separate shared acquisition experiment. For this K=1 comparison, the acquisition rule does not require a full covariance matrix over all unmeasured molecules.

**Ordinary transfer learning is the necessary control for claims about meta-learning.** Train a compact feedforward predictor on historical training series, with a mean and positive observation-variance output, and ensemble independent fits. At test time compare frozen weights against a few regularized gradient steps on the measured support. Keep the same backbone for the subsequent MAML comparison. The ensemble uncertainty construction has an established regression precedent ([Lakshminarayanan et al.](https://arxiv.org/abs/1612.01474)); the particular series-offset treatment and fine-tuning recipe would be our benchmark adaptations. Fine-tuning must not see query outcomes, and its learning rate, number of steps, and updated parameter subset must be selected on validation series.

This control is stronger than an unadapted network alone. If it matches a meta-learning method, the experiment suggests that historical representation learning and ordinary updating explain the benefit. It would not justify claiming that episodic optimization is essential. Conversely, a frozen model can still have context-dependent anchoring without its network weights learning anything new; that distinction must be explicit.

**Model-Agnostic Meta-Learning (MAML) learns weights that are useful after updating.** For a training series split into measured support \(C_s\) and hidden queries \(Q_s\), one inner step and the outer objective are

\[
\theta'_s=\theta-\alpha\nabla_\theta L(C_s;\theta),\qquad
\min_\theta\sum_s L(Q_s;\theta'_s).
\]

The original method includes regression ([Finn et al.](https://proceedings.mlr.press/v70/finn17a.html)). Our uncertainty-enabled version would use a Gaussian predictive head and independent ensembles; this is an extension, not a claim that vanilla MAML provides a Bayesian posterior. Preserve full second-order MAML initially; report a first-order approximation separately. Almost No Inner Loop (ANIL) keeps the body fixed during inner adaptation and updates only the head, while still meta-training the body ([Raghu et al.](https://arxiv.org/abs/1909.09157)). Freezing MiniMol by itself does not make a model ANIL.

This family tests the proposition that the update rule needs an initialization designed for rapid adaptation. Its main risk here is overfitting from one or two observations. The transfer control must therefore receive the same opportunity to tune regularization and adaptation steps. A probabilistic MAML method such as PLATIPUS is a defensible later extension, but adds another inference problem before we know whether gradient adaptation helps ([Finn et al., probabilistic MAML](https://arxiv.org/abs/1806.02817)).

**ALPaCA learns nonlinear features and a Bayesian prior for a linear output layer.** Its full name is Adaptive Learning for Probabilistic Connectionist Architectures. A neural feature vector \(h_\theta(x)\) feeds a series-specific head \(w_s\). In scalar-output notation,

\[
y_i=h_\theta(x_i)^\top w_s+\epsilon_i,\qquad
w_s\sim\mathcal N(m_0,S_0).
\]

For design matrix \(H_C\) and observation covariance \(R\), conditioning gives

\[
S_C=(S_0^{-1}+H_C^\top R^{-1}H_C)^{-1},\qquad
m_C=S_C(S_0^{-1}m_0+H_C^\top R^{-1}y_C).
\]

The query mean is \(h_q^\top m_C\); its variance is \(h_q^\top S_Ch_q\) plus observation noise. Features and prior are learned across tasks to improve conditional prediction ([Harrison et al.](https://arxiv.org/abs/1807.08912)). The core published formulation assumes known noise; estimating noise from historical training data or using an unknown-noise extension must be disclosed.

I give ALPaCA high priority because it is a clean alternative to our iterative correction. It tests whether most useful series adaptation fits into a small uncertain head. Feature dimensions of 16, 32, and 64 would probe that restriction. It supplies uncertainty from an explicit probability model, although that model can still be misspecified and poorly calibrated. Its potentially limiting assumption is that the learned basis adequately spans the behaviors of unseen series.

**Conditional Neural Processes (CNPs) learn a direct map from a measured set to predictive distributions.** A typical construction is

\[
r_C=\frac1n\sum_{i\in C}h_\theta(x_i,y_i),\qquad
(\mu_q,\sigma_q)=g_\theta(x_q,r_C).
\]

The decoder is trained with held-out query likelihood. It has no test-time weight update or matrix solve ([Garnelo et al.](https://proceedings.mlr.press/v80/garnelo18a.html)). This is the appropriate named baseline for a pooled context encoder. Its predicted variance can reflect uncertainty caused by sparse context; it should not be described as necessarily only measurement noise. However, it does not by itself provide an explicit decomposition of uncertainty or a shared random function across queries.

**Attentive Neural Processes (ANPs) make the context representation query-specific and include a latent task variable.** The query attends to relevant measurements, and a latent variable represents alternative functions consistent with the context. Conceptually,

\[
p(y_q\mid x_q,C)=\int p_\theta(y_q\mid x_q,r_q(C),z)\,p_\theta(z\mid C)\,dz.
\]

Train with the method's variational objective and marginalize latent samples at evaluation ([Kim et al.](https://arxiv.org/abs/1901.05761)). Removing the latent branch produces a conditional attentive variant, which should be named separately. CNP versus ANP does not isolate attention alone because the latent branch changes too; add a conditional attentive ablation if mechanistic attribution becomes important.

These models are particularly relevant to our earlier reference-weighting discussions. They learn which measured compounds matter for a query through conditioning, rather than through a prescribed similarity-weighted average. ANP is my first choice for an established neural architecture close to that idea. Its risk is that the learned conditioning rule will not generalize to unusual series. It also needs enough training tasks to learn an appropriate uncertainty response.

**Transformer Neural Process with diagonal predictive covariance (TNP-D) is the transformer comparator.** It uses masked attention over measured input-output tokens and query tokens without query labels, then emits a Gaussian marginal for each query ([Nguyen and Grover](https://proceedings.mlr.press/v162/nguyen22b.html)). This is a predictive transformer, unlike the acquisition transformers explored earlier in the project. It should receive molecular features and actual support measurements, not our reference model's precomputed mean and variance.

TNP-D is appropriate for the primary K=1 comparison because marginal means and variances suffice for the common EI rule. It does not supply a full correlated query distribution. Attention masking and position handling must preserve support permutation invariance and prevent hidden query labels from entering predictions. An implementation that lets candidate queries influence one another should be identified as transductive and assessed separately. Author code can use dense masked attention despite a sparse logical attention pattern, so actual memory and runtime require measurement.

**Deep Kernel Transfer (DKT) learns a feature space in which GP conditioning transfers across tasks.** It constructs

\[
k_\theta(x,x')=k_{\mathrm{base}}(h_\theta(x),h_\theta(x'))
\]

and learns shared parameters from per-task marginal likelihoods. On a new task, parameters stay fixed while its GP posterior conditions on the measurements ([Patacchiola et al.](https://arxiv.org/abs/1910.05199)). This is different from fitting a GP to fixed MiniMol coordinates; we need a trainable adapter above those coordinates. Conditional-query-loss training alone would be a DKT-inspired variant rather than a faithful reproduction of its standard training objective.

DKT is necessary to separate the value of our learned geometry from the particular residual update and variance head. Retain a conventional-kernel GP with a transferred neural mean as a simpler control. A support-dependent pairwise mean from our current architecture is not automatically a conventional GP prior mean; the control's mean and fitting procedure need an explicit definition. Standard GP mean functions and conditioning are described by [Rasmussen and Williams, Chapter 2](https://gaussianprocess.org/gpml/chapters/RW2.pdf).

**ADKF-IFT goes further by fitting some GP hyperparameters separately for each task.** Its outer training anticipates this fitting using implicit differentiation. This tests whether series-specific noise levels and lengthscales help beyond DKT's shared settings ([Chen et al.](https://arxiv.org/html/2205.02708v3)). I recommend it as the first extension after validating the DKT implementation. With only one or two local measurements, unconstrained hyperparameter fitting may be weakly identified. Bounds, initialization, numerical convergence, and any departure from the published procedure must be documented. The native method should not silently become “DKT with a few arbitrary test-time gradient steps.”

**Some recognizable few-shot methods are less suitable as primary comparators.** Prototypical classification and Matching Networks are not native continuous probabilistic regression baselines. A regression adaptation of attention-weighted support labels cannot extrapolate beyond their range and gives a constant mean with one support point unless an extra predictive mechanism is added; that would test our adaptation rather than the original method ([Matching Networks](https://arxiv.org/abs/1606.04080)). Memory-augmented neural networks did include regression experiments, but their sequential memory interface is less directly aligned with an unordered measured set ([Santoro et al.](https://proceedings.mlr.press/v48/santoro16.html)). Bayesian last-layer methods similar to ALPaCA can be added later if that family proves informative, rather than filling the initial suite with near-duplicates.

A pinned TabPFN regressor is worth a separate comparison because it uses large-scale synthetic pretraining to condition on small tabular datasets ([Hollmann et al.](https://www.nature.com/articles/s41586-024-08328-6)). It would share MiniMol inputs but not the same pretraining resources as internally trained methods. The exact checkpoint/version and predictive-density interface need recording. TabICLv2 is another external-pretraining candidate with regression support ([Qu et al.](https://arxiv.org/abs/2602.11139)); its name must not be confused with the earlier classification-only version. Neither paper establishes superiority for our extremely small within-series contexts. Keep these results in a clearly labeled track rather than treating them as equal-data ablations.

**A fair training protocol matters at least as much as the shortlist.** Retain the current five global linked-group folds, six endpoint transformations, species handling, initial-hit distribution, and K=1 acquisition task. Train one model per endpoint. Use the same frozen MiniMol inputs and a shared fold-specific PCA32 first. A later matched representation search can consider 16, 32, 64 components and full embeddings. Never fit PCA, scale factors, calibration parameters, or hyperparameters using held-out labels. Hold out linked series together even if a training method internally creates thousands of episodes from them.

There is one important choice before implementation. The current outer training set is divided into a predictor role and a policy-training role, inherited from the reinforcement-learning experiments. Direct EI does not need the latter. Two comparisons are valid:

1. Reproduce the current reference and give every new method the same predictor-label subset.
2. Reunite the two outer-training roles for every method and retrain the reference alongside them, while retaining outer validation/test groups.

The proposed main benchmark reunites predictor-training and policy-training roles within the outer-training split and refits the reference using the same data. The present reference remains an archival result. In the existing role split, cellular clearance and protein binding average about 34 and 31 predictor-training linked groups per fold, respectively ([split summary](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/neural_latent_acquisition/split_summary.csv)).

Keep a shared schedule of support sizes, with meaningful exposure to one-shot prediction and contexts of 2, 3, 5, and 10 measurements. Preserve the current documented preference for larger series in sampling/model selection, or change it for every method including the reference. Do not sample every possible pair as an independent observation: a series with n measurements still has n assay measurements, regardless of how many contrasts are constructed. The historical requested pair sampling rule makes expected sampled pair counts proportional to series size, rather than proportional to its number of possible pairs. Do not introduce sign-consistency losses.

Each algorithm should keep its defining training objective. Give MAML an outer loss after adaptation; give DKT its evidence-based training; give ANP its latent-variable objective. Force neither identical optimizers nor identical update counts on all families. Match a preregistered hyperparameter-search budget and record wall time, parameter counts, memory, and inference costs. Start with compact models given the effective task counts.

| Family | Proposed search dimensions, not claimed paper defaults |
|---|---|
| Transfer / MAML / ANIL | Hidden width 64 or 128; 2 or 3 layers; inner steps 1, 3, 5, 10; log-spaced inner learning rates; head-only versus full trainable-adapter updates; weight decay |
| ALPaCA | Basis dimension 16, 32, 64; feature width 64 or 128; full prior covariance versus a disclosed diagonal simplification; noise treatment |
| CNP / ANP | Width 64 or 128; latent dimension 8, 16, 32; 2 or 4 attention heads where applicable; decoder depth; latent Monte Carlo convergence |
| TNP-D | Width 64 or 128; 1, 2, 4 layers; 2 or 4 heads; dropout; pre-normalization and stable variance output |
| DKT / ADKF-IFT | Feature dimension 8, 16, 32; compact adapter depth; Matérn-5/2 versus RBF; lengthscale/noise bounds; scalar versus richer lengthscales; inner solve tolerance for ADKF |
| Shared | Learning rate, weight decay, validation stopping, and later the same representation-dimension search |

These are bounded searches, not an exhaustive Cartesian product. Select on a declared validation objective and retain all runs. I recommend the same validation negative log-likelihood (NLL) aggregation used for the reference as the primary selector, with ranking and squared-error metrics reported rather than silently used to choose different winners. If an acquisition-selected configuration is also desired, declare that as a separate selection track.

**Series offsets and the noisy reference need explicit treatment.** We do not want arbitrary assay offsets to dominate learning. Write a conceptual observation model as \(y_{s,i}=a_s+f_s(x_i)+\epsilon_{s,i}\), where \(a_s\) is a nuisance series offset. The current reference handles relative labels natively. A neural conditional model can instead center only on measured support values, use a fixed training-derived scale, and restore the support level when returning predictions. This is a task-specific wrapper, not an assumption that centered observation errors become independent. Bayesian comparators can explicitly include a series intercept or use a correctly specified contrast observation model. The precise choice must be documented before training; plain absolute-label prediction with an arbitrary global prior is not an equivalent treatment of batch offsets.

For independent raw measurement errors, nonreference differences to a noisy initial reference have covariance

\[
R_\Delta=\operatorname{diag}(\tau_i^2)+\tau_r^2\mathbf 1\mathbf 1^\top.
\]

This matters if fitting a probability model directly to those differences. It does not mean adding reference noise a second time after conditioning on its observed value. If a method conditions on the actual support observations including \(y_r\), then for the observed-reference target \(\Delta_q=y_q-y_r\),

\[
\mathbb E[\Delta_q\mid C]=\mathbb E[y_q\mid C]-y_r,\qquad
\operatorname{Var}(\Delta_q\mid C)=\operatorname{Var}(y_q\mid C).
\]

The observed reference is then a constant. This differs from inference about the latent contrast \(f_q-f_r\), whose variance includes posterior covariance with the latent reference. Do not mix these targets across methods. Exactly one measured molecule supplies an anchor but no observed within-series contrast. It cannot, by itself, identify a series-specific slope or reversed chemical effect independently of prior assumptions. Outcome-shift invariance, support permutation, and reference accounting are useful implementation checks; none require new labels.

**Prediction and acquisition should be evaluated separately.** For prediction, give all methods identical support trajectories and keep hidden query molecules fixed as context grows. Measure R², within-series Spearman correlation, marginal NLL, and interval coverage/width at 1, 2, 3, 5, and 10 measurements. A pool of 15 can reserve five fixed queries and reveal up to ten support measurements. Smaller pools contribute at feasible context sizes, with eligible counts reported. Do not attribute a change in average performance to adaptation when the composition of eligible series changes.

Report the exact R² denominator and aggregation. Do not average undefined per-series R² values from one-query panels. Likewise, Spearman correlation requires multiple nonconstant query outcomes; report exclusions. Larger and smaller series should have separate summaries. For common-context curves, use the same eligible series across the context sizes being compared where possible. The same transformed target units and scale conventions are required for comparing NLL values.

For acquisition, let each predictor drive its own direct-EI trajectory from the same four initial hits sampled from the worst half. Keep the initial hit free and report purchases to any top-1, top-2, top-3, or top-4 compound, including the existing tie handling. These remain the acquisition metrics; do not reintroduce regret measures as the main endpoint. Include all pools of at least three molecules, with pools of at least 15 as the primary practical stratum. Average pools within endpoint, then weight endpoints equally. Obtain paired uncertainty intervals by resampling linked groups, not individual pairs or trajectories as independent samples.

Use the actual marginal predictive density for NLL. For an ensemble this means the log of the mixture density, evaluated with log-sum-exp, rather than the density of a fitted Gaussian unless explicitly labeled. Match the reference's three-member ensemble budget in the main comparison and also report single-member results where useful. Three members combined into one predictor are one ensemble, not three independent experimental replications. Distinguish uncertainty across test groups from variability across independently retrained ensembles. The reference uses Gaussian and Student-t likelihoods across different endpoints, so a likelihood-matched sensitivity check is useful if a result is driven primarily by tail behavior.

For coverage and NLL, use prediction uncertainty for observed assay outcomes. For the primary EI comparison, preserve the reference's use of total predictive variance. Do not give one method latent-function variance and another observation variance while calling their acquisition rules identical. Report raw calibration and any validation-calibrated results separately. A larger standard deviation is not inherently better calibrated; NLL and coverage with interval width reveal different aspects of performance.

**The implementation order should support interpretable conclusions.** First establish the common prediction interface, support/target construction, uncertainty target, and data budget. Then run the three controls and ALPaCA, MAML, CNP, ANP, TNP-D, and DKT. Add ANIL and ADKF-IFT as paired extensions once their corresponding family implementations are verified. Keep externally pretrained tabular models in a separate track. Model-specific changes made after examining test results belong to another exploratory round, not a rewritten version of the original benchmark.

The comparisons have concrete interpretations. Transfer versus MAML tests meta-trained adaptation. MAML versus ANIL tests the need to change hidden representations. CNP versus ANP tests a richer context-conditioning model, with a further conditional-attention ablation needed to isolate attention. ALPaCA versus DKT tests a finite learned basis with Bayesian linear adaptation against a nonlinear GP covariance. DKT versus ADKF-IFT tests task-specific kernel hyperparameter adaptation. Each versus the current reference tests whether our bespoke residual and variance architecture adds value under the same data and acquisition rule.

**Primary implementations to audit before porting** are listed below. Availability of code is not a guarantee that its default configuration matches this benchmark. Pin a commit, record dependencies, retain the published algorithm's defining objective, and document every modification for continuous targets, support normalization, MiniMol inputs, and ensembles.

| Method | Author implementation |
|---|---|
| MAML | [cbfinn/maml](https://github.com/cbfinn/maml) |
| ALPaCA | [StanfordASL/ALPaCA](https://github.com/StanfordASL/ALPaCA) |
| Neural processes | [google-deepmind/neural-processes](https://github.com/google-deepmind/neural-processes) |
| PyTorch neural-process variants | [juho-lee/bnp](https://github.com/juho-lee/bnp) |
| TNP | [tung-nd/TNP-pytorch](https://github.com/tung-nd/TNP-pytorch) |
| DKT | [BayesWatch/deep-kernel-transfer](https://github.com/BayesWatch/deep-kernel-transfer) |
| ADKF-IFT | [Wenlin-Chen/ADKF-IFT](https://github.com/Wenlin-Chen/ADKF-IFT) |
| Molecular neural processes | [mgarort/graph-nps-for-mols](https://github.com/mgarort/graph-nps-for-mols) |
| TabPFN | [PriorLabs/TabPFN](https://github.com/PriorLabs/TabPFN) |

Before launching a full comparison, verify one-shot finite predictions, support-order invariance, query-order and chunking behavior, absence of hidden-label leakage, correct ensemble variance, stable predictive densities, and agreement of analytic updates with small direct calculations. Do not assume that adding measurements must reduce a learned predictive variance monotonically. Unexpected observations can legitimately increase uncertainty about a misspecified or ambiguous series.
