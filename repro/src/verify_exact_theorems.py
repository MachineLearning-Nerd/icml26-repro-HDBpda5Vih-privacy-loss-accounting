"""Exact finite-support checks for Theorems 4.4 and 3.3.

The checks use Fraction throughout. Equality is therefore mathematical equality
for each enumerated finite pair, not a floating-point closeness proxy.
"""

from __future__ import annotations

import itertools
import math
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    write_csv,
    write_json,
    write_text,
)


PMF = dict[Fraction, Fraction]
Distribution = tuple[Fraction, ...]

MECHANISMS: dict[str, tuple[Distribution, Distribution]] = {
    "binary_asymmetric": (
        (Fraction(1, 3), Fraction(2, 3)),
        (Fraction(3, 5), Fraction(2, 5)),
    ),
    "binary_strong": (
        (Fraction(1, 10), Fraction(9, 10)),
        (Fraction(4, 5), Fraction(1, 5)),
    ),
    "ternary": (
        (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)),
    ),
}
LAMBDAS = (Fraction(1, 10), Fraction(1, 3), Fraction(3, 4), Fraction(1, 1))


def _add(pmf: dict[Fraction, Fraction], key: Fraction, mass: Fraction) -> None:
    pmf[key] = pmf.get(key, Fraction(0)) + mass


def _product(values: Iterable[Fraction]) -> Fraction:
    out = Fraction(1)
    for value in values:
        out *= value
    return out


def _validate_distribution(p: Distribution) -> None:
    assert p and all(value > 0 for value in p)
    assert sum(p, Fraction(0)) == 1


def direct_allocation_ratio_pmf(
    p: Distribution, q: Distribution, t: int, direction: str
) -> PMF:
    """Enumerate the pair (Pbar_t, Q^t) directly on the product outcome space."""
    out: PMF = {}
    for outcome in itertools.product(range(len(p)), repeat=t):
        q_mass = _product(q[index] for index in outcome)
        pbar_mass = sum(
            p[outcome[i]]
            * _product(q[outcome[j]] for j in range(t) if j != i)
            for i in range(t)
        ) / t
        if direction == "remove":
            _add(out, pbar_mass / q_mass, pbar_mass)
        elif direction == "add":
            _add(out, q_mass / pbar_mass, q_mass)
        else:
            raise ValueError(direction)
    assert sum(out.values(), Fraction(0)) == 1
    return out


def theorem_44_ratio_pmf(
    p: Distribution,
    q: Distribution,
    t: int,
    direction: str,
    denominator_offset: int = 0,
) -> PMF:
    """Evaluate the exponentiated-PLD formula independently of Pbar enumeration."""
    out: PMF = {}
    denominator = t + denominator_offset
    for outcome in itertools.product(range(len(p)), repeat=t):
        ratios = [p[index] / q[index] for index in outcome]
        if direction == "remove":
            # Symmetry fixes the mixture's P-drawn coordinate at index zero.
            mass = p[outcome[0]] * _product(q[index] for index in outcome[1:])
            ratio = sum(ratios, Fraction(0)) / denominator
        elif direction == "add":
            mass = _product(q[index] for index in outcome)
            ratio = denominator / sum(ratios, Fraction(0))
        else:
            raise ValueError(direction)
        _add(out, ratio, mass)
    assert sum(out.values(), Fraction(0)) == 1
    return out


def direct_general_k_ratio_pmf(
    p: Distribution, q: Distribution, t: int, k: int, direction: str
) -> PMF:
    """Exact k-out-of-t pair, used only to audit the judge's scope paraphrase."""
    subsets = tuple(itertools.combinations(range(t), k))
    out: PMF = {}
    for outcome in itertools.product(range(len(p)), repeat=t):
        q_mass = _product(q[index] for index in outcome)
        alloc_mass = sum(
            _product(
                p[outcome[j]] if j in chosen else q[outcome[j]]
                for j in range(t)
            )
            for chosen in subsets
        ) / len(subsets)
        if direction == "remove":
            _add(out, alloc_mass / q_mass, alloc_mass)
        else:
            _add(out, q_mass / alloc_mass, q_mass)
    return out


