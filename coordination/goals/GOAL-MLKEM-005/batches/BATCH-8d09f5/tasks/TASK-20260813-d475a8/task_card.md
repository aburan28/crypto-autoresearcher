# TASK-20260813-d475a8 — LEDGER ARCHIVE, batch close

    goal / batch    GOAL-MLKEM-005 / BATCH-8d09f5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-01f482, TASK-20260813-0881f0
    review_required false
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## Identifier note

This task's own id, and every other id in this batch, was minted,
`--check`'d in the worktree, and cross-ref swept across the 25
most-recently-updated remote branches (0 hits in either scope) by the
dispatching session before this batch was drafted. `EV-MLKEM-552c58` and
`DEC-20260813-9c7353` are RESERVATIONS, not claims — leave them unused and
say so if this batch produces no evidence record (it should not: `PREREG-6`
§2.6 always fires exactly one of four named branches given a valid run
set). Re-run `tools/allocate_id.py --check` on both before staging and sweep
the remote refs again.

## What it must do

Name the frozen termination branch that fired (`T-MUTCTRL-NODATA` /
`-DETECTED` / `-NOT-DETECTED` / `-MIXED`, with or without `-PARTIAL`) and
state exactly what it licenses and forbids, per `PREREG-6` §2.6. If
`T-MUTCTRL-DETECTED` (full or partial) fired, record it as a narrow,
positive calibration result for this ONE defect class at these TWO cells —
no broader claim. If `T-MUTCTRL-NOT-DETECTED` (full or partial) fired,
record it plainly as a demonstrated limitation of the `D_route` mechanism
against this defect class, explicitly NOT as grounds to reopen
`T-HKZINDEP-CONFIRMED`'s own, separately-fired, unaffected branch in
`BATCH-a6fab5`. If `T-MUTCTRL-MIXED` fired, report per-cell only, no
aggregate. If `T-MUTCTRL-NODATA` fired, record it as infrastructure signal
only and make no claim about the instrument in either direction. Restate,
briefly and with its own reasoning (not only by citation), why this batch
is not an eleventh-through-twelfth consecutive gate repair, citing
`PREREG-6` §2.7 (the fifth independent re-derivation in this lineage). Make
and record the knowledge-promotion determination on the merits — state
explicitly whether THIS batch's own measured outcome (not merely
`KN-FIND-d29ece`'s already-carried open question) merits its own entry.
Checkpoint the goal record with exactly one `next_action`, superseding its
prior text verbatim under a `superseded_*` key — and verify the field was
actually written this time, not only the surrounding narrative (this exact
defect class was found and corrected in `BATCH-fbb639`'s own close, commit
`442159165`). Merge `origin/main` before committing and record the base and
outcome; run `tools/validate_ledger.py` before staging; run the post-commit
verifier before the push and record its verdict; push and open/refresh the
PR.

## Completion gate, in one sentence

**Extend this task's `artifact_paths` and the two review tasks' own
`artifact_paths`** to match declared gap G-1 before staging — the review
reports' own paths plus every probe path each review lists — then commit a
change set that equals exactly the union of this task's own four declared
paths (receipt, evidence, decision, goal record — plus one
`knowledge/findings/KN-FIND-*.md` path only if the promotion gate is met)
with both reviews' now-extended declared sets, 0 extra, 0 missing. Do not
re-declare the three notarization paths already committed by
`TASK-20260813-62cd6b` or the nine lead paths already committed by
`TASK-20260813-cb8943`.

## Artifacts — starts at FOUR paths, extended per G-1 before staging

    archives/TASK-20260813-d475a8/ledger-receipt.json
    ledger/evidence/EV-MLKEM-552c58.yaml           (reservation)
    ledger/decisions/DEC-20260813-9c7353.yaml      (reservation)
    ledger/goals/GOAL-MLKEM-005.yaml
