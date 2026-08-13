# Branch audit and cleanup map

This repository grew from an OpenResearch experiment tree. Before cleanup,
the default branch was `master` and all experiment branches used the `orx/`
namespace. The mapping below keeps every branch, including divergent shard
and judge-facing lines, while giving each one a readable public name.

Tip hashes are the pre-cleanup remote hashes. Commit identity normalization will
change commit IDs while preserving the branch histories and their contents.
`ancestor-of-master` means the branch tip is already contained in the old
publication branch; `divergent` means it remains an independent line.

| Previous branch | Clean branch | Pre-cleanup tip | Relationship | Role |
| --- | --- | --- | --- | --- |
| `master` | `main` | `a12dfff0c44be583747d48459e9186385469cbda` | publication surface | Current README, report, logbook, and release artifacts. |
| `orx/active-judge-tree-without-proxy-ambiguity` | `audit/active-judge-tree` | `6256e692ec4c4236790dbaeb651bfd588a68ca2d` | divergent | Judge-facing active tree that removes proxy ambiguity. |
| `orx/batch-shard-capable-preamble-runner` | `research/preamble-batch-shards` | `d2b4bdd1bac546f2a021e531a52ae35406595720` | ancestor-of-master | General Claim 6 batch-sharding runner. |
| `orx/confidence-consistent-figure-2-gate` | `research/figure-2-confidence-gate` | `cdd718aaa2c867f5e9517b87574f722f92f80065` | ancestor-of-master | Claim 4 confidence-consistency gate. |
| `orx/cumulative-claims-1-3-verifier` | `research/cumulative-claims-1-3` | `12431c264834e161bc7f069b94933b2107fe541f` | ancestor-of-master | Integrates Claims 1–3 contracts. |
| `orx/cumulative-claims-1-6-collector` | `research/cumulative-claims-1-6-collector` | `771d60323d098d1d66e6c1504d2f58e85acf6462` | ancestor-of-master | Collects all-claim evidence and binds Claim 6 provenance. |
| `orx/cumulative-claims-1-6-release-gate` | `release/privacy-loss-cumulative-gate` | `1eb57c864b5280952dbe86739fe4b869f69d10b4` | ancestor-of-master | Cumulative release gate and full-run status. |
| `orx/exact-figure-2-allocation-comparison` | `research/figure-2-allocation-comparison` | `30525b70770ae42cf620b65393cdd5972821e61b` | ancestor-of-master | Exact Claim 4 Figure 2 comparison. |
| `orx/exact-finite-support-theorem-contracts` | `research/exact-finite-support-theorems` | `7171c232e81992c2b91598106e8fc7420da70fd2` | ancestor-of-master | Exact Claims 1 and 3 theorem contracts. |
| `orx/frozen-judged-baseline` | `research/frozen-judged-baseline` | `f97be12ea0f7107e848fb58f942b05b3b3e8f553` | ancestor-of-master | Frozen judged baseline, environment, and startup audit. |
| `orx/full-bernoulli-utility-contract` | `research/bernoulli-utility-contract` | `c3df159ec9a5137468a702a91e744273ddddf633` | ancestor-of-master | Full Claim 5 privacy and utility contract. |
| `orx/full-preamble-accounting-contract` | `research/preamble-accounting-contract` | `f1f9602948f11803d51badd2844d34b008146ce3` | ancestor-of-master | Full Claim 6 accounting contract. |
| `orx/judge-aligned-self-contained-release` | `release/judge-aligned-self-contained` | `eb1c5a4432cd911b52fc5113e5964e25087e59bf` | divergent | Self-contained judge-aligned release candidate. |
| `orx/numerical-bounds-versus-lower-and-rdp` | `research/numerical-bounds-vs-rdp` | `f6f97ed978142e6882a8897de788fd57254fe844` | ancestor-of-master | Claim 4 numerical lower-bound and RDP comparison. |
| `orx/parallel-full-preamble-contract` | `research/parallel-preamble-contract` | `6251aad6675f38cf66c70a503f47e8e707790906` | ancestor-of-master | Parallel full-grid Claim 6 contract. |
| `orx/preamble-batch-512-shard` | `research/preamble-batch-512` | `f72e5377e6dcfea862c3d9ea50f78a85886cfdee` | ancestor-of-master | Claim 6 batch-size-512 shard. |
| `orx/preamble-batch-1028-shard` | `research/preamble-batch-1028` | `955357b7683ad0dbc0b118c28a2896f8ea585e1a` | divergent | Claim 6 batch-size-1028 shard. |
| `orx/preamble-batch-4096-shard` | `research/preamble-batch-4096` | `6f5a5af00841af3292ab8c5d2b16c09522760a27` | divergent | Claim 6 batch-size-4096 shard. |
| `orx/preamble-batch-600000-shard` | `research/preamble-batch-600000` | `5cf09b8e65bfb0e5d7c66aad5338af7847ddf48d` | ancestor-of-master | Claim 6 batch-size-600000 shard. |
| `orx/precision-stable-bernoulli-privacy-gate` | `research/bernoulli-precision-gate` | `2c82658559471076202e0be6993afb038b3d4193` | ancestor-of-master | Precision-stable Claim 5 privacy gate. |
| `orx/published-reproduction-release` | `release/published-reproduction` | `39c1dde9bc2332576c202eeb69574eb6186b7244` | ancestor-of-master | First published claim-by-claim release. |
| `orx/released-geometric-algorithm-contracts` | `research/geometric-algorithm-contracts` | `0678c73b870471f3dd5ec1937c70b43935ba4c27` | ancestor-of-master | Released Claim 2 algorithm contract. |
| `orx/stable-preamble-anchor-certificate` | `research/preamble-anchor-certificate` | `6aa326b9b78a3d837ed21384b9e3994f6239ba5b` | ancestor-of-master | Stable Claim 6 required-noise anchor. |
| `orx/unambiguous-current-run-provenance` | `audit/unambiguous-run-provenance` | `fce5c732f2757b998842649eaa3cda92ca08ed93` | divergent | Latest direct-evidence run and provenance audit. |

## Rename policy

The target repository is
[MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting](https://github.com/MachineLearning-Nerd/icml26-efficient-privacy-loss-accounting).
The old names are replaced only after this mapping is committed. Remote
verification must show `main` as default and all 24 mapped branches under their
clean names.
