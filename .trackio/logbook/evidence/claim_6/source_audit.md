# Claim 6 source audit

The audited paper PREAMBLE experiment fixes `n=6*10^5`, `d=2^20`,
`C=2^15`, `E=10`, and `(epsilon, delta)=(1, 1e-6)`. It uses block-sparse
random allocation with `k=C/B` out of `t=d/B`, user Poisson subsampling, and
heavy composition. The released source evaluates batch sizes
`{512,1028,4096,600000}` and `B=2^2,...,2^11`, with the PLD geometric grid
capped at one million bins per direction. The imported judge label “Figure 5”
does not match the audited source numbering; this contract follows the exact
parameters and quantifiers rather than that label.
