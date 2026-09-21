# TASK-20260813-fe3dec — LEDGER ARCHIVE

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            coordinator (archive, runs alone)
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-e04ebc, TASK-20260813-28eb06
    review_required false
    kind            ledger
    sources         TASK-20260813-e04ebc, TASK-20260813-28eb06
    budget          5400 s, 2 GB, 1 run
    claim tier      TOY

## What this task must do

Write the evidence record (`EV-MLKEM-bae519`, reserved) and decision record
(`DEC-20260813-a7826b`, reserved) for `BATCH-7033ee` — carrying `RC-3` as
committed, citable text — checkpoint `ledger/goals/GOAL-MLKEM-005.yaml` with
**exactly one** `next_action`, make and record the knowledge-promotion
determination, then commit the whole set together with both review reports
and every review probe. Run the post-commit verifier **before** the push.

## Completion gate highlights (see dispatch_queue.json for the full text)

- Use the exact reserved identifiers; re-`--check` both plus a remote-ref
  sweep before staging. They are reservations, not claims — leave unused
  and say so if no evidence record is warranted.
- Name the fired termination branch (`T-INDEP-NODATA`/`-CONFIRMS`/
  `-UNDERMINES`, with or without `-PARTIAL`), quote the `PREREG-4` clause,
  state what it licenses/forbids. If `T-INDEP-UNDERMINES` fired at any
  cell, record the superseding flag on that exact `BATCH-fbb639` cell's
  `EXCEEDS` verdict per `PREREG-4` §2.7 — **without** retroactively changing
  `T-C3LANE-OPEN-PARTIAL`.
- State explicitly that part (b) is not a gate repair (`PREREG-4` §2.8).
- Fill `knowledge_promotion`: promote a `KN-FIND` only on `support`/
  `reject_scoped` over `replicated`/`strong` evidence; otherwise a concrete
  `not_warranted` reason.
- Extend `artifact_paths` by exactly the probe paths both reviews list
  (declared gap `G-1`) before staging.
- `tools/validate_ledger.py` run before staging; post-commit verifier run
  before push; PR opened/refreshed naming every new record.
- `knowledge/INDEX.md` not staged, written or regenerated.

## Artifacts (minimum 4, extended per G-1 and the knowledge-promotion gate)

    archives/TASK-20260813-fe3dec/ledger-receipt.json
    ledger/evidence/EV-MLKEM-bae519.yaml
    ledger/decisions/DEC-20260813-a7826b.yaml
    ledger/goals/GOAL-MLKEM-005.yaml
    (+ both review reports' own artifact_paths)
    (+ every probe path both reviews list)
    (+ one knowledge/findings/KN-FIND-*.md path IFF the promotion gate is met)

## Constraints

Runs alone, after both reviews. No hypothesis status moves. No official
transition from uncommitted artifacts. Do not edit any prior record — every
narrowing is by reference/supersession. Claim tier stays TOY.
