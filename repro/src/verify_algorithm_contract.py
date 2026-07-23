"""Direct checks of the released Theorem 4.6 geometric algorithm."""

from __future__ import annotations

import math
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import PLD_accounting.geometric_convolution as geom_module
from PLD_accounting import (
    AllocationSchemeConfig,
    BoundType,
    ConvolutionMethod,
    PrivacyParams,
    gaussian_allocation_epsilon_configurable,
)
from PLD_accounting.discrete_dist import DenseDiscreteDist, Domain
from PLD_accounting.types import SpacingType

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    write_csv,
    write_json,
    write_text,
)


PROBABILITIES = np.array([0.07, 0.19, 0.31, 0.43], dtype=np.float64)
TARGET_VALUES = np.array([0.5, 1.0, 2.0, 4.0], dtype=np.float64)


def binary_call_count(t: int) -> int:
    return math.floor(math.log2(t)) + t.bit_count() - 1


def count_vectors(total: int, dimensions: int) -> Iterator[tuple[int, ...]]:
    if dimensions == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in count_vectors(total - first, dimensions - 1):
            yield (first, *rest)


def make_grid_distribution(
    total_alpha: float, operations: int
) -> tuple[DenseDiscreteDist, list[tuple[float, float]], float]:
    """Place four fixed atoms on a fine geometric grid spanning [0.5, 4]."""
    log_step = total_alpha / operations
    ratio = math.exp(log_step)
    bins = math.ceil(math.log(4.0 / 0.5) / log_step) + 1
    masses = np.zeros(bins, dtype=np.float64)
    indices = np.rint(np.log(TARGET_VALUES / 0.5) / log_step).astype(int)
    for index, probability in zip(indices, PROBABILITIES, strict=True):
        masses[index] += probability
    dist = DenseDiscreteDist(
        x_0=0.5,
        step=ratio,
        prob_arr=masses,
        p_min=0.0,
        p_max=0.0,
        spacing_type=SpacingType.GEOMETRIC,
        domain=Domain.POSITIVES,
    )
    nonzero = [
        (float(dist.x_array[index]), float(masses[index]))
        for index in np.flatnonzero(masses)
    ]
    return dist, nonzero, log_step


def exact_sum_atoms(
    base_atoms: list[tuple[float, float]], t: int
) -> list[tuple[float, float]]:
    """Independent multinomial enumeration of the t-fold exact sum."""
    atoms = []
    factorial_t = math.factorial(t)
    for counts in count_vectors(t, len(base_atoms)):
        coefficient = factorial_t
        value = 0.0
        probability = 1.0
        for count, (atom, mass) in zip(counts, base_atoms, strict=True):
            coefficient //= math.factorial(count)
            value += count * atom
            probability *= mass**count
        atoms.append((math.log(value), coefficient * probability))
    return atoms


def dense_log_atoms(dist: DenseDiscreteDist) -> list[tuple[float, float]]:
    atoms = [
        (math.log(float(value)), float(mass))
        for value, mass in zip(dist.x_array, dist.prob_arr, strict=True)
        if mass > 0
    ]
    if dist.p_min:
        atoms.append((-math.inf, float(dist.p_min)))
    if dist.p_max:
        atoms.append((math.inf, float(dist.p_max)))
    return atoms


def ccdf(atoms: list[tuple[float, float]], threshold: float) -> float:
    return math.fsum(mass for value, mass in atoms if value > threshold)


def stochastic_contract(
    exact: list[tuple[float, float]],
    upper: list[tuple[float, float]],
    alpha: float,
    beta: float,
) -> dict[str, Any]:
    finite_values = [
        value
        for value, _ in exact + upper
        if math.isfinite(value)
    ]
    thresholds = set(finite_values)
    thresholds.update(np.nextafter(value, -math.inf) for value in finite_values)
    thresholds.update(value + alpha for value in finite_values)
    validity_violation = 0.0
    tightness_violation = 0.0
    for threshold in thresholds:
        exact_tail = ccdf(exact, threshold)
        upper_tail = ccdf(upper, threshold)
        validity_violation = max(validity_violation, exact_tail - upper_tail)
        tightness_violation = max(
            tightness_violation,
            upper_tail - ccdf(exact, threshold - alpha) - beta,
        )
    tolerance = 2e-11
    return {
        "validity_max_violation": validity_violation,
        "tightness_max_violation": tightness_violation,
        "valid": validity_violation <= tolerance,
        "alpha_beta_tight": tightness_violation <= tolerance,
        "exact_mass": math.fsum(mass for _, mass in exact),
        "upper_mass": math.fsum(mass for _, mass in upper),
        "thresholds_checked": len(thresholds),
    }


