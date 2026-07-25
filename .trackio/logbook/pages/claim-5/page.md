# Claim 5 — Bernoulli mean estimation

## Direct result

**VERIFIED** at the released scale: `t=1000`, `p=0.9`, `δ=10⁻¹⁰`, the full
seven-point sample-size sweep, and the three `(ε,d)` panels. Required Gaussian
noise was:

| `(ε,d)` | Allocation `σ` | Poisson `σ` | Allocation reduction |
| --- | ---: | ---: | ---: |
| `(1,1)` | 0.889941 | 0.891829 | 0.21% |
| `(0.1,1)` | 1.865726 | 1.938765 | 3.77% |
| `(0.1,1000)` | 1.865726 | 1.938765 | 3.77% |

Both numerical resolutions preserve the strict ordering. Exact variance
decomposition and deterministic seeded Monte Carlo with 10,000 replicates per
panel agree. The mutation removing the allocation advantage is rejected.

- [Evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/EVAL.md)
- [Privacy roots](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/privacy_noise.csv)
- [Utility sweep](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/utility_mse.csv)
- [Independent checker](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/independent_checker.json)
- [Limitations](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_5/limitations.md)
