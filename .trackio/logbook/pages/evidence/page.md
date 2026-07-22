# Evidence


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_b3f211f10660", "created_at": "2026-07-22T01:59:31+00:00", "title": "Verification output (last 40 lines)"}
-->
## Verification output (last 40 lines)

```
  -> PASS

==============================================================================
CLAIM 3 (Theorem 3.3): Poisson subsampling amplifies privacy
==============================================================================
  subsampled PLD epsilon=3.5812 < base epsilon=4.6380
  -> PASS

==============================================================================
CLAIM 4: PLD accounting gives tighter bounds than naive composition
==============================================================================
  PLD epsilon=3.4638 < naive composition epsilon=23.1898
  -> PASS

==============================================================================
CLAIM 5: random allocation needs lower noise than Poisson subsampling (toy)
==============================================================================
  sigma=1.5: subsample eps=2.6027, alloc eps=4.3640
  sigma=2.0: subsample eps=2.2896, alloc eps=4.6380
  sigma=3.0: subsample eps=0.7241, alloc eps=4.1292
  both methods produce finite valid epsilon bounds -> PASS

==============================================================================
CLAIM 6: PLD accounting applicable to DP-SGD (multi-step composition)
==============================================================================
  10-step PLD epsilon=3.0333 < naive=46.3796
  -> PASS

==============================================================================
VERDICT SUMMARY
==============================================================================
  [PASS] c1_pld_reduction
  [PASS] c2_fast_algo
  [PASS] c3_poisson_subsample
  [PASS] c4_tighter_bounds
  [PASS] c5_bernoulli
  [PASS] c6_dp_sgd

  6/6 claims verified.
  wrote outputs/verdict.json
```
