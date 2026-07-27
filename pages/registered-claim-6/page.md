# Claim 6: Applied to a DP-SGD scenario with block-sparse coordinate sampling (n=6×10⁵, d=2²⁰, C=2¹⁵, E=10 epochs), the PLD accounting method improves privacy bounds over RDP composition even under heavy composition (Section 5, Figure 5).

## Verdict

**FALSIFIED.** exact n,d,C,E constants; PLD<RDP at 40/40 points; locator is literally false.

The substantive scientific result is **VERIFIED**. The exact registered claim is **FALSIFIED** because the PREAMBLE comparison is Figure 3 in the paper, not the registered Figure 5.

## Direct executed result

The run uses the exact `n=600000`, `d=2^20`, `C=2^15`, `E=10` constants over four batch sizes and ten block sizes. PLD is below independently recomputed RDP at **40/40 full-scale points** (minimum/median improvement **5.99%/26.55%**). At the matched-privacy anchor, PLD gives `epsilon=0.272300` where RDP gives `1.029195` at the same `sigma=1.802490`.

## Failure-sensitive gates

- `exact_registered_constants`: **PASS**
- `full_domain`: **PASS**
- `independent_checker`: **PASS**
- `negative_control`: **PASS**
- `parameter_identities`: **PASS**
- `pointwise_pld_below_rdp`: **PASS**
- `successful_anchor`: **PASS**
- `suite_verified`: **PASS**

The fixed command regenerated the raw results and exits nonzero if any gate
fails. Raw artifact environment files retain the originating accepted-run
commit; the linked definitive log records the cumulative re-execution from the
current immutable release commit. Evidence: [evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/EVAL.md) · [machine contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/claim_contract.json) · [source audit](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/source_audit.md) · [method](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/method.md) · [negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/negative_control.json) · [raw machine output](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/raw_results.json) · [executed verifier source](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_preamble_collector.py) · [exact-claim release gate](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/repro/src/verify_judge_contract.py) · [full PREAMBLE grid](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/full_grid.csv) · [definitive current-commit run log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/cumulative_run.log) · [definitive run metadata](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release_v3/formal_run_metadata.json).
