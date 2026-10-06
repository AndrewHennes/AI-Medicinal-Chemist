# Multi-hit training augmentation

Training augmentation is tested for both original and revised single-task neural acquisition processes (NAPs), across all six endpoints and the same five grouped outer folds. Each policy uses the same three seeds as its original comparison. Every test starts with one hit sampled from the worst half; test starts are identical across all seven curves.

Half of eligible training draws retain the existing recipe. The other half use a random initial measured set of two, three, four or five compounds drawn without replacement entirely from the worst half. Set size is uniform among the sizes feasible for that pool. The original reference hit is included and all outcomes remain relative to it. Pools with fewer than four compounds cannot supply an augmented set.

The added contexts are used for supervised prediction, controller warm starts and reinforcement-learning rollouts. The neural forecasters used by the revised NAP are also retrained on these contexts, with unchanged cross-fitting. Random, delta greedy and GP + EI are unchanged: their fitting objectives do not depend on this measured-set augmentation.

Supervised-step and sampled-episode budgets are unchanged. Augmented training episodes begin with multiple free observations, so some trajectories and PPO update sequences are shorter. This tests a change in the training distribution at a fixed episode budget; it is not an increase in training time or evidence that the additional measurements improve a multi-hit test scenario.

Validation stays single-hit and uses the original selection rules. Test cases have one free initial compound, and all subsequent selections count as purchases. Target-rank boundary ties qualify. If the hit already qualifies, the count is zero. Top-4 is zero for pools with three or four compounds. Complete acquisition trajectories use no oracle stopping signal.

Plots show the four purchase-count metrics versus minimum pool size. Starts and seeds are averaged within each pool, then pools within endpoint; the overall page gives equal weight to each endpoint. Lower counts are better. The accompanying paired differences compare augmented versus original training on identical test cases.

Paired 95% bootstrap intervals resample source groups with trained checkpoints held fixed. All checkpoints are locked before test scoring.

Overall pools with at least 15 compounds

endpoint,minimum_pool_size,model,metric,baseline_purchases,augmented_purchases,augmented_minus_baseline,bootstrap_low,bootstrap_high,pools,groups,bootstrap_draws
overall,15,single_task_NAP,top1_purchases,7.888540218867097,8.05531436364343,0.1667741447763331,-0.3263344222837871,0.5812360064915474,580,334,2000
overall,15,single_task_NAP,top2_purchases,5.448413667147246,5.34606664200392,-0.10234702514332505,-0.4349508475659024,0.29607701990035773,580,334,2000
overall,15,single_task_NAP,top3_purchases,4.243347506199547,4.2397642556514565,-0.0035832505480910917,-0.3716724822407028,0.3511413719176927,580,334,2000
overall,15,single_task_NAP,top4_purchases,3.4227200416759955,3.446564015830829,0.023843974154833355,-0.2379254996601968,0.3045426654886307,580,334,2000
overall,15,Cross-fitted single-task NAP,top1_purchases,7.200127713661566,7.292033593352541,0.09190587969097531,-0.05829702823209783,0.28215904727152696,580,334,2000
overall,15,Cross-fitted single-task NAP,top2_purchases,4.339301601653281,4.325745517232616,-0.013556084420664777,-0.13181692724395164,0.12686850127977492,580,334,2000
overall,15,Cross-fitted single-task NAP,top3_purchases,3.3319343903124814,3.349586418203742,0.017652027891260604,-0.0666282135190897,0.10877711586835015,580,334,2000
overall,15,Cross-fitted single-task NAP,top4_purchases,2.716178138663876,2.753885133936525,0.03770699527264939,-0.025564914447173258,0.1129170470973883,580,334,2000
