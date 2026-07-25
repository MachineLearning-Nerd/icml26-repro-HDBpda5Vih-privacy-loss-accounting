# Limitations and deviations

The public paper artifact contains only plotted points, not the original raw
random draws, so exact pixel-for-pixel stochastic replication is impossible.
The privacy computation and analytic MSE use the source parameters at full
scale. The claim is about the reported accounting bounds, not an exact
closed-form privacy threshold for either mechanism. Numerical robustness is
therefore assessed by grid refinement and explicit root brackets. New Monte
Carlo draws use fixed disclosed seeds and are checked against the exact moments
rather than expected to match historical random draws.
