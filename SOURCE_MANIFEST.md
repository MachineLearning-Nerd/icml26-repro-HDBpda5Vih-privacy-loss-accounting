# Paper and source manifest

## Paper identity

- Title: *Efficient Privacy Loss Accounting for Subsampling and Random Allocation*
- Authors: Vitaly Feldman and Moshe Shenfeld
- Version audited: [arXiv:2602.17284v2](https://arxiv.org/abs/2602.17284v2)
- OpenReview identifier: `HDBpda5Vih`
- DOI: `10.48550/arXiv.2602.17284`
- Source URL used by the audit: [ar5iv HTML v2](https://ar5iv.labs.arxiv.org/html/2602.17284v2)

## Source pins

The original audit records the exact paper hashes in [SOURCE_PIN.txt](SOURCE_PIN.txt)
and [`.openresearch/artifacts/baseline_audit/startup_audit.json`](.openresearch/artifacts/baseline_audit/startup_audit.json):

| Source | SHA-256 or commit |
| --- | --- |
| Paper HTML | `6e70fa5ab5a0a48536a8bb18be12cb5b159279cdddc9ab97059a2e36c6adf103` |
| Paper PDF | `a7f8934f84821aaaddfb53b79d4addf09efacf4a34726137726b508f3b957f8b` |
| Paper source | `e1b59bfc3f2fcfe503140d23e357dc4f907aa536f4a3d77f1e498305821b8da6` |
| Author PLD implementation | [`moshenfeld/PLD_accounting`](https://github.com/moshenfeld/PLD_accounting), commit `11ed6d14e846de658465fb91309f574ab933cdc9` |
| Author experiment configuration | Public author commit `d49e87d` as recorded in claim source audits |

## Paper anchors

| Paper object | Audit anchor and interpretation |
| --- | --- |
| Definition 3.1 | PLD realization and dual/support conditions. |
| Theorem 3.3 | Exact remove/add `φ_λ(l)=log(1+(exp(l)-1)/λ)` transformations. |
| Theorem 4.4 | Exact 1-out-of-`t` random-allocation PLD identities; general `k` is handled separately by Lemma 2.8. |
| Theorem 4.6 | `(α,β)`-tight geometric-grid approximation and general IQR-dependent complexity; Gaussian specialization supplies the stated log form. |
| Section 5 / Figure 2 | Numerical PLD, Chua lower-bound, and Monte Carlo comparisons. |
| Section 5 / PREAMBLE | Current rendered arXiv v2 source labels the PREAMBLE/DP-SGD comparison Figure 3. |
| Section 5 / Bernoulli utility | The pinned source audit records the `fig:utility_comparison` label; the current rendered arXiv v2 source captions this experiment Figure 5. |

The two registered-locator falsifications are source-numbering findings: the
registered Bernoulli locator says Figure 4 while the current rendered source
captions that experiment Figure 5; the registered PREAMBLE locator says Figure
5 while the current rendered source labels it Figure 3. The evidence contract
records this explicitly rather than silently changing the registered claim
strings.

## Implementation entrypoints

| Claim | Entrypoint |
| --- | --- |
| C1 | `repro/src/verify_exact_theorems.py::verify_claim_1` |
| C2 | `repro/src/verify_algorithm_contract.py::main` |
| C3 | `repro/src/verify_exact_theorems.py::verify_claim_3` |
| C4 | `repro/src/verify_numerical_comparison.py::main` |
| C5 | `repro/src/verify_bernoulli_utility.py::main` |
| C6 | `repro/src/verify_preamble_collector.py::main`, with shard computations in `verify_preamble.py` |
| Registered-claim gate | `repro/src/verify_judge_contract.py::main` |

## Evidence pins

The fixed command is:

```bash
uv run --frozen python repro/src/verify_pld.py
```

The latest direct-evidence run is pinned to commit
`fce5c732f2757b998842649eaa3cda92ca08ed93`, run
`448ed902-e449-4aed-b542-52282bb0138b`, with formal-log SHA-256
`9f09341c80f394255f47eb905bba6ad616d2e25e8a3ee2171c4c8f8295f066dd`.
The cumulative release gate is pinned separately to commit
`1eb57c864b5280952dbe86739fe4b869f69d10b4`.
