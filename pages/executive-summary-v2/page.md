# Executive summary

The exact registered-claim gate passes all six evidence contracts under the
fixed CPU command. Claims 1–4 are **VERIFIED**. Claims 5–6 are **FALSIFIED as
literally registered** because their figure locators are wrong, while their
substantive Bernoulli and PREAMBLE results are independently **VERIFIED**.

This release includes the actual executed verifier source, raw outputs,
independent checkers, negative controls, locked environment, source hashes, and
cumulative log.

| Claim | Direct result | Exact verdict |
| --- | --- | --- |
| 1 | 30 exact rational identities; 30/30 mutations rejected | **VERIFIED** |
| 2 | 17 fast/exact cases, 6 released API cases, α⁻² scaling | **VERIFIED** |
| 3 | 24 exact φ_λ identities; 24/24 mutations rejected | **VERIFIED** |
| 4 | t={1000,10000}, δ=10⁻⁶; PLD<RDP at 20/20 points; independent Chua and Monte Carlo checks | **VERIFIED** |
| 5 | n=1000, δ=10⁻¹⁰; allocation requires less noise in 3/3 panels; locator is literally false | **FALSIFIED** |
| 6 | exact n,d,C,E constants; PLD<RDP at 40/40 points; locator is literally false | **FALSIFIED** |

Run: `uv run --frozen python repro/src/verify_pld.py`

[cumulative entry point](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_pld.py) ·
[all machine gates](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/judge_release/results.json) ·
[definitive run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) ·
[definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json)
