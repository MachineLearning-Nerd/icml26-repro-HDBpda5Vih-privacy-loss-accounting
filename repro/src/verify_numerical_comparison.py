"""Figure 1 numerical PLD comparison against lower and RDP bounds."""

from __future__ import annotations

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
CONFIG = AllocationSchemeConfig(
    loss_discretization=0.01,
    tail_truncation=DELTA * 0.01,
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


def write_bundle(
    rows: list[dict[str, Any]],
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
            "evaluated_domain": {
                "t": list(T_VALUES),
                "sigma": [float(value) for value in SIGMAS],
                "delta": DELTA,
                "note": (
                    "t=1000 is the largest paper Figure 1 panel; t=10000 is "
                    "an explicit supplemental judge-requested stress test."
                ),
            },
            "verdict_rule": (
                "VERIFIED iff all PLD intervals are ordered and <=0.03 wide, "
                "all upper bounds are within 0.05 epsilon of the Chua lower "
                "bound, PLD improves on RDP at every point with >=10% median "
                "relative improvement, independent alpha=2 checks pass, and "
                "the shifted-lower-bound mutation is rejected."
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
bound, not a “Monte Carlo lower bound.”
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
""",
    )
    write_json(out / "raw_results.json", rows)
    write_csv(out / "comparison.csv", list(rows[0]), rows)
    write_json(
        out / "independent_checker.json",
        {
            "chua_equation_6": [
                {
                    "t": row["t"],
                    "sigma": row["sigma"],
                    "epsilon": row["chua_lower_epsilon"],
                    "threshold": row["chua_optimal_threshold"],
                    "delta": row["chua_delta_at_epsilon"],
                    "grid_delta": row["chua_grid_delta"],
                }
                for row in rows
            ],
            "rdp_alpha2": [
                {
                    "t": row["t"],
                    "sigma": row["sigma"],
                    "computed": row["rdp_remove_alpha2"],
                    "closed_form": row["rdp_alpha2_closed_form"],
                    "abs_error": row["rdp_alpha2_abs_error"],
                }
                for row in rows
            ],
        },
    )
    write_json(
        out / "negative_control.json",
        {
            "mutation": "add 0.1 epsilon to the independent lower bound",
            "rejected": summary["negative_control_ok"],
            "reason": "the mutated value no longer lies below the PLD upper bound",
        },
    )
    metadata = runtime_metadata()
    metadata.update(
        {
            "runtime_seconds": runtime,
            "source_experiment_commit": "d49e87d",
            "rdp_orders": [int(value) for value in ORDERS],
        }
    )
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

This verifier does not relabel the paper's Monte Carlo mean or confidence bound
as a lower bound. Reproducing the exact Figure 2 Monte Carlo curves would
require the paper's one-million-sample importance-sampling implementation; the
authors report that the predecessor computation used 60 CPU machines. Instead,
the stronger deterministic Equation (6) lower bound is recomputed exactly.
The Figure 1 sigma grid is complete for `t=1000`; `t=10000` is supplemental.
The smaller paper panels `t=10,100` are not rerun in this branch.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 4 evaluation

Verdict: **{'VERIFIED' if summary['passed'] else 'FALSIFIED'}**

- Full comparison points: {len(rows)}
- Maximum PLD interval width: {summary['max_pld_interval']:.6g}
- Maximum gap to Chua lower bound: {summary['max_lower_gap']:.6g}
- Median relative RDP improvement: {summary['median_rdp_improvement']:.2%}
- Runtime: {runtime:.6f} seconds
""",
    )


def main() -> int:
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
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
            rows.append(
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
        for row in rows
    )
    lower_ok = all(
        -1e-8 <= row["pld_upper_minus_chua_lower"] <= 0.05
        for row in rows
    )
    rdp_improvements = [row["rdp_relative_improvement"] for row in rows]
    rdp_ok = all(
        row["pld_epsilon_upper"] <= row["rdp_epsilon"] + 1e-10
        for row in rows
    ) and float(np.median(rdp_improvements)) >= 0.10
    independent_ok = all(
        row["rdp_alpha2_abs_error"] <= 1e-12
        and row["chua_delta_at_epsilon"] >= DELTA * (1 - 2e-4)
        and row["chua_grid_delta"] <= row["chua_delta_at_epsilon"] + 1e-12
        for row in rows
    )
    negative_ok = any(
        row["chua_lower_epsilon"] + 0.1
        > row["pld_epsilon_upper"] + 0.05
        for row in rows
    )
    passed = (
        intervals_ok
        and lower_ok
        and rdp_ok
        and independent_ok
        and negative_ok
    )
    runtime = time.perf_counter() - started
    summary = {
        "claim_4": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "points": len(rows),
        "intervals_ok": intervals_ok,
        "lower_bound_ok": lower_ok,
        "rdp_ok": rdp_ok,
        "independent_checker_ok": independent_ok,
        "negative_control_ok": negative_ok,
        "max_pld_interval": max(
            row["pld_interval_width"] for row in rows
        ),
        "max_lower_gap": max(
            row["pld_upper_minus_chua_lower"] for row in rows
        ),
        "median_rdp_improvement": float(np.median(rdp_improvements)),
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }
    write_bundle(rows, summary, runtime)
    write_json(ARTIFACTS / "claim_4_summary.json", summary)
    write_json(
        ARTIFACTS / "claim_4_manifest.json",
        manifest(ARTIFACTS / "claim_4"),
    )
    print("=" * 78)
    print("NUMERICAL PLD VERSUS LOWER-BOUND AND RDP CONTRACT")
    print("=" * 78)
    print(f"Claim 4: {summary['claim_4']} across {len(rows)} points")
    print(
        f"max PLD interval={summary['max_pld_interval']:.6g}; "
        f"max lower gap={summary['max_lower_gap']:.6g}; "
        f"median RDP improvement={summary['median_rdp_improvement']:.2%}"
    )
    print(
        f"Subchecks: intervals={intervals_ok}, lower={lower_ok}, RDP={rdp_ok}, "
        f"independent={independent_ok}, negative control={negative_ok}"
    )
    print(f"SUMMARY_JSON={summary}")
    return 0 if passed else 1
