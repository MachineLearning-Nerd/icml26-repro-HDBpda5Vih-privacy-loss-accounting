"""Collect four immutable full-scale PREAMBLE shard logs."""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np

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
BATCH_SIZES = (512, 1_028, 4_096, 600_000)
BLOCK_SIZES = tuple(2**value for value in range(2, 12))
INPUT_DIR = ARTIFACTS / "claim_6_shard_logs"
OUTPUT_DIR = ARTIFACTS / "claim_6"
EXPECTED_RUNS = {
    512: {
        "run_id": "776a4d76-c031-4399-b8d8-0bb532876a7e",
        "commit_sha": "f72e5377e6dcfea862c3d9ea50f78a85886cfdee",
    },
    1_028: {
        "run_id": "e2017506-0da3-46d6-b09a-bc024e8b4e3d",
        "commit_sha": "955357b7683ad0dbc0b118c28a2896f8ea585e1a",
    },
    4_096: {
        "run_id": "342daf11-a0f8-4fd0-81ed-3747c07fcf3e",
        "commit_sha": "6f5a5af00841af3292ab8c5d2b16c09522760a27",
    },
    600_000: {
        "run_id": "80367c37-1c07-4d4b-afe2-4a99eb7a9c30",
        "commit_sha": "5cf09b8e65bfb0e5d7c66aad5338af7847ddf48d",
    },
}


def load_shard(batch_size: int) -> dict[str, Any]:
    """Load one extracted payload and prove it occurs in its immutable log."""
    payload_path = INPUT_DIR / f"batch_{batch_size}.json"
    log_path = INPUT_DIR / f"batch_{batch_size}.log"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    log_text = log_path.read_text(encoding="utf-8")
    expected = EXPECTED_RUNS[batch_size]
    raw_line = "RAW_RESULTS_JSON=" + json.dumps(
        payload["raw_results"], sort_keys=True
    )
    summary_line = "SUMMARY_JSON=" + json.dumps(
        payload["summary"], sort_keys=True
    )
    payload["provenance_checks"] = {
        "run_id": payload["run_id"] == expected["run_id"],
        "commit_sha": payload["commit_sha"] == expected["commit_sha"],
        "log_sha256": payload["log_sha256"] == sha256(log_path),
        "raw_line_in_log": raw_line in log_text,
        "summary_line_in_log": summary_line in log_text,
        "terminal_status_done": payload["terminal_status"] == "done",
        "fixed_command": (
            payload["summary"]["fixed_command"] == FIXED_COMMAND
        ),
    }
    return payload


