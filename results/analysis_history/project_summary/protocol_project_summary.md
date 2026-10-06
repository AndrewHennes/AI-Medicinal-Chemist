PROJECT SYNTHESIS • 26 SEPTEMBER 2026

# Learning which molecule
to purchase next

A retrospective study of sequential acquisition within analog series, using MiniMol representations and six pharmacokinetic assay endpoints. This report consolidates the completed experiments and the conclusions supported by them.

| Coverage | Current evaluation | Main comparison |
| --- | --- | --- |
| 4,625 curated acquisition pools 580 pools with ≥15 compounds | Five grouped outer folds Four matched initial-hit draws per pool | Random, delta greedy, GP + EI, old NAP and new NAP |

What the evidence supports

**Useful acquisition signal.** Across endpoints, New NAP reduces the mean purchases to top-1 from 10.42 for random to 7.20 in pools with at least 15 compounds, using equal endpoint weighting. This is a descriptive reduction of 30.9%.

**Endpoint-specific winners.** Among the five main methods, New NAP has the lowest top-1 mean for large microsomal, protein-binding and cellular-clearance pools. Gaussian process plus expected improvement (GP + EI) leads for permeability and efflux. Old NAP has the lowest in vivo-clearance mean, supported by only 20 large pools.

How to read this report

Pages 2–5 describe the problem, data, models and evaluation. Pages 6–8 give the current six-endpoint benchmark. Pages 9–14 explain the predictor, multitask, augmentation, value-learning and interpretation experiments. Pages 15–16 state the conclusions, priorities and source records.

All numerical results are retrospective internal cross-validation or earlier development analyses. Source labels [S1]–[S15] resolve to saved project reports on the final page. No models were retrained to produce this summary.

01 • SCIENTIFIC QUESTION

# Background and objective

The practical question is how to spend a limited number of purchases or assays within a known analog series. The candidate structures and their MiniMol feature vectors are available from the start, but only the initial hit has a revealed assay value. Each purchase reveals the stored value of one additional compound. The policy then updates its ranking of the remaining candidates.

Complete historical assay labels provide a lookup simulator. Training can generate new acquisition sequences without collecting laboratory measurements. Reusing one historical series for many episodes increases the number of training contexts, but does not create additional independent chemical series.

How the objective evolved

The original handoff discussed obtaining the best observed value after a fixed purchase budget. The project moved to finding a recorded optimum as quickly as possible, so that short series could remain useful. The current evaluation relaxes exact-optimum discovery by measuring purchases to **any top-1, top-2, top-3 or top-4 compound**. This is distinct from requiring all of the best four compounds or measuring success after a four-purchase budget. [S1, S2]

| Stage | Information available to the policy |
| --- | --- |
| Start | All candidate embeddings and one measured hit sampled from the worst half of the pool. |
| Choose | An acquisition rule scores the unmeasured candidates and selects one. |
| Reveal | Its assay outcome is revealed relative to the original hit. The measured context is updated. |
| Score afterward | The complete purchase order is evaluated against the stored pool labels. The policy is not told when the true optimum has been found. |

Reference-relative outcomes

After applying the endpoint transformation and orienting the objective so lower is better, every observed outcome is expressed relative to the initial hit.

$$
z_i = y_i-y_{\mathrm{reference}},\qquad y_i=\log_{10}(c_i)\ \mathrm{for\ clearance}
$$

For clearance, a relative value of −1 corresponds to tenfold lower clearance before training-scale normalization. Log subtraction cancels a common multiplicative series offset.

The simulator uses fixed recorded values, equal purchase costs, and sampling without replacement to evaluate acquisition orderings.

02 • WHAT WAS BENCHMARKED

# Data and assay scope

A pool is one retained analog series within an endpoint and species/assay context. It contains at least three distinct molecules and nonconstant transformed outcomes. Each molecule has a 512-dimensional MiniMol representation. The same chemical series can contribute several species pools. [S3, S4]

