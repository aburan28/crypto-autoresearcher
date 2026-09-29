# TASK-20260813-5d1920 — SNAPSHOT ARCHIVE of the lead producer's artifacts

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            coordinator (archive, runs alone)
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-415c21
    review_required false
    kind            snapshot
    sources         TASK-20260813-415c21
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What this task must do

Commit the lead producer's seven artifacts, **alone**, before either
independent review is dispatched, so both reviews review committed
immutable bytes.

## Completion gate (see dispatch_queue.json for the full text)

- The commit changes **exactly the eight declared paths** (this task's own
  receipt + the lead's seven artifacts). 0 extra, 0 missing.
- Cross-check `report_route_i2.md`'s own "every path written" list against
  the declared set; on any discrepancy, **do not commit** — return to the
  producer.
- **Before interpreting anything**: check expected run count (one),
  schema-complete manifest, RC-3 carried verbatim (not recomputed), and the
  independence self-certification is present (the report names a genuine
  algorithmic difference; `measure_route_i2.py` does not import
  `measure_am4`/`measure_relvar`/`replicate_l7l8`). An invalid or
  incomplete run set goes back to the producer with concrete defects
  listed — it is not evidence and is not archived.
- Confirm no reduction above `d = 40` was performed.
- `origin/main` fetched and merged before the commit; base commit and merge
  outcome recorded. Verifier run before push; PR refreshed naming
  `BATCH-7033ee`.
- `knowledge/INDEX.md` is not written, regenerated or staged.

## Declared path set (8)

    archives/TASK-20260813-5d1920/snapshot-receipt.json
    tasks/TASK-20260813-415c21/measure_route_i2.py
    tasks/TASK-20260813-415c21/results_route_i2.json
    tasks/TASK-20260813-415c21/report_route_i2.md
    tasks/TASK-20260813-415c21/command.txt
    tasks/TASK-20260813-415c21/stdout.log
    tasks/TASK-20260813-415c21/stderr.log
    tasks/TASK-20260813-415c21/run_manifest.yaml

## Blocks

No review of this batch may be dispatched until this commit exists and the
verifier has accepted it. Do not interpret the lead's result here; do not
write any ledger record here.
