# EXP-ECDLP-02bd1c analysis

Review of Stages 0–1 for `H-ECDLP-f6a43a`. The coordinator subagent
could not be launched (model usage quota), so this session executed
`TASK-20261004-16ddd8` against the pre-committed prior
`3ad17754b1938d7cecad666499e8ea8c4c8f8205`. Amazon Bedrock was not
selected. No Magma, Sage, or AUXIN. No Stage-1 process was executed.

## Observation

Stage 0 `RUN-ECDLP-92b600` is `output_validated`. The receipt return
code and check return code are 0. `check.stdout.log` is `PASS`. The
raw record has `worksheet_ok: true` and `selfchecks_all_pass: true`.
`stage0/selfchecks.json` records `A0_identity` computed 1, the
two-point floor, regime alphas 0.5 and 0.75, and seven H1 table rows,
with `all_pass: true`. The wall span is 0.108095 seconds. The manifest
certificate kind is `none` and `verified` is null.

Stage 1 `RUN-ECDLP-44795f` produced no census. The receipt status is
`claim_expired`, `returncode` is null, and `check_returncode` is null.
The span from `started_at` `2026-10-04T05:30:14.540102+00:00` to
`finished_at` `2026-10-04T13:35:27.151883+00:00` is 29112.611781
seconds, after `expires_at` `2026-10-04T13:30:06+00:00`. Both check
logs are empty and hash to
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
`raw-result.json` is a declared absence: `THIS_IS_NOT_A_RESULT`,
`no_census`, `producer_O_star_emitted: false`, and
`failure_classification: infrastructure_error`. The stage-1 tree has
no `census.json`, `ladder.json`, or `cells.yaml`.

`RUN-ECDLP-0110e6` is a launch directory with command, environment,
launch, heartbeat, stdout, and stderr only. It has no execution
receipt and no raw result.

## Comparison

H1, `O-E-RANDOM`, `O-E-POWER`, and `O-E-WEIL-TIGHT` need an A(1)
census on field bits 10..16. No cell was written, so none of those
labels can be compared with NULL-1. Stage 0 self-checks do not
substitute for that census. The manifest maps the expiry to
`O-IMPEDIMENT` and says the producer never emitted an `O-*` label.
That mapping matches the frozen control that timeouts and crashes are
`O-IMPEDIMENT` and never `E-RANDOM`, `E-POWER`, or `E-WEIL`.

## Inference

The committed Stage-1 attempt is an infrastructure stop. It does not
support H1, weaken H1, or reject H1. The decision is `refine`.
Direction is neutral. Strength is inconclusive. `claim_tier` stays
toy because the authorized ladder was a toy and no larger claim was
measured. `proof_status` is `not_applicable`. Hypothesis
`H-ECDLP-f6a43a` stays `approved`. Experiment status moves from
`approved` to `invalid` because the scientific stage did not produce
a census. `authorizes_rerun` is false. The in-flight launch package
is not authorized by this decision and is not evidence.

## Limitation

No discrete logarithm and no exponent were claimed or recovered.
`certificate.kind: none` is not a solve certificate. The toy ladder
was not executed, so nothing here transfers to a cryptographic prime.
PD-1 concentrates J1, J2, and J3 in one task, and that task ran in
the session that wrote the prior because the coordinator subagent
could not start. The prior was not rewritten after the check.
