"""Fixed entry point for the claim-by-claim reproduction."""

from __future__ import annotations

from verify_algorithm_contract import main as verify_algorithm
from verify_exact_theorems import main as verify_exact
from verify_numerical_comparison import main as verify_numerical
from verify_preamble import main as verify_preamble


def main() -> int:
    """Run every accepted claim gate; any failing suite fails the node."""
    exact_status = verify_exact()
    algorithm_status = verify_algorithm()
    numerical_status = verify_numerical()
    preamble_status = verify_preamble()
    print(
        "CUMULATIVE_STATUS="
        f"{{'claims_1_3': {exact_status}, 'claim_2': {algorithm_status}, "
        f"'claim_4': {numerical_status}, 'claim_6': {preamble_status}}}"
    )
    return (
        0
        if exact_status == 0
        and algorithm_status == 0
        and numerical_status == 0
        and preamble_status == 0
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
