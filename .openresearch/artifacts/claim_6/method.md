# Method

Four CPU-upgrade runs evaluated disjoint ten-point panels using the pinned
author PLD implementation. Their evidence-bearing stdout lines are preserved
with immutable run IDs, commits, complete-log hashes, byte counts, and exact
excerpt hashes. Two runs failed only after all ten points in a superseded
optional root search; two were deliberately cancelled at that same boundary.
The collector never labels those runs successful and accepts only their
complete pre-terminal grid lines.

The collector reconstructs the exact 40-point domain and independently
recomputes every RDP epsilon using a separate loop-based implementation of the
paper formulas. A fifth run brackets the RDP epsilon=1 noise root and performs
one full PLD evaluation on the RDP-failing side. PLD epsilon below one there
proves by monotonicity that PLD needs strictly less noise.
