# TASK-20260812-b53c2f — SNAPSHOT ARCHIVE of the three riders (runs alone)

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           coordinator
    policy         coordinator-orchestration-code      effort high
    state          queued
    depends_on     TASK-20260812-78a6e3, TASK-20260812-4b8ede,
                   TASK-20260812-0e930c
    archive kind   snapshot   sources  the same three riders
    budget         1800 s wall clock, 2 GB, 1 run
    claim tier     TOY

## Why this task exists

It did not exist when the batch was drafted. The opening session flagged the
cost of not having it as declared gap **G-2** and declined to mint an identifier
unilaterally; the dispatching session minted `TASK-20260812-b53c2f`
(**two-scope confirmed**: worktree `--check`, well-formed and free, plus a
bounded sweep of the 25 most-recently-updated origin branches, 0 hits) and
directed that the better shape be taken.

The trade is not close. This batch's entire recorded archive history is
integrity failure: two terminally defective archives in BATCH-9e3584, defects
D3 and DEF-3, and a PD-4 instance that already destroyed two reviews in
GOAL-MLKEM-004. One identifier against that is cheap.

**With this task, every producer artifact in BATCH-4ed139 is committed before
either review reads it** — the lead at TASK-20260812-b581a8, the three riders
here.

## Declared path set — EXACTLY TWENTY-TWO PATHS

    archives/TASK-20260812-b53c2f/snapshot-receipt.json            (own, 1)
    tasks/TASK-20260812-78a6e3/  7 artifacts                       (source)
    tasks/TASK-20260812-4b8ede/  7 artifacts                       (source)
    tasks/TASK-20260812-0e930c/  7 artifacts                       (source)

Compare the commit's change set against the queue's `declared_path_set`
explicitly and record **both counts** in the receipt. 0 extra, 0 missing.

## The one-comparison check that would have prevented D3

`report_c1res.md`, `report_falserefusal.md` and `report_l7l8.md` each list every
path that task wrote. If any of those lists and the declared set differ **in
either direction**, DO NOT COMMIT — return that run to its producer with the
discrepancy stated.

## Validity per rider, before anything is archived

Expected run count, schema-complete manifest, seed integrity, raw/summary
agreement, control comparability, artifact policy (durable `command.txt` /
`stdout.log` / `stderr.log`, no path inside a folded YAML scalar). An invalid or
incomplete run set goes **back to its producer**.

**A rider that reports an infrastructure outcome is still archived, and is
archived as one.** If rider (iii)'s fpylll install failed, its seven artifacts
declaring that failure are committed unchanged and the receipt records it as
INFRASTRUCTURE SIGNAL — never as a negative result, and never as a reason to
withhold the archive.

## What this task must NOT do

It must not interpret any rider result and must not write any ledger record. In
particular **the C-1 ruling is not made here** — it belongs to the ledger
archive, after the Validator has re-derived rider (i) independently.

## Mandatory patterns

Receipt inside its own commit with `commit_sha: null`; real sha and parent into
the queue afterwards; `Base checked: origin/main <sha>`; merge, never rebase;
verifier **before** the push. `knowledge/INDEX.md` not staged.

## Downstream gate

Neither review is dispatched until this commit exists and the verifier has
accepted it.
