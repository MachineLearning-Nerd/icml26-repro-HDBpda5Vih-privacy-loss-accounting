# Reproducing efficient privacy loss accounting, claim by claim

![](images/01_claim_matrix.png)

The paper asks whether privacy loss distributions (PLDs) can account efficiently
and tightly for two operations that appear throughout private learning:
subsampling records and randomly allocating coordinates or examples. The
original public logbook received **0/12** because its checks were proxies—for
example, “amplification happened” or “PLD beat naive composition”—rather than
tests of the stated theorems, algorithms, or experiments.

This reproduction replaces those proxies with six failure-sensitive contracts.
All six now have local **VERIFIED** evidence. This is not a claim about the
unrun public judge: the Hugging Face Space still points to its judged revision,
and no score increase is claimed before publication approval and re-evaluation.

## Results at a glance

| Claim | Paper evidence tested | Observed evidence | Assessment |
| --- | --- | --- | --- |
| 1 | Theorem 4.4 PLD reduction, with its exact scope | 30 exact add/remove identities and 6 `k=2` scope checks using rational arithmetic; 30/30 mutations rejected | **VERIFIED** |
| 2 | Geometric rounding, exponentiation by squaring, `(α,β)` accuracy, and work scaling | 17 fast-versus-exact cases, 6 released Gaussian API cases; fitted exponents 2.487 in `log(t)` and 1.984 in `1/α` | **VERIFIED** |
| 3 | The `φ_λ` Poisson transformations and unified composition | 24 exact transformation identities and 4 allocation-then-subsampling checks; 24/24 mutations rejected | **VERIFIED** |
| 4 | Numerical proximity to deterministic/Monte Carlo lower bounds and improvement over RDP | 20 Figure-1 and 80 Figure-2 points; median RDP improvement 83.03%; 44 statistically resolved Monte Carlo points | **VERIFIED** |
| 5 | Bernoulli mean estimation at `n=1,000`, `δ=10⁻¹⁰` | Allocation required strictly less noise in all 3 privacy panels; exact and seeded Monte Carlo utility checks agreed | **VERIFIED** |
| 6 | Full PREAMBLE/DP-SGD parameters, heavy composition, PLD versus RDP | All 40 published parameter-grid points favored PLD; minimum/median improvement 5.99%/26.55%; matched-privacy anchor passed | **VERIFIED** |

The source audit corrected several imported descriptions before testing them.
In particular, Theorem 4.4 is the 1-out-of-`t` result and general `k` uses
Lemma 2.8; Theorem 4.6 includes an IQR factor and its Gaussian specialization
contains `σ⁻²`; and the released Figure-1 sweep uses `t∈{10,100,1000}`, not
`t=10000`. Contracts follow the paper and released source, not the inaccurate
imported labels.

## The strongest full-scale result

![](images/02_claim6_heatmap.png)

Claim 6 uses the full released PREAMBLE grid:
`n=600,000`, `d=2²⁰`, communication budget `C=2¹⁵`, ten epochs,
`δ=10⁻⁶`, four batch sizes, and ten block sizes. The pinned author PLD
implementation was evaluated once per grid point at global `σ=1`, while a
separate implementation recomputed every RDP value from the paper formulas.
PLD produced a lower epsilon at **40/40** points.

The matched-privacy certificate avoids an unstable, unnecessary PLD root
search. It first brackets the cheap RDP `ε=1` root. At the RDP-failing endpoint
`σ=1.802490234375`, RDP gives `ε=1.029195098`, but one full PLD evaluation gives
`ε=0.272299981`. Monotonicity therefore proves that PLD needs strictly less
noise at this heavy-composition point.

Four long grid runs ended after their useful panel output: two hit a released
subsampling-grid degeneracy in the superseded optional root search and two were
cancelled at the same boundary. The collector does **not** relabel these runs as
successful. It accepts only their ten complete, pre-terminal grid lines, binds
each full log by run ID, commit, byte count, and SHA-256, and requires the
separate successful anchor.

## Numerical comparisons to lower bounds

![](images/03_claim4_diagnostics.png)

For Claim 4, PLD intervals contain the deterministic quantities with the
required ordering at every point. The median absolute log₁₀ gap to the Chua
deterministic lower bound is `0.00484`; its 90th percentile is `0.03031`.
Against Monte Carlo, the corresponding values are `0.01359` and `0.03088` on
the 44 points whose simultaneous confidence bound resolves the comparison.
Unresolved tail points remain marked unresolved rather than being converted
into passes.

The same experiment directly compares PLD to the paper’s RDP analytic bound,
not naive linear composition. The median epsilon-bound improvement is 83.03%.

## Privacy advantage in the Bernoulli experiment

![](images/04_claim5_noise.png)