def elementary_symmetric_k_ratio_pmf(
    p: Distribution, q: Distribution, t: int, k: int, direction: str
) -> PMF:
    """Independent elementary-symmetric likelihood-ratio identity for k > 1."""
    subsets = tuple(itertools.combinations(range(t), k))
    out: PMF = {}
    for outcome in itertools.product(range(len(p)), repeat=t):
        ratios = [p[index] / q[index] for index in outcome]
        mean_product = sum(
            _product(ratios[j] for j in chosen) for chosen in subsets
        ) / len(subsets)
        q_mass = _product(q[index] for index in outcome)
        alloc_mass = q_mass * mean_product
        if direction == "remove":
            _add(out, mean_product, alloc_mass)
        else:
            _add(out, 1 / mean_product, q_mass)
    return out


def pair_ratio_pmf(
    p: Distribution, q: Distribution, direction: str
) -> PMF:
    out: PMF = {}
    for p_mass, q_mass in zip(p, q, strict=True):
        if direction == "remove":
            _add(out, p_mass / q_mass, p_mass)
        else:
            _add(out, q_mass / p_mass, q_mass)
    return out


def direct_subsample_ratio_pmf(
    p: Distribution, q: Distribution, lam: Fraction, direction: str
) -> PMF:
    p_lam = tuple(lam * pv + (1 - lam) * qv for pv, qv in zip(p, q, strict=True))
    return pair_ratio_pmf(p_lam, q, direction)


def theorem_33_ratio_pmf(
    p: Distribution,
    q: Distribution,
    lam: Fraction,
    direction: str,
    mutated: bool = False,
) -> PMF:
    out: PMF = {}
    if direction == "remove":
        # f_L supplies P mass and f_-D(L) supplies Q mass at the same P/Q ratio.
        p_by_ratio: PMF = defaultdict(Fraction)
        q_by_ratio: PMF = defaultdict(Fraction)
        for pv, qv in zip(p, q, strict=True):
            p_by_ratio[pv / qv] += pv
            q_by_ratio[pv / qv] += qv
        for ratio in p_by_ratio.keys() | q_by_ratio.keys():
            transformed = 1 + lam * ratio if mutated else 1 + lam * (ratio - 1)
            mass = lam * p_by_ratio[ratio] + (1 - lam) * q_by_ratio[ratio]
            _add(out, transformed, mass)
    elif direction == "add":
        for pv, qv in zip(p, q, strict=True):
            ratio = qv / pv
            denominator = lam + (1 - lam) * ratio
            transformed = ratio / denominator
            if mutated:
                transformed = ratio / (lam + ratio)
            _add(out, transformed, qv)
    else:
        raise ValueError(direction)
    return dict(out)


def _fraction_pmf(pmf: PMF) -> list[dict[str, str]]:
    return [
        {"likelihood_ratio": str(key), "mass": str(pmf[key])}
        for key in sorted(pmf)
    ]


def verify_claim_1() -> tuple[bool, dict]:
    rows = []
    negative_rows = []
    detailed = []
    for name, (p, q) in MECHANISMS.items():
        _validate_distribution(p)
        _validate_distribution(q)
        for t in range(1, 6):
            for direction in ("remove", "add"):
                direct = direct_allocation_ratio_pmf(p, q, t, direction)
                formula = theorem_44_ratio_pmf(p, q, t, direction)
                mutated = theorem_44_ratio_pmf(
                    p, q, t, direction, denominator_offset=1
                )
                equal = direct == formula
                mutation_rejected = direct != mutated
                rows.append(
                    {
                        "mechanism": name,
                        "support": len(p),
                        "t": t,
                        "direction": direction,
                        "direct_atoms": len(direct),
                        "formula_atoms": len(formula),
                        "exact_equal": equal,
                    }
                )
                negative_rows.append(
                    {
                        "mechanism": name,
                        "t": t,
                        "direction": direction,
                        "mutation": "replace denominator t by t+1",
                        "rejected": mutation_rejected,
                    }
                )
                if name == "binary_asymmetric" and t == 3:
                    detailed.append(
                        {
                            "direction": direction,
                            "direct": _fraction_pmf(direct),
                            "formula": _fraction_pmf(formula),
                        }
                    )

    # Scope audit: an exact elementary-symmetric identity is checked for k=2,
    # while the report retains that Theorem 4.4 itself states k=1.
    scope_rows = []
    p, q = MECHANISMS["binary_asymmetric"]
    for t in (3, 4, 5):
        for direction in ("remove", "add"):
            direct = direct_general_k_ratio_pmf(p, q, t, 2, direction)
            independent = elementary_symmetric_k_ratio_pmf(p, q, t, 2, direction)
            scope_rows.append(
                {
                    "t": t,
                    "k": 2,
                    "direction": direction,
                    "exact_equal": direct == independent,
                    "note": "supporting identity; not attributed to Theorem 4.4",
                }
            )

    passed = (
        all(row["exact_equal"] for row in rows)
        and all(row["rejected"] for row in negative_rows)
        and all(row["exact_equal"] for row in scope_rows)
    )
    return passed, {
        "checks": rows,
        "scope_checks": scope_rows,
        "representative_exact_pmfs": detailed,
        "negative_controls": negative_rows,
    }