| Endpoint | Transformed objective to minimize | Pools ≥3 | Pools ≥15 | Groups ≥15 |
| --- | --- | --- | --- | --- |
| Microsomal clearance | log₁₀(clearance) | 1,827 | 311 | 183 |
| In vivo clearance | log₁₀(clearance) | 537 | 20 | 16 |
| Protein binding | log₁₀((1 − fᵤ)/fᵤ) | 880 | 44 | 29 |
| Cellular clearance | log₁₀(clearance) | 524 | 79 | 53 |
| A→B permeability | −log₁₀(permeability) | 516 | 72 | 62 |
| Efflux ratio | log₁₀(B→A / A→B) | 341 | 54 | 49 |

Clearance and binding use human, rat and mouse data. Permeability and efflux use human and dog-derived assay pools. Species and assay systems remain separate pools. The protein-binding transform is an apparent bound/free ratio, not a molar binding constant; minimizing it favors higher unbound fraction for this benchmark. The efflux direction follows curated row annotations despite the original filename.

![](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/size_distribution.png)

Curation selects the largest assay-compatible source group within a series/species pair and aggregates replicates by median on the transformed scale. Invalid log inputs and binding values outside the open 0–100% range are excluded. Explicit nonintravenous clearance records are excluded. [S3]

Overlap offers an opportunity, with uncertain series identity

Exact shared standardized molecules link 3,644 endpoint-local series into 2,245 inferred groups. Of these, 676 cover at least two assays, 237 cover at least three, and two cover all six. [S15]

03 • WHAT EACH METHOD LEARNS

# Models and acquisition rules

| Method | Prediction and selection |
| --- | --- |
| Random | Uniform purchase order. Evaluation uses the exact expected purchase count, including ties. |
| Delta greedy | A supervised ordered-pair predictor estimates query-minus-anchor differences. The next purchase has the lowest mean estimate across measured anchors. |
| GP + EI | A Gaussian process (GP) learns a reference-relative Matérn-5/2 prior from historical acquisition-training pools. It conditions on the current measured outcomes and maximizes expected improvement (EI). |
| Old NAP | The original compact Neural Acquisition Process (NAP) adaptation uses a transformer to predict a 101-bin conditional outcome distribution. Its acquisition head uses this distribution, candidate features and state summaries. Delta mean and spread are added to the input. |
| New NAP | The revised policy uses frozen, group-cross-fitted GP and neural forecasters. A small context-dependent controller mixes five candidate ranks, followed by policy optimization. It is a GP-conditioned hybrid, not a pure neural surrogate. |

The delta model and its dynamic features

Two ordered MiniMol vectors are concatenated into 1,024 inputs. A 256/128/64-unit multilayer perceptron predicts the transformed difference using squared-error training on within-pool pairs. The predictor is frozen before acquisition learning. No sign-consistency or antisymmetry constraint is imposed. [S5]

$$
\widehat{z}^{(j)}_q=z_j+\widehat{\Delta}(q,j),\qquad \mu_q=\operatorname{mean}_{j\in O}\widehat{z}^{(j)}_q,\quad s_q=\operatorname{SD}_{j\in O}\widehat{z}^{(j)}_q
$$

Only the measured set O contributes. Anchor disagreement is summarized by the sample standard deviation, defined as zero for one anchor.

Policy optimization

Both NAP versions use clipped **Proximal Policy Optimization (PPO)** with a learned critic and undiscounted returns based on remaining purchases to top-1. Old NAP retains a prediction loss during PPO. New NAP freezes its forecasters and updates its acquisition controller and critic after a supervised warm start. The critic is a training baseline; evaluation selects from the policy head. [S6]

Delta greedy uses the delta-training role; GP + EI uses the acquisition-training role; augmented NAP combines its training role with the frozen delta predictor. [S3]

