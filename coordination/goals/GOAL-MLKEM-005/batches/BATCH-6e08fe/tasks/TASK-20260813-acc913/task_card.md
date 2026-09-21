# TASK-20260813-acc913 — LEDGER ARCHIVE, batch close

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-71d65d, TASK-20260813-7930a6
    review_required false
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## Identifier note

This task's own id was withheld at batch open (declared gap G-1, the
Coordinator that drafted this batch held no shell and would not invent one)
and was minted, `--check`'d in the worktree, and cross-ref swept across the
25 most-recently-updated remote branches (0 hits) by the dispatching session
before this card was written. `EV-MLKEM-5aa471` and `DEC-20260813-1aae44`
were minted and two-scope confirmed at batch open and are RESERVATIONS, not
claims — leave them unused and say so if this batch produces no evidence
record.

## What it must do

Write RC-3 as committed, citable text (not merely a pointer back to
PREREG-4); name the frozen termination branch that fired
(`T-INDVERIFY-NODATA` / `-ARTIFACT` / `-CONFIRMED`, with or without
`-PARTIAL`) and state exactly what it licenses and forbids. If
`T-INDVERIFY-ARTIFACT` fired at any cell, discharge the revisit condition
**in this same archive**: flag that cell's `BATCH-fbb639` `EXCEEDS` verdict
methodologically unsupported, explicitly, satisfying PREREG-4 2.8's
superseding-record requirement here rather than deferring it —
`T-C3LANE-OPEN-PARTIAL` itself is NOT retroactively changed regardless of
this batch's outcome. Restate, briefly and with its own reasoning, why this
batch is not an eighth or ninth consecutive gate repair, citing PREREG-4
2.7. Make and record the knowledge-promotion determination on the merits —
state explicitly whether the *measured outcome* (not merely the
instrument-design lesson `KN-FIND-9b5df0` already carries) merits its own
entry. Checkpoint the goal record with exactly one `next_action`,
superseding its prior text verbatim under a `superseded_*` key — and verify
the field was actually written this time, not only the surrounding
narrative (this exact defect was found and corrected in `BATCH-fbb639`'s
own close, commit `442159165`). Merge `origin/main` before committing and
record the base and outcome; run `tools/validate_ledger.py` before staging;
run the post-commit verifier before the push and record its verdict; push
and open/refresh the PR.

## Completion gate, in one sentence

**Extend this task's `artifact_paths` and the two review tasks' own
`artifact_paths`** to match declared gap G-1 before staging — the review
reports' own paths plus every probe path each review lists — then commit a
change set that equals exactly the union of this task's own four declared
paths (receipt, evidence, decision, goal record — plus one
`knowledge/findings/KN-FIND-*.md` path only if the promotion gate is met)
with both reviews' now-extended declared sets, 0 extra, 0 missing. Do not
re-declare the three notarization paths already committed by
TASK-20260813-e24ad9 or the eight lead paths already committed by
TASK-20260813-2d6b5e.

## Artifacts — starts at FOUR paths, extended per G-1 before staging

    archives/TASK-20260813-acc913/ledger-receipt.json
    ledger/evidence/EV-MLKEM-5aa471.yaml           (reservation)
    ledger/decisions/DEC-20260813-1aae44.yaml      (reservation)
    ledger/goals/GOAL-MLKEM-005.yaml
