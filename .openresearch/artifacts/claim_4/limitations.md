# Limitations and deviations

This verifier does not relabel a Monte Carlo estimate as a lower bound. The
manuscript says its displayed curves used one million importance samples and
95% confidence, while public author commit `d49e87d` configures 500,000
order-statistics samples and 99% confidence. We reproduce the public executable
configuration and strengthen it to a simultaneous 99% family confidence bound.
Chua et al.'s predecessor full-profile computation used 5e8 samples on 60 CPU
machines; the statistically unresolved tail is excluded by an explicit rule.
The Figure 1 grid is complete for `t=1000`; `t=10000` is a judge-requested
stress test. The smaller paper panels `t=10,100` are not rerun.
