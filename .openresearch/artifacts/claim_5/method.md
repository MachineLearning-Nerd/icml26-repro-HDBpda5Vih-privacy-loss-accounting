# Method

For every unique privacy epsilon, required Gaussian noise is found by
deterministic bisection. Random-allocation epsilon comes from the pinned
released author API and Poisson epsilon is computed independently with Google's
`dp-accounting` PLD accountant. Both are pessimistic upper bounds, matching the
paper's comparison of accounting guarantees. Each root is evaluated at two
grid resolutions. Both grids must preserve the strict ordering, and the
fine-grid separation must exceed the sum of both bisection widths and both
observed coarse-to-fine shifts. Duplicate panels share the same privacy result.

MSE is independently derived from the sampling process. Allocation has data
variance `p(1-p)/n`; Poisson additionally has exact participation variance
`p(1-1/t)/n`. Both add Gaussian variance `sigma^2*d*t/n^2`. Seeded, chunked
Monte Carlo at `n=1000` checks these formulas with 10,000 replicates per panel.
