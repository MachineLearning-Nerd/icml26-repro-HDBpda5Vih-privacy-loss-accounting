# Legacy output directory

The former `outputs/verify_run.log` and `outputs/verdict.json` were generated
by a generic proxy script. Their all-pass summary does not represent the
source-pinned six-claim contracts and conflicts with the current literal
locator findings for Claims 5 and 6.

They were removed from the reader-facing surface. Use these authoritative
paths instead:

- [`repro/src/verify_pld.py`](../repro/src/verify_pld.py) — fixed cumulative runner;
- [`.openresearch/artifacts/judge_release/`](../.openresearch/artifacts/judge_release/) — registered-claim gate;
- [`.openresearch/artifacts/claim_1/` through `claim_6/`](../.openresearch/artifacts/) — claim evidence;
- [`publication_gate.json`](../publication_gate.json) — conservative status;
- [`STATUS.md`](../STATUS.md) — human-readable state.

Do not recreate proxy verdict files with the same names. New runs should use a
new evidence directory and manifest.
