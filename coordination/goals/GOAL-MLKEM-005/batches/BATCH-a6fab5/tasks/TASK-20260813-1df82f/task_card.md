# TASK-20260813-1df82f — LEDGER ARCHIVE, batch close

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-968dc8, TASK-20260813-5b09b0
    review_required false
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## Identifier note

This task's own id, and every other id in this batch, was minted,
`--check`'d in the worktree, and cross-ref swept across the 25
most-recently-updated remote branches (0 hits in either scope) by the
dispatching session before this batch was drafted. `EV-MLKEM-f65f00` and
`DEC-20260813-894568` are RESERVATIONS, not claims — leave them unused and
say so if this batch produces no evidence record (it should not: `PREREG-5`
§2.6 always fires exactly one of three named branches given a valid run set).

## What it must do

Name the frozen termination branch that fired (`T-HKZINDEP-NODATA` /
`-ARTIFACT` / `-CONFIRMED`, with or without `-PARTIAL`) and state exactly
what it licenses and forbids. If `T-HKZINDEP-ARTIFACT` fired at any cell,
discharge the revisit condition **in this same archive**: flag that cell's
`BATCH-fbb639` `EXCEEDS` verdict methodologically unsupported, explicitly,
satisfying `PREREG-4` §2.8's superseding-record requirement on ITS OWN
evidentiary terms this time. If `T-HKZINDEP-CONFIRMED` fired, discharge
`hkz`'s status to `T-INDVERIFY-CONFIRMED`-equivalent for the cells checked,
explicitly, matching `lam1n`'s own discharge pattern in `EV-MLKEM-5aa471`.
If `T-HKZINDEP-NODATA` branch (b) fired, record the standing
infrastructure-limited open question PLAINLY per `DEC-20260813-1aae44` §11's
declared boundary and explicitly DO NOT commission a fourth attempt absent a
change in available tooling — this is a hard constraint on this task, not a
discretionary call. `T-C3LANE-OPEN-PARTIAL` and `T-INDVERIFY-ARTIFACT-PARTIAL`
themselves are NOT retroactively changed regardless of this batch's outcome.
Restate, briefly and with its own reasoning, why this batch is not an
eighth through tenth consecutive gate repair, citing `PREREG-5` §2.7. Make
and record the knowledge-promotion determination on the merits. Checkpoint
the goal record with exactly one `next_action`, superseding its prior text
verbatim under a `superseded_*` key — and verify the field was actually
written this time, not only the surrounding narrative (this exact defect was
found and corrected in `BATCH-fbb639`'s own close, commit `442159165`).
Merge `origin/main` before committing and record the base and outcome; run
`tools/validate_ledger.py` before staging; run the post-commit verifier
before the push and record its verdict; push and open/refresh the PR.

## Completion gate, in one sentence

**Extend this task's `artifact_paths` and the two review tasks' own
`artifact_paths`** to match declared gap G-1 before staging — the review
reports' own paths plus every probe path each review lists — then commit a
change set that equals exactly the union of this task's own four declared
paths (receipt, evidence, decision, goal record — plus one
`knowledge/findings/KN-FIND-*.md` path only if the promotion gate is met)
with both reviews' now-extended declared sets, 0 extra, 0 missing. Do not
re-declare the three notarization paths already committed by
TASK-20260813-d63082 or the eight lead paths already committed by
TASK-20260813-861a58.

## Artifacts — starts at FOUR paths, extended per G-1 before staging

    archives/TASK-20260813-1df82f/ledger-receipt.json
    ledger/evidence/EV-MLKEM-f65f00.yaml           (reservation)
    ledger/decisions/DEC-20260813-894568.yaml      (reservation)
    ledger/goals/GOAL-MLKEM-005.yaml
