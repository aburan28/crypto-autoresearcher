# TASK-20260813-e5254a — LEDGER ARCHIVE, batch close

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-451a6d, TASK-20260813-6ab893
    review_required false
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## Identifier note

This task's own id was withheld at batch open (declared gap G-5, the
Coordinator that drafted this batch did not invent one) and was minted,
`--check`'d in the worktree, and cross-ref swept across the 25
most-recently-updated remote branches (0 hits) by the dispatching session
before this card was written. `EV-MLKEM-965a37` and `DEC-20260813-28d7b2`
were minted and two-scope confirmed at batch open and are RESERVATIONS, not
claims — leave them unused and say so if this batch produces no evidence
record.

## What it must do

Write RC-1 and RC-2 as committed, citable text (not merely a pointer back to
PREREG-3); name the frozen termination branch that fired
(`T-C3LANE-NODATA` / `-OBSTRUCTED` / `-OPEN`, with or without `-PARTIAL`) and
state exactly what it licenses and forbids; if `T-C3LANE-OBSTRUCTED` fired,
do **not** close the admissibility-gate lane in this decision — PREREG-3 3.5
requires that in its own separate committed decision; state explicitly that
part (c) is not an eighth consecutive gate repair and does not trigger
PREREG-2 7.5, citing PREREG-3 3.6; make and record the knowledge-promotion
determination on the merits; checkpoint the goal record with exactly one
`next_action`, superseding its prior text verbatim under a `superseded_*`
key; merge `origin/main` before committing and record the base and outcome;
run `tools/validate_ledger.py` before staging; run the post-commit verifier
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
TASK-20260813-6ad846 or the seven lead paths already committed by
TASK-20260813-7ac7cd.

## Artifacts — starts at FOUR paths, extended per G-1 before staging

    archives/TASK-20260813-e5254a/ledger-receipt.json
    ledger/evidence/EV-MLKEM-965a37.yaml           (reservation)
    ledger/decisions/DEC-20260813-28d7b2.yaml      (reservation)
    ledger/goals/GOAL-MLKEM-005.yaml
