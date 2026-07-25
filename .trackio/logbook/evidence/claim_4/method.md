# Method

PLD upper and lower epsilons call the pinned released author implementation.
The independent lower checker implements Chua et al. Equation (6):
`sup_C P(max X_i >= C) - exp(epsilon) Q(max X_i >= C)`. Gaussian independence
makes both probabilities closed form; a dense grid plus bounded refinement
optimizes C, and bisection inverts the profile at delta.

The RDP checker is independent of the PLD code. It calculates the exact
remove-direction integer moments of the average Gaussian likelihood ratio using
truncated exponential-generating-function exponentiation, combines this with
the published DCO add-direction upper bound, and applies the optimal RDP-to-DP
conversion over integer orders 2–60. The order-2 result is checked against a
separate closed form.

The Monte Carlo checker independently implements Algorithms 4 and 6 of Chua
et al. using their published Criteo order-index grids. One joint sample of
500,000 pessimistic privacy-loss envelopes per profile and direction is reused
over all epsilon values. A Bernoulli-KL Chernoff inversion gives simultaneous
99% upper confidence bounds over all 160 directional estimates. Comparisons to
the Monte Carlo mean are made only where at least 200 expected nonzero samples
make the estimate statistically resolved. Confidence consistency requires the
Monte Carlo upper confidence bound to be no smaller than the rigorous PLD lower
bound. It does not compare two upper bounds, whose unrelated numerical slack
need not be ordered.
