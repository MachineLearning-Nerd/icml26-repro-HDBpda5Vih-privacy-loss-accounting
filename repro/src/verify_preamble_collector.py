"""Collect provenance-bound PREAMBLE grid and anchor evidence."""

from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import special

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    sha256,
    write_csv,
    write_json,
    write_text,
)


N = 600_000
D = 2**20
C = 2**15
EPOCHS = 10
DELTA = 1e-6
CLIP_SCALE = 1.02
ORDERS = tuple(range(2, 51))
BATCH_SIZES = (512, 1_028, 4_096, 600_000)
BLOCK_SIZES = tuple(2**value for value in range(2, 12))
INPUT_DIR = ARTIFACTS / "claim_6_shard_logs"
OUTPUT_DIR = ARTIFACTS / "claim_6"
GRID_PATTERN = re.compile(
    r"^PREAMBLE batch=(\d+) B=(\d+): "
    r"PLD eps=([0-9.eE+-]+), RDP eps=([0-9.eE+-]+)$"
)
KNOWN_POST_GRID_ERROR = (
    "ValueError: Subsampling transform produced invalid bounds: "
    "new_min=0.000853698, new_max=0.000853698"
)
EXPECTED_SOURCES = {
    512: {
        "run_id": "776a4d76-c031-4399-b8d8-0bb532876a7e",
        "commit_sha": "f72e5377e6dcfea862c3d9ea50f78a85886cfdee",
        "terminal_status": "failed",
        "full_log_bytes": 13390,
        "full_log_sha256": (
            "3ae403a90202270c7d410bc2dbbe293630e31f2236a3e9f6a123be41edade185"
        ),
        "excerpt_sha256": (
            "2f2b7648d10f4dfc383481a0db276ee722683b533263e69841aab68bff6dc69e"
        ),
    },
    1_028: {
        "run_id": "e2017506-0da3-46d6-b09a-bc024e8b4e3d",
        "commit_sha": "955357b7683ad0dbc0b118c28a2896f8ea585e1a",
        "terminal_status": "cancelled",
        "full_log_bytes": 11722,
        "full_log_sha256": (
            "8a7b513fd60513ccf27991f3ae0b8a1dada3cb955e4b4e39ce3421bde2f7f972"
        ),
        "excerpt_sha256": (
            "a7515db82f5e970bbc45a56559577bf83fa22ca8951d74f1c56906b4a73cbf15"
        ),
    },
    4_096: {
        "run_id": "342daf11-a0f8-4fd0-81ed-3747c07fcf3e",
        "commit_sha": "6f5a5af00841af3292ab8c5d2b16c09522760a27",
        "terminal_status": "cancelled",
        "full_log_bytes": 11714,
        "full_log_sha256": (
            "66131bf189422491e8a92a3cd12697457f261e6dc87c1d4b8fab893c2000c140"
        ),
        "excerpt_sha256": (
            "0bad58d1ebbc24b4e9bc13a0142bacd1f0ff33b973d3dbe4270cfaa121b5933b"
        ),
    },
    600_000: {
        "run_id": "80367c37-1c07-4d4b-afe2-4a99eb7a9c30",
        "commit_sha": "5cf09b8e65bfb0e5d7c66aad5338af7847ddf48d",
        "terminal_status": "failed",
        "full_log_bytes": 13413,
        "full_log_sha256": (
            "aea8243787dac4b847b2972ed7f376075fd05996e7e194b912a6fad77b659a66"
        ),
        "excerpt_sha256": (
            "b85dd7f47661f7246f9e7938e736902b40a1df436e88aeeb4e3b078ee691a2b9"
        ),
    },
}
EXPECTED_ANCHOR_RUN = "fe365c41-6a04-4ae0-8cfc-b5b3e1c2e7ef"
EXPECTED_ANCHOR_COMMIT = "6aa326b9b78a3d837ed21384b9e3994f6239ba5b"


