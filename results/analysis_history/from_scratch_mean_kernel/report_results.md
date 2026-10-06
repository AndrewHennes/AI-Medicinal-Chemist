# Prediction architectures trained from scratch

Every task-specific predictor was newly initialized. No fitted predictor tensors were transferred. MiniMol embeddings, training-only PCA, fold assignments and previously selected architecture configurations were retained. All main rows use three independently trained members.

Primary table: five linked-group folds, six equally weighted endpoints, pools with at least 15 compounds, ten measured molecules including the initial hit, and fixed hidden queries. Negative log-likelihood is validation-calibrated and lower is better.

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5806 | 0.4107 | 0.6139 |
| Original neural architecture | 0.5644 | 0.3964 | 0.5832 |
| Average mean only | 0.5709 | 0.3996 | 0.5939 |
| Average-reference kernel only | 0.5810 | 0.4045 | 0.5809 |
| Average mean + average-reference kernel | 0.5810 | 0.4075 | 0.5831 |
| Kernel-softmax weighted mean + average kernel | 0.5809 | 0.4045 | 0.5837 |

## Findings

Validation selected the initial task-specific state in 120 of 720 fits, including 33 of 90 GP fits. Every run still completed at least 4,000 updates.

## Paired changes

Positive values favor the first model. NLL improvement is baseline NLL minus model NLL. Paired 95% intervals resample linked groups 5,000 times.

| Model versus baseline | Metric | Improvement | 95% interval |
|---|---|---:|---:|
| Average mean only versus Original neural architecture | r2 | +0.0064 | [-0.0011, +0.0120] |
| Average mean only versus Original neural architecture | rho | +0.0032 | [-0.0082, +0.0143] |
| Average mean only versus Original neural architecture | nll | -0.0107 | [-0.0216, +0.0006] |
| Average-reference kernel only versus Original neural architecture | r2 | +0.0166 | [+0.0093, +0.0212] |
| Average-reference kernel only versus Original neural architecture | rho | +0.0081 | [-0.0023, +0.0172] |
| Average-reference kernel only versus Original neural architecture | nll | +0.0024 | [-0.0054, +0.0108] |
| Average mean + average-reference kernel versus Original neural architecture | r2 | +0.0166 | [+0.0082, +0.0220] |
| Average mean + average-reference kernel versus Original neural architecture | rho | +0.0111 | [-0.0008, +0.0209] |
| Average mean + average-reference kernel versus Original neural architecture | nll | +0.0001 | [-0.0087, +0.0092] |
| Average mean + average-reference kernel versus Average-reference kernel only | r2 | +0.0000 | [-0.0019, +0.0015] |
| Average mean + average-reference kernel versus Average-reference kernel only | rho | +0.0030 | [-0.0034, +0.0086] |
| Average mean + average-reference kernel versus Average-reference kernel only | nll | -0.0022 | [-0.0059, +0.0013] |
| Kernel-softmax weighted mean + average kernel versus Average mean + average-reference kernel | r2 | -0.0001 | [-0.0031, +0.0035] |
| Kernel-softmax weighted mean + average kernel versus Average mean + average-reference kernel | rho | -0.0030 | [-0.0091, +0.0045] |
| Kernel-softmax weighted mean + average kernel versus Average mean + average-reference kernel | nll | -0.0006 | [-0.0056, +0.0055] |
| Average mean + average-reference kernel versus GP: neural mean + conventional kernel | r2 | +0.0004 | [-0.0063, +0.0101] |
| Average mean + average-reference kernel versus GP: neural mean + conventional kernel | rho | -0.0032 | [-0.0249, +0.0168] |
| Average mean + average-reference kernel versus GP: neural mean + conventional kernel | nll | +0.0308 | [-0.0060, +0.0668] |
| Kernel-softmax weighted mean + average kernel versus GP: neural mean + conventional kernel | r2 | +0.0003 | [-0.0072, +0.0112] |
| Kernel-softmax weighted mean + average kernel versus GP: neural mean + conventional kernel | rho | -0.0062 | [-0.0281, +0.0154] |
| Kernel-softmax weighted mean + average kernel versus GP: neural mean + conventional kernel | nll | +0.0301 | [-0.0053, +0.0662] |
| GP: neural mean + conventional kernel versus GP: single seed 11 | r2 | +0.0076 | [+0.0046, +0.0120] |
| GP: neural mean + conventional kernel versus GP: single seed 11 | rho | +0.0109 | [+0.0033, +0.0180] |
| GP: neural mean + conventional kernel versus GP: single seed 11 | nll | +0.0121 | [+0.0082, +0.0170] |

