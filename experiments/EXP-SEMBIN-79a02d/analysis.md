# EXP-SEMBIN-79a02d analysis

Review of Stages 0–3 for `H-SEMBIN-8e8bef`. The coordinator subagent
could not be launched (model usage quota on inherit, resolved as
grok-4.7-high-fast), so this session executed `TASK-20261006-239b78`
against the pre-committed prior
`1968df074a4edfd451f73b9e465c5f1cb8d26f75`. Amazon Bedrock was not
selected. No Magma, Sage, or AUXIN. No new census was executed.

## Observation

`RESULTS.md` and `stage2/census.json` are absent. The success
criterion requires `RESULTS.md` to name exactly one `O-*` label. That
label was not emitted.

Stage 1 `RUN-SEMBIN-bdfd41` is `completed_valid`. The gate is `PASS`
and `builder_equality_pass` is true. The n=12 and n=15 searches both
record `matched: true`. Elapsed time is 67.5 seconds from
`2026-10-05T17:01:58Z`. The certificate kind is `none`.

Stage 2 `RUN-SEMBIN-694183` is `completed_valid`, 41 of 41 records,
0 censored, n=12 only. Elapsed time is 340.0 seconds from
`2026-10-05T17:03:39Z`. Recomputation from the raw records: 0
enumeration disagreements, 0 dual-rank failures, and 0 Macaulay
blocks at degree at least 4 with rank equal to nrows (82 blocks have
rank strictly below nrows). Thirty-three records have first-fall
degree 2 and SOLV degree 4. All 8 null records have both quantities
above 4. The certificate kind is `none`.

Stage 3 `RUN-SEMBIN-6c5c56` is `completed_valid` with decision
`O-IMPEDIMENT` and `engine_selected` null. Elapsed time is 0.6
seconds from `2026-10-05T17:04:11Z`. `stage3/impediment.json` limits
that label to Stage 3 and says productive and raw `d_F4` are
unmeasured.

`RUN-SEMBIN-004d51` is `failed_implementation` and states that it is
not evidence. `RUN-SEMBIN-5d7618` is a Stage-2 n=15 command with
empty stdout and no raw result.

## Comparison

`O-C2-FALSE` needs SOLV4 to disagree with independent enumeration.
No archived record disagrees. `O-C3-FALSE` needs rank equal to nrows
at a measured cell with degree at least 4. No such block exists.
Dual-rank `O-ARTIFACT` needs a disagreement. None is present. Those
three non-firings are not `O-SEPARATED`: `d_F4` was not measured, and
the 8 null cells do not separate first-fall from SOLV. They are not
`O-COINCIDE` either: 33 cells separate those two quantities, and the
four-quantity test includes the unmeasured step degree. `O-C1-FALSE`
needs a Stage-3 engine trace. The missing engine is the SR-5 stop,
which the invalidation rule says is not falsification of C1. Stage-1
builder equality does not decide C1. n=15 has no Stage-2 census.

## Inference

The package does not meet its success criterion, because the terminal
label file is absent. The decision is `refine`. Direction is neutral.
Strength is inconclusive. `claim_tier` is toy: the executed census is
n=12 on a Boolean system. `proof_status` is `not_applicable`.
Hypothesis `H-SEMBIN-8e8bef` stays `approved`. Experiment status moves
from `approved` to `invalid`. `authorizes_rerun` is false. The goal
head is not edited.

## Limitation

No discrete logarithm, no exponent, and no Assumption 1 verdict are
claimed. `certificate.kind: none` is not a solve certificate. The
n=12 gate counts are observations of an unlabeled census, not a
promoted separation result. PD-1 concentrates J1, J2, and J3 in one
task, and that task ran in the session that wrote the prior because
the coordinator subagent could not start. The prior was not rewritten.
