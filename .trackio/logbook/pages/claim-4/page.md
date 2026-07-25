# Claim 4 — numerical comparisons

## Source scope

The released Figure-1 sweep uses `t ∈ {10,100,1000}`, not `t=10000`.
Figure 2 contains distinct Monte Carlo and Chua deterministic lower-bound
curves. The contract preserves that distinction and uses `δ=10⁻⁶`.

## Direct result

**VERIFIED.** The run evaluated all 20 Figure-1 and 80 Figure-2 points.
The median improvement over the paper-formula RDP bound is **83.03%**.
All 80 Chua points resolve with median absolute `log10` gap `0.00484`.
Forty-four Monte Carlo points are statistically resolved under simultaneous
confidence bounds, with median `log10` gap `0.01359`; unresolved tails remain
unresolved rather than being converted into passes. Independent and negative
controls pass.

- [Evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/EVAL.md)
- [Figure 1 data](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/figure_1_comparison.csv)
- [Figure 2 data](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/figure_2_profiles.csv)
- [Independent checker](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/independent_checker.json)
- [Limitations](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_4/limitations.md)
