"""Full-scale Figure 4 Bernoulli privacy/utility contract."""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
from dp_accounting import pld as google_pld
from PLD_accounting import (
    AllocationSchemeConfig,
    BoundType,
    ConvolutionMethod,
    PrivacyParams,
    gaussian_allocation_epsilon_configurable,
)

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    write_csv,
    write_json,
    write_text,
)


T = 1_000
DELTA = 1e-10
P = 0.9
N = 1_000
REPLICATES = 10_000
SEEDS = [1729, 2718, 31415]
SETTINGS = [(1.0, 1), (0.1, 1), (0.1, 1_000)]
ALLOCATION_RESOLUTIONS = [0.002, 0.001]
POISSON_RESOLUTIONS = [2e-4, 1e-4]


def allocation_epsilon(sigma: float, resolution: float) -> float:
    return gaussian_allocation_epsilon_configurable(
        PrivacyParams(
            sigma=sigma,
            num_steps=T,
            num_selected=1,
            num_epochs=1,
            delta=DELTA,
        ),
        AllocationSchemeConfig(
            loss_discretization=resolution,
            tail_truncation=DELTA * 0.01,
            max_grid_mult=100_000,
            convolution_method=ConvolutionMethod.GEOM,
        ),
        bound_type=BoundType.DOMINATES,
    )


def poisson_epsilon(sigma: float, resolution: float) -> float:
    one_step = google_pld.privacy_loss_distribution.from_gaussian_mechanism(
        standard_deviation=sigma,
        value_discretization_interval=resolution,
        sampling_prob=1 / T,
        pessimistic_estimate=True,
        use_connect_dots=True,
    )
    return one_step.self_compose(T).get_epsilon_for_delta(DELTA)


def invert_decreasing(
    function: Callable[[float], float],
    target: float,
    *,
    lower: float = 0.1,
    upper: float = 10.0,
    iterations: int = 18,
) -> dict[str, float]:
    """Return a conservative upper bracket for the target crossing."""
    low_value = function(lower)
    high_value = function(upper)
    if low_value <= target or high_value > target:
        raise RuntimeError(
            f"invalid bracket: f({lower})={low_value}, f({upper})={high_value}"
        )
    left, right = lower, upper
    left_value = low_value
    right_value = high_value
    for _ in range(iterations):
        midpoint = (left + right) / 2
        value = function(midpoint)
        if value <= target:
            right = midpoint
            right_value = value
        else:
            left = midpoint
            left_value = value
    return {
        "sigma_lower_bracket": left,
        "sigma_upper_bracket": right,
        "epsilon_at_lower": left_value,
        "epsilon_at_upper": right_value,
        "bracket_width": right - left,
    }


def analytic_mse(
    scheme: str, sample_size: int, sigma: float, dimension: int
) -> float:
    scaled_sigma = sigma * math.sqrt(dimension)
    data_variance = P * (1 - P) / sample_size
    noise_variance = scaled_sigma**2 * T / sample_size**2
    if scheme == "allocation":
        return data_variance + noise_variance
    if scheme == "poisson":
        participation_variance = P * (1 - 1 / T) / sample_size
        return data_variance + participation_variance + noise_variance
    raise ValueError(scheme)


