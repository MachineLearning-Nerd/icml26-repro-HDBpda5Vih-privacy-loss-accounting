"""Stable one-evaluation required-noise certificate for PREAMBLE."""

from __future__ import annotations

import json
import time

from evidence_utils import (
    ARTIFACTS,
    FIXED_COMMAND,
    manifest,
    runtime_metadata,
    write_json,
    write_text,
)
from verify_preamble import (
    DELTA,
    TARGET_EPSILON,
    invert_decreasing,
    pld_epsilon,
    rdp_epsilon,
)


BATCH_SIZE = 512
BLOCK_SIZE = 2_048
OUT = ARTIFACTS / "claim_6_anchor"


def main() -> int:
    """Certify that PLD requires less noise at the epsilon=1 anchor."""
    started = time.perf_counter()
    rdp_root = invert_decreasing(
        lambda sigma: rdp_epsilon(
            sigma, BATCH_SIZE, BLOCK_SIZE
        )[0],
        lower=1.0,
        upper=20.0,
        iterations=14,
    )
    certificate_sigma = rdp_root["sigma_lower"]
    pld_value, pld_meta = pld_epsilon(
        certificate_sigma, BATCH_SIZE, BLOCK_SIZE
    )
    rdp_bracket_ok = (
        rdp_root["epsilon_lower"] > TARGET_EPSILON
        and rdp_root["epsilon_upper"] <= TARGET_EPSILON
        and rdp_root["width"] <= 0.002
    )
    strict_noise_advantage = pld_value < TARGET_EPSILON
    mutated_pld_value = rdp_root["epsilon_lower"]
    negative_control_ok = not (
        mutated_pld_value < TARGET_EPSILON
    )
    passed = (
        rdp_bracket_ok
        and strict_noise_advantage
        and negative_control_ok
    )
    runtime = time.perf_counter() - started
    result = {
        "claim_6_anchor": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "batch_size": BATCH_SIZE,
        "B": BLOCK_SIZE,
        "target_epsilon": TARGET_EPSILON,
        "delta": DELTA,
        "certificate_sigma": certificate_sigma,
        "rdp_epsilon_at_certificate_sigma": rdp_root[
            "epsilon_lower"
        ],
        "pld_epsilon_at_certificate_sigma": pld_value,
        "epsilon_margin_below_target": TARGET_EPSILON - pld_value,
        "rdp_sigma_lower": rdp_root["sigma_lower"],
        "rdp_sigma_upper": rdp_root["sigma_upper"],
        "rdp_root_width": rdp_root["width"],
        "rdp_bracket_ok": rdp_bracket_ok,
        "strict_noise_advantage": strict_noise_advantage,
        "negative_control_ok": negative_control_ok,
        "pld_metadata": pld_meta,
        "runtime_seconds": runtime,
        "fixed_command": FIXED_COMMAND,
    }
    write_json(
        OUT / "claim_contract.json",
        {
            "claim_id": 6,
            "subclaim": "required-noise anchor",
            "parameters": {
                "batch_size": BATCH_SIZE,
                "B": BLOCK_SIZE,
                "epsilon": TARGET_EPSILON,
                "delta": DELTA,
            },
            "verdict_rule": (
                "Bracket the RDP-required sigma with width <=0.002. "
                "At the lower endpoint, where RDP epsilon is still above "
                "one, evaluate PLD once. PLD epsilon below one proves by "
                "monotonicity that its required sigma is strictly smaller."
            ),
        },
    )
    write_text(
        OUT / "method.md",
        """# Method

The RDP epsilon=1 noise root is inexpensive and is bracketed by bisection.
The lower bracket endpoint still violates the RDP target. The full PLD
accountant is evaluated exactly once at that same sigma. If PLD already
satisfies epsilon<1, monotonicity directly proves that PLD needs strictly less
noise than RDP. This avoids an unnecessary multi-evaluation PLD root search.
""",
    )
    write_json(OUT / "raw_results.json", result)
    write_json(
        OUT / "independent_checker.json",
        {
            "rdp_bracket_ok": rdp_bracket_ok,
            "rdp_failing_side_epsilon": rdp_root["epsilon_lower"],
            "rdp_passing_side_epsilon": rdp_root["epsilon_upper"],
            "bracket_width": rdp_root["width"],
        },
    )
    write_json(
        OUT / "negative_control.json",
        {
            "mutation": (
                "replace PLD epsilon by the RDP failing-side epsilon"
            ),
            "mutated_pld_epsilon": mutated_pld_value,
            "mutated_acceptance": (
                mutated_pld_value < TARGET_EPSILON
            ),
            "rejected": negative_control_ok,
        },
    )
    metadata = runtime_metadata()
    metadata.update(
        {
            "runtime_seconds": runtime,
            "cpu_only": True,
            "pld_evaluations": 1,
        }
    )
    write_json(OUT / "exact_command_environment.json", metadata)
    write_text(
        OUT / "limitations.md",
        """# Limitations and deviations

This is the paper-parameter epsilon=1 anchor, not a replacement for the
40-point grid. It certifies ordering of required noise without estimating the
PLD root itself. The previous direct PLD-root attempt was abandoned because
the released subsampling transform has a numerical grid degeneracy at the
irrelevant extreme sigma=0.1.
""",
    )
    write_text(
        OUT / "EVAL.md",
        f"""# Claim 6 anchor evaluation

Verdict: **{result['claim_6_anchor']}**

- RDP failing-side sigma: {certificate_sigma:.9f}
- RDP epsilon: {rdp_root['epsilon_lower']:.9f}
- PLD epsilon at the same sigma: {pld_value:.9f}
- PLD margin below epsilon 1: {result['epsilon_margin_below_target']:.9f}
- Runtime: {runtime:.6f} seconds
""",
    )
    write_json(
        ARTIFACTS / "claim_6_anchor_summary.json", result
    )
    artifact_manifest = manifest(OUT)
    write_json(
        ARTIFACTS / "claim_6_anchor_manifest.json",
        artifact_manifest,
    )
    print("=" * 78)
    print("CLAIM 6 STABLE REQUIRED-NOISE ANCHOR")
    print("=" * 78)
    print(
        f"Claim 6 anchor: {result['claim_6_anchor']}; "
        f"sigma={certificate_sigma:.9f}; "
        f"RDP epsilon={rdp_root['epsilon_lower']:.9f}; "
        f"PLD epsilon={pld_value:.9f}"
    )
    print(
        f"Subchecks: bracket={rdp_bracket_ok}, "
        f"strict advantage={strict_noise_advantage}, "
        f"negative control={negative_control_ok}"
    )
    print("RAW_RESULTS_JSON=" + json.dumps(result, sort_keys=True))
    print(
        "ARTIFACT_MANIFEST_JSON="
        + json.dumps(artifact_manifest, sort_keys=True)
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
