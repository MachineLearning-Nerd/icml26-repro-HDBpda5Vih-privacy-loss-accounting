# Claim 1 source audit

Theorem 4.4 is `body.tex` label `thm:PLDrandAlloc`, lines 214–227 of the
retrieved v2 source. It quantifies over every positive integer `t` and every PLD
realization. It gives separate remove and add identities as logarithms of
averages/sums of independent exponentiated PLD and dual-PLD terms.

The judge wording says “k-out-of-t”, but the theorem itself is explicitly the
1-out-of-t identity. General `k` is treated by Lemma 2.8. The verifier preserves
this distinction and also checks the exact elementary-symmetric likelihood-ratio
identity for small `k=2` instances without attributing that extension to
Theorem 4.4.
