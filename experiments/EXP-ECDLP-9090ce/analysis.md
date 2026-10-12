# EXP-ECDLP-9090ce analysis

Review of Stages 0–1 for `H-ECDLP-42f434`. The coordinator subagent
could not be launched (model usage quota on inherit, resolved as
grok-4.7-high-fast), so this session executed `TASK-20261004-caead2`
against the pre-committed prior
`a8acff4667eb2192443c2c91a7de0fb9fb222e20`. Amazon Bedrock was not
selected. No Magma, Sage, or AUXIN. No new Stage-1 seed was executed.

## Observation

Stage 0 `RUN-ECDLP-c7017a` is `output_validated`. The receipt return
code and check return code are 0. `check.stdout.log` is `PASS`. The
raw record has `worksheet_ok: true`, `selfchecks_all_pass: true`,
`n_checks` 16, and `n_pass` 16. `stage0/selfchecks.json` has
`all_pass: true` on those 16 checks. The wall span from
`2026-10-04T15:35:51.587634+00:00` to
`2026-10-04T15:35:51.695313+00:00` is 0.107679 seconds. The manifest
certificate kind is `none` and `verified` is null. `claims.break` and
`claims.exponent_move` are false on the Stage-1 raw file; the Stage-0
raw file records the same two flags as false.

Stage 1 `RUN-ECDLP-ce3061` is `output_validated`. The receipt return
code and check return code are 0. `check.stdout.log` is `PASS`
(SHA-256
`c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431`).
The span from `started_at` `2026-10-04T15:35:52.127845+00:00` to
`finished_at` `2026-10-04T15:35:52.634287+00:00` is 0.506442 seconds.
The census and the raw file both label the outcome `O-ARTIFACT` with
`artifact_reason` `m4_kangaroo`. At `n=65537`, `kangaroo_mean` is
387.1 and `kangaroo_pred` is 512.003906235099, so the ratio is
0.7560489193265133. The absolute deviation from 1 is
0.2439510806734867, above `m4_rel_tol` 0.10. `rho_mean` is 436.0 and
`rho_pred` is 226.81773046214883, so the ratio is
1.9222483141491415. The absolute deviation from 1 is
0.9222483141491415, above 0.10. `m5_ratio` is 1.4833333333333332,
outside the frozen band [2.5, 6.0]. `m3_false` is 0 and `m3_true` is
40. `n_m1` is 27 and `n_m2` is 18. Census `elapsed_s` is
0.3885917663574219. Raw `elapsed_s` is 0.3892638683319092. The
manifest certificate kind is `none` and `verified` is null.

## Comparison

`O-LAW-HOLDS` requires M1 within 0.07, M2 inside [0.8, 1.25], and
M3, M4, and M5 all passing. M4 misses on both constants and M5 misses
the ratio band, so that label does not fire. `m3_false` 0 does not
repair the miss. `O-SHAPE-EFFECT` requires M2 out of band at the
largest executed `n` after the controls pass. An M2 interval ratio at
`n_bits` 16 and alpha 0.6 is 1.4978859129900004, outside [0.8, 1.25],
and the stopping rule says an M4 or M5 miss yields `O-ARTIFACT` and
stops scoring. The shape label is therefore not the archived outcome.
`O-IMPEDIMENT` is the timeout, crash, and incomplete mapping. This
receipt is `output_validated` with a completed census, so that mapping
does not apply. The archived label `O-ARTIFACT` matches the decision
rule "Lemma V false cert or M4/M5 miss" and the falsification sentence
that planted-control failures void the run.

Stage 0 self-checks compare closed forms with the frozen worksheet.
They do not decide H1. Executed `n_bits` are 16, 18, and 20. The
declared taper toward 22, 24, and 26 is not a measured transfer.

## Inference

The committed Stage-1 result is a voided planted-control run. It does
not support H1, weaken H1, or reject H1. The decision is `refine`.
Direction is neutral. Strength is inconclusive. `claim_tier` stays
toy because the authorized pipeline was a planted Z/n instrument and
no larger claim was measured. `proof_status` is `not_applicable`.
Hypothesis `H-ECDLP-42f434` stays `approved`. Experiment status moves
from `approved` to `invalid` because the falsification says the
control failure voids the run. `authorizes_rerun` is false.

## Limitation

No discrete logarithm and no exponent were claimed or recovered.
`certificate.kind: none` is not a solve certificate. The miss is on
planted kangaroo and rho constants at `n=65537`, not on a curve
discrete logarithm. Nothing here transfers to a cryptographic group.
PD-1 concentrates J1, J2, and J3 in one task, and that task ran in
the session that wrote the prior because the coordinator subagent
could not start. The prior was not rewritten after the check.
