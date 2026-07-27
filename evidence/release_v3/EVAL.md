# Release v3 evaluation

The definitive cumulative run completed successfully on Hugging Face
`cpu-upgrade`, without a GPU, from immutable Git commit
`fce5c732f2757b998842649eaa3cda92ca08ed93`.

- Fixed command: `uv run --frozen python repro/src/verify_pld.py`
- Run: `448ed902-e449-4aed-b542-52282bb0138b`
- Status: `done`
- Duration: 3h11m
- Formal-log SHA-256:
  `9f09341c80f394255f47eb905bba6ad616d2e25e8a3ee2171c4c8f8295f066dd`
- Cumulative component exits: all zero
- Exact registered-claim release gate: `JUDGE_RELEASE_ALL_PASSED=True`

## Claim outcomes

1. **VERIFIED** — 30 exact rational identities, six general-`k` scope cases,
   and 30/30 destructive controls.
2. **VERIFIED** — 17 fast-versus-exact cases, six released-API cases,
   empirical exponents 2.487 for logarithmic `t` scaling and 1.984 for
   inverse-accuracy scaling, and 4/4 destructive controls.
3. **VERIFIED** — 24 exact transformation identities, four unified
   composition cases, and 24/24 destructive controls.
4. **VERIFIED** — exact registered `t={1000,10000}` and `delta=1e-6`;
   PLD below RDP at 20/20 points; median improvement 83.03%; independent
   Chua and Monte Carlo comparisons.
5. **FALSIFIED as literally registered; substantive result VERIFIED** —
   exact `n=1000`, `delta=1e-10`; allocation required less noise in 3/3
   panels. The registered locator says Figure 4, while the Bernoulli
   experiment is Figure 5 in the paper.
6. **FALSIFIED as literally registered; substantive result VERIFIED** —
   exact `n=600000`, `d=2^20`, `C=2^15`, `E=10`; PLD below RDP at 40/40
   points with 5.99% minimum and 26.55% median improvement. The registered
   locator says Figure 5, while the PREAMBLE comparison is Figure 3.

## Score statement

The currently published revision was judged 5/12. This candidate has not been
published or evaluated, so no score increase is claimed. The release package
is designed to answer every cited judge criticism with direct, reproducible,
failure-sensitive evidence.
