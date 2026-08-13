# TASK-20260813-6ad846 — SNAPSHOT ARCHIVE notarizing PREREG-3

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           not_started
    depends_on      TASK-20260813-0eb5a3
    review_required false
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Commit `prereg.md` (already sitting unstaged in the working tree) together
with `prereg_sha256.txt` (which THIS task computes — `PREREG-3`'s authoring
session held no shell and could not; declared gap `G-2`) and its own receipt,
**alone**, before `TASK-20260813-7b3039` is dispatched. Runs the exact
split-producer notarization pattern this goal has now used six times.

## Completion gate, in one sentence

The commit changes **exactly three paths** — `prereg.md`, `prereg_sha256.txt`,
this task's own `snapshot-receipt.json` — verified against the parent (no
prior appearance of `prereg.md` anywhere in history) and against
`TASK-20260813-7b3039`'s directory (zero producer artifacts exist yet). The
receipt carries `commit_sha: null` inside its own commit; the real sha and
parent are written back into `dispatch_queue.json`'s archive block afterward.

## Artifacts — TWO PATHS

    archives/TASK-20260813-6ad846/snapshot-receipt.json
    tasks/TASK-20260813-0eb5a3/prereg_sha256.txt

(`prereg.md` itself is the pre-existing file this task commits, not a file it
writes new content into.)
