"""Source-faithful Figure 1 and Figure 2 numerical comparisons."""

from __future__ import annotations

import json
import math
import time
from typing import Any

import numpy as np
from PLD_accounting import (
    AllocationSchemeConfig,
    BoundType,
    ConvolutionMethod,
    PrivacyParams,
    gaussian_allocation_epsilon_configurable,
    gaussian_allocation_pld,
)
from scipy import optimize, special, stats

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    write_csv,
    write_json,
    write_text,
)


DELTA = 1e-6
T_VALUES = (1_000, 10_000)
SIGMAS = np.linspace(1.0, 4.0, 10)
ORDERS = np.arange(2, 61, dtype=int)
PROFILE_SETTINGS = (
    (35_938, 0.3, "Criteo pCTR, batch 1024"),
    (4_492, 0.4, "Criteo pCTR, batch 8192"),
    (12_500, 0.3, "Criteo Search, batch 1024"),
    (1_563, 0.4, "Criteo Search, batch 8192"),
)
PROFILE_EPSILONS = np.linspace(0.1, 8.0, 20)
PROFILE_TAIL = 1e-12
MC_SAMPLE_SIZE = 500_000
MC_SEED = 260217284
MC_BATCH_SIZE = 2_000
MC_FAMILY_ERROR_PROBABILITY = 0.01
CONFIG = AllocationSchemeConfig(
    loss_discretization=0.01,
    tail_truncation=DELTA * 0.01,
    max_grid_mult=50_000,
    convolution_method=ConvolutionMethod.GEOM,
)
PROFILE_CONFIG = AllocationSchemeConfig(
    loss_discretization=0.1,
    tail_truncation=PROFILE_TAIL,
    max_grid_mult=50_000,
    convolution_method=ConvolutionMethod.GEOM,
)


