# TASK-20260812-b581a8 — SNAPSHOT ARCHIVE of the lead producer (runs alone)

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           coordinator
    policy         coordinator-orchestration-code      effort high
    state          queued
    depends_on     TASK-20260812-56b9da
    archive kind   snapshot        sources  TASK-20260812-56b9da
    budget         1800 s wall clock, 2 GB, 1 run
    claim tier     TOY

## Objective

Make the lead's run package durable and reviewable under a contract the verifier
accepts, **before either review is dispatched and before any rider runs**.

## Declared path set — EXACTLY EIGHT PATHS

    archives/TASK-20260812-b581a8/snapshot-receipt.json        (own)
    tasks/TASK-20260812-56b9da/measure_gvar2.py                (source)
    tasks/TASK-20260812-56b9da/results_gvar2.json              (source)
    tasks/TASK-20260812-56b9da/report_gvar2.md                 (source)
    tasks/TASK-20260812-56b9da/command.txt                     (source)
    tasks/TASK-20260812-56b9da/stdout.log                      (source)
    tasks/TASK-20260812-56b9da/stderr.log                      (source)
    tasks/TASK-20260812-56b9da/run_manifest.yaml               (source)

Compare the commit's change set against this set explicitly and record **both
counts** in the receipt. 0 extra, 0 missing.

## The one-comparison check that would have prevented D3

`report_gvar2.md` lists every path the lead wrote. If that list and the declared
set differ **in either direction**, DO NOT COMMIT — return the run to the
producer with the discrepancy stated.

## Validity before durability

Verify before archiving: expected run count, schema-complete manifest, seed
integrity, raw/summary agreement, control comparability, artifact policy
(durable `command.txt` / `stdout.log` / `stderr.log`, no path inside a folded
YAML scalar). An invalid or incomplete run set goes **back to the producer** with
concrete defects listed. It is not evidence and it is not archived.

## Mandatory patterns

Receipt inside its own commit with `commit_sha: null`; real sha and parent into
the queue afterwards; `Base checked: origin/main <sha>` in the message; merge,
never rebase; verifier **before** the push.

## What this task must NOT do

It must not interpret the lead's result and must not write any ledger record.
This archive makes bytes durable; the decision comes after review.

## Downstream gate

No review and no rider is dispatched until this commit exists.
