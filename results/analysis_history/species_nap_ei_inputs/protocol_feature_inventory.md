# Feature inventory for the corrected New NAP

Only the Gaussian-process expected-improvement branch is replaced. The table records how the previous information remains available.

| Information | Corrected path |
| --- | --- |
| MiniMol representation | The original 512 coordinates enter the species-specific neural forecaster. |
| Measured relative outcomes | The neural forecaster attends to currently measured values; the incumbent and progress enter the controller context. |
| Delta mean | Retains its original candidate rank expert and its disagreement statistic with the GP mean. |
| Delta standard deviation | Retains its neural-forecaster input and controller-context summary. |
| GP mean | Retains its original rank expert; also enters the learned replacement branch. |
| GP standard deviation | Retains uncertainty summaries and the GP information expert; also enters the replacement branch. |
| Best measured relative value | Retains its original context feature and enters the replacement branch. |
| GP expected improvement | Removed, including its precomputed rank. The replacement branch learns a bounded score from the preceding three values. |
| Neural predictive distribution | Retained, with species-specific prediction residuals around a shared forecast. |
| Neural expected improvement | Retains its original candidate rank expert. |
| Neural standard deviation | Retains its controller-context summary. |
| GP information | Retains its original uncertainty-weighted candidate rank expert. |
| Pool size and acquisition progress | Retain their original controller-context inputs. |
| Agreement with delta | Retained, comparing delta's ordering with the learned replacement branch instead of the removed GP-EI ordering. |
| Species | Routes residual prediction, acquisition and value heads; the original context slot is retained. |

The GP-EI branch used to contribute a percentile rank in the range zero to one. Its replacement is a learned three-input network with a sigmoid output in the same range. The other four experts keep their existing rank transforms and remain mixed by the contextual gate. This preserves a differentiable path for training the replacement from acquisition rewards.

The separate neural expected-improvement feature is retained.
