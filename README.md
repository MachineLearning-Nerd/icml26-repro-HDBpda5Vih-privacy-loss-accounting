# ICML 2026 — Efficient Privacy Loss Accounting

[![Open in Molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/blob/main/reports/privacy_loss_reproduction/notebook.py)

This repository is an independent, claim-faithful reproduction audit of
[*Efficient Privacy Loss Accounting for Subsampling and Random
Allocation*](https://arxiv.org/abs/2602.17284v2). It checks the paper's exact
PLD identities, approximation algorithm, subsampling transformations, numerical
comparisons, Bernoulli utility experiment, and PREAMBLE/DP-SGD experiment.

## Current status

The direct-evidence release passed its internal contracts, independent checks,
negative controls, provenance checks, and publication-manifest checks. The
corrected Hugging Face logbook revision is published but **awaiting a new live
judge evaluation**. The latest recorded live score is **5/12**; no score
increase is claimed for the corrected revision.

| Claim | Status | What the evidence supports |
| --- | --- | --- |
| 1 | `VERIFIED_SCOPED` | Theorem 4.4's exact 1-out-of-`t` add/remove PLD identities match direct finite-support enumeration in exact `Fraction` arithmetic; denominator mutations are rejected. |
| 2 | `VERIFIED_SCOPED` | Theorem 4.6's released geometric self-convolution algorithm passes finite exactness, validity, tightness, call-count, released Gaussian API, and primitive-work checks. |
| 3 | `VERIFIED_SCOPED` | Theorem 3.3's `φ_λ` remove/add transformations and the unified subsampling-plus-allocation interface pass exact finite-support checks and mutations. |
| 4 | `VERIFIED_SCOPED_WITH_REPRODUCTION_DEVIATIONS` | The PLD/RDP comparison and Chua/Monte Carlo comparison pass the declared audit domain; `t=10,000` is an explicit stress test, while smaller source panels and the author's exact sampling configuration are documented deviations. |
| 5 | `FALSIFIED_AS_REGISTERED_LOCATOR` | The Bernoulli privacy/utility result is reproduced in all three panels, but the registered sentence says Figure 4 while the audited paper source places the experiment in Figure 5. |
| 6 | `FALSIFIED_AS_REGISTERED_LOCATOR` | The full 40-point PREAMBLE/DP-SGD result is reproduced, but the registered sentence says Figure 5 while the audited paper source places PREAMBLE in Figure 3. |

For claims 5 and 6, the falsification is about the literal registered claim's
figure locator, not the nearby numerical result. Their substantive results are
`VERIFIED_SCOPED`. `VERIFIED_SCOPED` means that the declared source statement,
parameters, finite or executable contract, and evidence path pass within the
stated scope; it is not a machine-checked proof of every universal theorem
quantifier.

Overall status: **partial success with two literal registered-locator
falsifications**. The evidence-release gate is **passed**. The strict
paper-level publication gate is **not ready** until the locator qualification
and a new live judge evaluation are resolved.

## Paper

- **Title:** *Efficient Privacy Loss Accounting for Subsampling and Random Allocation*
- **Authors:** Vitaly Feldman and Moshe Shenfeld
- **Paper:** [arXiv:2602.17284v2](https://arxiv.org/abs/2602.17284v2)
- **OpenReview identifier:** `HDBpda5Vih`
- **DOI:** [10.48550/arXiv.2602.17284](https://doi.org/10.48550/arXiv.2602.17284)
- **Corrected logbook:** [DineshAI/HDBpda5Vih](https://huggingface.co/spaces/DineshAI/HDBpda5Vih)
- **Published correction revision:** [`bd20a58`](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/commit/bd20a58b84d5a076b4d9e5b2108eb6715a0d6eb9)
- **Source pins:** [SOURCE_PIN.txt](SOURCE_PIN.txt) and [SOURCE_MANIFEST.md](SOURCE_MANIFEST.md)

The paper develops privacy-loss-distribution (PLD) methods for Poisson
subsampling and `k`-out-of-`t` random allocation. Its goal is accurate,
efficient privacy accounting that can be composed and compared with RDP,
including a heavy-composition PREAMBLE/DP-SGD application.

## How each claim is produced

The fixed entrypoint is
[`repro/src/verify_pld.py`](repro/src/verify_pld.py):

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_pld.py
```

| Claim | Production path | Evidence and controls |
| --- | --- | --- |
| 1 | [`verify_exact_theorems.py::verify_claim_1`](repro/src/verify_exact_theorems.py) directly enumerates positive rational product spaces for `t=1..5` in both directions and compares exact PMFs. | `.openresearch/artifacts/claim_1/` contains the contract, exact outputs, source audit, independent checker, and denominator-`t+1` mutation controls. |
| 2 | [`verify_algorithm_contract.py::main`](repro/src/verify_algorithm_contract.py) compares the released geometric self-convolution to an independent multinomial sum, checks `(α,β)` validity/tightness, counts calls, fits primitive work, and calls the released Gaussian API. | `.openresearch/artifacts/claim_2/` contains exact cases, released API cases, scaling data, checker, limitations, and invalid-rounding controls. |
| 3 | [`verify_exact_theorems.py::verify_claim_3`](repro/src/verify_exact_theorems.py) constructs `P_λ` directly, applies the independent `φ_λ` transform, checks both PLD directions and the unified allocation interface. | `.openresearch/artifacts/claim_3/` contains exact transformations, invariants, checker, source audit, and an incorrect-affine-map control. |
| 4 | [`verify_numerical_comparison.py::main`](repro/src/verify_numerical_comparison.py) evaluates PLD against RDP, Chua et al.'s lower bound, and seeded Monte Carlo with simultaneous confidence bounds. | `.openresearch/artifacts/claim_4/` contains the 20-point Figure-1 comparison, 80 profile points, checker, source audit, limitations, and a lower-bound mutation control. |
| 5 | [`verify_bernoulli_utility.py::main`](repro/src/verify_bernoulli_utility.py) computes noise roots at two grid resolutions, derives exact MSE, and compares fixed-seed Monte Carlo at the full `n=1000` point and the full sample-size sweep. | `.openresearch/artifacts/claim_5/` contains privacy roots, utility MSE, checker, source audit, and a reversed-ordering control. |
| 6 | [`verify_preamble_collector.py::main`](repro/src/verify_preamble_collector.py) collects four provenance-bound ten-point shards from [`verify_preamble.py`](repro/src/verify_preamble.py), reconstructs the 40-point grid, independently recomputes RDP, and checks a stable required-noise anchor. | `.openresearch/artifacts/claim_6/` contains the full grid, shard logs, source provenance, checker, parameter identities, negative controls, and anchor certificate. |
| Gate | [`verify_judge_contract.py::main`](repro/src/verify_judge_contract.py) binds all six registered claim strings to the evidence and assigns the literal/substantive verdicts. | `.openresearch/artifacts/judge_release/` contains the machine-readable claim gate and manifest. |

## Evidence at a glance

| Result | Recorded evidence |
| --- | --- |
| Claims 1 and 3 | 30 exact Theorem-4.4 identities and 24 exact `φ_λ` identities; every registered mutation rejected. |
| Claim 2 | 17 fast/exact cases, six released Gaussian API cases, observed `α⁻²` exponent `1.984` and log-`t` primitive-work exponent `2.487`. |
| Claim 4 | PLD below RDP at 20/20 primary points; 80 profile points; median RDP improvement `83.03%`; 44 statistically resolved Monte Carlo points. |
| Claim 5 substantive result | Allocation needs less noise in all three panels; exact roots include `0.889941` vs `0.891829` at `(ε,d)=(1,1)` and `1.865726` vs `1.938765` at both `ε=0.1` panels. |
| Claim 6 substantive result | PLD below RDP at all 40 released PREAMBLE points; minimum and median improvements `5.99%` and `26.55%`; anchor PLD `ε=0.272300` vs RDP `ε=1.029195`. |

The full-scale Claim 6 audit uses `n=600,000`, `d=2²⁰`, `C=2¹⁵`, ten
epochs, `(ε,δ)=(1,10⁻⁶)`, batch sizes `{512, 1028, 4096, 600000}`, and block
sizes `2²` through `2¹¹`. The optional root search is not mislabeled as a
success: the release records the four complete pre-terminal shard panels and
uses a separate stable matched-privacy anchor.

## Repository map

| Path | Purpose |
| --- | --- |
| [`repro/src/verify_pld.py`](repro/src/verify_pld.py) | Fixed cumulative runner. |
| [`repro/src/pld.py`](repro/src/pld.py) | PLD implementation helpers used by the audit. |
| [`repro/src/registered_claims.py`](repro/src/registered_claims.py) | Exact registered claim strings. |
| [`repro/src/verify_exact_theorems.py`](repro/src/verify_exact_theorems.py) | Claims 1 and 3. |
| [`repro/src/verify_algorithm_contract.py`](repro/src/verify_algorithm_contract.py) | Claim 2. |
| [`repro/src/verify_numerical_comparison.py`](repro/src/verify_numerical_comparison.py) | Claim 4. |
| [`repro/src/verify_bernoulli_utility.py`](repro/src/verify_bernoulli_utility.py) | Claim 5. |
| [`repro/src/verify_preamble.py`](repro/src/verify_preamble.py) and [`verify_preamble_collector.py`](repro/src/verify_preamble_collector.py) | Claim 6 shard and collection path. |
| [`repro/src/verify_judge_contract.py`](repro/src/verify_judge_contract.py) | Literal registered-claim gate. |
| [`reports/privacy_loss_reproduction/report.md`](reports/privacy_loss_reproduction/report.md) | Illustrated claim-by-claim report. |
| [`reports/privacy_loss_reproduction/notebook.py`](reports/privacy_loss_reproduction/notebook.py) | Self-contained summary notebook; it does not rerun multi-hour evidence. |
| [`evidence/`](evidence/) and [`.openresearch/artifacts/`](.openresearch/artifacts/) | Source-pinned evidence, logs, manifests, and controls. |
| [`STATUS.md`](STATUS.md) | Current gate and publication status. |
| [`SOURCE_MANIFEST.md`](SOURCE_MANIFEST.md) | Paper/source anchors and claim entrypoints. |
| [`BRANCH_AUDIT.md`](BRANCH_AUDIT.md) | Every old branch, clean name, tip, relationship, and role. |
| [`publication_gate.json`](publication_gate.json) | Conservative machine-readable status. |

The old root `outputs/verify_run.log` and `outputs/verdict.json` were generic
proxy artifacts and are intentionally removed. See
[`outputs/README.md`](outputs/README.md); the source-pinned evidence bundles
are authoritative.

## Branches

The current reader-facing surface is [`main`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/main).
The former `master` and every `orx/*` branch are mapped to clean
`research/*`, `audit/*`, and `release/*` names. All 24 branches are retained,
including divergent shards and judge-facing lines; the full map is in
[`BRANCH_AUDIT.md`](BRANCH_AUDIT.md).

The primary lines are:

- [`research/frozen-judged-baseline`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/research/frozen-judged-baseline) — frozen starting point and environment audit;
- [`research/exact-finite-support-theorems`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/research/exact-finite-support-theorems) — Claims 1 and 3;
- [`research/geometric-algorithm-contracts`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/research/geometric-algorithm-contracts) — Claim 2;
- [`research/figure-2-confidence-gate`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/research/figure-2-confidence-gate) — Claim 4;
- [`research/bernoulli-precision-gate`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/research/bernoulli-precision-gate) — Claim 5;
- [`research/preamble-anchor-certificate`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/research/preamble-anchor-certificate) — Claim 6 anchor;
- [`release/privacy-loss-cumulative-gate`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/release/privacy-loss-cumulative-gate) — cumulative release gate;
- [`audit/unambiguous-run-provenance`](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting/tree/audit/unambiguous-run-provenance) — latest direct-evidence and provenance audit.

## Reproduce locally

The lockfile pins Python 3.12 and the author's PLD implementation at commit
`11ed6d14e846de658465fb91309f574ab933cdc9`. The full command includes the
multi-hour Claim 5 and Claim 6 suites:

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_pld.py
```

The notebook displays embedded results without rerunning the expensive suite:

```bash
uv run marimo edit reports/privacy_loss_reproduction/notebook.py
uv run marimo run reports/privacy_loss_reproduction/notebook.py
```

Known limits and deviations are recorded per claim in the evidence bundles;
in particular, finite exact checks do not replace universal proofs, finite
timing does not prove Big-O, and the numerical experiments do not reproduce
pixel-level stochastic plots or end-to-end model training.

## Citation

```bibtex
@article{feldman2026efficient,
  title={Efficient Privacy Loss Accounting for Subsampling and Random Allocation},
  author={Feldman, Vitaly and Shenfeld, Moshe},
  journal={arXiv preprint arXiv:2602.17284},
  year={2026},
  doi={10.48550/arXiv.2602.17284}
}
```

## Thank you

Thank you to **Vitaly Feldman and Moshe Shenfeld** for developing and sharing
this careful work on privacy-loss distributions, random allocation, and
privacy accounting. This repository is an independent reproduction and audit
intended to make the paper's methods and evidence easier to inspect; it is not
an official artifact from, or an endorsement by, the authors.

## Maintainer attribution

Repository cleanup, documentation, branch normalization, and approved
publication changes are maintained under the GitHub identity
**MachineLearning-Nerd**.
