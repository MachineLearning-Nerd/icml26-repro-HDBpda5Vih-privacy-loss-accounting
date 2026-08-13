# Reproduction status

Updated during repository cleanup on 2026-08-14.

| Item | Status |
| --- | --- |
| Paper association | Confirmed: arXiv `2602.17284v2`, OpenReview `HDBpda5Vih` |
| Authors | Vitaly Feldman; Moshe Shenfeld |
| Evidence release | Internal contracts, independent checkers, negative controls, source pins, and publication-manifest checks passed |
| Literal claim gate | Claims 1–4 pass within declared scope; Claims 5–6 are falsified only because their registered figure locators are wrong |
| Substantive numerical findings | Claims 5–6 are independently reproduced within their declared parameters and controls |
| Live judge | Latest recorded score `5/12`; corrected logbook revision `bd20a58...` is awaiting judge |
| Strict publication gate | Not ready |
| Compute | Local CPU for contract checks; Hugging Face `cpu-upgrade` for the full Claim 6 shards; no GPU |

## Known limitations and deviations

- Exact finite-support checks do not replace the paper's universal algebraic
  proofs.
- Finite primitive-work fits are evidence for the stated implementation, not a
  proof of asymptotic Big-O.
- Claim 4 uses `t=10,000` as a declared stress test; the smaller `t=10,100`
  paper panels are not rerun. The public author configuration uses 500,000
  samples and simultaneous 99% confidence, while the manuscript describes
  1,000,000 samples and 95% confidence.
- Claim 5 cannot reproduce historical random draws because only plotted points
  are public; exact moments and disclosed-seed Monte Carlo are checked instead.
- Claim 6 uses complete pre-terminal shard grids plus a separate stable
  matched-privacy anchor; the optional root-search termination is not counted
  as a successful run.
- This work audits accounting methods, not end-to-end private model training or
  pixel equality with the paper's plots.
