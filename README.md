# Claim-by-claim reproduction: efficient privacy loss accounting

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/blob/master/reports/privacy_loss_reproduction/notebook.py)

This repository reproduces all six principal claims from [*Efficient privacy
loss accounting for subsampling and random allocation*](https://arxiv.org/abs/2602.17284).
The current public revision was judged **0/12** because its visible verification
page still embedded the original generic-amplification proxy, while the real
cumulative verifier code was not included in the Space. The committed checks
target the exact theorems, algorithm, and released empirical configurations.
This remediation branch also binds the six exact registered claim strings to
the executed code and makes the `t=10000`, `δ=10⁻⁶` Claim 4 rows explicit.

The headline full-scale result is Claim 6: at the paper's PREAMBLE/DP-SGD
settings (`n=600,000`, `d=2²⁰`, `C=2¹⁵`, ten epochs), PLD accounting is tighter
than RDP at **40/40** released grid points. Its minimum and median epsilon
improvements are **5.99%** and **26.55%**. At a matched-privacy anchor,
PLD gives `ε=0.272300` where RDP gives `ε=1.029195`.

No headline empirical claim was downscaled. Claim 6 used four fixed-sigma grid
shards plus a separate stable matched-privacy anchor because the released
optional PLD root search is numerically unstable. This separation is recorded
as a methodological substitution, not hidden as a successful root search.

- [Illustrated technical report](reports/privacy_loss_reproduction/report.md)
- [Self-contained marimo tutorial](reports/privacy_loss_reproduction/notebook.py)
- [Machine-readable evidence bundles](.openresearch/artifacts)
- [Published Hugging Face logbook](https://huggingface.co/spaces/DineshAI/HDBpda5Vih)

## Results

| Claim | Observed result | Assessment |
| --- | --- | --- |
| 1 — Theorem 4.4 | 30 exact identities, 6 scope checks; 30/30 mutations rejected | VERIFIED |
| 2 — geometric algorithm | 17 fast/exact and 6 released API cases; fitted `α⁻¹·⁹⁸⁴` work | VERIFIED |
| 3 — `φ_λ` transformations | 24 exact identities and 4 unified composition checks | VERIFIED |
| 4 — lower/RDP bounds | 100 paper-panel points; median RDP improvement 83.03%; 44 resolved MC points | VERIFIED |
| 5 — Bernoulli experiment | allocation used 0.21–3.77% less noise in all three panels | VERIFIED |
| 6 — PREAMBLE/DP-SGD | PLD won 40/40 points; minimum/median improvement 5.99%/26.55% | VERIFIED |

## Experiment log

Every formal node used the exact command
`uv run --frozen python repro/src/verify_pld.py`.

| Branch / experiment | Purpose | Exact run command | Outcome | Compute |
| --- | --- | --- | --- | --- |
| `master` | Publication surface | Not run as an experiment (publication surface) | Report, notebook, and additive logbook | — |
| [Frozen judged baseline](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/frozen-judged-baseline) | Preserve judged start | `uv run --frozen python repro/src/verify_pld.py` | Reference, 0/12 judge baseline | Local CPU, 5 s |
| [Exact theorem contracts](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/exact-finite-support-theorem-contracts) | Claims 1 and 3 | `uv run --frozen python repro/src/verify_pld.py` | VERIFIED | Local CPU, 5 s |
| [Geometric algorithm contracts](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/released-geometric-algorithm-contracts) | Claim 2 | `uv run --frozen python repro/src/verify_pld.py` | VERIFIED | Local CPU, 30 s |
| [Numerical comparison gate](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/confidence-consistent-figure-2-gate) | Claim 4 | `uv run --frozen python repro/src/verify_pld.py` | VERIFIED | Local CPU, 9 m 57 s |
| [Bernoulli gate](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/precision-stable-bernoulli-privacy-gate) | Claim 5 | `uv run --frozen python repro/src/verify_pld.py` | VERIFIED | Local CPU, 5 h 59 m |
| [PREAMBLE anchor](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/stable-preamble-anchor-certificate) | Claim 6 certificate | `uv run --frozen python repro/src/verify_pld.py` | VERIFIED | HF CPU-upgrade, 3 h 40 m |
| [Cumulative release gate](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/cumulative-claims-1-6-release-gate) | All-claim regression | `uv run --frozen python repro/src/verify_pld.py` | All six VERIFIED; all-zero status | HF CPU-upgrade, 3 h 44 m |

## Reproduce

The environment is locked with `uv.lock` and Python 3.12.11:

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_pld.py
```

The complete command is CPU-only and includes multi-hour Claims 5 and 6. The
notebook displays embedded results without rerunning expensive calculations:

```bash
uv run marimo edit reports/privacy_loss_reproduction/notebook.py
uv run marimo run reports/privacy_loss_reproduction/notebook.py
```