def log_poly_convolve(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    degree = len(left) - 1
    output = np.full(degree + 1, -np.inf)
    for total in range(degree + 1):
        values = left[: total + 1] + right[total::-1]
        output[total] = special.logsumexp(values)
    return output


def log_sum_moments(t: int, sigma: float, max_order: int) -> np.ndarray:
    """Log E[(sum_i Y_i)^a], with Gaussian likelihood ratios Y_i."""
    indices = np.arange(max_order + 1, dtype=float)
    base = (
        indices * (indices - 1) / (2 * sigma**2)
        - special.gammaln(indices + 1)
    )
    result = np.full(max_order + 1, -np.inf)
    result[0] = 0.0
    exponent = t
    while exponent:
        if exponent & 1:
            result = log_poly_convolve(result, base)
        exponent >>= 1
        if exponent:
            base = log_poly_convolve(base, base)
    return (
        special.gammaln(indices + 1)
        + result
        - indices * math.log(t)
    )


def allocation_rdp(t: int, sigma: float) -> tuple[np.ndarray, dict[str, float]]:
    log_moments = log_sum_moments(t, sigma, int(ORDERS[-1]))
    remove = np.array(
        [log_moments[order] / (order - 1) for order in ORDERS]
    )
    add = np.array(
        [
            order / (2 * sigma**2 * t)
            + order * (t - 1) / (2 * sigma**2 * t * (order - 1))
            - t
            * math.log1p(
                order
                * math.expm1((t - 1) / (sigma**2 * t**2))
            )
            / (2 * (order - 1))
            for order in ORDERS
        ]
    )
    rdp = np.maximum(remove, add)
    converted = (
        rdp
        - (math.log(DELTA) + np.log(ORDERS)) / (ORDERS - 1)
        + np.log((ORDERS - 1) / ORDERS)
    )
    best = int(np.argmin(converted))
    alpha2_closed = math.log1p(math.expm1(1 / sigma**2) / t)
    diagnostics = {
        "optimal_order": int(ORDERS[best]),
        "remove_rdp_alpha2": float(remove[0]),
        "alpha2_closed_form": alpha2_closed,
        "alpha2_abs_error": abs(float(remove[0]) - alpha2_closed),
    }
    return converted, diagnostics


def stable_max_tail_probability(
    threshold: float, t: int, sigma: float, shifted: bool
) -> float:
    base_logcdf = stats.norm.logcdf(threshold / sigma)
    if shifted:
        log_all_below = (
            stats.norm.logcdf((threshold - 1) / sigma)
            + (t - 1) * base_logcdf
        )
    else:
        log_all_below = t * base_logcdf
    return float(-math.expm1(min(log_all_below, 0.0)))


def chua_lower_delta(
    epsilon: float, t: int, sigma: float
) -> tuple[float, float, float]:
    """Equation (6) lower bound, optimized over the threshold C."""

    def value(threshold: float) -> float:
        p_tail = stable_max_tail_probability(
            threshold, t, sigma, shifted=True
        )
        q_tail = stable_max_tail_probability(
            threshold, t, sigma, shifted=False
        )
        return p_tail - math.exp(epsilon) * q_tail

    grid = np.linspace(-4 * sigma, 1 + 10 * sigma, 601)
    grid_values = np.array([value(float(point)) for point in grid])
    best_index = int(np.argmax(grid_values))
    left = float(grid[max(0, best_index - 1)])
    right = float(grid[min(len(grid) - 1, best_index + 1)])
    refined = optimize.minimize_scalar(
        lambda threshold: -value(float(threshold)),
        bounds=(left, right),
        method="bounded",
        options={"xatol": 1e-12},
    )
    refined_value = max(0.0, -float(refined.fun))
    grid_value = max(0.0, float(grid_values[best_index]))
    return (
        max(refined_value, grid_value),
        float(refined.x),
        grid_value,
    )


def chua_lower_epsilon(t: int, sigma: float) -> dict[str, float]:
    left, right = 0.0, 20.0
    if chua_lower_delta(left, t, sigma)[0] <= DELTA:
        return {
            "epsilon": 0.0,
            "threshold": chua_lower_delta(left, t, sigma)[1],
            "delta": chua_lower_delta(left, t, sigma)[0],
            "grid_delta": chua_lower_delta(left, t, sigma)[2],
        }
    for _ in range(40):
        midpoint = (left + right) / 2
        if chua_lower_delta(midpoint, t, sigma)[0] > DELTA:
            left = midpoint
        else:
            right = midpoint
    delta_value, threshold, grid_value = chua_lower_delta(left, t, sigma)
    return {
        "epsilon": left,
        "threshold": threshold,
        "delta": delta_value,
        "grid_delta": grid_value,
    }


def pld_epsilon(t: int, sigma: float, bound: BoundType) -> float:
    return gaussian_allocation_epsilon_configurable(
        PrivacyParams(
            sigma=sigma,
            num_steps=t,
            num_selected=1,
            num_epochs=1,
            delta=DELTA,
        ),
        CONFIG,
        bound_type=bound,
    )


def profile_order_statistics(t: int) -> np.ndarray:
    """Order indices used by Chua et al. for the four Criteo profiles."""
    if t == 35_938:
        segments = (
            np.arange(1, 501),
            np.arange(510, 1_001, 10),
            np.arange(1_100, 19_901, 100),
        )
    elif t == 4_492:
        segments = (
            np.arange(1, 501),
            np.arange(510, 1_001, 10),
            np.arange(1_050, 2_951, 50),
        )
    elif t == 12_500:
        segments = (
            np.arange(1, 501),
            np.arange(510, 1_001, 10),
            np.arange(1_100, 6_901, 100),
        )
    elif t == 1_563:
        segments = (np.arange(1, 501), np.arange(510, 991, 10))
    else:
        raise ValueError(f"no preregistered order-statistics grid for t={t}")
    orders = np.concatenate(segments).astype(int)
    if orders[0] != 1 or orders[-1] >= t or np.any(np.diff(orders) <= 0):
        raise AssertionError(f"invalid order-statistics grid for t={t}")
    return orders


def sample_uniform_order_statistics(
    rng: np.random.Generator,
    dimension: int,
    orders: np.ndarray,
    sample_size: int,
) -> np.ndarray:
    """Algorithm 6 joint order-statistics sampler of Chua et al."""
    first = np.insert(orders, 0, 0)
    beta_a = dimension - orders + 1
    beta_b = np.diff(first)
    factors = rng.beta(
        beta_a,
        beta_b,
        size=(sample_size, len(orders)),
    )
    return np.exp(np.cumsum(np.log(factors), axis=1))


def sample_order_statistic_losses(
    rng: np.random.Generator,
    t: int,
    sigma: float,
    orders: np.ndarray,
    adjacency: str,
) -> np.ndarray:
    """Sample the primary implementation's pessimistic PLD envelope."""
    losses: list[np.ndarray] = []
    for first in range(0, MC_SAMPLE_SIZE, MC_BATCH_SIZE):
        batch = min(MC_BATCH_SIZE, MC_SAMPLE_SIZE - first)
        if adjacency == "remove":
            uniforms = sample_uniform_order_statistics(
                rng, t - 1, orders, batch
            )
            ranked = stats.norm.ppf(uniforms, scale=sigma)
            first_coordinate = rng.normal(
                loc=1.0, scale=sigma, size=(batch, 1)
            )
            values = np.concatenate((first_coordinate, ranked), axis=1)
            weights = np.insert(np.diff(np.append(orders, t)), 0, 1)
            sign = 1.0
        elif adjacency == "add":
            uniforms = sample_uniform_order_statistics(rng, t, orders, batch)
            values = stats.norm.ppf(uniforms, scale=sigma)
            weights = np.diff(np.insert(orders, 0, 0))
            sign = -1.0
        else:
            raise ValueError(f"invalid adjacency: {adjacency}")
        approximate_loss = (
            special.logsumexp(
                values / sigma**2,
                axis=1,
                b=weights,
            )
            - math.log(t)
            - 1 / (2 * sigma**2)
        )
        losses.append(sign * approximate_loss)
    return np.concatenate(losses)


def bernoulli_kl(q: float, p: float) -> float:
    """KL(Ber(q) || Ber(p)), including endpoint cases."""
    if q <= 0:
        return -math.log1p(-p)
    if q >= 1:
        return -math.log(p)
    return q * math.log(q / p) + (1 - q) * math.log(
        (1 - q) / (1 - p)
    )


def kl_upper_confidence_bound(
    mean: float,
    sample_size: int,
    error_probability: float,
) -> float:
    """Primary estimator's bounded-variable Chernoff/KL upper bound."""
    if mean >= 1:
        return 1.0
    target = -math.log(error_probability) / sample_size
    if mean <= 0:
        return 1 - math.exp(-target)
    return float(
        optimize.brentq(
            lambda candidate: bernoulli_kl(mean, candidate) - target,
            mean,
            1 - np.finfo(float).eps,
        )
    )


def monte_carlo_profile(
    rng: np.random.Generator,
    t: int,
    sigma: float,
    orders: np.ndarray,
) -> list[dict[str, float]]:
    """Evaluate all epsilon values from one reusable loss sample per direction."""
    remove_losses = sample_order_statistic_losses(
        rng, t, sigma, orders, "remove"
    )
    add_losses = sample_order_statistic_losses(rng, t, sigma, orders, "add")
    family_size = len(PROFILE_SETTINGS) * len(PROFILE_EPSILONS) * 2
    point_error = MC_FAMILY_ERROR_PROBABILITY / family_size
    rows: list[dict[str, float]] = []
    for epsilon in PROFILE_EPSILONS:
        remove_values = np.maximum(
            0.0, -np.expm1(float(epsilon) - remove_losses)
        )
        add_values = np.maximum(0.0, -np.expm1(float(epsilon) - add_losses))
        remove_mean = float(np.mean(remove_values))
        add_mean = float(np.mean(add_values))
        remove_se = float(np.std(remove_values, ddof=1) / math.sqrt(len(remove_values)))
        add_se = float(np.std(add_values, ddof=1) / math.sqrt(len(add_values)))
        remove_upper = kl_upper_confidence_bound(
            remove_mean, MC_SAMPLE_SIZE, point_error
        )
        add_upper = kl_upper_confidence_bound(
            add_mean, MC_SAMPLE_SIZE, point_error
        )
        rows.append(
            {
                "epsilon": float(epsilon),
                "mc_remove_mean": remove_mean,
                "mc_add_mean": add_mean,
                "mc_mean": max(remove_mean, add_mean),
                "mc_remove_standard_error": remove_se,
                "mc_add_standard_error": add_se,
                "mc_simultaneous_upper": max(remove_upper, add_upper),
                "mc_point_error_probability": point_error,
            }
        )
    return rows


def figure_2_profiles() -> list[dict[str, Any]]:
    """Compute exact paper profiles and the independent stochastic check."""
    rng = np.random.default_rng(MC_SEED)
    rows: list[dict[str, Any]] = []
    for t, sigma, label in PROFILE_SETTINGS:
        params = PrivacyParams(
            sigma=sigma,
            num_steps=t,
            num_selected=1,
            num_epochs=1,
        )
        upper_pld = gaussian_allocation_pld(
            params, PROFILE_CONFIG, BoundType.DOMINATES
        )
        lower_pld = gaussian_allocation_pld(
            params, PROFILE_CONFIG, BoundType.IS_DOMINATED
        )
        orders = profile_order_statistics(t)
        mc_rows = monte_carlo_profile(rng, t, sigma, orders)
        for mc_row in mc_rows:
            epsilon = mc_row["epsilon"]
            upper = float(upper_pld.get_delta_for_epsilon(epsilon))
            lower = float(lower_pld.get_delta_for_epsilon(epsilon))
            chua, threshold, grid_chua = chua_lower_delta(epsilon, t, sigma)
            stable = (
                chua >= 1e-10
                and mc_row["mc_mean"] >= 200 / MC_SAMPLE_SIZE
            )
            row: dict[str, Any] = {
                "profile": label,
                "t": t,
                "sigma": sigma,
                "epsilon": epsilon,
                "pld_delta_upper": upper,
                "pld_delta_lower": lower,
                "chua_lower_delta": chua,
                "chua_threshold": threshold,
                "chua_grid_delta": grid_chua,
                "stable_monte_carlo": stable,
                "order_statistics": len(orders),
                "log10_pld_chua_gap": (
                    math.log10(upper) - math.log10(chua)
                    if upper > 0 and chua > 0
                    else math.inf
                ),
                **mc_row,
            }
            row["log10_pld_mc_gap"] = (
                abs(math.log10(upper) - math.log10(row["mc_mean"]))
                if stable and upper > 0
                else math.nan
            )
            rows.append(row)
    return rows


def write_bundle(
    figure_1_rows: list[dict[str, Any]],
    figure_2_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    runtime: float,
) -> None:
    out = ARTIFACTS / "claim_4"
    write_json(
        out / "claim_contract.json",
        {
            "claim_id": 4,
            "source_statement": (
                "Figure 1 compares PLD upper/lower epsilon with FS25/DCO25 "
                "analytic bounds for t in {10,100,1000}, sigma in [1,4], "
                "delta=1e-6. Figure 2 separately compares privacy profiles "
                "with Monte Carlo estimates and the Chua et al. lower bound "
                "at Criteo-derived t values."
            ),
            "figure_1_domain": {
                "t": list(T_VALUES),
                "sigma": [float(value) for value in SIGMAS],
                "delta": DELTA,
            },
            "figure_2_domain": {
                "profiles": [
                    {"t": t, "sigma": sigma, "label": label}
                    for t, sigma, label in PROFILE_SETTINGS
                ],
                "epsilon": [float(value) for value in PROFILE_EPSILONS],
                "monte_carlo_samples_per_direction": MC_SAMPLE_SIZE,
                "seed": MC_SEED,
                "family_confidence": 1 - MC_FAMILY_ERROR_PROBABILITY,
            },
            "verdict_rule": (
                "VERIFIED iff Figure 1 PLD intervals are ordered and <=0.03 "
                "epsilon wide; PLD beats RDP at every point with >=10% median "
                "relative improvement; all Figure 2 PLD intervals contain the "
                "Chua lower bound; on resolved Figure 2 points the median and "
                "90th-percentile PLD/Chua gaps are <=0.15 and <=0.30 log10 "
                "decades; every profile has >=3 statistically stable Monte "
                "Carlo points; each rigorous PLD lower bound lies below its "
                "simultaneous 99% Monte Carlo upper bound and the PLD/MC "
                "median/90th-percentile gaps are <=0.15/0.30 decades; "
                "independent numerical checks and the 10x-lower-bound mutation "
                "test pass."
            ),
        },
    )
    write_text(
        out / "source_audit.md",
        """# Claim 4 source audit

The imported judge claim conflates Figures 1 and 2. `intro.tex` lines 48–55 and
the public historical experiment script at author commit `d49e87d` establish
that Figure 1 uses `t={10,100,1000}`, ten sigma values from 1 to 4, and
`delta=1e-6`; it compares PLD with FS25/DCO25 analytic bounds and Poisson.
`body.tex` lines 307–317 and `appendix.tex` lines 516–524 instead compare full
privacy profiles at Criteo-derived `t={35938,4492,12500,1563}` with Monte Carlo
mean/high-probability estimates and the distinct efficiently computable lower
bound from Chua et al. Equation (6) of arXiv:2412.16802.

There is no `t=10000` panel in the cited paper figure. This contract evaluates
the exact largest Figure 1 panel (`t=1000`) and adds `t=10000` solely to answer
the judge wording. It labels Equation (6) accurately as a deterministic lower
bound, not a “Monte Carlo lower bound.” The exact Figure 2 settings are
`(t,sigma)={(35938,.3),(4492,.4),(12500,.3),(1563,.4)}` with 20 epsilon
values from 0.1 to 8, as recovered from public author commit `d49e87d`.
""",
    )
    write_text(
        out / "method.md",
        """# Method

PLD upper and lower epsilons call the pinned released author implementation.
The independent lower checker implements Chua et al. Equation (6):
`sup_C P(max X_i >= C) - exp(epsilon) Q(max X_i >= C)`. Gaussian independence
makes both probabilities closed form; a dense grid plus bounded refinement
optimizes C, and bisection inverts the profile at delta.

The RDP checker is independent of the PLD code. It calculates the exact
remove-direction integer moments of the average Gaussian likelihood ratio using
truncated exponential-generating-function exponentiation, combines this with
the published DCO add-direction upper bound, and applies the optimal RDP-to-DP
conversion over integer orders 2–60. The order-2 result is checked against a
separate closed form.

The Monte Carlo checker independently implements Algorithms 4 and 6 of Chua
et al. using their published Criteo order-index grids. One joint sample of
500,000 pessimistic privacy-loss envelopes per profile and direction is reused
over all epsilon values. A Bernoulli-KL Chernoff inversion gives simultaneous
99% upper confidence bounds over all 160 directional estimates. Comparisons to
the Monte Carlo mean are made only where at least 200 expected nonzero samples
make the estimate statistically resolved. Confidence consistency requires the
Monte Carlo upper confidence bound to be no smaller than the rigorous PLD lower
bound. It does not compare two upper bounds, whose unrelated numerical slack
need not be ordered.
""",
    )
    write_json(
        out / "raw_results.json",
        {"figure_1": figure_1_rows, "figure_2": figure_2_rows},
    )
    write_csv(
        out / "figure_1_comparison.csv",
        list(figure_1_rows[0]),
        figure_1_rows,
    )
    write_csv(
        out / "figure_2_profiles.csv",
        list(figure_2_rows[0]),
        figure_2_rows,
    )
    write_json(
        out / "independent_checker.json",
        {
            "figure_2_chua_equation_6": [
                {
                    "t": row["t"],
                    "sigma": row["sigma"],
                    "epsilon": row["epsilon"],
                    "threshold": row["chua_threshold"],
                    "delta": row["chua_lower_delta"],
                    "grid_delta": row["chua_grid_delta"],
                }
                for row in figure_2_rows
            ],
            "figure_1_rdp_alpha2": [
                {
                    "t": row["t"],
                    "sigma": row["sigma"],
                    "computed": row["rdp_remove_alpha2"],
                    "closed_form": row["rdp_alpha2_closed_form"],
                    "abs_error": row["rdp_alpha2_abs_error"],
                }
                for row in figure_1_rows
            ],
        },
    )
    write_json(
        out / "negative_control.json",
        {
            "mutation": "multiply every Chua lower-bound delta by 10",
            "rejected": summary["negative_control_ok"],
            "reason": (
                "the mutated lower bound exceeds a rigorous PLD upper bound "
                "on at least one resolved profile point"
            ),
        },
    )
    metadata = runtime_metadata()
    metadata.update(
        {
            "runtime_seconds": runtime,
            "source_experiment_commit": "d49e87d",
            "rdp_orders": [int(value) for value in ORDERS],
            "monte_carlo_seed": MC_SEED,
            "monte_carlo_samples_per_direction": MC_SAMPLE_SIZE,
            "monte_carlo_family_confidence": (
                1 - MC_FAMILY_ERROR_PROBABILITY
            ),
        }
    )
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

This verifier does not relabel a Monte Carlo estimate as a lower bound. The
manuscript says its displayed curves used one million importance samples and
95% confidence, while public author commit `d49e87d` configures 500,000
order-statistics samples and 99% confidence. We reproduce the public executable
configuration and strengthen it to a simultaneous 99% family confidence bound.
Chua et al.'s predecessor full-profile computation used 5e8 samples on 60 CPU
machines; the statistically unresolved tail is excluded by an explicit rule.
The Figure 1 grid is complete for `t=1000`; `t=10000` is a judge-requested
stress test. The smaller paper panels `t=10,100` are not rerun.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 4 evaluation

Verdict: **{'VERIFIED' if summary['passed'] else 'FALSIFIED'}**

- Figure 1 comparison points: {len(figure_1_rows)}
- Figure 2 profile points: {len(figure_2_rows)}
- Stable Monte Carlo points: {summary['stable_monte_carlo_points']}
- Maximum Figure 1 PLD interval width: {summary['max_pld_interval']:.6g}
- Median relative RDP improvement: {summary['median_rdp_improvement']:.2%}
- Figure 2 median/90th-percentile PLD-Chua gap:
  {summary['median_chua_log10_gap']:.6g}/{summary['p90_chua_log10_gap']:.6g}
- Stable median/90th-percentile PLD-MC gap:
  {summary['median_mc_log10_gap']:.6g}/{summary['p90_mc_log10_gap']:.6g}
- Runtime: {runtime:.6f} seconds
""",
    )


def main() -> int:
    started = time.perf_counter()
    figure_1_rows: list[dict[str, Any]] = []
    for t in T_VALUES:
        for sigma_value in SIGMAS:
            sigma = float(sigma_value)
            upper = pld_epsilon(t, sigma, BoundType.DOMINATES)
            lower = pld_epsilon(t, sigma, BoundType.IS_DOMINATED)
            lower_result = chua_lower_epsilon(t, sigma)
            converted, diagnostics = allocation_rdp(t, sigma)
            rdp_epsilon = float(np.min(converted))
            relative_improvement = (
                (rdp_epsilon - upper) / rdp_epsilon
                if rdp_epsilon > 0
                else 0.0
            )
            figure_1_rows.append(
                {
                    "t": t,
                    "sigma": sigma,
                    "delta": DELTA,
                    "pld_epsilon_upper": upper,
                    "pld_epsilon_lower": lower,
                    "pld_interval_width": upper - lower,
                    "chua_lower_epsilon": lower_result["epsilon"],
                    "pld_upper_minus_chua_lower": (
                        upper - lower_result["epsilon"]
                    ),
                    "chua_optimal_threshold": lower_result["threshold"],
                    "chua_delta_at_epsilon": lower_result["delta"],
                    "chua_grid_delta": lower_result["grid_delta"],
                    "rdp_epsilon": rdp_epsilon,
                    "rdp_optimal_order": diagnostics["optimal_order"],
                    "rdp_relative_improvement": relative_improvement,
                    "rdp_remove_alpha2": diagnostics["remove_rdp_alpha2"],
                    "rdp_alpha2_closed_form": diagnostics[
                        "alpha2_closed_form"
                    ],
                    "rdp_alpha2_abs_error": diagnostics["alpha2_abs_error"],
                }
            )

    intervals_ok = all(
        row["pld_epsilon_upper"] >= row["pld_epsilon_lower"]
        and row["pld_interval_width"] <= 0.03
        for row in figure_1_rows
    )
    rdp_improvements = [
        row["rdp_relative_improvement"] for row in figure_1_rows
    ]
    rdp_ok = all(
        row["pld_epsilon_upper"] <= row["rdp_epsilon"] + 1e-10
        for row in figure_1_rows
    ) and float(np.median(rdp_improvements)) >= 0.10
    rdp_independent_ok = all(
        row["rdp_alpha2_abs_error"] <= 1e-12
        and row["chua_delta_at_epsilon"] >= DELTA * (1 - 2e-4)
        and row["chua_grid_delta"] <= row["chua_delta_at_epsilon"] + 1e-12
        for row in figure_1_rows
    )

    figure_2_rows = figure_2_profiles()
    resolved_rows = [
        row
        for row in figure_2_rows
        if row["chua_lower_delta"] >= 1e-10
        and math.isfinite(row["log10_pld_chua_gap"])
    ]
    stable_rows = [
        row for row in figure_2_rows if row["stable_monte_carlo"]
    ]
    profile_interval_ok = all(
        row["pld_delta_upper"] + 1e-15 >= row["pld_delta_lower"]
        and row["pld_delta_upper"] + max(1e-15, 0.01 * row["pld_delta_upper"])
        >= row["chua_lower_delta"]
        for row in figure_2_rows
    )
    chua_gaps = [row["log10_pld_chua_gap"] for row in resolved_rows]
    chua_close_ok = (
        len(resolved_rows) >= 40
        and float(np.median(chua_gaps)) <= 0.15
        and float(np.quantile(chua_gaps, 0.9)) <= 0.30
    )
    stable_counts = {
        label: sum(
            row["stable_monte_carlo"] and row["profile"] == label
            for row in figure_2_rows
        )
        for _, _, label in PROFILE_SETTINGS
    }
    mc_gaps = [row["log10_pld_mc_gap"] for row in stable_rows]
    mc_ok = (
        all(count >= 3 for count in stable_counts.values())
        and all(
            row["pld_delta_lower"]
            <= row["mc_simultaneous_upper"]
            + max(PROFILE_TAIL, 0.01 * row["mc_simultaneous_upper"])
            for row in stable_rows
        )
        and float(np.median(mc_gaps)) <= 0.15
        and float(np.quantile(mc_gaps, 0.9)) <= 0.30
    )
    profile_independent_ok = all(
        row["chua_grid_delta"] <= row["chua_lower_delta"] + 1e-12
        and row["mc_remove_standard_error"] >= 0
        and row["mc_add_standard_error"] >= 0
        for row in figure_2_rows
    )
    independent_ok = rdp_independent_ok and profile_independent_ok
    negative_ok = any(
        10 * row["chua_lower_delta"]
        > row["pld_delta_upper"]
        + max(1e-15, 0.01 * row["pld_delta_upper"])
        for row in resolved_rows
    )
    passed = (
        intervals_ok
        and rdp_ok
        and profile_interval_ok
        and chua_close_ok
        and mc_ok
        and independent_ok
        and negative_ok
    )
    runtime = time.perf_counter() - started
    summary = {
        "claim_4": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "figure_1_points": len(figure_1_rows),
        "figure_2_points": len(figure_2_rows),
        "figure_1_intervals_ok": intervals_ok,
        "figure_1_rdp_ok": rdp_ok,
        "figure_2_intervals_and_lower_ordering_ok": profile_interval_ok,
        "figure_2_chua_closeness_ok": chua_close_ok,
        "figure_2_monte_carlo_ok": mc_ok,
        "independent_checker_ok": independent_ok,
        "negative_control_ok": negative_ok,
        "resolved_chua_points": len(resolved_rows),
        "stable_monte_carlo_points": len(stable_rows),
        "stable_points_per_profile": stable_counts,
        "max_pld_interval": max(
            row["pld_interval_width"] for row in figure_1_rows
        ),
        "median_rdp_improvement": float(np.median(rdp_improvements)),
        "median_chua_log10_gap": float(np.median(chua_gaps)),
        "p90_chua_log10_gap": float(np.quantile(chua_gaps, 0.9)),
        "median_mc_log10_gap": float(np.median(mc_gaps)),
        "p90_mc_log10_gap": float(np.quantile(mc_gaps, 0.9)),
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }
    write_bundle(figure_1_rows, figure_2_rows, summary, runtime)
    write_json(ARTIFACTS / "claim_4_summary.json", summary)
    write_json(
        ARTIFACTS / "claim_4_manifest.json",
        manifest(ARTIFACTS / "claim_4"),
    )
    print("=" * 78)
    print("SOURCE-FAITHFUL FIGURE 1 AND FIGURE 2 CONTRACT")
    print("=" * 78)
    print(
        f"Claim 4: {summary['claim_4']} across "
        f"{len(figure_1_rows)} Figure 1 and {len(figure_2_rows)} Figure 2 points"
    )
    print(
        f"max Figure 1 PLD interval={summary['max_pld_interval']:.6g}; "
        f"median RDP improvement={summary['median_rdp_improvement']:.2%}"
    )
    print(
        "Figure 2 gaps (median/p90 decades): "
        f"Chua={summary['median_chua_log10_gap']:.4f}/"
        f"{summary['p90_chua_log10_gap']:.4f}; "
        f"MC={summary['median_mc_log10_gap']:.4f}/"
        f"{summary['p90_mc_log10_gap']:.4f}"
    )
    print(f"Stable Monte Carlo points per profile: {stable_counts}")
    print(
        f"Subchecks: Figure1 intervals={intervals_ok}, RDP={rdp_ok}, "
        f"Figure2 ordering={profile_interval_ok}, Chua={chua_close_ok}, "
        f"Monte Carlo={mc_ok}, independent={independent_ok}, "
        f"negative control={negative_ok}"
    )
    print(
        "RAW_FIGURE1_JSON="
        + json.dumps(figure_1_rows, sort_keys=True, separators=(",", ":"))
    )
    print(
        "RAW_FIGURE2_JSON="
        + json.dumps(figure_2_rows, sort_keys=True, separators=(",", ":"))
    )
    print(f"SUMMARY_JSON={summary}")
    return 0 if passed else 1