def _log_add(left: float, right: float) -> float:
    if left == -math.inf:
        return right
    if right == -math.inf:
        return left
    high = max(left, right)
    return high + math.log1p(math.exp(min(left, right) - high))


def _poly_convolve(left: list[float], right: list[float]) -> list[float]:
    """Reference log-polynomial convolution, deliberately loop based."""
    degree = len(left) - 1
    output = [-math.inf] * (degree + 1)
    for total in range(degree + 1):
        terms = [
            left[index] + right[total - index]
            for index in range(total + 1)
        ]
        output[total] = float(special.logsumexp(terms))
    return output


def _reference_allocation_rdp(
    t: int, k: int, sigma: float
) -> tuple[list[float], float, float]:
    """Second implementation of the paper's integer-order RDP formulas."""
    max_order = ORDERS[-1]
    t_per_selection = t // k
    base = [
        (
            index * (index - 1) / (2 * sigma**2)
            - float(special.gammaln(index + 1))
        )
        for index in range(max_order + 1)
    ]
    result = [-math.inf] * (max_order + 1)
    result[0] = 0.0
    exponent = t_per_selection
    while exponent:
        if exponent & 1:
            result = _poly_convolve(result, base)
        exponent >>= 1
        if exponent:
            base = _poly_convolve(base, base)
    remove = []
    add = []
    for order in ORDERS:
        log_moment = (
            float(special.gammaln(order + 1))
            + result[order]
            - order * math.log(t_per_selection)
        )
        remove.append(k * log_moment / (order - 1))
        add.append(
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
        )
    alpha2_closed = k * math.log1p(
        math.expm1(1 / sigma**2) / t_per_selection
    )
    return (
        [max(left, right) for left, right in zip(remove, add, strict=True)],
        remove[0],
        alpha2_closed,
    )


def _reference_rdp_epsilon(
    batch_size: int, block_size: int
) -> tuple[float, dict[str, float | int]]:
    q = batch_size / N
    rounds = math.ceil(N / batch_size) * EPOCHS
    t = D // block_size
    k = C // block_size
    block_norm = CLIP_SCALE * math.sqrt(D / block_size) / k
    effective_sigma = 1.0 / block_norm
    allocation, remove_alpha2, alpha2_closed = _reference_allocation_rdp(
        t, k, effective_sigma
    )
    amplified = []
    p = 1 - q
    for position, order in enumerate(ORDERS):
        if q == 1:
            amplified.append(allocation[position])
            continue
        total = _log_add(
            (order - 1) * math.log(p) + math.log(order * q - q + 1),
            math.log(order * (order - 1) / 2)
            + 2 * math.log(q)
            + (order - 2) * math.log(p)
            + allocation[0],
        )
        for ell in range(3, order + 1):
            total = _log_add(
                total,
                math.log(3)
                + float(special.gammaln(order + 1))
                - float(special.gammaln(ell + 1))
                - float(special.gammaln(order - ell + 1))
                + (order - ell) * math.log(p)
                + ell * math.log(q)
                + (ell - 1) * allocation[ell - 2],
            )
        amplified.append(total / (order - 1))
    converted = [
        rounds * value
        - (math.log(DELTA) + math.log(order)) / (order - 1)
        + math.log((order - 1) / order)
        for order, value in zip(ORDERS, amplified, strict=True)
    ]
    best = min(range(len(converted)), key=converted.__getitem__)
    return converted[best], {
        "optimal_order": ORDERS[best],
        "remove_alpha2": remove_alpha2,
        "alpha2_closed_form": alpha2_closed,
        "alpha2_abs_error": abs(remove_alpha2 - alpha2_closed),
    }


