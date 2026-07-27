# Claim 4: Numerical experiments show the new random allocation privacy bounds are nearly identical to the Monte Carlo lower bounds of Chua et al. (2024a) and substantially tighter than RDP-based analytic bounds, for t ∈ {1000, 10000} and δ = 10⁻⁶ (Section 5, Figures 1-2).

## Verdict

**VERIFIED.** t={1000,10000}, δ=10⁻⁶; PLD<RDP at 20/20 points; independent Chua and Monte Carlo checks.

## Direct executed result

At the exact registered domain `t in {1000,10000}` and `delta=1e-6`, the run evaluates **20/20** primary comparison points and PLD is below the analytic RDP bound at every point (median improvement **83.03%**). Independent Chua and seeded Monte Carlo checks pass; 44 Monte Carlo points are statistically resolved rather than treating unresolved tails as passes.

## Failure-sensitive gates

- `chua_lower_gate`: **PASS**
- `exact_registered_domain`: **PASS**
- `independent_checker`: **PASS**
- `monte_carlo_gate`: **PASS**
- `negative_control`: **PASS**
- `pointwise_pld_below_rdp`: **PASS**
- `suite_verified`: **PASS**

The fixed command regenerated the raw results and exits nonzero if any gate
fails. Raw artifact environment files retain the originating accepted-run
commit; the linked definitive log records the cumulative re-execution from the
current immutable release commit. Evidence: [evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/EVAL.md) · [machine contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/claim_contract.json) · [source audit](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/source_audit.md) · [method](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/method.md) · [negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/negative_control.json) · [raw machine output](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/raw_results.json) · [executed verifier source](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_numerical_comparison.py) · [exact-claim release gate](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_judge_contract.py) · [t=1000/10000 table](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/figure_1_comparison.csv) · [definitive current-commit run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) · [definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json).
