# Claim 2 source audit

Theorem 4.6 is `body.tex` label `thm:num_acc_RA`, lines 266–280. Its general
runtime is `O((IQR_{beta/t}/alpha)^2 log^3(t))`; for the unit-sensitivity
Gaussian mechanism it specializes to
`O(log_2^3(t) ln(t/beta)/(sigma^2 alpha^2))`. The algorithm outline at lines
253–262 specifies direct convolution, a geometrically spaced grid,
domination-preserving directional rounding, and at most
`2 ceil(log_2(t))` convolution steps. Appendix C states the exact binary count
`floor(log_2(t)) + popcount(t) - 1`.

The judge paraphrase omits the general IQR factor and the Gaussian `sigma^-2`
factor. The contract tests the exact source statement.