The implementation is inspired by Maraval et al., *End-to-End Meta-Bayesian Optimisation with Transformer Neural Processes* ([paper](https://arxiv.org/abs/2305.15930)). It is a project-specific adaptation. PPO follows Schulman et al. ([paper](https://arxiv.org/abs/1707.06347)).

04 • WHAT THE RESULTS ESTIMATE

# Validation and purchase-count metrics

The primary evidence now uses five grouped outer folds. Every curated pool appears in an outer test fold exactly once. Molecules, related source documents and linked species/endpoint pools remain together where models share data. Microsomal clearance was added with separate grouped folds for its independent single-task models. [S2, S4]

| Partition | Target share within outer non-test data | Approximate share of full data¹ |
| --- | --- | --- |
| Delta training | 45% | 36% |
| Delta validation | 5% | 4% |
| Acquisition training | 45% | 36% |
| Acquisition validation | 5% | 4% |
| Outer test | Held out | 20% |

¹ Fractions are design targets with source groups assigned intact. Each outer fold fits its own preprocessing, predictors, and policies. Revised forecasters use three inner teacher folds with held-group loss exclusion and common outer-training scales.

Each test pool has four matched worst-half starting draws. Neural policies average three seeds, 11, 29 and 47; delta and GP baselines use one fit per fold. Starts and seeds are averaged within pool, pools within endpoint, and overall means give endpoints equal weight. Starts and seeds are not independent chemical samples.

Current evaluation

**Top-k purchases** count additional purchases until any compound tied at or better than the kth-best recorded value is observed. The initial hit is free. An already qualifying hit gives zero. All current performance charts use only top-1 through top-4 purchase counts. Policies remain primarily trained for top-1; reporting top-2 through top-4 does not retrain them.

$$
\mathbb{E}[T_{\mathrm{random}}]=\frac{n}{g+1}\quad\mathrm{if\ the\ initial\ hit\ does\ not\ qualify}
$$

Here n includes the free hit and g is the number of acceptable unmeasured compounds, including boundary ties. With one unique optimum, random takes n/2 purchases, including the purchase revealing the optimum. Top-4 is automatically zero for pools of three or four. Small pools contain ranking signal, but larger top-k targets can be trivial.

Paired intervals resample source groups conditional on fitted models and are generally unadjusted for multiple comparisons. The grouped folds form the exploratory development benchmark.

05 • FIVE-FOLD RESULTS, AT LEAST 15 COMPOUNDS

# Main results in larger analog pools

Entries are mean additional purchases to any top-1 compound. Lower is better. Bold values identify the lowest unrounded mean among these five methods, not a statistically established winner. These are the current matched worst-half test starts used in the later experiments. [S7]

| Endpoint | Random | Delta greedy | GP + EI | Old NAP | New NAP |
| --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 8.62 | 5.70 | 5.84 | 6.11 | **5.40** |
| In vivo clearance | 10.65 | 9.76 | 9.38 | **8.84** | 9.60 |
| Protein binding | 12.20 | 6.91 | 7.72 | 7.44 | **6.72** |
| Cellular clearance | 9.45 | 6.83 | 7.00 | 7.30 | **6.50** |
| A→B permeability | 11.92 | 9.80 | **7.47** | 9.12 | 8.13 |
| Efflux ratio | 9.69 | 7.12 | **6.39** | 8.52 | 6.86 |

![New NAP versus delta greedy on identical test pools and starts. Error bars are paired 95% source-group bootstrap intervals conditional on saved models. Positive values favor New NAP. [S14]](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/paired_new_vs_greedy.png)

New NAP versus delta greedy on identical test pools and starts. Error bars are paired 95% source-group bootstrap intervals conditional on saved models. Positive values favor New NAP. [S14]

06 • WHY ONE AGGREGATE IS INSUFFICIENT

# Small series and pool-size sensitivity

All pools with at least three molecules remain in training and evaluation. The table gives top-1 purchase counts across all eligible sizes. New NAP leads on three endpoints, Old NAP on in vivo clearance, and delta greedy on protein binding and efflux. [S7]

| Endpoint | Random | Delta greedy | GP + EI | Old NAP | New NAP |
| --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 3.53 | 2.72 | 2.70 | 2.75 | **2.60** |
| In vivo clearance | 2.75 | 2.61 | 2.63 | **2.54** | 2.59 |
| Protein binding | 2.98 | **2.20** | 2.43 | 2.29 | 2.26 |
| Cellular clearance | 3.58 | 2.90 | 2.95 | 3.03 | **2.78** |
| A→B permeability | 4.27 | 3.49 | 3.35 | 3.56 | **3.33** |
| Efflux ratio | 4.13 | **3.15** | 3.27 | 3.56 | 3.15 |

![Each minimum-size cutoff uses its eligible pools. Counts at the four labeled ticks are shown in each panel.](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/cutoff_curves.png)

Each minimum-size cutoff uses its eligible pools. Counts at the four labeled ticks are shown in each panel.

07 • CURRENT RANK-TOLERANT EVALUATION

# Relaxing the target to any top-k compound

These curves use the same full purchase orders and the same pools with at least 15 compounds. Top-2 means reaching either of the two best compounds, top-3 any of the three best, and top-4 any of the four best. Rank-boundary ties also qualify. [S7]

![Mean additional purchases as the acceptable target set expands. Lower is better. The policies were primarily optimized for exact top-1 acquisition; these are evaluations of the same policies under broader success definitions.](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/topk_large.png)

Mean additional purchases as the acceptable target set expands. Lower is better. The policies were primarily optimized for exact top-1 acquisition; these are evaluations of the same policies under broader success definitions.

Method rankings can depend on the target. For large protein-binding pools, New NAP has the lowest top-1 mean among the five methods, while delta greedy is better on top-3 and top-4. For permeability, GP + EI has the lowest top-1 mean, while New NAP is better on top-2 through top-4.

Top-k targets count acquisition of any compound within the specified rank boundary.

08 • EARLY MICROSOMAL DIAGNOSTICS

# What the relative predictor learned

The historical independent predictor-test subset contains 77 pools. [S5]

| Statistic | Value | Aggregation |
| --- | --- | --- |
| R² | 0.199 | All ordered pairs pooled together |
| Spearman rank correlation | 0.448 | All ordered pairs pooled together |
| Pearson correlation | 0.454 | All ordered pairs pooled together |
| R² | 0.115 | Each pool given equal total weight |
| Mean fixed-anchor Spearman correlation | 0.343 | Rank candidates against one anchor, then average anchors and pools |
| Mean absolute error | 0.446 log₁₀ units | Losses averaged within pool, then across pools |
| Root mean squared error | 0.571 log₁₀ units | Equal-pool weighting; zero predictor 0.607 |

Why NAP prediction could look better

NAP uses a conditional-distribution objective and measured-set transformer. Augmented NAP includes the frozen delta model, and supervised updates continue during PPO. [S5]

09 • ARCHITECTURAL RECOVERY WITHOUT PROVEN POSITIVE TRANSFER

# Multitask learning and the revised NAP

Recovery experiments evaluate context connections, private heads, selective sharing, gradient projection, policy adaptation, alternative distributions, sampling, and GP-conditioned policies. Group-cross-fitted teachers generate training forecasts. [S8, S9]

The revised design

New NAP freezes GP and neural forecasters, warm-starts its controller, and applies PPO. The controller mixes GP EI, GP mean, delta mean, neural EI, and an uncertainty/correlation score.

| Five-endpoint architecture | Single-task top-1 | Multitask top-1 |
| --- | --- | --- |
| Original NAP | 8.24 | 10.00 |
| Revised NAP | 7.61 | 7.97 |
| GP + EI | 7.58 | 8.07 |
| Delta greedy | 8.06 | 8.12 |

Five-fold, equal-endpoint mean purchases for pools ≥15 on the original five-endpoint test-start bank. Microsomal clearance is excluded from these multitask fits. [S2]

10 • TESTING THE TRAINING DISTRIBUTION

# Starting-hit distribution and multi-hit contexts

The initial hit was varied from the worst 50% to the worst 10%, 20%, 30% and 40% of each pool. Eligible-set size was the larger of one and the floored fraction of pool size. Each new training condition was compared with the original 50%-trained model on exactly the same test starts. This separates retraining from merely changing the starting problem. [S10]

![Equal-endpoint top-1 means for pools ≥15. Solid lines retrain at the displayed starting fraction; dashed lines keep the 50%-trained model fixed. Comparing different x values also changes the task distribution.](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/initial_hit_sensitivity.png)

Equal-endpoint top-1 means for pools ≥15. Solid lines retrain at the displayed starting fraction; dashed lines keep the 50%-trained model fixed. Comparing different x values also changes the task distribution.

Multi-hit starting sets as data augmentation

Half of eligible training draws retained one free hit. The other half started with two to five molecules sampled entirely from the worst half, including the reference hit. This is data augmentation of measured contexts from existing series. It does not create new independent chemistry or provide extra free measurements at evaluation. Validation and testing still began with one hit. [S11]

| Model, pools ≥15 | Original | Multi-hit | Change with 95% interval |
| --- | --- | --- | --- |
| Old NAP | 7.89 | 8.06 | +0.17 [−0.33, +0.58] |
| New NAP | 7.20 | 7.29 | +0.09 [−0.06, +0.28] |

Equal-endpoint means at fixed supervised-step and episode budgets. Positive changes indicate more purchases.

11 • TWO LATER MATCHED EXPERIMENTS

# Top-removal and auxiliary acquisition losses

Cumulatively remove the best one through five compounds

Half of eligible training draws used an intact pool. The remainder removed a uniformly sampled feasible count of its top one to five molecules, leaving at least three. The next-best remaining compound became the target, subject to ties. The remaining pool supplied a fresh worst-half hit. This tested resistance to repeatedly targeting the same best molecule. Validation and test pools stayed intact. [S12]

Predict the cost of reaching any top-2 through top-6 compound

Five auxiliary heads shared the actor representation and predicted normalized continuation purchase costs for the sampled action. Their squared-error loss was added with fixed weight 1.0. The primary policy still optimized and selected for top-1. These heads predict costs under the current policy, not separately optimized top-k action values. No top-removal or multi-hit augmentation was combined with this study. [S7]

![Paired top-1 changes in pools ≥15 with 95% source-group bootstrap intervals. Negative values favor the added training condition. Models and starts are matched; intervals are unadjusted.](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/augmentation_effects.png)

Paired top-1 changes in pools ≥15 with 95% source-group bootstrap intervals. Negative values favor the added training condition. Models and starts are matched; intervals are unadjusted.

12 • COMPLETED ACROSS ALL SIX ENDPOINTS

# Value learning and explicit search

Value learning estimates expected future acquisition cost and selects the action with the lowest learned cost. The implemented models use Double-Q cost updates, with an online network choosing the next action and a target network evaluating it. This is different from using the PPO critic only as a training baseline. [S6, S13]

| Value method | Representation or planning rule |
| --- | --- |
| Compact | Candidate GP/delta prediction summaries, measured outcomes and pooled set context. |
| Set pooling | Learned MiniMol projections with mean/max pooling over observed and available molecules. |
| Attention | Learned MiniMol projections with two attention layers over the pool. |
| Selected recipe | Architecture and refinements selected within each outer fold using validation only. |
| Lookahead / tree search | Selected model plus GP-sampled hypothetical outcomes. Search is shallow and limited to the first eight real purchases. |

Top-1 purchase counts in pools ≥15 use the same held-out pools and starts. New NAP is the comparator. Value-model development includes size-balanced sampling, random-return regularization, and auxiliary rank targets; budgets are recorded by method.

| Endpoint | New NAP | Compact | Set pool | Attention | Selected | Look ahead | Tree |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Microsomal clearance | 5.40 | **5.35** | 6.62 | 6.16 | 5.67 | 5.70 | 5.65 |
| In vivo clearance | 9.60 | **8.79** | 11.02 | 10.87 | 11.07 | 10.62 | 9.37 |
| Protein binding | **6.72** | 7.40 | 8.89 | 8.80 | 8.95 | 8.33 | 8.76 |
| Cellular clearance | **6.50** | 6.91 | 8.01 | 8.78 | 7.17 | 7.41 | 7.11 |
| A→B permeability | **8.13** | 8.61 | 9.49 | 9.69 | 9.49 | 9.49 | 8.85 |
| Efflux ratio | **6.86** | 7.15 | 9.56 | 9.11 | 7.00 | 7.15 | 6.94 |

13 • INTERPRETING THE LEARNED ACQUISITION RULE

# When New NAP departs from greedy

The decision audit replays the unaugmented New NAP and evaluates delta greedy on the identical measured context. All tied delta minima count as agreement. All 148,476 pre-optimum actions matched saved trajectories. Summary rates weight pools equally and exclude forced final-candidate decisions. [S14]

$$
s(a\mid S)=T(S)\sum_{j=1}^{5} w_j(S)r_j(a\mid S)
$$

The five ranks represent GP EI, GP mean, delta mean, neural EI and an information heuristic equal to GP uncertainty times average absolute posterior correlation with unmeasured candidates. State-dependent weights sum to one. The positive temperature does not change the deterministic best-scoring action. There is no explicit tree search.

![Disagreement with delta greedy in pools ≥15.](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/project_summary/figures/decision_disagreement.png)

Disagreement with delta greedy in pools ≥15.

**Predictor disagreement dominates.** Among departures from delta greedy, GP mean prefers the NAP choice over the delta choice in 89.8–93.5% of cases across endpoints. GP EI is the largest positive rank contribution in 73.1–94.3% of disagreements.

14 • WHAT TO CARRY FORWARD

# Conclusions and priorities

Conclusions supported by the completed analyses

**Historical analog pools contain useful acquisition signal.** Even a simple relative predictor can rank candidates well enough to outperform random acquisition. Small pools are useful training examples and valid evaluation cases when the target is not structurally trivial.

Recommended next experiments, not completed findings

**Align the target with measurement reliability.** Use replicates or assay-specific uncertainty to define a near-optimal set, or train a policy conditioned on the desired top-k target. These objectives could reduce dependence on a noisy winner without reverting to average regret over the trajectory.

15 • GUIDE TO THE PROJECT RECORD

# Sources and reproducibility

This synthesis uses saved reports, paired comparisons and pool-level results. The accompanying source_manifest.json records absolute source paths and SHA-256 hashes. benchmark_summary.csv and cutoff_curves.csv contain the values used to regenerate the main charts. The project_summary.md companion preserves the narrative in editable form.

| Source | Saved analysis record |
| --- | --- |
| S1 | [Original handoff and objective evolution](/Users/asselism/Downloads/acquisition_optimization_codex_handoff.pdf) |
| S2 | [Five-fold methods, multitask and delta + EI results](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/reports/report.md) |
| S3 | [Endpoint definitions and curation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/multi_endpoint_acquisition/report.md) |
| S4 | [Microsomal extension and independent grouped folds](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/microsomal_stability/reports/report.md) |
| S5 | [Delta model and matched prediction diagnostics](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/delta_acquisition_experiment/results/report.md) |
| S6 | [Policy optimization and value-learning distinction](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/policy_optimization.md) |
| S7 | [Current matched controls and top-k auxiliary study](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_topk_auxiliary/reports/results.md) |
| S8 | [Initial multitask study and recovery diagnostics](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_recovery/report.md) |
| S9 | [Cross-fitted NAP design and warm-start controls](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/nap_multitask_crossfit/report.md) |
| S10 | [Starting-hit sensitivity](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/initial_hit_sensitivity/reports/report.md) |
| S11 | [Multi-hit training augmentation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/acquisition_fivefold/lower_half_multihit_augmentation/reports/report.md) |
| S12 | [Cumulative top-removal augmentation](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/top_removal_augmentation/reports/results.md) |
| S13 | [All value methods across six datasets](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/value_all_methods/reports/results.md) |
| S14 | [New NAP versus greedy decision audit](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/new_nap_greedy_diagnostics/reports/findings.md) |
| S15 | [Cross-assay overlap definitions and counts](/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/assay_overlap/README.md) |

The source manifest also includes predictor-correlation JSON files, all three training-augmentation paired tables, current per-pool outcomes, the value-method comparison and the decision-effect table. Full experiment PDFs and interactive viewers remain in their respective source directories. These materials distinguish historical single-split findings from later cross-validation.

Earlier branches retained for context

A delta-plus-EI baseline using training-anchor disagreement was also tested. [S2]

Changes to initial-hit case banks explain small numeric differences between some earlier PDFs and the matched current controls. The current headline values come from the unaugmented 50% control bank reused by the value, top-removal, auxiliary and decision-audit experiments. Historical multitask values remain explicitly labeled with their original five-endpoint bank.
