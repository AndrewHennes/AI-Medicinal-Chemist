# NAP set-context acquisition benchmark

| Method | Top 1 | Top 2 | Top 3 | Top 4 |
| --- | ---: | ---: | ---: | ---: |
| NAP: GP mean + SD | 5.695 | 3.838 | 3.080 | 2.539 |
| + incumbent | 5.654 | 3.784 | 3.036 | 2.497 |
| + delta summaries | 5.673 | 3.769 | 2.991 | 2.475 |
| + incumbent + delta | 5.692 | 3.809 | 3.032 | 2.494 |
| + molecular features | 6.169 | 4.327 | 3.400 | 2.834 |
| + Deep Sets | 6.299 | 4.384 | 3.444 | 2.904 |
| + cross-attention | 6.210 | 4.277 | 3.400 | 2.854 |
| + Set Transformer | 6.173 | 4.259 | 3.374 | 2.800 |
| GP + Set Transformer (no delta) | 6.038 | 4.201 | 3.260 | 2.751 |
| + state statistics | 5.729 | 3.785 | 3.019 | 2.493 |
| + molecules + state statistics | 6.299 | 4.366 | 3.435 | 2.908 |
| + compact Set Transformer | 5.877 | 3.961 | 3.204 | 2.644 |
| Neural-mean GP + EI | 5.570 | 3.659 | 2.911 | 2.423 |
| Neural-mean GP greedy | 5.817 | 3.966 | 3.177 | 2.606 |
| Delta greedy | 6.722 | 4.451 | 3.494 | 2.788 |
| Random expectation | 9.588 | 6.598 | 5.174 | 4.278 |

Lower is better. Five grouped folds; four starts per test pool; three policy seeds; fixed neural-mean GP seed 11.
Predictor and acquisition training series are disjoint. Outcomes are relative to the starting hit. This is an exploratory benchmark comparison.

See paired_comparisons.csv for linked-group bootstrap intervals and primary multiplicity correction.
