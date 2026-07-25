# Claim 6 — PREAMBLE / DP-SGD

## Direct result

**VERIFIED** at the full released parameters: `n=600,000`, `d=2²⁰`,
communication budget `C=2¹⁵`, ten epochs, `δ=10⁻⁶`, four batch sizes, and ten
block sizes. At global `σ=1`, PLD accounting is tighter than the independent
paper-formula RDP calculation at **40/40** grid points:

- minimum epsilon improvement: **5.99%**
- median epsilon improvement: **26.55%**
- maximum epsilon improvement: **56.59%**

At the conservative RDP-failing endpoint `σ=1.802490234375`, RDP gives
`ε=1.029195098` and PLD gives `ε=0.272299981`. Together with the verified
monotone bracket, this certifies a strict required-noise advantage.

Four long grid source runs ended after emitting their complete grid panels.
The collector does not relabel them successful: it hash-binds the complete
pre-terminal rows and separately requires the successful anchor run
`fe365c41-6a04-4ae0-8cfc-b5b3e1c2e7ef`. Provenance, domain, parameter
identities, independent computation, anchor, and negative control all pass.

- [Evaluation](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/EVAL.md)
- [Full grid](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/full_grid.csv)
- [Provenance](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/provenance.json)
- [Independent checker](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/independent_checker.json)
- [Anchor log](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/release/claim6_anchor_run.log)
- [Limitations](https://huggingface.co/spaces/DineshAI/HDBpda5Vih/blob/main/evidence/claim_6/limitations.md)
