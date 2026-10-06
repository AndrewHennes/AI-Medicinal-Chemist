# Auxiliary GP loss-weight search

Balanced fixed-query squared error changes from 0.6846 to 0.6844 relative to the previous weight search. The estimated reduction is 0.03%, with paired 95% interval [-0.44, 0.55]%. Holm-adjusted p = 1.0000 across six primary contrasts.

EI top-1 purchases changes from 5.5118 to 5.4767 relative to the previous weight search. The estimated reduction is 0.64%, with paired 95% interval [-0.15, 1.49]%. Holm-adjusted p = 0.5924 across six primary contrasts.

PPO top-1 purchases changes from 5.6109 to 5.6664 relative to the previous weight search. The estimated reduction is -0.99%, with paired 95% interval [-2.28, 0.22]%. Holm-adjusted p = 0.5924 across six primary contrasts.

Prediction and EI results average three GP training seeds. PPO holds the GP at seed11 and repeats three policy seeds; its optimizer settings are inherited from the previous auxiliary-GP PPO. Intervals resample linked series groups and are conditional on fitted models.

## Purchases, pools ≥15

top_k              1       2       3       4
method
original_ei   5.5168  3.5747  2.8440  2.3734
original_ppo  5.7144  3.8527  3.0792  2.5425
previous_ei   5.5118  3.6050  2.8553  2.3750
previous_ppo  5.6109  3.8079  3.0398  2.5014
tuned_ei      5.4767  3.5799  2.8576  2.3747
tuned_ppo     5.6664  3.8425  3.0635  2.5115

## Pair prediction, pools ≥15

endpoint  minimum_pool_size   method  pools       r2     rmse  spearman
     all                 15 original    580 0.063318 0.940810  0.314943
     all                 15 previous    580 0.086469 0.929111  0.322994
     all                 15    tuned    580 0.086547 0.929071  0.323686