## Baseline and correction

| Model | Baseline R² | Final R² | Gain from correction |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.0698 | 0.5806 | +0.5108 |
| Original neural architecture | 0.0885 | 0.5644 | +0.4759 |
| Average mean only | 0.4847 | 0.5709 | +0.0862 |
| Average-reference kernel only | 0.5059 | 0.5810 | +0.0752 |
| Average mean + average-reference kernel | 0.5059 | 0.5810 | +0.0751 |
| Kernel-softmax weighted mean + average kernel | 0.5445 | 0.5809 | +0.0364 |

## Microsomal clearance

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.6141 | 0.4318 | 0.5094 |
| Original neural architecture | 0.5977 | 0.4161 | 0.5289 |
| Average mean only | 0.5913 | 0.4123 | 0.5223 |
| Average-reference kernel only | 0.6042 | 0.4255 | 0.5204 |
| Average mean + average-reference kernel | 0.6059 | 0.4294 | 0.5209 |
| Kernel-softmax weighted mean + average kernel | 0.6045 | 0.4278 | 0.5227 |

## In vivo clearance

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5485 | 0.3111 | 0.5235 |
| Original neural architecture | 0.5034 | 0.2673 | 0.4994 |
| Average mean only | 0.5201 | 0.2879 | 0.5233 |
| Average-reference kernel only | 0.5309 | 0.2892 | 0.4975 |
| Average mean + average-reference kernel | 0.5322 | 0.2942 | 0.4966 |
| Kernel-softmax weighted mean + average kernel | 0.5456 | 0.2997 | 0.4746 |

## Protein binding

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5447 | 0.4963 | 0.7963 |
| Original neural architecture | 0.5313 | 0.5211 | 0.6479 |
| Average mean only | 0.5533 | 0.5121 | 0.6572 |
| Average-reference kernel only | 0.5574 | 0.5349 | 0.6437 |
| Average mean + average-reference kernel | 0.5587 | 0.5419 | 0.6445 |
| Kernel-softmax weighted mean + average kernel | 0.5581 | 0.5349 | 0.6473 |

## Cellular clearance

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5498 | 0.3842 | 0.5270 |
| Original neural architecture | 0.5414 | 0.3760 | 0.5156 |
| Average mean only | 0.5438 | 0.3712 | 0.5239 |
| Average-reference kernel only | 0.5552 | 0.3721 | 0.5189 |
| Average mean + average-reference kernel | 0.5557 | 0.3732 | 0.5212 |
| Kernel-softmax weighted mean + average kernel | 0.5484 | 0.3567 | 0.5328 |

## Permeability

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.6350 | 0.4414 | 0.6902 |
| Original neural architecture | 0.6236 | 0.4127 | 0.6677 |
| Average mean only | 0.6306 | 0.4282 | 0.6850 |
| Average-reference kernel only | 0.6386 | 0.4215 | 0.6634 |
| Average mean + average-reference kernel | 0.6358 | 0.4194 | 0.6656 |
| Kernel-softmax weighted mean + average kernel | 0.6361 | 0.4176 | 0.6735 |

## Efflux ratio

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: neural mean + conventional kernel | 0.5917 | 0.3997 | 0.6368 |
| Original neural architecture | 0.5893 | 0.3855 | 0.6400 |
| Average mean only | 0.5862 | 0.3861 | 0.6518 |
| Average-reference kernel only | 0.5997 | 0.3840 | 0.6413 |
| Average mean + average-reference kernel | 0.5978 | 0.3869 | 0.6497 |
| Kernel-softmax weighted mean + average kernel | 0.5928 | 0.3905 | 0.6516 |

## Supplementary models

Fixed-temperature results are descriptive; temperature selection used validation only. The GP single-seed row permits comparison with the ensemble-size convention in earlier reports.

| Model | R² | Spearman ρ | NLL |
|---|---:|---:|---:|
| GP: single seed 11 | 0.5730 | 0.3999 | 0.6260 |
| Weighted, temperature 0.1 | 0.5758 | 0.4002 | 0.5920 |
| Weighted, temperature 0.3 | 0.5791 | 0.4020 | 0.5843 |
| Weighted, temperature 1.0 | 0.5805 | 0.4050 | 0.5852 |

## Training and evaluation details

| Architecture | Fits | Median updates | Median selected step | Selected initialization |
|---|---:|---:|---:|---:|
| Original neural architecture | 90 | 4000 | 500 | 13 |
| Average mean only | 90 | 4000 | 500 | 4 |
| Average-reference kernel only | 90 | 4000 | 250 | 17 |
| Average mean + average-reference kernel | 90 | 4000 | 250 | 17 |
| Weighted, temperature 0.1 | 90 | 4000 | 500 | 6 |
| Weighted, temperature 0.3 | 90 | 4000 | 500 | 13 |
| Weighted, temperature 1.0 | 90 | 4000 | 250 | 17 |
| GP: neural mean + conventional kernel | 90 | 4000 | 250 | 33 |