Claim 5 fixes `n=1,000` and `δ=10⁻¹⁰`, solves for the noise needed by each
privacy accountant, and then evaluates the estimator utility. Allocation needs
0.21% less noise in the `ε=1` panel and 3.77% less noise in both `ε=0.1`
panels. The `d=1,000` panel keeps the full problem size rather than replacing
it with a lower-dimensional proxy.

The privacy roots are checked independently; exact variance and deterministic,
seeded Monte Carlo estimates agree. A mutation that removes the allocation
advantage is rejected.

## Algorithmic implementation

![](images/05_claim2_scaling.png)

The algorithm verifier follows the consequential implementation path:

1. exponentiate PLD terms by squaring;
2. round onto the geometric grid after each multiplication;
3. compare the fast result with direct exact convolution under the same
   `(t,α,β)` contract;
4. count primitive work instead of timing Python overhead;
5. exercise the pinned released Gaussian API.

The observed inverse-`α` exponent, 1.984, closely tracks the predicted
quadratic dependence. The finite `t` sweep gives 2.487 versus the theorem’s
cubic upper-bound exponent; this is treated as consistency evidence, not as an
empirical proof of an asymptotic upper bound.

Claims 1 and 3 use independent exact rational checkers. This matters because
simple observations such as “subsampling improves privacy” cannot identify
whether Theorem 4.4 or the `φ_λ` rules were implemented correctly.

## How the judge criticisms were answered

| Previous criticism | Direct replacement |
| --- | --- |
| Claim 1 tested only generic amplification | Exact theorem formula versus an independently enumerated finite-support PLD |
| Claim 2 compared different computations and omitted `(α,β)` and timing | Same-case fast/exact comparisons, accuracy sweeps, primitive-work scaling, and released API checks |
| Claim 3 tested only amplification | Exact `φ_λ` realization transformations plus unified allocation/subsampling composition |
| Claim 4 omitted RDP, Monte Carlo, and source parameters | Published numerical panels, deterministic Chua bound, confidence-aware Monte Carlo, and direct RDP comparison |
| Claim 5 used a generic Gaussian toy at the wrong `δ` | Full Bernoulli privacy–utility contract at `n=1,000`, `δ=10⁻¹⁰` |
| Claim 6 used ten Gaussian convolutions and naive composition | Full PREAMBLE dimensions, allocation identities, Poisson users, heavy composition, and paper-formula RDP |

Every gate exits nonzero when its contract fails. Each contains a negative
control and writes a claim contract, source audit, raw machine-readable output,
independent checker, exact command/environment, limitations, evaluation, and
manifest.

## Experiment lineage and compute

All formal nodes inherit the exact command:

```bash
uv run --frozen python repro/src/verify_pld.py
```

| Experiment branch | Purpose | Outcome | Compute |
| --- | --- | --- | --- |
| [Frozen judged baseline](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/frozen-judged-baseline) | Preserve the judged starting point and lock the environment | Reference only | Local CPU, 5 s |
| [Exact theorem contracts](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/exact-finite-support-theorem-contracts) | Claims 1 and 3 | VERIFIED | Local CPU, 5 s |
| [Released geometric algorithm](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/released-geometric-algorithm-contracts) | Claim 2 | VERIFIED | Local CPU, 30 s |
| [Confidence-consistent numerical gate](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/confidence-consistent-figure-2-gate) | Claim 4 | VERIFIED | Local CPU, 9 m 57 s |
| [Precision-stable Bernoulli gate](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/precision-stable-bernoulli-privacy-gate) | Claim 5 | VERIFIED | Local CPU, 5 h 59 m |
| [Stable PREAMBLE anchor](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/stable-preamble-anchor-certificate) | Claim 6 required-noise certificate | VERIFIED | HF CPU-upgrade, 3 h 40 m |
| [Cumulative Claims 1–6 release gate](https://github.com/MachineLearning-Nerd/icml26-repro-HDBpda5Vih-privacy-loss-accounting/tree/orx/cumulative-claims-1-6-release-gate) | Full regression and release candidate | All six VERIFIED; cumulative status all zero | HF CPU-upgrade, 3 h 44 m |

The long Claim 6 grid was split across four CPU-upgrade panels. Including the
anchor and cumulative gate, recorded HF CPU-upgrade usage was 5,285 minutes
(88.08 hours). At the provider's July 2026 price of $0.03/hour, the estimated
cost is **$2.64**. Local formal checks used about 6 h 10 m of CPU time. No GPU
was used.

## Assessment

The evidence currently supports local **VERIFIED** verdicts for all six claims.
The most consequential empirical claims were tested at their released scale,
not as toy substitutes. Stochastic evidence is restricted to resolved
confidence regions, and numerical failures outside the tested contract remain
visible in provenance and limitations.

The cumulative regression finished successfully and publication was explicitly
approved. The release preserves the judged Space files additively and publishes
the new claim pages and evidence. Until the live judge evaluates this revision,
the official score remains **0/12**.
