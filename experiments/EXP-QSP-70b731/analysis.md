# EXP-QSP-70b731 analysis

Review of the archived Band L census for `H-QSP-cd0c90`. The
coordinator subagent could not be launched (model usage quota on
inherit, resolved as grok-4.7-high-fast), so this session executed
`TASK-20261009-ab979f` against the pre-committed prior
`ef2acf35ae773392fff1845afafd98ba8d75b78d`. Amazon Bedrock was not
selected. No Magma, Sage, or AUXIN. No new stage was executed.

## Observation

`RESULTS.md` and `execution-report.yaml` are absent. Band L `n' = 3`
`RUN-QSP-097ecd` is `output_validated`. Its raw file has 244 rows,
`agreement_ok` true, and 0 disagreements. 182 rows have a positive
count and 62 have count 0. Every `certificate_path` is null, and the
run directory has no root-list certificate file. The same 244 / 182 /
62 split, with `agreement_ok` true, is the summary on every Band L
cell `n' = 3..14`. Certificate kind is `none`.

Stage 0 `RUN-QSP-1df59e` has `hand_gate_ok` true. Stage 1
`RUN-QSP-9312f7` summary says `all_agree` true, `rows_completed` 756,
`certificate_bearing` 575, and `zero_N_rows` 181, while its in-file
`rows` list is empty and its directory has no certificate file.

Stage 3 `RUN-QSP-715b58` is `claim_expired` on trial
`stage3-bridge-n22`. The span from
`2026-09-21T04:33:17.259316+00:00` to
`2026-09-21T07:23:17.027386+00:00` is 10199.76807 seconds. It has no
raw result. `RUN-QSP-ef2490` is `infrastructure_error` on that same
trial. `RUN-QSP-cec70a` is an earlier Stage-0 `infrastructure_error`.
No Band H raw result is present.

## Comparison

Success requires S1 through S5 together. S5 requires a
wrapper-re-verified root list for every positive count and a
certificate-bearing count that matches files on disk. The Band L
directories have zero such files, so the recorded
`certificate_bearing` value 182 is F_acct. F_acct invalidates the
success headline. It does not by itself say the two instruments
disagreed: the archived rows still report `agree: true`. R2 is the
claim that those Band L counts are exact and certified. The files
that would certify them are absent, so R2 is not supported.

R1 needs Band H `n' in {33, 44, 66}` against the sealed census. Those
runs are not in the tree. R3 needs the bridge `n' = 22`. The bridge
attempt expired and a later attempt stopped in `preexec_fn`. Both are
F6. F6 is not negative mathematical evidence, so the expiry does not
weaken R1 or R3.

## Inference

The decision is `refine`. Direction is neutral. Strength is
inconclusive. `claim_tier` stays crypto because that label in this
contract names the `n = 131` field, not an ECDLP solve, and this
review does not treat the tier as a success. `proof_status` is
`not_applicable`. Hypothesis `H-QSP-cd0c90` stays `approved`.
Experiment status moves from `approved` to `invalid`.
`authorizes_rerun` is false. No goal head is edited.

## Limitation

No discrete logarithm and no exponent were claimed or recovered.
`certificate.kind: none` is not a solve certificate. Band L agreement
without root lists is not a certified `N_K(L)` headline. PD-1
concentrates J1, J2, and J3 in one task, and that task ran in the
session that wrote the prior because the coordinator subagent could
not start. The prior was not rewritten.
