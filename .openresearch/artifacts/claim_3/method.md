# Method

For the same three rational mechanisms and four exact rational sampling rates,
construct `(P_lambda,Q)` directly and independently transform grouped base
likelihood-ratio PMFs according to Theorem 3.3. Compare exact `Fraction` PMFs in
both directions, test the theorem's support bounds, and test
`E[exp(-L)] <= 1`.

For the unified-framework check, first build the exact `t=3` random-allocation
pair `(Pbar_3,Q^3)`, then apply subsampling both directly and through the PLD
transformation. The negative control uses an incorrect affine ratio map and
must disagree.
