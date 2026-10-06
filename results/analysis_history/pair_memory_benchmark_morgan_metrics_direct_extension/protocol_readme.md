# Direct covariance extension of the Morgan metric comparison

This exploratory extension adds direct Tanimoto, Dice, cosine, Braun–Blanquet, Sokal, and Pearson similarity kernels. Hamming uses a linear fingerprint dot-product kernel.

For each metric and radius, the direct candidate is trained for 2400 steps with the same frozen MiniMol mean and episodic likelihood. The best validation score is selected among the existing radial winner and both direct radii. Additional seeds are trained only if the direct option wins; otherwise the completed radial checkpoints are reused. The metric chosen across families is also selected on validation only. Tests retain identical fixed hidden queries, folds, outcomes and seeds.

Direct normalized similarities have unit diagonal and use learned signal amplitude and molecule-level nugget. The Hamming counterpart is $k(x,y)=x^\mathsf{T}y/(D s)$, where $D=2048$ and $s$ is the existing training-only median squared-distance normalization. It is positive semidefinite. Its implied relative covariance is the linear kernel on reference-centered fingerprint differences. No covariance is constructed by simply negating a distance matrix.

Outputs in this directory are the final comparison across direct, Gaussian, Matérn-5/2 and rational-quadratic covariance options for each of seven geometries. The parent directory preserves the radial-only comparison. The original MiniMol/Tanimoto kernel-remapping report is also retained separately. No models or results from those earlier runs are overwritten.
