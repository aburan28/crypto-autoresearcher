# TASK-20260813-861a58 — SNAPSHOT ARCHIVE of the lead producer's artifacts

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-c0ec71
    review_required false
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Make the lead's run package durable and reviewable, before either
independent review is dispatched. Check validity BEFORE archiving: expected
run count, schema-complete manifest, the section-1 `fpylll` re-verification
result is stated plainly and its consequent branch (A/B) declared, seed
integrity, raw/summary agreement between `results_hkz_indep.json` and the
report, and that the reduction/enumeration code does not import or
structurally paraphrase `make_A`/`build_basis`/`hkz_profile` from the barred
lineage OR `BATCH-6e08fe`'s own `measure_route_reimpl.py` reduction code —
grep the committed script. Cross-check the producer's own declared path list
against the actual committed change set — if they differ, DO NOT COMMIT;
return the run to the producer. An invalid or incomplete run set is not
evidence and is not archived.

The receipt carries `commit_sha: null` and rides inside its own commit; the
real sha/parent go into `dispatch_queue.json`'s archive block afterwards.
Fetch and MERGE `origin/main` (never rebase) before committing. Run the
post-commit verifier BEFORE the push; push and refresh the PR naming
`BATCH-a6fab5`.

## Constraints

ARCHIVE TASK. RUNS ALONE. Sources exactly one non-archive task. Do not
interpret the lead's result here; write no ledger record. Stage paths
explicitly; never `git add -A`.

## Artifacts — declared_path_set of EIGHT (own receipt + the lead's seven)

    archives/TASK-20260813-861a58/snapshot-receipt.json      (own)
    tasks/TASK-20260813-c0ec71/measure_hkz_indep.py
    tasks/TASK-20260813-c0ec71/results_hkz_indep.json
    tasks/TASK-20260813-c0ec71/report_hkz_indep.md
    tasks/TASK-20260813-c0ec71/command.txt
    tasks/TASK-20260813-c0ec71/stdout.log
    tasks/TASK-20260813-c0ec71/stderr.log
    tasks/TASK-20260813-c0ec71/run_manifest.yaml