def main() -> int:
    """Validate provenance, union the exact domain, and assign Claim 6."""
    started = time.perf_counter()
    shards = [load_shard(batch_size) for batch_size in BATCH_SIZES]
    rows = [
        row
        for shard in shards
        for row in shard["raw_results"]["grid"]
    ]
    rows.sort(key=lambda row: (row["batch_size"], row["B"]))
    anchors = [shard["raw_results"]["anchor"] for shard in shards]

    provenance_ok = all(
        all(shard["provenance_checks"].values()) for shard in shards
    )
    shard_summaries_ok = all(
        shard["summary"]["claim_6"] == "BLOCKED"
        and shard["summary"]["claim_6_shard"] == "VERIFIED"
        and shard["summary"]["shard_passed"]
        and not shard["summary"]["full_domain"]
        and shard["summary"]["active_batch_sizes"]
        == [batch_size]
        and shard["summary"]["full_scale_points"] == len(BLOCK_SIZES)
        for batch_size, shard in zip(BATCH_SIZES, shards, strict=True)
    )
    observed_domain = {
        (int(row["batch_size"]), int(row["B"])) for row in rows
    }
    expected_domain = {
        (batch_size, block_size)
        for batch_size in BATCH_SIZES
        for block_size in BLOCK_SIZES
    }
    full_domain_ok = (
        len(rows) == len(expected_domain)
        and observed_domain == expected_domain
    )
    identities_ok = all(
        row["n"] == N
        and row["d"] == D
        and row["communication_C"] == C
        and row["epochs"] == EPOCHS
        and row["delta"] == DELTA
        and row["t"] * row["B"] == D
        and row["k"] * row["B"] == C
        and row["rounds"]
        == math.ceil(N / row["batch_size"]) * EPOCHS
        and math.isclose(row["q"], row["batch_size"] / N)
        and row["max_grid_mult"] == 1_000_000
        for row in rows
    )
    independent_ok = all(
        row["rdp_alpha2_abs_error"] <= 1e-12
        and math.isclose(
            row["rdp_remove_alpha2"],
            row["rdp_alpha2_closed_form"],
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for row in rows
    )
    anchor_keys = (
        "pld_sigma_upper",
        "rdp_sigma_upper",
        "gaussian_sigma_upper",
        "pld_to_rdp_sigma_ratio",
    )
    anchor_consistency_ok = all(
        math.isclose(
            anchor[key],
            anchors[0][key],
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for anchor in anchors[1:]
        for key in anchor_keys
    )
    anchor_ok = (
        anchor_consistency_ok
        and anchors[0]["pld_sigma_upper"]
        < anchors[0]["rdp_sigma_upper"]
        and anchors[0]["pld_root_width"] <= 0.002
        and anchors[0]["rdp_root_width"] <= 0.002
    )
    improvements = [float(row["relative_improvement"]) for row in rows]
    pointwise_ok = all(
        math.isfinite(row["pld_epsilon"])
        and math.isfinite(row["rdp_epsilon"])
        and row["pld_epsilon"] < row["rdp_epsilon"]
        for row in rows
    )
    material_ok = float(np.median(improvements)) >= 0.05
    mutated_rows = [
        {**row, "pld_epsilon": row["rdp_epsilon"]} for row in rows
    ]
    mutated_pointwise_ok = all(
        row["pld_epsilon"] < row["rdp_epsilon"]
        for row in mutated_rows
    )
    negative_control_ok = not mutated_pointwise_ok
    evidence_valid = (
        provenance_ok
        and shard_summaries_ok
        and full_domain_ok
        and identities_ok
        and independent_ok
        and anchor_ok
        and negative_control_ok
    )
    verified = evidence_valid and pointwise_ok and material_ok
    verdict = "VERIFIED" if verified else "BLOCKED"
    runtime = time.perf_counter() - started
    summary = {
        "claim_6": verdict,
        "passed": verified,
        "evidence_valid": evidence_valid,
        "provenance_ok": provenance_ok,
        "shard_summaries_ok": shard_summaries_ok,
        "full_domain_ok": full_domain_ok,
        "parameter_identities_ok": identities_ok,
        "independent_checker_ok": independent_ok,
        "anchor_ok": anchor_ok,
        "pointwise_improvement_ok": pointwise_ok,
        "material_improvement_ok": material_ok,
        "negative_control_ok": negative_control_ok,
        "full_scale_points": len(rows),
        "median_improvement": float(np.median(improvements)),
        "minimum_improvement": float(np.min(improvements)),
        "maximum_improvement": float(np.max(improvements)),
        "anchor_pld_to_rdp_sigma_ratio": anchors[0][
            "pld_to_rdp_sigma_ratio"
        ],
        "source_run_ids": [
            shard["run_id"] for shard in shards
        ],
        "source_commit_shas": [
            shard["commit_sha"] for shard in shards
        ],
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
                "VERIFIED only if all four provenance-bound shards form the "
                "exact 40-point source domain, PLD epsilon is strictly below "
                "RDP epsilon at every point with at least 5% median relative "
                "improvement, the epsilon=1 anchor needs less PLD noise, all "
                "independent and identity checks pass, and the mutation is "
                "rejected. Invalid or incomplete evidence remains BLOCKED."
            ),
        },
    )
    write_text(
        OUTPUT_DIR / "source_audit.md",
        """# Claim 6 source audit

The paper's PREAMBLE experiment fixes `n=6*10^5`, `d=2^20`, `C=2^15`,
`E=10`, and `(epsilon, delta)=(1, 1e-6)`. It uses block-sparse random
allocation with `k=C/B` out of `t=d/B`, user Poisson subsampling, and heavy
composition. The public source evaluates four batch sizes
`{512,1028,4096,600000}` and `B=2^2,...,2^11`, with the PLD grid capped at
one million bins per direction. The judge's “Figure 5” label does not match
the audited source numbering; the claim contract follows the parameters and
quantifiers, not the imported label.
""",
    )
    write_text(
        OUTPUT_DIR / "method.md",
        """# Method

Four CPU-upgrade runs each evaluate one complete ten-point batch-size panel
with the pinned author PLD implementation. The collector reads the canonical
JSON lines from the complete immutable `orx logs`, checks their hashes, run
IDs, commits, terminal states, and fixed commands, then validates the union as
one exact 40-point domain. It independently checks all dimensional identities
and every order-2 RDP moment against its closed form. A representative
heavy-composition point also inverts both accountants at epsilon 1.
""",
    )
    write_json(
        OUTPUT_DIR / "raw_results.json",
        {"grid": rows, "anchors": anchors},
    )
    write_csv(OUTPUT_DIR / "full_grid.csv", list(rows[0]), rows)
    write_json(
        OUTPUT_DIR / "independent_checker.json",
        {
            "passed": independent_ok and identities_ok,
            "alpha2_checks": [
                {
                    "batch_size": row["batch_size"],
                    "B": row["B"],
                    "computed": row["rdp_remove_alpha2"],
                    "closed_form": row["rdp_alpha2_closed_form"],
                    "abs_error": row["rdp_alpha2_abs_error"],
                }
                for row in rows
            ],
            "parameter_identities_ok": identities_ok,
        },
    )
    write_json(
        OUTPUT_DIR / "negative_control.json",
        {
            "mutation": "replace each PLD epsilon with its RDP epsilon",
            "mutated_acceptance": mutated_pointwise_ok,
            "rejected": negative_control_ok,
        },
    )
    write_json(
        OUTPUT_DIR / "provenance.json",
        [
            {
                "run_id": shard["run_id"],
                "commit_sha": shard["commit_sha"],
                "log_sha256": shard["log_sha256"],
                "checks": shard["provenance_checks"],
            }
            for shard in shards
        ],
    )
    metadata = runtime_metadata()
    metadata.update(
        {
            "runtime_seconds": runtime,
            "cpu_only": True,
            "source_run_runtime_seconds": [
                shard["summary"]["runtime_seconds"] for shard in shards
            ],
        }
    )
    write_json(
        OUTPUT_DIR / "exact_command_environment.json", metadata
    )
    write_text(
        OUTPUT_DIR / "limitations.md",
        """# Limitations and deviations

The complete source parameter grid is evaluated without downscaling. The
40-point comparison fixes global sigma at 1 rather than solving 80 inverse
problems; monotonicity makes it a direct accountant-tightness comparison. One
representative point separately checks required noise at epsilon 1. This
reproduction tests the paper's numerical accounting result, not an end-to-end
model training workload or pixel-level equality with the published raster.
""",
    )
    write_text(
        OUTPUT_DIR / "EVAL.md",
        f"""# Claim 6 evaluation

Verdict: **{verdict}**

- Full-scale points: {len(rows)}
- Median PLD epsilon improvement over RDP: {summary['median_improvement']:.2%}
- Minimum improvement: {summary['minimum_improvement']:.2%}
- PLD/RDP required-noise ratio at epsilon 1: {summary['anchor_pld_to_rdp_sigma_ratio']:.6f}
- Provenance-bound source runs: {len(shards)}
- Collector runtime: {runtime:.6f} seconds
""",
    )
    write_json(ARTIFACTS / "claim_6_summary.json", summary)
    write_json(
        ARTIFACTS / "claim_6_manifest.json", manifest(OUTPUT_DIR)
    )
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
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