def run_fast_case(
    t: int, alpha: float, beta: float, *, check_exact: bool
) -> dict[str, Any]:
    operations = binary_call_count(t)
    dist, base_atoms, log_step = make_grid_distribution(alpha, operations)
    calls: list[dict[str, int]] = []
    original = geom_module.geometric_convolve

    def tracked_convolve(**kwargs):
        left = kwargs["dist_1"]
        right = kwargs["dist_2"]
        output = original(**kwargs)
        calls.append(
            {
                "left_bins": len(left.prob_arr),
                "right_bins": len(right.prob_arr),
                "output_bins": len(output.prob_arr),
                "pair_products": len(left.prob_arr) * len(right.prob_arr),
            }
        )
        return output

    geom_module.geometric_convolve = tracked_convolve
    try:
        started = time.perf_counter()
        upper = geom_module.geometric_self_convolve(
            dist=dist,
            T=t,
            tail_truncation=beta,
            bound_type=BoundType.DOMINATES,
        )
        runtime = time.perf_counter() - started
    finally:
        geom_module.geometric_convolve = original

    if check_exact:
        exact = exact_sum_atoms(base_atoms, t)
        contract = stochastic_contract(
            exact=exact,
            upper=dense_log_atoms(upper),
            alpha=alpha,
            beta=beta,
        )

        # Negative control: lower rounding is invalid if mislabeled as an upper bound.
        lower = geom_module.geometric_self_convolve(
            dist=dist,
            T=t,
            tail_truncation=beta,
            bound_type=BoundType.IS_DOMINATED,
        )
        mutation_contract = stochastic_contract(
            exact=exact,
            upper=dense_log_atoms(lower),
            alpha=alpha,
            beta=beta,
        )
        negative_control = {
            "mutation": "use IS_DOMINATED rounding but label it DOMINATES",
            "rejected": not mutation_contract["valid"],
            "validity_max_violation": mutation_contract[
                "validity_max_violation"
            ],
        }
    else:
        contract = {
            "validity_max_violation": None,
            "tightness_max_violation": None,
            "valid": None,
            "alpha_beta_tight": None,
            "exact_mass": None,
            "upper_mass": float(
                np.sum(upper.prob_arr) + upper.p_min + upper.p_max
            ),
            "thresholds_checked": 0,
        }
        negative_control = {
            "mutation": "not run: operation-count-only scaling case",
            "rejected": None,
            "validity_max_violation": None,
        }
    work = sum(call["pair_products"] for call in calls)
    return {
        "t": t,
        "alpha": alpha,
        "beta": beta,
        "exact_checked": check_exact,
        "stage_log_grid_step": log_step,
        "expected_convolution_calls": operations,
        "observed_convolution_calls": len(calls),
        "input_bins": len(dist.prob_arr),
        "output_bins": len(upper.prob_arr),
        "primitive_pair_products": work,
        "runtime_seconds": runtime,
        **contract,
        "negative_control": negative_control,
        "call_trace": calls,
    }


