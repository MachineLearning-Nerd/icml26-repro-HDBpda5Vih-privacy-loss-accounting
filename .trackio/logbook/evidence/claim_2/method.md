# Method

The released implementation pinned in `uv.lock` is exercised directly. Four
fixed atoms are placed on increasingly fine geometric grids. Its
`geometric_self_convolve` output is compared to a separately implemented
multinomial enumeration of the exact t-fold sum. CCDF inequalities are checked
at all exact and rounded atom boundaries for both validity and
`(alpha,beta)` tightness.

The convolution function is wrapped only to count calls and input-bin pair
products; numeric work is still performed by the unmodified released function.
Sweeps over `t` and `alpha` fit the exponents of primitive work. A second suite
calls the released Gaussian public API and checks its dominating and dominated
epsilon bounds at explicit alpha/beta settings. The negative control substitutes
downward rounding where an upper bound is required and must violate validity.