def verify_claim_3() -> tuple[bool, dict]:
    rows = []
    negative_rows = []
    for name, (p, q) in MECHANISMS.items():
        for lam in LAMBDAS:
            for direction in ("remove", "add"):
                direct = direct_subsample_ratio_pmf(p, q, lam, direction)
                formula = theorem_33_ratio_pmf(p, q, lam, direction)
                mutated = theorem_33_ratio_pmf(p, q, lam, direction, mutated=True)
                if direction == "remove":
                    support_ok = min(direct) >= 1 - lam
                else:
                    support_ok = lam == 1 or max(direct) <= 1 / (1 - lam)
                realization_expectation = sum(
                    mass / ratio for ratio, mass in formula.items()
                )
                rows.append(
                    {
                        "mechanism": name,
                        "lambda": str(lam),
                        "direction": direction,
                        "exact_equal": direct == formula,
                        "support_ok": support_ok,
                        "pld_realization_expectation": str(realization_expectation),
                        "realization_ok": realization_expectation <= 1,
                    }
                )
                negative_rows.append(
                    {
                        "mechanism": name,
                        "lambda": str(lam),
                        "direction": direction,
                        "mutation": "incorrect affine likelihood-ratio map",
                        "rejected": direct != mutated,
                    }
                )

    # Unified path: construct the exact random-allocation pair and then feed that
    # finite pair to the same subsampling transformation.
    p, q = MECHANISMS["binary_asymmetric"]
    outcomes = tuple(itertools.product(range(len(p)), repeat=3))
    q_product: Distribution = tuple(
        _product(q[index] for index in outcome) for outcome in outcomes
    )
    pbar: Distribution = tuple(
        sum(
            p[outcome[i]]
            * _product(q[outcome[j]] for j in range(3) if j != i)
            for i in range(3)
        )
        / 3
        for outcome in outcomes
    )
    unified_rows = []
    for lam in (Fraction(1, 5), Fraction(2, 3)):
        for direction in ("remove", "add"):
            direct = direct_subsample_ratio_pmf(pbar, q_product, lam, direction)
            transformed = theorem_33_ratio_pmf(
                pbar, q_product, lam, direction
            )
            unified_rows.append(
                {
                    "t": 3,
                    "lambda": str(lam),
                    "direction": direction,
                    "exact_equal": direct == transformed,
                    "atoms": len(direct),
                }
            )

    passed = (
        all(
            row["exact_equal"]
            and row["support_ok"]
            and row["realization_ok"]
            for row in rows
        )
        and all(row["rejected"] for row in negative_rows)
        and all(row["exact_equal"] for row in unified_rows)
    )
    return passed, {
        "checks": rows,
        "unified_allocation_then_subsampling": unified_rows,
        "negative_controls": negative_rows,
    }


