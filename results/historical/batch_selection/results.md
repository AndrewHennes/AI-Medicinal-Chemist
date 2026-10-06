# Batch subset selection

At K=2, the lowest learned-method point estimate is Deep Sets + search at 3.189 batches to the best compound, compared with 3.091 for joint batch EI. The estimated reduction is -3.16%, with paired 95% interval [-7.09, 0.71]% and Holm-adjusted p=0.4038.

At K=5, the lowest learned-method point estimate is Deep Sets + search at 1.673 batches to the best compound, compared with 1.659 for joint batch EI. The estimated reduction is -0.81%, with paired 95% interval [-3.62, 1.82]% and Holm-adjusted p=1.0000.

At K=8, the lowest learned-method point estimate is Deep Sets + search at 1.320 batches to the best compound, compared with 1.328 for joint batch EI. The estimated reduction is 0.55%, with paired 95% interval [-1.63, 2.85]% and Holm-adjusted p=1.0000.

The primary population contains 580 held-out pools with at least 15 molecules. All methods use the same frozen auxiliary neural-mean GP and the same four starting hits. Increasing K reduces experimental rounds but usually spends more compounds. Compare methods at the same K and inspect both costs. Inference conditions on fitted models and development folds.

K                     1       2       3       4       5       7       8       10
method                                                                          
batch_ppo         6.1112  3.3749  2.4690  2.0155  1.7703  1.4675  1.3786  1.2532
deep_sets         5.7652  3.1886  2.3213  1.9253  1.6726  1.3987  1.3203  1.2195
ei_topk           5.5246  3.0552  2.2672  1.8733  1.6556  1.3754  1.3091  1.2203
fantasy_ei        5.5237  3.0172  2.2573  1.8659  1.6496  1.3905  1.3155  1.2194
gumbel            6.0463  3.3364  2.4339  2.0000  1.7428  1.4556  1.3687  1.2481
nap_topk          5.6111  3.1507  2.3000  1.9019  1.6698  1.3997  1.3224  1.2187
pair_transformer  5.8208  3.2345  2.3700  1.9595  1.7148  1.4328  1.3519  1.2412
qei               5.5246  3.0909  2.2705  1.8960  1.6591  1.4007  1.3276  1.2287
random            9.5882  5.0567  3.5529  2.8055  2.3590  1.8557  1.7001  1.4945
