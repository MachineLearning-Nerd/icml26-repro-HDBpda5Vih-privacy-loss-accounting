# Claim 5 source audit

The experiment is described in `body.tex` lines 356–365 and its settings are
recoverable from the authors' deleted-but-versioned script
`comparisons/paper_experiments.py` at public commit `d49e87d`: `t=1000`,
`p=0.9`, `delta=1e-10`, 10,000 experiments, sample sizes from `10^2` through
`10^5`, and panels `(epsilon,d)=(1,1),(0.1,1),(0.1,1000)`.

The judge's phrase “n=1000” selects one point of that sweep rather than the
full source quantifier. This contract evaluates both the exact `n=1000` point
and the full seven-point source sweep.
