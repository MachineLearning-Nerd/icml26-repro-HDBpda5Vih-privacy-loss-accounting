# Method

For three strictly positive rational pairs `(P,Q)` (two binary, one ternary),
enumerate every outcome of the product space for `t=1..5`. One implementation
constructs `Pbar_t` and `Q^t` directly. A separately written implementation
constructs the likelihood-ratio random variables from the theorem while fixing
the P-drawn coordinate by symmetry. PMFs are dictionaries keyed by exact
`Fraction` likelihood ratios; equality is exact before applying the injective
log transform.

The negative control changes the theorem's denominator from `t` to `t+1` and
must disagree with direct enumeration. A separate `k=2` checker compares direct
subset-mixture enumeration with an elementary-symmetric-polynomial calculation.