def write_claim_1_bundle(result: dict, runtime_seconds: float, passed: bool) -> None:
    out = ARTIFACTS / "claim_1"
    write_json(
        out / "claim_contract.json",
        {
            "claim_id": 1,
            "source_statement": "Theorem 4.4 exact add/remove PLD identities for 1-out-of-t allocation.",
            "domain": "t in positive integers; any PLD realization induced here by positive finite P,Q.",
            "machine_check": "Direct product-space likelihood-ratio PMFs equal independent exponentiated-PLD formula PMFs exactly in Fraction arithmetic for both directions.",
            "verdict_rule": "VERIFIED iff every exact equality holds and every denominator mutation is rejected.",
            "scope_qualification": "The theorem states k=1. General k uses Lemma 2.8; k=2 elementary-symmetric checks are supporting evidence, not misattributed to Theorem 4.4.",
        },
    )
    write_text(
        out / "source_audit.md",
        """# Claim 1 source audit

Theorem 4.4 is `body.tex` label `thm:PLDrandAlloc`, lines 214–227 of the
retrieved v2 source. It quantifies over every positive integer `t` and every PLD
realization. It gives separate remove and add identities as logarithms of
averages/sums of independent exponentiated PLD and dual-PLD terms.

The judge wording says “k-out-of-t”, but the theorem itself is explicitly the
1-out-of-t identity. General `k` is treated by Lemma 2.8. The verifier preserves
this distinction and also checks the exact elementary-symmetric likelihood-ratio
identity for small `k=2` instances without attributing that extension to
Theorem 4.4.
""",
    )
    write_text(
        out / "method.md",
        """# Method

For three strictly positive rational pairs `(P,Q)` (two binary, one ternary),
enumerate every outcome of the product space for `t=1..5`. One implementation
constructs `Pbar_t` and `Q^t` directly. A separately written implementation
constructs the likelihood-ratio random variables from the theorem while fixing
the P-drawn coordinate by symmetry. PMFs are dictionaries keyed by exact
`Fraction` likelihood ratios; equality is exact before applying the injective
log transform.

The negative control changes the theorem's denominator from `t` to `t+1` and
must disagree with direct enumeration. A separate `k=2` checker compares direct
subset-mixture enumeration with an elementary-symmetric-polynomial calculation.
""",
    )
    write_json(out / "raw_results.json", result)
    write_csv(
        out / "raw_results.csv",
        [
            "mechanism",
            "support",
            "t",
            "direction",
            "direct_atoms",
            "formula_atoms",
            "exact_equal",
        ],
        result["checks"],
    )
    write_json(
        out / "independent_checker.json",
        {
            "method": "direct Pbar_t/Q^t enumeration versus theorem formula",
            "checks": result["checks"],
            "scope_checks": result["scope_checks"],
        },
    )
    write_json(out / "negative_control.json", result["negative_controls"])
    metadata = runtime_metadata()
    metadata["runtime_seconds"] = runtime_seconds
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

Finite exhaustive instances validate the identity without floating-point error
but do not replace the paper's universal algebraic proof. Continuous Gaussian
PLDs are deferred to the released-algorithm branch. The verdict concerns the
source-faithful `k=1` theorem; it does not claim Theorem 4.4 directly proves the
judge's broader `k` paraphrase.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 1 evaluation

Verdict: **{'VERIFIED' if passed else 'FALSIFIED'}**

- Exact add/remove checks: {len(result['checks'])}
- Exact `k=2` scope-audit checks: {len(result['scope_checks'])}
- Rejected mutations: {sum(r['rejected'] for r in result['negative_controls'])}/{len(result['negative_controls'])}
- Arithmetic: exact rational `Fraction`
- Runtime: {runtime_seconds:.6f} CPU seconds wall-clock
""",
    )


def write_claim_3_bundle(result: dict, runtime_seconds: float, passed: bool) -> None:
    out = ARTIFACTS / "claim_3"
    write_json(
        out / "claim_contract.json",
        {
            "claim_id": 3,
            "source_statement": "Theorem 3.3 exact remove/add phi_lambda transformations on PLD realizations.",
            "domain": "lambda in (0,1]; positive finite P,Q used for exhaustive checks.",
            "machine_check": "Direct PLDs of (P_lambda,Q) and (Q,P_lambda) equal transformed base PLDs exactly; supports and PLD-realization invariant hold; allocation output can be subsampled through the same interface.",
            "verdict_rule": "VERIFIED iff all exact equalities/invariants hold and every map mutation is rejected.",
        },
    )
    write_text(
        out / "source_audit.md",
        """# Claim 3 source audit

Definition 3.1 is `body.tex` label `def:PLDreal`, lines 133–137. Theorem 3.3 is
label `thm:PLD_subsam`, lines 155–171. It quantifies over every
`lambda in (0,1]` and every PLD realization, specifies separate add/remove PMFs,
defines `phi_lambda(l)=log(1+(exp(l)-1)/lambda)`, states support restrictions,
and identifies the results exactly with the PLDs of `(P_lambda,Q)` and
`(Q,P_lambda)`.
""",
    )
    write_text(
        out / "method.md",
        """# Method