def complexity_sweeps() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    # Trigger JIT compilation outside recorded timing.
    run_fast_case(t=3, alpha=0.3, beta=0.0, check_exact=True)

    accuracy_rows = [
        run_fast_case(t=t, alpha=alpha, beta=beta, check_exact=True)
        for t, alpha, beta in (
            (3, 0.30, 0.0),
            (5, 0.20, 1e-8),
            (8, 0.15, 1e-8),
            (12, 0.10, 1e-8),
        )
    ]
    t_rows = [
        run_fast_case(t=t, alpha=0.2, beta=1e-8, check_exact=False)
        for t in (8, 16, 32, 64, 128, 256)
    ]
    alpha_rows = [
        run_fast_case(t=64, alpha=alpha, beta=1e-8, check_exact=False)
        for alpha in (0.4, 0.2, 0.1, 0.05)
    ]
    beta_rows = [
        run_fast_case(t=21, alpha=0.15, beta=beta, check_exact=False)
        for beta in (0.0, 1e-8, 1e-5)
    ]

    loglog_t = np.log([math.log(row["t"]) for row in t_rows])
    log_work_t = np.log([row["primitive_pair_products"] for row in t_rows])
    t_exponent = float(np.polyfit(loglog_t, log_work_t, 1)[0])
    log_inv_alpha = np.log([1 / row["alpha"] for row in alpha_rows])
    log_work_alpha = np.log(
        [row["primitive_pair_products"] for row in alpha_rows]
    )
    alpha_exponent = float(np.polyfit(log_inv_alpha, log_work_alpha, 1)[0])
    normalized = [
        row["primitive_pair_products"]
        * row["alpha"] ** 2
        / math.log(row["t"]) ** 3
        for row in t_rows
    ]
    scaling = {
        "t_work_exponent_against_log_t": t_exponent,
        "alpha_work_exponent_against_inverse_alpha": alpha_exponent,
        "normalized_work_min": min(normalized),
        "normalized_work_max": max(normalized),
        "normalized_work_ratio": max(normalized) / min(normalized),
        "t_exponent_expected": 3.0,
        "alpha_exponent_expected": 2.0,
        "t_exponent_acceptance": [1.5, 4.5],
        "alpha_exponent_acceptance": [1.5, 2.5],
        "normalized_ratio_acceptance_max": 8.0,
    }
    return accuracy_rows + t_rows + alpha_rows + beta_rows, scaling


def high_level_accuracy() -> list[dict[str, Any]]:
    """Check released Gaussian upper/lower outputs at explicit alpha and beta."""
    rows = []
    # Warm up the full author path separately.
    warm_params = PrivacyParams(sigma=2.0, num_steps=4, delta=1e-5)
    warm_config = AllocationSchemeConfig(
        loss_discretization=0.3,
        tail_truncation=1e-7,
        convolution_method=ConvolutionMethod.GEOM,
    )
    gaussian_allocation_epsilon_configurable(
        warm_params, warm_config, bound_type=BoundType.DOMINATES
    )
    for t in (16, 64, 256):
        for alpha in (0.2, 0.1):
            beta = 1e-8
            config = AllocationSchemeConfig(
                loss_discretization=alpha,
                tail_truncation=beta,
                convolution_method=ConvolutionMethod.GEOM,
            )
            params = PrivacyParams(
                sigma=2.0, num_steps=t, num_selected=1, delta=1e-5
            )
            started = time.perf_counter()
            upper = gaussian_allocation_epsilon_configurable(
                params, config, bound_type=BoundType.DOMINATES
            )
            lower = gaussian_allocation_epsilon_configurable(
                params, config, bound_type=BoundType.IS_DOMINATED
            )
            runtime = time.perf_counter() - started
            gap = upper - lower
            rows.append(
                {
                    "t": t,
                    "sigma": 2.0,
                    "delta": 1e-5,
                    "alpha": alpha,
                    "beta": beta,
                    "epsilon_upper": upper,
                    "epsilon_lower": lower,
                    "epsilon_gap": gap,
                    "gap_bound_2alpha": 2 * alpha,
                    "ordered": upper >= lower,
                    "gap_within_2alpha": gap <= 2 * alpha + 1e-8,
                    "runtime_seconds": runtime,
                }
            )
    return rows


