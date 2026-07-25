# Claim 4 source audit

The imported judge claim conflates Figures 1 and 2. `intro.tex` lines 48–55 and
the public historical experiment script at author commit `d49e87d` establish
that Figure 1 uses `t={10,100,1000}`, ten sigma values from 1 to 4, and
`delta=1e-6`; it compares PLD with FS25/DCO25 analytic bounds and Poisson.
`body.tex` lines 307–317 and `appendix.tex` lines 516–524 instead compare full
privacy profiles at Criteo-derived `t={35938,4492,12500,1563}` with Monte Carlo
mean/high-probability estimates and the distinct efficiently computable lower
bound from Chua et al. Equation (6) of arXiv:2412.16802.

There is no `t=10000` panel in the cited paper figure. This contract evaluates
the exact largest Figure 1 panel (`t=1000`) and adds `t=10000` solely to answer
the judge wording. It labels Equation (6) accurately as a deterministic lower
bound, not a “Monte Carlo lower bound.” The exact Figure 2 settings are
`(t,sigma)={(35938,.3),(4492,.4),(12500,.3),(1563,.4)}` with 20 epsilon
values from 0.1 to 8, as recovered from public author commit `d49e87d`.
