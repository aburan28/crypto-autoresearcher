# TASK-20260813-2d6b5e — SNAPSHOT ARCHIVE of the lead producer's artifacts

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-ea2e96
    review_required false
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Make the lead's run package durable and reviewable, before either
independent review is dispatched. Check validity BEFORE archiving: expected
run count, schema-complete manifest, seed integrity (verify the declared
`ROUTE-I'` implementation choice is stated and does not import/transcribe
`make_A`/`build_basis`/`hkz_profile` from the barred lineage — grep the
committed script), raw/summary agreement between `results_route_reimpl.json`
and the report, RC-3 carried verbatim. Cross-check the producer's own
declared path list against the actual committed change set — if they
differ, DO NOT COMMIT; return the run to the producer. An invalid or
incomplete run set is not evidence and is not archived.

The receipt carries `commit_sha: null` and rides inside its own commit; the
real sha/parent go into `dispatch_queue.json`'s archive block afterwards.
Fetch and MERGE `origin/main` (never rebase) before committing. Run the
post-commit verifier BEFORE the push; push and refresh the PR naming
`BATCH-6e08fe`.

## Constraints

ARCHIVE TASK. RUNS ALONE. Sources exactly one non-archive task. Do not
interpret the lead's result here; write no ledger record. Stage paths
explicitly; never `git add -A`.

## Artifacts — declared_path_set of EIGHT (own receipt + the lead's seven)

    archives/TASK-20260813-2d6b5e/snapshot-receipt.json      (own)
    tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
    tasks/TASK-20260813-ea2e96/results_route_reimpl.json
    tasks/TASK-20260813-ea2e96/report_route_reimpl.md
    tasks/TASK-20260813-ea2e96/command.txt
    tasks/TASK-20260813-ea2e96/stdout.log
    tasks/TASK-20260813-ea2e96/stderr.log
    tasks/TASK-20260813-ea2e96/run_manifest.yaml
