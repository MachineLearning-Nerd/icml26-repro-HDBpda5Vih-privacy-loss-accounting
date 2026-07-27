# Claim 1: Theorem 4.4 gives a closed-form reduction of the privacy loss distribution (PLD) of k-out-of-t random allocation to t-wise convolutions of exponentiated PLD terms (Section 4, Theorem 4.4).

## Verdict

**VERIFIED.** 30 exact rational identities; 30/30 mutations rejected.

## Direct executed result

The executed checker enumerates three asymmetric finite-support mechanisms for `t=1..5` in both add and remove directions. All **30/30 rational PLD identities are exactly equal**; six separate `k=2` scope identities also pass. Replacing the theorem denominator `t` by `t+1` is rejected in **30/30** cases.

## Failure-sensitive gates

- `all_identities_pass`: **PASS**
- `all_mutations_rejected`: **PASS**
- `exact_identities`: **PASS**
- `suite_verified`: **PASS**

The fixed command regenerated the raw results and exits nonzero if any gate
fails. Raw artifact environment files retain the originating accepted-run
commit; the linked definitive log records the cumulative re-execution from the
current immutable release commit. Evidence: [evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/EVAL.md) · [machine contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/claim_contract.json) · [source audit](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/source_audit.md) · [method](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/method.md) · [negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/negative_control.json) · [raw machine output](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/raw_results.json) · [executed verifier source](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_exact_theorems.py) · [exact-claim release gate](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_judge_contract.py) · [exact identity table](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/raw_results.csv) · [definitive current-commit run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) · [definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json).
