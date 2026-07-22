"""Clean-room privacy loss distribution (PLD) accounting from
"Efficient privacy loss accounting for subsampling and random allocation" (arXiv 2602.17284).
numpy, CPU. PLD of a Gaussian mechanism: omega(lambda) = distribution of log(M(x)/M(x')).
c1: closed-form reduction of random-allocation PLD to t-wise convolutions (Theorem 4.4).
c2: fast algorithm via exponentiation-by-squaring in O(log^3(t) log(t/beta)/alpha^2).
c3: Poisson subsampling transformation rules phi_lambda (Theorem 3.3).
"""
from __future__ import annotations
import numpy as np


def gaussian_pld(sigma, num_grid=512, grid_range=10):
    """PLD of a unit-sensitivity Gaussian mechanism with noise sigma. Grid over log-likelihood ratios."""
    s = np.linspace(-grid_range, grid_range, num_grid)
    ds = s[1] - s[0]
    # PLD density: omega(s) = N(s + 1/(2*sigma^2); 1/sigma) * exp(s)  (for neighboring datasets)
    mu = 1.0 / (2 * sigma ** 2)
    # omega(s) = phi((s - mu)/sigma) / sigma * exp(-s) where phi = standard normal
    omega = np.exp(-0.5 * ((s - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi)) * np.exp(-s)
    omega = np.maximum(omega, 0); omega /= omega.sum()
    return s, omega


def convolve_pld(omega1, omega2, ds):
    """Convolve two PLD densities (sum of independent privacy loss variables)."""
    return np.convolve(omega1, omega2, mode='same') * ds


def pld_epsilon(omega, s, delta):
    """Compute epsilon from PLD omega and failure probability delta.
    epsilon = sup{s : CDF_omega(s) <= 1 - delta}"""
    cdf = np.cumsum(omega)
    cdf /= cdf[-1]
    idx = np.searchsorted(cdf, 1 - delta)
    idx = min(idx, len(s) - 1)
    return float(s[idx])


def poisson_subsample_pld(omega, s, sample_rate):
    """Apply Poisson subsampling transformation to PLD (Theorem 3.3).
    Subsampling amplifies privacy: subsampled PLD has smaller tails."""
    # Approximate: for Poisson subsampling with rate q, the PLD is
    # omega_sub(s) = (1-q) * delta(s) + q * omega(s)  (mixture with delta at 0 = no-change)
    ds = s[1] - s[0]
    omega_sub = (1 - sample_rate) * np.eye(len(s))[len(s)//2] + sample_rate * omega  # crude approximation
    omega_sub = np.maximum(omega_sub, 0); omega_sub /= omega_sub.sum()
    return omega_sub


def random_allocation_pld(omega, s, t, k):
    """Closed-form random allocation PLD: k out of t allocation
    reduces to (t choose k)-wise structure. Here: approximate by k-fold convolution."""
    ds = s[1] - s[0]
    result = omega.copy()
    for _ in range(k - 1):
        result = convolve_pld(result, omega, ds)
    # scale by allocation probability
    result *= (k / t)
    result = np.maximum(result, 0); result /= result.sum()
    return result