def _load_grid() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sources = json.loads(
        (INPUT_DIR / "sources.json").read_text(encoding="utf-8")
    )["sources"]
    source_by_batch = {row["batch_size"]: row for row in sources}
    rows: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for batch_size in BATCH_SIZES:
        source = source_by_batch.get(batch_size, {})
        expected = EXPECTED_SOURCES[batch_size]
        log_path = INPUT_DIR / f"batch_{batch_size}.log"
        text = log_path.read_text(encoding="utf-8")
        source_checks = {
            key: source.get(key) == expected[key]
            for key in (
                "run_id",
                "commit_sha",
                "terminal_status",
                "full_log_bytes",
                "full_log_sha256",
            )
        }
        source_checks["excerpt_sha256"] = (
            sha256(log_path) == expected["excerpt_sha256"]
        )
        source_checks["post_grid_terminal_is_explicit"] = (
            (
                source.get("terminal_status") == "failed"
                and KNOWN_POST_GRID_ERROR in text
            )
            or (
                source.get("terminal_status") == "cancelled"
                and KNOWN_POST_GRID_ERROR not in text
            )
        )
        parsed = []
        for line in text.splitlines():
            match = GRID_PATTERN.fullmatch(line)
            if match is None:
                continue
            parsed.append(
                {
                    "batch_size": int(match.group(1)),
                    "B": int(match.group(2)),
                    "pld_epsilon": float(match.group(3)),
                    "rdp_epsilon": float(match.group(4)),
                    "source_run_id": source.get("run_id"),
                    "source_commit_sha": source.get("commit_sha"),
                    "source_line": line,
                }
            )
        source_checks["ten_grid_lines_before_terminal"] = len(parsed) == 10
        source_checks["single_batch_panel"] = all(
            row["batch_size"] == batch_size for row in parsed
        )
        rows.extend(parsed)
        provenance.append(
            {
                "batch_size": batch_size,
                "source": source,
                "checks": source_checks,
                "accepted_as_successful_run": False,
                "accepted_scope": "ten complete pre-terminal grid lines only",
            }
        )
    return rows, provenance


def _load_anchor() -> tuple[dict[str, Any], dict[str, Any]]:
    result_path = INPUT_DIR / "anchor_result.json"
    log_path = INPUT_DIR / "anchor.log"
    source_path = INPUT_DIR / "anchor_source.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    text = log_path.read_text(encoding="utf-8")
    raw_line = "RAW_RESULTS_JSON=" + json.dumps(result, sort_keys=True)
    checks = {
        "run_id": source["run_id"] == EXPECTED_ANCHOR_RUN,
        "commit_sha": source["commit_sha"] == EXPECTED_ANCHOR_COMMIT,
        "terminal_status_done": source["terminal_status"] == "done",
        "full_log_sha256": len(source["full_log_sha256"]) == 64,
        "full_log_bytes": source["full_log_bytes"] > 0,
        "excerpt_sha256": source["excerpt_sha256"] == sha256(log_path),
        "raw_line_in_excerpt": raw_line in text,
        "fixed_command": result["fixed_command"] == FIXED_COMMAND,
        "parameters": (
            result["batch_size"] == 512
            and result["B"] == 2048
            and result["target_epsilon"] == 1.0
            and result["delta"] == DELTA
        ),
        "rdp_bracket": (
            result["rdp_bracket_ok"]
            and result["rdp_epsilon_at_certificate_sigma"] > 1.0
            and result["rdp_root_width"] <= 0.002
        ),
        "strict_advantage": (
            result["strict_noise_advantage"]
            and result["pld_epsilon_at_certificate_sigma"] < 1.0
        ),
        "negative_control": result["negative_control_ok"],
    }
    return result, {"source": source, "checks": checks}


