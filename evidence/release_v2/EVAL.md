# Judge-aligned release evaluation

The fixed cumulative command was executed on Hugging Face CPU Upgrade from
commit `eb1c5a4432cd911b52fc5113e5964e25087e59bf`. The run finished successfully
in 2h39m and printed:

- `CUMULATIVE_STATUS={'claims_1_3': 0, 'claim_2': 0, 'claim_4': 0, 'claim_5': 0, 'claim_6': 0, 'judge_release': 0}`
- `JUDGE_RELEASE_ALL_PASSED=True`

Claims 1–4 are `VERIFIED`. Claims 5–6 are `FALSIFIED` as exactly registered
because their figure locators are incorrect; their substantive numerical
statements are independently `VERIFIED`.

The complete captured run log is `cumulative_run.log`. Its SHA-256 is
`dd1f0947e66d2e7822ff777ce7dd28fd52404071345f7bc5fce40c09c89ae9f2`.

This result is pre-publication evidence. It does not claim a live judge score.