def write_bundle(
    fast_rows: list[dict[str, Any]],
    scaling: dict[str, Any],
    high_level: list[dict[str, Any]],
    passed: bool,
    total_runtime: float,
) -> None:
    out = ARTIFACTS / "claim_2"
    write_json(
        out / "claim_contract.json",
        {
            "claim_id": 2,
            "source_statement": "Theorem 4.6 validity, (alpha,beta)-tightness, and O((IQR/alpha)^2 log^3(t)) runtime; Gaussian specialization adds log(t/beta)/sigma^2.",
            "machine_checks": [
                "Exact independent multinomial sum versus released geometric self-convolution.",
                "CCDF validity and (alpha,beta) inequalities at every atom boundary.",
                "Exact exponentiation-by-squaring call count floor(log2 t)+popcount(t)-1.",
                "Primitive pair-product work scaling in log(t)^3 and alpha^-2.",
                "Released Gaussian upper/lower epsilon gap no greater than 2 alpha.",
            ],
            "verdict_rule": "VERIFIED iff all accuracy, operation-count, scaling, released-path checks pass and lower-rounding mutations are rejected.",
        },
    )
    write_text(
        out / "source_audit.md",
        """# Claim 2 source audit

Theorem 4.6 is `body.tex` label `thm:num_acc_RA`, lines 266–280. Its general
runtime is `O((IQR_{beta/t}/alpha)^2 log^3(t))`; for the unit-sensitivity
Gaussian mechanism it specializes to
`O(log_2^3(t) ln(t/beta)/(sigma^2 alpha^2))`. The algorithm outline at lines
253–262 specifies direct convolution, a geometrically spaced grid,
domination-preserving directional rounding, and at most
`2 ceil(log_2(t))` convolution steps. Appendix C states the exact binary count
`floor(log_2(t)) + popcount(t) - 1`.

The judge paraphrase omits the general IQR factor and the Gaussian `sigma^-2`
factor. The contract tests the exact source statement.
""",
    )
    write_text(
        out / "method.md",
        """# Method

The released implementation pinned in `uv.lock` is exercised directly. Four
fixed atoms are placed on increasingly fine geometric grids. Its
`geometric_self_convolve` output is compared to a separately implemented
multinomial enumeration of the exact t-fold sum. CCDF inequalities are checked
at all exact and rounded atom boundaries for both validity and
`(alpha,beta)` tightness.

The convolution function is wrapped only to count calls and input-bin pair
products; numeric work is still performed by the unmodified released function.
Sweeps over `t` and `alpha` fit the exponents of primitive work. A second suite
calls the released Gaussian public API and checks its dominating and dominated
epsilon bounds at explicit alpha/beta settings. The negative control substitutes
downward rounding where an upper bound is required and must violate validity.
""",
    )
    serializable_rows = [
        {key: value for key, value in row.items() if key != "call_trace"}
        for row in fast_rows
    ]
    write_json(
        out / "raw_results.json",
        {
            "fast_convolution_checks": fast_rows,
            "scaling": scaling,
            "released_gaussian_checks": high_level,
        },
    )
    write_csv(
        out / "complexity_raw.csv",
        [
            "t",
            "alpha",
            "beta",
            "exact_checked",
            "stage_log_grid_step",
            "expected_convolution_calls",
            "observed_convolution_calls",
            "input_bins",
            "output_bins",
            "primitive_pair_products",
            "runtime_seconds",
            "validity_max_violation",
            "tightness_max_violation",
            "valid",
            "alpha_beta_tight",
            "exact_mass",
            "upper_mass",
            "thresholds_checked",
        ],
        [
            {
                key: row[key]
                for key in (
                    "t",
                    "alpha",
                    "beta",
                    "exact_checked",
                    "stage_log_grid_step",
                    "expected_convolution_calls",
                    "observed_convolution_calls",
                    "input_bins",
                    "output_bins",
                    "primitive_pair_products",
                    "runtime_seconds",
                    "validity_max_violation",
                    "tightness_max_violation",
                    "valid",
                    "alpha_beta_tight",
                    "exact_mass",
                    "upper_mass",
                    "thresholds_checked",
                )
            }
            for row in serializable_rows
        ],
    )
    write_csv(
        out / "released_gaussian_accuracy.csv",
        list(high_level[0].keys()),
        high_level,
    )
    write_json(
        out / "independent_checker.json",
        {
            "implementation": "multinomial count-vector enumeration and direct CCDF inequalities",
            "fast_checks": serializable_rows,
            "scaling": scaling,
        },
    )
    write_json(
        out / "negative_control.json",
        [row["negative_control"] for row in fast_rows],
    )
    metadata = runtime_metadata()
    metadata["runtime_seconds"] = total_runtime
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