def simulate_mse(
    scheme: str,
    sample_size: int,
    sigma: float,
    dimension: int,
    seed: int,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    errors: list[np.ndarray] = []
    scaled_sigma = sigma * math.sqrt(dimension)
    for start in range(0, REPLICATES, 500):
        count = min(500, REPLICATES - start)
        data = rng.binomial(1, P, size=(count, sample_size))
        if scheme == "allocation":
            totals = np.sum(data, axis=1)
        else:
            participation = rng.binomial(T, 1 / T, size=(count, sample_size))
            totals = np.sum(data * participation, axis=1)
        noise = rng.normal(0, scaled_sigma * math.sqrt(T), size=count)
        estimates = (totals + noise) / sample_size
        errors.append((estimates - P) ** 2)
    squared_errors = np.concatenate(errors)
    return {
        "mse": float(np.mean(squared_errors)),
        "std": float(np.std(squared_errors, ddof=1)),
        "standard_error": float(
            np.std(squared_errors, ddof=1) / math.sqrt(REPLICATES)
        ),
    }


def write_bundle(
    privacy_rows: list[dict[str, Any]],
    utility_rows: list[dict[str, Any]],
    verdict: str,
    runtime: float,
) -> None:
    out = ARTIFACTS / "claim_5"
    write_json(
        out / "claim_contract.json",
        {
            "claim_id": 5,
            "source_statement": (
                "Figure 4 repeats the FS25 Bernoulli mean-estimation experiment "
                "with t=1000, p=0.9, delta=1e-10 and reports lower required "
                "noise and MSE for random allocation in all three panels."
            ),
            "quantifiers": {
                "privacy_settings": [
                    {"epsilon": epsilon, "dimension": dimension}
                    for epsilon, dimension in SETTINGS
                ],
                "sample_size_sweep": [100, 316, 1_000, 3_162, 10_000, 31_622, 100_000],
                "required_relationship": (
                    "allocation upper-bound sigma < Poisson upper-bound sigma, "
                    "and allocation analytic MSE < Poisson analytic MSE"
                ),
            },
            "verdict_rule": (
                "VERIFIED iff the noise ordering holds at both numerical "
                "resolutions in every panel, the fine-resolution separation "
                "exceeds the measured convergence and bisection envelope, "
                "the exact-MSE ordering holds over the full n sweep, seeded "
                "Monte Carlo agrees with the exact formulas, and the mutation "
                "is rejected."
            ),
        },
    )
    write_text(
        out / "source_audit.md",
        """# Claim 5 source audit

The experiment is described in `body.tex` lines 356–365 and its settings are
recoverable from the authors' deleted-but-versioned script
`comparisons/paper_experiments.py` at public commit `d49e87d`: `t=1000`,
`p=0.9`, `delta=1e-10`, 10,000 experiments, sample sizes from `10^2` through
`10^5`, and panels `(epsilon,d)=(1,1),(0.1,1),(0.1,1000)`.

The judge's phrase “n=1000” selects one point of that sweep rather than the
full source quantifier. This contract evaluates both the exact `n=1000` point
and the full seven-point source sweep.
""",
    )
    write_text(
        out / "method.md",
        """# Method

For every unique privacy epsilon, required Gaussian noise is found by
deterministic bisection. Random-allocation epsilon comes from the pinned
released author API and Poisson epsilon is computed independently with Google's
`dp-accounting` PLD accountant. Both are pessimistic upper bounds, matching the
paper's comparison of accounting guarantees. Each root is evaluated at two
grid resolutions. Both grids must preserve the strict ordering, and the
fine-grid separation must exceed the sum of both bisection widths and both
observed coarse-to-fine shifts. Duplicate panels share the same privacy result.

MSE is independently derived from the sampling process. Allocation has data
variance `p(1-p)/n`; Poisson additionally has exact participation variance
`p(1-1/t)/n`. Both add Gaussian variance `sigma^2*d*t/n^2`. Seeded, chunked
Monte Carlo at `n=1000` checks these formulas with 10,000 replicates per panel.
""",
    )
    write_json(
        out / "raw_results.json",
        {"privacy": privacy_rows, "utility": utility_rows},
    )
    write_csv(out / "privacy_noise.csv", list(privacy_rows[0]), privacy_rows)
    write_csv(out / "utility_mse.csv", list(utility_rows[0]), utility_rows)
    write_json(
        out / "independent_checker.json",
        {
            "checker": (
                "independent Google Poisson accountant at two resolutions, "
                "closed-form variance decomposition, and seeded simulation"
            ),
            "rows": utility_rows,
        },
    )
    write_json(
        out / "negative_control.json",
        {
            "mutation": (
                "reverse the claimed mechanism ordering; the mutated claim "
                "that Poisson requires less noise must be rejected"
            ),
            "rejected_in_every_panel": all(
                row["negative_control_rejected"] for row in privacy_rows
            ),
        },
    )
    metadata = runtime_metadata(SEEDS)
    metadata.update(
        {
            "runtime_seconds": runtime,
            "replicates_per_panel_method": REPLICATES,
            "source_experiment_commit": "d49e87d",
        }
    )
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

The public paper artifact contains only plotted points, not the original raw
random draws, so exact pixel-for-pixel stochastic replication is impossible.
The privacy computation and analytic MSE use the source parameters at full
scale. The claim is about the reported accounting bounds, not an exact
closed-form privacy threshold for either mechanism. Numerical robustness is
therefore assessed by grid refinement and explicit root brackets. New Monte
Carlo draws use fixed disclosed seeds and are checked against the exact moments
rather than expected to match historical random draws.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 5 evaluation

Verdict: **{verdict}**

- Privacy panels: {len(privacy_rows)}
- Utility rows: {len(utility_rows)}
- Monte Carlo replicates per panel and method: {REPLICATES}
- Runtime: {runtime:.6f} seconds
""",
    )


def main() -> int:
    started = time.perf_counter()
    privacy_rows: list[dict[str, Any]] = []
    utility_rows: list[dict[str, Any]] = []
    sample_sizes = [100, 316, 1_000, 3_162, 10_000, 31_622, 100_000]
    privacy_by_epsilon: dict[float, dict[str, Any]] = {}

    for panel, (epsilon, dimension) in enumerate(SETTINGS):
        if epsilon not in privacy_by_epsilon:
            allocation_roots = [
                invert_decreasing(
                    lambda sigma, resolution=resolution: allocation_epsilon(
                        sigma, resolution
                    ),
                    epsilon,
                )
                for resolution in ALLOCATION_RESOLUTIONS
            ]
            poisson_roots = [
                invert_decreasing(
                    lambda sigma, resolution=resolution: poisson_epsilon(
                        sigma, resolution
                    ),
                    epsilon,
                )
                for resolution in POISSON_RESOLUTIONS
            ]
            allocation_sigma = allocation_roots[-1]["sigma_upper_bracket"]
            poisson_sigma = poisson_roots[-1]["sigma_upper_bracket"]
            fine_gap = (
                poisson_roots[-1]["sigma_lower_bracket"]
                - allocation_roots[-1]["sigma_upper_bracket"]
            )
            convergence_envelope = (
                abs(
                    allocation_roots[0]["sigma_upper_bracket"]
                    - allocation_roots[1]["sigma_upper_bracket"]
                )
                + abs(
                    poisson_roots[0]["sigma_upper_bracket"]
                    - poisson_roots[1]["sigma_upper_bracket"]
                )
                + allocation_roots[-1]["bracket_width"]
                + poisson_roots[-1]["bracket_width"]
            )
            ordering_at_both_resolutions = all(
                allocation["sigma_upper_bracket"]
                < poisson["sigma_lower_bracket"]
                for allocation, poisson in zip(
                    allocation_roots, poisson_roots, strict=True
                )
            )
            privacy_by_epsilon[epsilon] = {
                "allocation_roots": allocation_roots,
                "poisson_roots": poisson_roots,
                "allocation_sigma": allocation_sigma,
                "poisson_sigma": poisson_sigma,
                "fine_gap": fine_gap,
                "convergence_envelope": convergence_envelope,
                "ordering_at_both_resolutions": ordering_at_both_resolutions,
                "robust_lower_noise": (
                    ordering_at_both_resolutions
                    and fine_gap > convergence_envelope
                ),
            }
        privacy_result = privacy_by_epsilon[epsilon]
        allocation_sigma = privacy_result["allocation_sigma"]
        poisson_sigma = privacy_result["poisson_sigma"]
        robust_lower_noise = privacy_result["robust_lower_noise"]
        privacy_rows.append(
            {
                "panel": panel,
                "epsilon": epsilon,
                "dimension": dimension,
                "t": T,
                "delta": DELTA,
                "allocation_sigma_upper": allocation_sigma,
                "poisson_sigma_upper": poisson_sigma,
                "allocation_to_poisson_ratio": (
                    allocation_sigma / poisson_sigma
                ),
                "allocation_roots_by_resolution": dict(
                    zip(ALLOCATION_RESOLUTIONS, privacy_result["allocation_roots"])
                ),
                "poisson_roots_by_resolution": dict(
                    zip(POISSON_RESOLUTIONS, privacy_result["poisson_roots"])
                ),
                "fine_root_separation": privacy_result["fine_gap"],
                "convergence_and_bracket_envelope": privacy_result[
                    "convergence_envelope"
                ],
                "ordering_at_both_resolutions": privacy_result[
                    "ordering_at_both_resolutions"
                ],
                "robust_lower_noise": robust_lower_noise,
                "negative_control_rejected": not (
                    poisson_sigma < allocation_sigma
                ),
            }
        )

        for sample_size in sample_sizes:
            allocation_exact = analytic_mse(
                "allocation", sample_size, allocation_sigma, dimension
            )
            poisson_exact = analytic_mse(
                "poisson", sample_size, poisson_sigma, dimension
            )
            row: dict[str, Any] = {
                "panel": panel,
                "epsilon": epsilon,
                "dimension": dimension,
                "sample_size": sample_size,
                "allocation_mse_exact": allocation_exact,
                "poisson_mse_exact": poisson_exact,
                "allocation_better_exact": allocation_exact < poisson_exact,
                "allocation_mse_mc": None,
                "allocation_mc_se": None,
                "poisson_mse_mc": None,
                "poisson_mc_se": None,
                "mc_matches_exact": None,
                "mc_allocation_better": None,
            }
            if sample_size == N:
                allocation_mc = simulate_mse(
                    "allocation",
                    sample_size,
                    allocation_sigma,
                    dimension,
                    SEEDS[panel],
                )
                poisson_mc = simulate_mse(
                    "poisson",
                    sample_size,
                    poisson_sigma,
                    dimension,
                    SEEDS[panel] + 100_000,
                )
                matches = (
                    abs(allocation_mc["mse"] - allocation_exact)
                    <= 5 * allocation_mc["standard_error"]
                    and abs(poisson_mc["mse"] - poisson_exact)
                    <= 5 * poisson_mc["standard_error"]
                )
                row.update(
                    {
                        "allocation_mse_mc": allocation_mc["mse"],
                        "allocation_mc_se": allocation_mc["standard_error"],
                        "poisson_mse_mc": poisson_mc["mse"],
                        "poisson_mc_se": poisson_mc["standard_error"],
                        "mc_matches_exact": matches,
                        "mc_allocation_better": (
                            allocation_mc["mse"] < poisson_mc["mse"]
                        ),
                    }
                )
            utility_rows.append(row)

    privacy_ok = all(row["robust_lower_noise"] for row in privacy_rows)
    exact_utility_ok = all(
        row["allocation_better_exact"] for row in utility_rows
    )
    mc_rows = [row for row in utility_rows if row["sample_size"] == N]
    mc_ok = all(
        row["mc_matches_exact"] and row["mc_allocation_better"]
        for row in mc_rows
    )
    negative_ok = all(
        row["negative_control_rejected"] for row in privacy_rows
    )
    passed = privacy_ok and exact_utility_ok and mc_ok and negative_ok
    reversed_at_both_resolutions = all(
        all(
            poisson["sigma_upper_bracket"]
            < allocation["sigma_lower_bracket"]
            for allocation, poisson in zip(
                row["allocation_roots_by_resolution"].values(),
                row["poisson_roots_by_resolution"].values(),
                strict=True,
            )
        )
        for row in privacy_rows
    )
    verdict = (
        "VERIFIED"
        if passed
        else "FALSIFIED"
        if reversed_at_both_resolutions
        else "BLOCKED"
    )
    runtime = time.perf_counter() - started
    write_bundle(privacy_rows, utility_rows, verdict, runtime)
    summary = {
        "claim_5": verdict,
        "privacy_panels": len(privacy_rows),
        "full_scale_n1000_mc_panels": len(mc_rows),
        "privacy_ok": privacy_ok,
        "exact_utility_ok": exact_utility_ok,
        "mc_ok": mc_ok,
        "negative_control_ok": negative_ok,
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }
    write_json(ARTIFACTS / "claim_5_summary.json", summary)
    write_json(
        ARTIFACTS / "claim_5_manifest.json",
        manifest(ARTIFACTS / "claim_5"),
    )
    print("=" * 78)
    print("FULL BERNOULLI PRIVACY–UTILITY CONTRACT")
    print("=" * 78)
    print(f"Claim 5: {summary['claim_5']}")
    for row in privacy_rows:
        print(
            f"panel={row['panel']} eps={row['epsilon']} d={row['dimension']}: "
            f"sigma allocation={row['allocation_sigma_upper']:.6f}, "
            f"Poisson={row['poisson_sigma_upper']:.6f}, "
            f"ratio={row['allocation_to_poisson_ratio']:.6f}"
        )
    print(
        f"Subchecks: privacy={privacy_ok}, exact utility={exact_utility_ok}, "
        f"Monte Carlo={mc_ok}, negative control={negative_ok}"
    )
    print(f"SUMMARY_JSON={summary}")
    return 0 if passed else 1