For the same three rational mechanisms and four exact rational sampling rates,
construct `(P_lambda,Q)` directly and independently transform grouped base
likelihood-ratio PMFs according to Theorem 3.3. Compare exact `Fraction` PMFs in
both directions, test the theorem's support bounds, and test
`E[exp(-L)] <= 1`.

For the unified-framework check, first build the exact `t=3` random-allocation
pair `(Pbar_3,Q^3)`, then apply subsampling both directly and through the PLD
transformation. The negative control uses an incorrect affine ratio map and
must disagree.
""",
    )
    write_json(out / "raw_results.json", result)
    write_csv(
        out / "raw_results.csv",
        [
            "mechanism",
            "lambda",
            "direction",
            "exact_equal",
            "support_ok",
            "pld_realization_expectation",
            "realization_ok",
        ],
        result["checks"],
    )
    write_json(
        out / "independent_checker.json",
        {
            "method": "direct mixture-pair PLD versus grouped base-PLD transformation",
            "checks": result["checks"],
            "unified_checks": result["unified_allocation_then_subsampling"],
        },
    )
    write_json(out / "negative_control.json", result["negative_controls"])
    metadata = runtime_metadata()
    metadata["runtime_seconds"] = runtime_seconds
    write_json(out / "exact_command_environment.json", metadata)
    write_text(
        out / "limitations.md",
        """# Limitations and deviations

The checks are exhaustive only for the enumerated positive finite pairs. They
exercise exact atoms and both directions, including lambda=1 and nontrivial
sampling rates, but do not cover infinite atoms or prove the theorem for every
measurable distribution. The allocation-plus-subsampling test is `t=3`; larger
continuous cases are delegated to application experiments.
""",
    )
    write_text(
        out / "EVAL.md",
        f"""# Claim 3 evaluation

Verdict: **{'VERIFIED' if passed else 'FALSIFIED'}**

- Exact transformation checks: {len(result['checks'])}
- Unified allocation-then-subsampling checks: {len(result['unified_allocation_then_subsampling'])}
- Rejected mutations: {sum(r['rejected'] for r in result['negative_controls'])}/{len(result['negative_controls'])}
- Runtime: {runtime_seconds:.6f} CPU seconds wall-clock
""",
    )


def main() -> int:
    started = time.perf_counter()
    c1_start = time.perf_counter()
    c1_passed, c1_result = verify_claim_1()
    c1_runtime = time.perf_counter() - c1_start
    write_claim_1_bundle(c1_result, c1_runtime, c1_passed)

    c3_start = time.perf_counter()
    c3_passed, c3_result = verify_claim_3()
    c3_runtime = time.perf_counter() - c3_start
    write_claim_3_bundle(c3_result, c3_runtime, c3_passed)

    summary = {
        "claim_1": "VERIFIED" if c1_passed else "FALSIFIED",
        "claim_3": "VERIFIED" if c3_passed else "FALSIFIED",
        "fixed_command": FIXED_COMMAND,
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(ARTIFACTS / "round_1a_summary.json", summary)
    write_json(
        ARTIFACTS / "round_1a_manifest.json",
        manifest(ARTIFACTS / "claim_1") + manifest(ARTIFACTS / "claim_3"),
    )

    print("=" * 78)
    print("ROUND 1A — EXACT FINITE-SUPPORT THEOREM CONTRACTS")
    print("=" * 78)
    print(
        f"Claim 1: {summary['claim_1']} — "
        f"{len(c1_result['checks'])} exact add/remove checks; "
        f"{len(c1_result['scope_checks'])} k=2 scope checks"
    )
    print(
        f"Claim 3: {summary['claim_3']} — "
        f"{len(c3_result['checks'])} exact transformations; "
        f"{len(c3_result['unified_allocation_then_subsampling'])} unified checks"
    )
    print(
        "Negative controls rejected: "
        f"C1 {sum(r['rejected'] for r in c1_result['negative_controls'])}/"
        f"{len(c1_result['negative_controls'])}; "
        f"C3 {sum(r['rejected'] for r in c3_result['negative_controls'])}/"
        f"{len(c3_result['negative_controls'])}"
    )
    print(f"Artifacts: {ARTIFACTS.relative_to(Path.cwd())}")
    print(f"SUMMARY_JSON={summary}")
    return 0 if c1_passed and c3_passed else 1
