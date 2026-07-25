# Claim 2 — geometric-grid algorithm

## Source scope

Theorem 4.6's general runtime contains the PLD interquartile-range factor, and
the Gaussian specialization contains `σ⁻²`. The verifier uses these corrected
quantifiers rather than the shortened imported statement.

## Direct result

**VERIFIED.** Seventeen fast-versus-exact cases use the same `(t, α, β)`
contract, and six cases exercise the pinned released Gaussian API. The
implementation path explicitly checks exponentiation by squaring and geometric
rounding. Primitive-work fits scale as `log(t)^2.487` and `α^-1.984`; the latter
matches the quadratic dependence. Four deliberate mutations are rejected.

The finite sweep is consistency evidence for the asymptotic upper bound, not a
claim that timing data proves big-O.

- [Evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/EVAL.md)
- [Contract](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/claim_contract.json)
- [Complexity data](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/complexity_raw.csv)
- [Released API cases](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/released_gaussian_accuracy.csv)
- [Negative control](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_2/negative_control.json)
