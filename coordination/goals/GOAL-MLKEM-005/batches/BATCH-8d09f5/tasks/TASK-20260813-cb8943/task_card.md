# TASK-20260813-cb8943 — SNAPSHOT ARCHIVE of the lead producer's artifacts

    goal / batch    GOAL-MLKEM-005 / BATCH-8d09f5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-630414
    review_required false
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Make the lead's run package durable and reviewable, before either
independent review is dispatched. Check validity BEFORE archiving: expected
run count, schema-complete manifest, the section-1 `fpylll`
re-verification result is stated plainly, the section-2.3 independent
recomputation of the frozen prediction is present and its match/mismatch
stated, the machine-generated diff confirming exactly one functional line
differs from `measure_hkz_indep.py` is present and actually shows only that
one line, raw/summary agreement between `results_hkz_mutation6.json` and
the report, and that `measure_hkz_indep.py` itself was NOT edited anywhere
in this commit (diff the committed tree against the frozen file at
`3d3f5fde552f1a4783616a624f602917719701e8` and confirm zero change). Confirm
the mutant script does not import from `measure_hkz_indep.py`,
`measure_relvar.py`, `measure_am4.py`, `replicate_l7l8.py` or
`measure_route_reimpl.py`. Cross-check the producer's own declared path
list against the actual committed change set — if they differ, DO NOT
COMMIT; return the run to the producer. An invalid or incomplete run set is
not evidence and is not archived.

The receipt carries `commit_sha: null` and rides inside its own commit; the
real sha/parent go into `dispatch_queue.json`'s archive block afterwards.
Fetch and MERGE `origin/main` (never rebase) before committing. Run the
post-commit verifier BEFORE the push; push and refresh the PR naming
`BATCH-8d09f5`.

## Constraints

ARCHIVE TASK. RUNS ALONE. Sources exactly one non-archive task. Do not
interpret the lead's result here; write no ledger record. Stage paths
explicitly; never `git add -A`.

## Artifacts — declared_path_set of NINE (own receipt + the lead's eight)

    archives/TASK-20260813-cb8943/snapshot-receipt.json      (own)
    tasks/TASK-20260813-630414/measure_hkz_mutation6.py
    tasks/TASK-20260813-630414/results_hkz_mutation6.json
    tasks/TASK-20260813-630414/hkz_mutation6_writeup.md
    tasks/TASK-20260813-630414/command.txt
    tasks/TASK-20260813-630414/stdout.log
    tasks/TASK-20260813-630414/stderr.log
    tasks/TASK-20260813-630414/run_manifest.yaml
    tasks/TASK-20260813-630414/environment.json
