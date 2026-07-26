"""Exact OpenResearch claim strings used by the live judge."""

from __future__ import annotations


REGISTERED_CLAIMS = (
    (
        "Theorem 4.4 gives a closed-form reduction of the privacy loss "
        "distribution (PLD) of k-out-of-t random allocation to t-wise "
        "convolutions of exponentiated PLD terms (Section 4, Theorem 4.4)."
    ),
    (
        "The proposed algorithm computes an (α,β)-accurate approximation of "
        "the random allocation PLD in time "
        "O(log³(t)·log(t/β)/α²), using exponentiation-by-squaring with "
        "geometric-grid rounding (Section 4, Theorem 4.6)."
    ),
    (
        "Theorem 3.3 introduces transformation rules φ_λ that apply Poisson "
        "subsampling directly to PLD realizations, allowing subsampling and "
        "random allocation to be composed within one unified PLD framework "
        "(Section 3, Theorem 3.3, Definition 3.1)."
    ),
    (
        "Numerical experiments show the new random allocation privacy bounds "
        "are nearly identical to the Monte Carlo lower bounds of Chua et al. "
        "(2024a) and substantially tighter than RDP-based analytic bounds, "
        "for t ∈ {1000, 10000} and δ = 10⁻⁶ "
        "(Section 5, Figures 1-2)."
    ),
    (
        "A toy Bernoulli mean-estimation experiment (n=10³, δ=10⁻¹⁰) shows "
        "random allocation requires strictly lower noise than Poisson "
        "subsampling for the same privacy level, demonstrating a genuine "
        "privacy (not just variance) advantage (Section 5, Figure 4)."
    ),
    (
        "Applied to a DP-SGD scenario with block-sparse coordinate sampling "
        "(n=6×10⁵, d=2²⁰, C=2¹⁵, E=10 epochs), the PLD accounting method "
        "improves privacy bounds over RDP composition even under heavy "
        "composition (Section 5, Figure 5)."
    ),
)

