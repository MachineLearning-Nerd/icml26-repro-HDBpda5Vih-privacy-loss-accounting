# Claim 1 — exact PLD reduction

## Source scope

The imported description overstates Theorem 4.4: the theorem is the
**1-out-of-`t`** allocation identity. General `k` uses Lemma 2.8. The contract
tests the theorem in its actual scope and separately checks `k=2` composition.

## Direct result

**VERIFIED.** An independently enumerated finite-support mechanism agreed with
the theorem formula in 30/30 exact rational add/remove checks. Six `k=2` scope
checks passed. A mutation of the formula was rejected in 30/30 cases.

This is a test of the closed-form reduction itself, not the previous proxy
“allocation amplifies privacy.”

- [Evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/EVAL.md)
- [Contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/claim_contract.json)
- [Raw results](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/raw_results.csv)
- [Independent checker](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/independent_checker.json)
- [Negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_1/negative_control.json)