Asymptotic Big-O cannot be proven by finite timing. The gate therefore uses the
released operation structure and primitive pair-product counts as its primary
complexity evidence; wall time is recorded but not used as a brittle pass
condition. Exact accuracy checks use finite four-atom inputs. The Gaussian API
checks cover t up to 256 rather than the paper's largest application and use
coarse alpha values so this branch remains a targeted CPU contract test.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 2 evaluation

Verdict: **{'VERIFIED' if passed else 'FALSIFIED'}**

- Direct fast-versus-exact cases: {len(fast_rows)}
- Released Gaussian alpha/beta cases: {len(high_level)}
- `log(t)` work exponent: {scaling['t_work_exponent_against_log_t']:.4f}
- inverse-alpha work exponent: {scaling['alpha_work_exponent_against_inverse_alpha']:.4f}
- normalized work spread: {scaling['normalized_work_ratio']:.4f}x
- Runtime: {total_runtime:.6f} CPU wall-clock seconds
""",
    )


def main() -> int:
    started = time.perf_counter()
    fast_rows, scaling = complexity_sweeps()
    high_level = high_level_accuracy()

    fast_ok = all(
        row["observed_convolution_calls"]
        == row["expected_convolution_calls"]
        and (
            not row["exact_checked"]
            or (
                row["valid"]
                and row["alpha_beta_tight"]
                and row["negative_control"]["rejected"]
            )
        )
        for row in fast_rows
    )
    scaling_ok = (
        1.5 <= scaling["t_work_exponent_against_log_t"] <= 4.5
        and 1.5
        <= scaling["alpha_work_exponent_against_inverse_alpha"]
        <= 2.5
        and scaling["normalized_work_ratio"] <= 8.0
    )
    high_level_ok = all(
        row["ordered"] and row["gap_within_2alpha"] for row in high_level
    )
    passed = fast_ok and scaling_ok and high_level_ok
    runtime = time.perf_counter() - started
    write_bundle(fast_rows, scaling, high_level, passed, runtime)
    summary = {
        "claim_2": "VERIFIED" if passed else "FALSIFIED",
        "fast_accuracy_cases": len(fast_rows),
        "released_gaussian_cases": len(high_level),
        "fast_ok": fast_ok,
        "scaling_ok": scaling_ok,
        "released_gaussian_ok": high_level_ok,
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }
    write_json(ARTIFACTS / "round_1b_summary.json", summary)
    write_json(
        ARTIFACTS / "round_1b_manifest.json",
        manifest(ARTIFACTS / "claim_2"),
    )

    print("=" * 78)
    print("ROUND 1B — RELEASED GEOMETRIC ALGORITHM CONTRACT")
    print("=" * 78)
    print(f"Claim 2: {summary['claim_2']}")
    print(
        f"Fast cases={len(fast_rows)}; Gaussian API cases={len(high_level)}; "
        "negative controls="
        f"{sum(r['negative_control']['rejected'] is True for r in fast_rows)}/"
        f"{sum(r['exact_checked'] for r in fast_rows)}"
    )
    print(
        "Primitive-work exponents: "
        f"log(t)^{scaling['t_work_exponent_against_log_t']:.3f}, "
        f"alpha^-{scaling['alpha_work_exponent_against_inverse_alpha']:.3f}; "
        f"normalized spread={scaling['normalized_work_ratio']:.3f}x"
    )
    print(
        f"Subchecks: accuracy={fast_ok}, scaling={scaling_ok}, "
        f"released Gaussian={high_level_ok}"
    )
    print(f"SUMMARY_JSON={summary}")
    return 0 if passed else 1
