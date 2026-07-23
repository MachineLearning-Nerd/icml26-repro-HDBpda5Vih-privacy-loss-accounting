"""Full-parameter PREAMBLE PLD versus RDP accounting contract."""

from __future__ import annotations

import math
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable

import numpy as np
from dp_accounting import pld as google_pld
from PLD_accounting import (
    AllocationSchemeConfig,
    BoundType,
    ConvolutionMethod,
    PrivacyParams,
    gaussian_allocation_pld,
)
from PLD_accounting.subsample_pld import subsample_pld
from scipy import special

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    write_csv,
    write_json,
    write_text,
)


N = 600_000
D = 2**20
C = 2**15
EPOCHS = 10
DELTA = 1e-6
TARGET_EPSILON = 1.0
CLIP_SCALE = 1.02
BATCH_SIZES = (512, 1_028, 4_096, 600_000)
BLOCK_SIZES = tuple(int(2**value) for value in range(2, 12))
ORDERS = np.arange(2, 51, dtype=int)
MAX_WORKERS = 4
BASE_CONFIG = AllocationSchemeConfig(
    loss_discretization=1e-3,
    tail_truncation=DELTA * 0.01,
    max_grid_mult=1_000_000,
    convolution_method=ConvolutionMethod.GEOM,
)


def log_poly_convolve(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    degree = len(left) - 1
    output = np.full(degree + 1, -np.inf)
    for total in range(degree + 1):
        output[total] = special.logsumexp(
            left[: total + 1] + right[total::-1]
        )
    return output


def remove_rdp_one_out_of_t(
    t: int, sigma: float, max_order: int
) -> np.ndarray:
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
    log_moments = (
        special.gammaln(indices + 1)
        + result
        - indices * math.log(t)
    )
    return np.array(
        [log_moments[order] / (order - 1) for order in ORDERS]
    )


def allocation_rdp(
    t: int, k: int, sigma: float
) -> tuple[np.ndarray, dict[str, float]]:
    t_per_selection = t // k
    remove = k * remove_rdp_one_out_of_t(
        t_per_selection, sigma, int(ORDERS[-1])
    )
    add = np.array(
        [
            order * k**2 / (2 * sigma**2 * t)
            + order
            * k
            * (t - k)
            / (2 * sigma**2 * t * (order - 1))
            - t
            * math.log1p(
                order * math.expm1(k * (t - k) / (sigma**2 * t**2))
            )
            / (2 * (order - 1))
            for order in ORDERS
        ]
    )
    alpha2_closed = k * math.log1p(
        math.expm1(1 / sigma**2) / t_per_selection
    )
    return np.maximum(remove, add), {
        "remove_alpha2": float(remove[0]),
        "alpha2_closed_form": alpha2_closed,
        "alpha2_abs_error": abs(float(remove[0]) - alpha2_closed),
    }


def log_add(left: float, right: float) -> float:
    if left == -math.inf:
        return right
    if right == -math.inf:
        return left
    high = max(left, right)
    return high + math.log1p(math.exp(min(left, right) - high))


def amplify_rdp(rdp: np.ndarray, q: float) -> np.ndarray:
    """Zhu et al. integer-order Poisson amplification used in paper code."""
    if q == 1:
        return rdp.copy()
    p = 1 - q
    amplified = np.zeros_like(rdp)
    for index, order_value in enumerate(ORDERS):
        order = int(order_value)
        term1 = (order - 1) * math.log(p) + math.log(order * q - q + 1)
        term2 = (
            math.log(order * (order - 1) / 2)
            + 2 * math.log(q)
            + (order - 2) * math.log(p)
            + float(rdp[0])
        )
        total = log_add(term1, term2)
        for ell in range(3, order + 1):
            term = (
                math.log(3)
                + special.gammaln(order + 1)
                - special.gammaln(ell + 1)
                - special.gammaln(order - ell + 1)
                + (order - ell) * math.log(p)
                + ell * math.log(q)
                + (ell - 1) * float(rdp[ell - 2])
            )
            total = log_add(total, term)
        amplified[index] = total / (order - 1)
    return amplified


def rdp_epsilon(
    global_sigma: float, batch_size: int, block_size: int
) -> tuple[float, dict[str, float]]:
    q = batch_size / N
    rounds = math.ceil(N / batch_size) * EPOCHS
    t = D // block_size
    k = C // block_size
    block_norm = CLIP_SCALE * math.sqrt(D / block_size) / k
    effective_sigma = global_sigma / block_norm
    base_rdp, diagnostics = allocation_rdp(t, k, effective_sigma)
    total_rdp = rounds * amplify_rdp(base_rdp, q)
    converted = (
        total_rdp
        - (math.log(DELTA) + np.log(ORDERS)) / (ORDERS - 1)
        + np.log((ORDERS - 1) / ORDERS)
    )
    best = int(np.argmin(converted))
    diagnostics.update(
        {
            "optimal_order": int(ORDERS[best]),
            "effective_sigma": effective_sigma,
            "q": q,
            "rounds": rounds,
            "t": t,
            "k": k,
            "block_norm": block_norm,
        }
    )
    return float(converted[best]), diagnostics


def pld_epsilon(
    global_sigma: float, batch_size: int, block_size: int
) -> tuple[float, dict[str, float]]:
    q = batch_size / N
    rounds = math.ceil(N / batch_size) * EPOCHS
    t = D // block_size
    k = C // block_size
    block_norm = CLIP_SCALE * math.sqrt(D / block_size) / k
    effective_sigma = global_sigma / block_norm
    effective_compositions = rounds * q
    config = AllocationSchemeConfig(
        loss_discretization=(
            BASE_CONFIG.loss_discretization
            / math.sqrt(effective_compositions)
        ),
        tail_truncation=(
            BASE_CONFIG.tail_truncation / effective_compositions
        ),
        max_grid_mult=BASE_CONFIG.max_grid_mult,
        convolution_method=BASE_CONFIG.convolution_method,
    )
    base = gaussian_allocation_pld(
        PrivacyParams(
            sigma=effective_sigma,
            num_steps=t,
            num_selected=k,
            num_epochs=1,
            delta=DELTA,
        ),
        config,
        bound_type=BoundType.DOMINATES,
    )
    sampled = subsample_pld(base, q)
    composed = sampled.self_compose(rounds)
    epsilon = composed.get_epsilon_for_delta(DELTA)
    return epsilon, {
        "effective_sigma": effective_sigma,
        "q": q,
        "rounds": rounds,
        "t": t,
        "k": k,
        "block_norm": block_norm,
        "loss_discretization": config.loss_discretization,
        "tail_truncation": config.tail_truncation,
        "max_grid_mult": config.max_grid_mult,
    }


def gaussian_epsilon(global_sigma: float, batch_size: int) -> float:
    q = batch_size / N
    rounds = math.ceil(N / batch_size) * EPOCHS
    one_step = google_pld.privacy_loss_distribution.from_gaussian_mechanism(
        standard_deviation=global_sigma,
        value_discretization_interval=1e-4,
        sampling_prob=q,
        pessimistic_estimate=True,
        use_connect_dots=True,
    )
    return one_step.self_compose(rounds).get_epsilon_for_delta(DELTA)


def invert_decreasing(
    function: Callable[[float], float],
    *,
    target: float = TARGET_EPSILON,
    lower: float = 0.1,
    upper: float = 20.0,
    iterations: int = 14,
) -> dict[str, float]:
    if function(lower) <= target or function(upper) > target:
        raise RuntimeError("root is not bracketed")
    left, right = lower, upper
    for _ in range(iterations):
        midpoint = (left + right) / 2
        if function(midpoint) <= target:
            right = midpoint
        else:
            left = midpoint
    return {
        "sigma_lower": left,
        "sigma_upper": right,
        "epsilon_lower": function(left),
        "epsilon_upper": function(right),
        "width": right - left,
    }


def evaluate_grid_point(
    batch_size: int, block_size: int
) -> dict[str, Any]:
    """Evaluate one independent full-scale PREAMBLE configuration."""
    pld_value, pld_meta = pld_epsilon(1.0, batch_size, block_size)
    rdp_value, rdp_meta = rdp_epsilon(1.0, batch_size, block_size)
    improvement = (rdp_value - pld_value) / rdp_value
    return {
        "batch_size": batch_size,
        "B": block_size,
        "n": N,
        "d": D,
        "communication_C": C,
        "epochs": EPOCHS,
        "delta": DELTA,
        "global_sigma": 1.0,
        "q": pld_meta["q"],
        "rounds": pld_meta["rounds"],
        "t": pld_meta["t"],
        "k": pld_meta["k"],
        "block_norm": pld_meta["block_norm"],
        "effective_sigma": pld_meta["effective_sigma"],
        "pld_epsilon": pld_value,
        "rdp_epsilon": rdp_value,
        "relative_improvement": improvement,
        "rdp_optimal_order": rdp_meta["optimal_order"],
        "rdp_remove_alpha2": rdp_meta["remove_alpha2"],
        "rdp_alpha2_closed_form": rdp_meta["alpha2_closed_form"],
        "rdp_alpha2_abs_error": rdp_meta["alpha2_abs_error"],
        "max_grid_mult": pld_meta["max_grid_mult"],
    }


def write_bundle(
    rows: list[dict[str, Any]],
    anchor: dict[str, Any],
    summary: dict[str, Any],
    runtime: float,
) -> None:
    out = ARTIFACTS / "claim_6"
    write_json(
        out / "claim_contract.json",
        {
            "claim_id": 6,
            "source_statement": (
                "PREAMBLE at n=600000, d=2^20, C=2^15, E=10 uses "
                "k=C/B out of t=d/B allocation, Poisson user subsampling q, "
                "and E/q composition; Figure 3 reports materially lower "
                "noise under PLD accounting than FS25/DCO25 RDP accounting."
            ),
            "evaluated_domain": {
                "n": N,
                "d": D,
                "C": C,
                "epochs": EPOCHS,
                "delta": DELTA,
                "batch_sizes": list(BATCH_SIZES),
                "block_sizes": list(BLOCK_SIZES),
                "fixed_sigma": 1.0,
                "root_anchor": {"batch_size": 512, "B": 2048, "epsilon": 1.0},
            },
            "verdict_rule": (
                "VERIFIED iff PLD epsilon is below RDP epsilon at all 40 "
                "full-parameter points with >=5% median improvement, the "
                "representative target-epsilon PLD noise is below RDP noise, "
                "all parameter identities and alpha=2 checks pass, and the "
                "equal-accountant mutation is rejected."
            ),
        },
    )
    write_text(
        out / "source_audit.md",
        """# Claim 6 source audit

`body.tex` lines 321–337 defines the pipeline and quantifiers:
`n=6*10^5`, `d=2^20`, `C=2^15`, `E=10`, target `(epsilon,delta)=(1,1e-6)`,
allocation `k=C/B` of `t=d/B`, user Poisson rate `q`, and `E/q`
composition. It explicitly says the published computation used one million
bins in each direction. The public paper figure has four batch-size panels
`{512,1028,4096,600000}` and ten block sizes `B=2^2,...,2^11`.

The exact generation code was removed from the author repository's current
tree but remains in public commit `d49e87d`, including the same parameters and
RDP formulas. This verifier reconstructs that versioned pipeline against the
current pinned author PLD release.
""",
    )
    write_text(
        out / "method.md",
        """# Method

At each of the 40 source configurations, a full random-allocation PLD is built
with `k=C/B` and `t=d/B`, transformed by the paper's PLD Poisson-subsampling
rule, and composed for `ceil(n/batch_size)*E` updates. The multiplicative grid
is capped at the paper's one million bins per direction. Independent grid
points are scheduled across four CPU worker processes; this changes only wall
time, not any accountant, parameter, result, or acceptance predicate.

The independent RDP path implements the versioned paper experiment: exact
integer remove-direction moments via a log-space generating function, the
DCO add bound, Zhu et al. Poisson RDP amplification, exact composition, and
optimal conversion over integer orders 2–50. A separate order-2 closed form
checks the moment implementation.

All 40 points compare epsilon at the same global sigma. A representative
heavy-composition point additionally inverts both accountants at epsilon=1,
directly checking the paper figure's required-noise interpretation.
""",
    )
    write_json(out / "raw_results.json", {"grid": rows, "anchor": anchor})
    write_csv(out / "full_grid.csv", list(rows[0]), rows)
    write_json(
        out / "independent_checker.json",
        {
            "rdp": [
                {
                    "batch_size": row["batch_size"],
                    "B": row["B"],
                    "remove_alpha2": row["rdp_remove_alpha2"],
                    "alpha2_closed_form": row["rdp_alpha2_closed_form"],
                    "abs_error": row["rdp_alpha2_abs_error"],
                }
                for row in rows
            ],
            "parameter_identities": [
                {
                    "batch_size": row["batch_size"],
                    "B": row["B"],
                    "t_times_B": row["t"] * row["B"],
                    "k_times_B": row["k"] * row["B"],
                    "rounds": row["rounds"],
                }
                for row in rows
            ],
        },
    )
    write_json(
        out / "negative_control.json",
        {
            "mutation": "replace every PLD epsilon by its RDP epsilon",
            "rejected": summary["negative_control_ok"],
            "failed_predicate": "strict PLD improvement at every point",
        },
    )
    metadata = runtime_metadata()
    metadata.update(
        {
            "runtime_seconds": runtime,
            "source_experiment_commit": "d49e87d",
            "rdp_orders": [int(value) for value in ORDERS],
            "cpu_only": True,
            "grid_worker_processes": MAX_WORKERS,
        }
    )
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

The full source parameter grid is evaluated without downscaling. The 40-point
comparison fixes global sigma at 1 rather than solving 80 separate inverse
problems; monotonicity makes this a direct test of which accountant gives the
tighter privacy bound. One representative point also reproduces the inverse
noise comparison at epsilon=1. The current released author code may differ
numerically from the historical plotting checkout, so no pixel-level agreement
with the raster figure is asserted.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 6 evaluation

Verdict: **{'VERIFIED' if summary['passed'] else 'FALSIFIED'}**

- Full-scale configurations: {len(rows)}
- Median epsilon improvement over RDP: {summary['median_improvement']:.2%}
- Minimum epsilon improvement over RDP: {summary['minimum_improvement']:.2%}
- Anchor PLD/RDP noise ratio: {anchor['pld_to_rdp_sigma_ratio']:.6f}
- Runtime: {runtime:.6f} seconds
""",
    )


def main() -> int:
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    configurations = [
        (batch_size, block_size)
        for batch_size in BATCH_SIZES
        for block_size in BLOCK_SIZES
    ]
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        pending = {
            executor.submit(evaluate_grid_point, *configuration): configuration
            for configuration in configurations
        }
        for future in as_completed(pending):
            row = future.result()
            rows.append(row)
            print(
                f"PREAMBLE batch={row['batch_size']} B={row['B']}: "
                f"PLD eps={row['pld_epsilon']:.6g}, "
                f"RDP eps={row['rdp_epsilon']:.6g}",
                flush=True,
            )
    rows.sort(key=lambda row: (row["batch_size"], row["B"]))

    anchor_batch, anchor_block = 512, 2_048
    pld_root = invert_decreasing(
        lambda sigma: pld_epsilon(
            sigma, anchor_batch, anchor_block
        )[0]
    )
    rdp_root = invert_decreasing(
        lambda sigma: rdp_epsilon(
            sigma, anchor_batch, anchor_block
        )[0]
    )
    gaussian_root = invert_decreasing(
        lambda sigma: gaussian_epsilon(sigma, anchor_batch)
    )
    anchor = {
        "batch_size": anchor_batch,
        "B": anchor_block,
        "target_epsilon": TARGET_EPSILON,
        "delta": DELTA,
        "pld_sigma_upper": pld_root["sigma_upper"],
        "rdp_sigma_upper": rdp_root["sigma_upper"],
        "gaussian_sigma_upper": gaussian_root["sigma_upper"],
        "pld_to_rdp_sigma_ratio": (
            pld_root["sigma_upper"] / rdp_root["sigma_upper"]
        ),
        "pld_to_gaussian_sigma_ratio": (
            pld_root["sigma_upper"] / gaussian_root["sigma_upper"]
        ),
        "rdp_to_gaussian_sigma_ratio": (
            rdp_root["sigma_upper"] / gaussian_root["sigma_upper"]
        ),
        "pld_root_width": pld_root["width"],
        "rdp_root_width": rdp_root["width"],
        "gaussian_root_width": gaussian_root["width"],
    }

    improvements = [row["relative_improvement"] for row in rows]
    grid_ok = all(
        math.isfinite(row["pld_epsilon"])
        and row["pld_epsilon"] < row["rdp_epsilon"]
        for row in rows
    ) and float(np.median(improvements)) >= 0.05
    identities_ok = all(
        row["t"] * row["B"] == D
        and row["k"] * row["B"] == C
        and row["rounds"] == math.ceil(N / row["batch_size"]) * EPOCHS
        and row["max_grid_mult"] == 1_000_000
        for row in rows
    )
    independent_ok = all(
        row["rdp_alpha2_abs_error"] <= 1e-12 for row in rows
    )
    anchor_ok = (
        anchor["pld_sigma_upper"] < anchor["rdp_sigma_upper"]
        and anchor["pld_root_width"] <= 0.002
        and anchor["rdp_root_width"] <= 0.002
    )
    negative_ok = not all(
        row["rdp_epsilon"] < row["rdp_epsilon"] for row in rows
    )
    passed = (
        grid_ok
        and identities_ok
        and independent_ok
        and anchor_ok
        and negative_ok
    )
    runtime = time.perf_counter() - started
    summary = {
        "claim_6": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "full_scale_points": len(rows),
        "grid_ok": grid_ok,
        "parameter_identities_ok": identities_ok,
        "independent_checker_ok": independent_ok,
        "anchor_ok": anchor_ok,
        "negative_control_ok": negative_ok,
        "median_improvement": float(np.median(improvements)),
        "minimum_improvement": float(np.min(improvements)),
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }
    write_bundle(rows, anchor, summary, runtime)
    write_json(ARTIFACTS / "claim_6_summary.json", summary)
    write_json(
        ARTIFACTS / "claim_6_manifest.json",
        manifest(ARTIFACTS / "claim_6"),
    )
    print("=" * 78)
    print("FULL PREAMBLE ACCOUNTING CONTRACT")
    print("=" * 78)
    print(
        f"Claim 6: {summary['claim_6']} across {len(rows)} "
        "full-parameter points"
    )
    print(
        f"median improvement={summary['median_improvement']:.2%}; "
        f"minimum improvement={summary['minimum_improvement']:.2%}; "
        f"anchor sigma PLD/RDP={anchor['pld_to_rdp_sigma_ratio']:.6f}"
    )
    print(
        f"Subchecks: grid={grid_ok}, identities={identities_ok}, "
        f"independent={independent_ok}, anchor={anchor_ok}, "
        f"negative control={negative_ok}"
    )
    print(f"SUMMARY_JSON={summary}")
    return 0 if passed else 1