All 720 fits started with fresh task-specific parameters, including the neural pair predictor, context encoder, iterative-correction parameters, uncertainty heads and kernel parameters. Standard architecture defaults such as zero output heads and initial length scales are not fitted weights. Training constructors do not read historical checkpoints; a mock test blocks torch.load during initialization.

MiniMol foundation representations remain fixed input features. PCA was fitted only on training molecules, and the existing five linked-group folds were reused. Existing fold-specific network widths, PCA dimensions, likelihoods and kernel families were retained as architecture choices. There was no new architecture hyperparameter search.

Seven neural conditions comprise the original architecture, average mean only, average-reference kernel only, both changes, and both changes with RBF-softmax weighting at temperatures 0.1, 0.3, and 1.0. Each has 90 fresh fits across five folds, six endpoints and seeds 11, 29, and 47. The GP adds 90 fresh fits, for 720 total.

All models train from step 1 with AdamW at learning rate 0.001, batch size 16, gradient clipping 5, at least 4,000 and at most 16,000 updates. Validation is checked every 250 updates. A plateau scheduler halves learning rate, down to 1e-5. Early stopping requires 2,000 updates without an NLL improvement of at least 1e-4 and learning rate at most 0.000125. The checkpoint with minimum validation NLL is selected, including the diagnostic initialization checkpoint.

Updates ranged from 4000 to 7500. No fit reached the maximum budget. Validation selected initialization for 120 runs after completion of their training budgets. Detailed histories, stop reasons and initial/final parameter hashes are saved.

Neural variants share the same input dimension and episode stream within fold/endpoint/seed. GP uses the same sampling random stream, but its chemically clustered contexts can differ when its inherited input dimension differs. Sampling retains the previous mixture of pool sizes, starting-hit choices and random/chemically clustered contexts. There is no sign-consistency objective. No training updates use validation or test outcomes.

GP uses its existing neural-pair-mean/conventional-kernel architecture and the previously selected auxiliary-loss weight, with no mean warm-up or fitted initialization. It trains jointly from scratch. Off-policy pairs are sampled by choosing a series in proportion to its molecule count, then choosing an ordered pair uniformly. This retains the requested total pair exposure proportional to molecule count.

All primary rows use three-member predictive mixtures, including the GP. A seed 11 GP is reported separately. Earlier tables used a single GP, so historical GP values should be compared to the supplementary single-seed row rather than interpreted as an ensemble-independent architecture effect.

For weighting, one temperature per endpoint/fold is chosen by raw ensemble validation NLL. Selection counts are {'weighted_t100': 13, 'weighted_t010': 10, 'weighted_t030': 7}. The weighted selection excludes uniform weighting to measure the effect directly. Predictive scale calibration is fitted on validation only for each ensemble and for the supplementary single GP.

The original neural architecture uses a first-hit pair baseline and anchored covariance. Mean-only averages aligned pair predictions and uses leave-one-out measured baselines. Kernel-only consistently centers means, measurements, covariance and noise around the measured-set mean. The combined arm also averages pair means. Kernel-reference changes therefore include required coordinate and noise transformations, not only a matrix replacement.

Kernel-softmax weighting is exactly the recent simple RBF-softmax implementation. It shares the learned diagonal distance scale and bandwidth with the residual branch. We retain the existing covariance architecture and uncertainty heads; we do not add a covariance-aware adjustment of the attention weights or a sign-consistency penalty.

Evaluation covers 4625 pools in 2011 linked groups. The primary >=15 panel contains 580 pools in 334 linked groups. The same query molecules stay hidden as context grows through 1, 2, 3, 5, and 10 total measurements. Smaller-pool curves have changing eligibility at larger context counts.

R² uses pooled target moments with equal pool weight inside each endpoint, then equal endpoint averages. Spearman is computed within each fixed query set. NLL is the exact Gaussian/Student predictive mixture in transformed endpoint units. Raw and calibrated NLL, 50/80/95% coverage and uncorrected-baseline metrics are supplied. Point metrics are computed from the same uncalibrated mean in both calibration conditions to avoid float32 tie perturbations.

Historical fine-tuning results are supplied separately. The main from-scratch comparisons share the new protocol.

Paired intervals use 5,000 linked-group bootstrap draws conditional on fitted models.
