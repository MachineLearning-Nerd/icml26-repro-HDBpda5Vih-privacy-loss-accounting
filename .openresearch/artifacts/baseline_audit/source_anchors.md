# Paper source audit anchors

Source: arXiv `2602.17284v2`, retrieved 2026-07-23 with the explicit user agent
recorded in `startup_audit.json`.

- Definition 3.1 (`body.tex`, label `def:PLDreal`, lines 133–137): a PLD
  realization satisfies \(\mathbb{E}[e^{-L}]\leq 1\) and has no mass at
  \(-\infty\); it also defines the dual.
- Theorem 3.3 (`body.tex`, label `thm:PLD_subsam`, lines 155–171): for every
  \(\lambda\in(0,1]\) and every PLD realization, gives the remove and add
  transformations using
  \(\phi_\lambda(l)=\ln(1+(e^l-1)/\lambda)\), their support restrictions, and
  exact identities for \(L_{P_\lambda,Q}\) and \(L_{Q,P_\lambda}\).
- Theorem 4.4 (`body.tex`, label `thm:PLDrandAlloc`, lines 214–227): for every
  \(t\in\mathbb{N}\) and every PLD realization, gives exact remove and add
  identities for **1-out-of-\(t\)** random allocation as logarithms of sums of
  independent exponentiated PLD/dual terms. General \(k\) is handled separately
  by Lemma 2.8.
- Theorem 4.6 (`body.tex`, label `thm:num_acc_RA`, lines 266–280): for
  \(\alpha>0\), \(\beta\in[0,1]\), and \(t\in\mathbb{N}\), returns valid,
  \((\alpha,\beta)\)-tight dominating PLD realizations in
  \(O((\mathrm{IQR}_{\beta/t}/\alpha)^2\log^3 t)\). The paper then specializes
  the Gaussian runtime to
  \(O(\log_2^3(t)\ln(t/\beta)/(\sigma^2\alpha^2))\).
- Section 5 (`body.tex`, label `sec:numRes`, lines 292–377): numerical privacy
  profiles, PREAMBLE, runtime, and Bernoulli utility experiments.
- Figure 2 source (`body.tex`, label `fig:delta_comparison_partial`, lines
  307–317; Appendix lines 513–524): comparison with Chua et al. lower and
  Monte Carlo estimates; Appendix specifies \(10^6\) importance samples and
  95% confidence.
- Figure 3 source (`body.tex`, label `fig:PREAMBLE`, lines 321–337):
  \(n=6\cdot10^5\), \(d=2^{20}\), \(C=2^{15}\), \(E=10\),
  \((\varepsilon,\delta)=(1,10^{-6})\), with \(10^6\) bins in each direction.
- Figure 4 source (`body.tex`, label `fig:utility_comparison`, lines 356–373):
  Bernoulli mean estimation with \(p=0.9\), \(t=n=10^3\), and
  \(\delta=10^{-10}\).

The judge paraphrases are preserved as evaluation targets, but the contracts
must not erase two source-level qualifications: Theorem 4.4 itself is a
1-out-of-\(t\) identity, and Theorem 4.6's general complexity includes the IQR
factor (with the stated log form only after Gaussian specialization).
