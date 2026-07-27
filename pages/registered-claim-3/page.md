# Claim 3: Theorem 3.3 introduces transformation rules φ_λ that apply Poisson subsampling directly to PLD realizations, allowing subsampling and random allocation to be composed within one unified PLD framework (Section 3, Theorem 3.3, Definition 3.1).

## Verdict

**VERIFIED.** 24 exact φ_λ identities; 24/24 mutations rejected.

## Direct executed result

The executed checker compares the `phi_lambda` realization maps pointwise with directly mixed distributions. All **24/24 exact transformations** and four allocation-then-subsampling unified composition identities pass; omitting the required mixture term is rejected in **24/24** cases.

## Failure-sensitive gates

- `all_mutations_rejected`: **PASS**
- `all_transformations_pass`: **PASS**
- `exact_transformations`: **PASS**
- `suite_verified`: **PASS**

The fixed command regenerated the raw results and exits nonzero if any gate
fails. Raw artifact environment files retain the originating accepted-run
commit; the linked definitive log records the cumulative re-execution from the
current immutable release commit. Evidence: [evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/EVAL.md) · [machine contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/claim_contract.json) · [source audit](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/source_audit.md) · [method](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/method.md) · [negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/negative_control.json) · [raw machine output](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/raw_results.json) · [executed verifier source](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_exact_theorems.py) · [exact-claim release gate](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_judge_contract.py) · [transformation table](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_3/raw_results.csv) · [definitive current-commit run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) · [definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json).
