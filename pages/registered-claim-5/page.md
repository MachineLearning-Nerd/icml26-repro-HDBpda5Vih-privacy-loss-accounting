# Claim 5: A toy Bernoulli mean-estimation experiment (n=10³, δ=10⁻¹⁰) shows random allocation requires strictly lower noise than Poisson subsampling for the same privacy level, demonstrating a genuine privacy (not just variance) advantage (Section 5, Figure 4).

## Verdict

**FALSIFIED.** n=1000, δ=10⁻¹⁰; allocation requires less noise in 3/3 panels; locator is literally false.

The substantive scientific result is **VERIFIED**. The exact registered claim is **FALSIFIED** because the Bernoulli experiment is Figure 5 in the paper, not the registered Figure 4.

## Direct executed result

At `n=t=1000` and `delta=1e-10`, allocation requires less noise in all three privacy panels: `0.889941 < 0.891829` for `epsilon=1`, and `1.865726 < 1.938765` for both `epsilon=0.1` panels. Exact utility and seeded Monte Carlo checks agree, and participation variance is audited separately from privacy.

## Failure-sensitive gates

- `exact_registered_parameters`: **PASS**
- `monte_carlo_gate`: **PASS**
- `negative_control`: **PASS**
- `privacy_gate`: **PASS**
- `strict_noise_advantage`: **PASS**
- `suite_verified`: **PASS**
- `variance_separated`: **PASS**

The fixed command regenerated the raw results and exits nonzero if any gate
fails. Raw artifact environment files retain the originating accepted-run
commit; the linked definitive log records the cumulative re-execution from the
current immutable release commit. Evidence: [evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/EVAL.md) · [machine contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/claim_contract.json) · [source audit](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/source_audit.md) · [method](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/method.md) · [negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/negative_control.json) · [raw machine output](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/raw_results.json) · [executed verifier source](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_bernoulli_utility.py) · [exact-claim release gate](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_judge_contract.py) · [privacy-noise roots](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/privacy_noise.csv) · [definitive current-commit run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) · [definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json).