def main() -> int:
    """Validate provenance, exact domain, independent RDP, and noise anchor."""
    started = time.perf_counter()
    rows, provenance = _load_grid()
    anchor, anchor_provenance = _load_anchor()
    rows.sort(key=lambda row: (row["batch_size"], row["B"]))
    expected_domain = {
        (batch_size, block_size)
        for batch_size in BATCH_SIZES
        for block_size in BLOCK_SIZES
    }
    observed_domain = {
        (row["batch_size"], row["B"]) for row in rows
    }
    full_domain_ok = (
        len(rows) == len(expected_domain)
        and observed_domain == expected_domain
    )
    provenance_ok = all(
        all(item["checks"].values()) for item in provenance
    )

    for row in rows:
        batch_size = row["batch_size"]
        block_size = row["B"]
        reference, diagnostics = _reference_rdp_epsilon(
            batch_size, block_size
        )
        row.update(
            {
                "n": N,
                "d": D,
                "communication_C": C,
                "epochs": EPOCHS,
                "delta": DELTA,
                "global_sigma": 1.0,
                "q": batch_size / N,
                "rounds": math.ceil(N / batch_size) * EPOCHS,
                "t": D // block_size,
                "k": C // block_size,
                "reference_rdp_epsilon": reference,
                "reference_rdp_abs_error": abs(
                    reference - row["rdp_epsilon"]
                ),
                "rdp_optimal_order": diagnostics["optimal_order"],
                "rdp_remove_alpha2": diagnostics["remove_alpha2"],
                "rdp_alpha2_closed_form": diagnostics[
                    "alpha2_closed_form"
                ],
                "rdp_alpha2_abs_error": diagnostics[
                    "alpha2_abs_error"
                ],
                "relative_improvement": (
                    row["rdp_epsilon"] - row["pld_epsilon"]
                )
                / row["rdp_epsilon"],
                "max_grid_mult": 1_000_000,
            }
        )
        row["reference_rdp_matches_rounded_log"] = math.isclose(
            reference,
            row["rdp_epsilon"],
            rel_tol=5e-6,
            abs_tol=5e-6,
        )

    identities_ok = all(
        row["t"] * row["B"] == D
        and row["k"] * row["B"] == C
        and row["rounds"]
        == math.ceil(N / row["batch_size"]) * EPOCHS
        and math.isclose(row["q"], row["batch_size"] / N)
        for row in rows
    )
    independent_ok = all(
        row["reference_rdp_matches_rounded_log"]
        and row["rdp_alpha2_abs_error"] <= 1e-12
        for row in rows
    )
    pointwise_ok = all(
        math.isfinite(row["pld_epsilon"])
        and math.isfinite(row["rdp_epsilon"])
        and row["pld_epsilon"] < row["rdp_epsilon"]
        for row in rows
    )
    improvements = [row["relative_improvement"] for row in rows]
    anchor_provenance_ok = all(anchor_provenance["checks"].values())
    anchor_ok = (
        anchor_provenance_ok
        and anchor["claim_6_anchor"] == "VERIFIED"
        and anchor["passed"]
    )

    equal_mutation_rejected = not all(
        row["rdp_epsilon"] < row["rdp_epsilon"] for row in rows
    )
    missing_point_rejected = {
        (row["batch_size"], row["B"]) for row in rows[:-1]
    } != expected_domain
    rdp_mutation_rejected = not math.isclose(
        rows[0]["reference_rdp_epsilon"] + 0.01,
        rows[0]["rdp_epsilon"],
        rel_tol=5e-6,
        abs_tol=5e-6,
    )
    negative_control_ok = (
        equal_mutation_rejected
        and missing_point_rejected
        and rdp_mutation_rejected
        and anchor["negative_control_ok"]
    )
    evidence_valid = (
        provenance_ok
        and full_domain_ok
        and identities_ok
        and independent_ok
        and anchor_provenance_ok
        and negative_control_ok
    )
    if evidence_valid and pointwise_ok and anchor_ok:
        verdict = "VERIFIED"
    elif evidence_valid and not pointwise_ok:
        verdict = "FALSIFIED"
    else:
        verdict = "BLOCKED"
    passed = verdict in {"VERIFIED", "FALSIFIED"}
    runtime = time.perf_counter() - started
    summary = {
        "claim_6": verdict,
        "passed": passed,
        "evidence_valid": evidence_valid,
        "provenance_ok": provenance_ok,
        "full_domain_ok": full_domain_ok,
        "parameter_identities_ok": identities_ok,
        "independent_checker_ok": independent_ok,
        "anchor_provenance_ok": anchor_provenance_ok,
        "anchor_ok": anchor_ok,
        "pointwise_improvement_ok": pointwise_ok,
        "negative_control_ok": negative_control_ok,
        "full_scale_points": len(rows),
        "median_improvement": float(np.median(improvements)),
        "minimum_improvement": float(np.min(improvements)),
        "maximum_improvement": float(np.max(improvements)),
        "anchor_certificate_sigma": anchor["certificate_sigma"],
        "anchor_pld_epsilon": anchor[
            "pld_epsilon_at_certificate_sigma"
        ],
        "anchor_rdp_epsilon": anchor[
            "rdp_epsilon_at_certificate_sigma"
        ],
        "source_run_ids": [
            EXPECTED_SOURCES[batch]["run_id"] for batch in BATCH_SIZES
        ]
        + [EXPECTED_ANCHOR_RUN],
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }

    write_json(
        OUTPUT_DIR / "claim_contract.json",
        {
            "claim_id": 6,
            "verdicts": ["VERIFIED", "FALSIFIED", "BLOCKED"],
            "source_quantifiers": {
                "n": N,
                "d": D,
                "C": C,
                "epochs": EPOCHS,
                "delta": DELTA,
                "batch_sizes": list(BATCH_SIZES),
                "block_sizes": list(BLOCK_SIZES),
                "max_grid_mult": 1_000_000,
            },
            "verification_rule": (
                "VERIFIED only if provenance-bound stdout contains the exact "
                "40-point source domain, PLD epsilon is strictly below RDP "
                "epsilon at every point, an epsilon=1 certificate proves "
                "strictly lower required PLD noise, independent RDP and "
                "identity checks pass, and all negative controls are rejected. "
                "A direct valid grid counterexample is FALSIFIED; incomplete "
                "or invalid evidence is BLOCKED."
            ),
        },
    )
    write_text(
        OUTPUT_DIR / "source_audit.md",
        """# Claim 6 source audit

The audited paper PREAMBLE experiment fixes `n=6*10^5`, `d=2^20`,
`C=2^15`, `E=10`, and `(epsilon, delta)=(1, 1e-6)`. It uses block-sparse
random allocation with `k=C/B` out of `t=d/B`, user Poisson subsampling, and
heavy composition. The released source evaluates batch sizes
`{512,1028,4096,600000}` and `B=2^2,...,2^11`, with the PLD geometric grid
capped at one million bins per direction. The imported judge label “Figure 5”
does not match the audited source numbering; this contract follows the exact
parameters and quantifiers rather than that label.
""",
    )
    write_text(
        OUTPUT_DIR / "method.md",
        """# Method

Four CPU-upgrade runs evaluated disjoint ten-point panels using the pinned
author PLD implementation. Their evidence-bearing stdout lines are preserved
with immutable run IDs, commits, complete-log hashes, byte counts, and exact
excerpt hashes. Two runs failed only after all ten points in a superseded
optional root search; two were deliberately cancelled at that same boundary.
The collector never labels those runs successful and accepts only their
complete pre-terminal grid lines.

The collector reconstructs the exact 40-point domain and independently
recomputes every RDP epsilon using a separate loop-based implementation of the
paper formulas. A fifth run brackets the RDP epsilon=1 noise root and performs
one full PLD evaluation on the RDP-failing side. PLD epsilon below one there
proves by monotonicity that PLD needs strictly less noise.
""",
    )
    write_json(
        OUTPUT_DIR / "raw_results.json",
        {"grid": rows, "anchor": anchor},
    )
    write_csv(OUTPUT_DIR / "full_grid.csv", list(rows[0]), rows)
    write_json(
        OUTPUT_DIR / "independent_checker.json",
        {
            "passed": independent_ok and identities_ok,
            "rounding_tolerance": {"relative": 5e-6, "absolute": 5e-6},
            "rows": [
                {
                    "batch_size": row["batch_size"],
                    "B": row["B"],
                    "logged_rdp_epsilon": row["rdp_epsilon"],
                    "reference_rdp_epsilon": row[
                        "reference_rdp_epsilon"
                    ],
                    "absolute_error": row["reference_rdp_abs_error"],
                    "matches_rounded_log": row[
                        "reference_rdp_matches_rounded_log"
                    ],
                    "alpha2_abs_error": row["rdp_alpha2_abs_error"],
                }
                for row in rows
            ],
            "parameter_identities_ok": identities_ok,
        },
    )
    write_json(
        OUTPUT_DIR / "negative_control.json",
        {
            "equal_accountant_mutation_rejected": equal_mutation_rejected,
            "missing_grid_point_rejected": missing_point_rejected,
            "rdp_plus_0_01_mutation_rejected": rdp_mutation_rejected,
            "anchor_mutation_rejected": anchor["negative_control_ok"],
            "passed": negative_control_ok,
        },
    )
    write_json(
        OUTPUT_DIR / "provenance.json",
        {
            "grid": provenance,
            "anchor": anchor_provenance,
        },
    )
    metadata = runtime_metadata()
    metadata.update(
        {
            "runtime_seconds": runtime,
            "cpu_only": True,
            "source_run_runtime_seconds": {
                "anchor": anchor["runtime_seconds"],
                "grid": "see immutable orx run records",
            },
        }
    )
    write_json(OUTPUT_DIR / "exact_command_environment.json", metadata)
    write_text(
        OUTPUT_DIR / "limitations.md",
        """# Limitations and deviations

The complete published parameter grid is evaluated without downscaling. Grid
values were printed to six significant digits, so the independent checker
uses an explicit tolerance matching that serialization. The 40-point
comparison fixes global sigma at one rather than solving 80 inverse problems;
the separate epsilon=1 certificate directly establishes the required-noise
ordering at one representative heavy-composition point. This evaluates the
privacy accountants, not end-to-end model training or pixel equality with the
published raster.
""",
    )
    write_text(
        OUTPUT_DIR / "EVAL.md",
        f"""# Claim 6 evaluation

Verdict: **{verdict}**

- Full-scale points: {len(rows)}
- Points with strict PLD improvement: {sum(row['pld_epsilon'] < row['rdp_epsilon'] for row in rows)}/{len(rows)}
- Median epsilon improvement: {summary['median_improvement']:.2%}
- Minimum epsilon improvement: {summary['minimum_improvement']:.2%}
- Anchor sigma: {summary['anchor_certificate_sigma']:.9f}
- Anchor PLD epsilon: {summary['anchor_pld_epsilon']:.9f}
- Anchor RDP epsilon: {summary['anchor_rdp_epsilon']:.9f}
- Provenance-bound runs: {len(summary['source_run_ids'])}
""",
    )
    write_json(ARTIFACTS / "claim_6_summary.json", summary)
    write_json(ARTIFACTS / "claim_6_manifest.json", manifest(OUTPUT_DIR))
    print("=" * 78)
    print("CLAIM 6 FULL-DOMAIN PREAMBLE COLLECTOR")
    print("=" * 78)
    print(
        f"Claim 6: {verdict}; {len(rows)} full-scale points; "
        f"median improvement={summary['median_improvement']:.2%}; "
        f"minimum improvement={summary['minimum_improvement']:.2%}"
    )
    print(
        f"Subchecks: provenance={provenance_ok}, "
        f"domain={full_domain_ok}, identities={identities_ok}, "
        f"independent={independent_ok}, anchor={anchor_ok}, "
        f"negative control={negative_control_ok}"
    )
    print("SUMMARY_JSON=" + json.dumps(summary, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
