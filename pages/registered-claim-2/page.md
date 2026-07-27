# Claim 2: The proposed algorithm computes an (α,β)-accurate approximation of the random allocation PLD in time O(log³(t)·log(t/β)/α²), using exponentiation-by-squaring with geometric-grid rounding (Section 4, Theorem 4.6).

## Verdict

**VERIFIED.** 17 fast/exact cases, 6 released API cases, α⁻² scaling.

## Direct executed result

The executed checker compares rounded exponentiation-by-squaring against direct exact convolution in **17 cases**, exercises the pinned released Gaussian API in **6 cases**, and audits every binary multiplication schedule. Primitive-work fits give `log(t)^2.487` and `alpha^-1.984`; all four destructive lower-rounding controls are rejected.

## Failure-sensitive gates

- `accuracy_and_scaling`: **PASS**
- `fast_exact_cases`: **PASS**
- `released_gaussian_cases`: **PASS**
- `suite_verified`: **PASS**

The fixed command regenerated the raw results and exits nonzero if any gate
fails. Raw artifact environment files retain the originating accepted-run
commit; the linked definitive log records the cumulative re-execution from the
current immutable release commit. Evidence: [evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/EVAL.md) · [machine contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/claim_contract.json) · [source audit](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/source_audit.md) · [method](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/method.md) · [negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/negative_control.json) · [raw machine output](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/raw_results.json) · [executed verifier source](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_algorithm_contract.py) · [exact-claim release gate](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_judge_contract.py) · [complexity table](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/complexity_raw.csv) · [definitive current-commit run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) · [definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json).
