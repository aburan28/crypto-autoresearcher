# TASK-20260812-1ed548 — SNAPSHOT ARCHIVE that NOTARIZES PREREG-1 (runs alone)

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           coordinator
    policy         coordinator-orchestration-code      effort high
    state          queued
    depends_on     TASK-20260812-34b86c
    archive kind   snapshot        sources  TASK-20260812-34b86c
    budget         1800 s wall clock, 2 GB, 1 run
    claim tier     TOY

## Objective

Notarize PREREG-1 by committing the frozen text and its hash, **alone**, before
any measuring task of BATCH-4ed139 is dispatched — so that the three-way
termination clause is provably prior to every number this batch produces.

## Declared path set — EXACTLY THREE PATHS

    coordination/.../BATCH-4ed139/archives/TASK-20260812-1ed548/snapshot-receipt.json   (own)
    coordination/.../BATCH-4ed139/tasks/TASK-20260812-34b86c/prereg_sha256.txt          (own)
    coordination/.../BATCH-4ed139/tasks/TASK-20260812-34b86c/prereg.md                  (source)

The commit must change **exactly** these three, 0 extra and 0 missing.
`dispatch_queue.json` and the nine `task_card.md` files belong to the **opening
commit** and must already be committed or left unstaged; if either rides here
the set-equality test fails exactly as it did for D1, D2 and D3.

## Mandatory patterns

* The receipt body carries `commit_sha: null` and rides **inside its own
  commit**. Inverting this cost BATCH-9e3584 two archives.
* The real `commit_sha`, `parent_sha` and `path_sha256` go into the queue's
  `archive` block **after** the commit.
* `Base checked: origin/main <sha>` in the commit message; merge, never rebase.
* Run the post-commit verifier **before** the push, not after.

## Hard precondition on the rest of the batch

No measuring task is dispatched until this commit exists and the verifier has
accepted it. Verify that **zero** producer artifacts exist under
`tasks/TASK-20260812-56b9da`, `-78a6e3`, `-4b8ede` or `-0e930c` at this commit —
check it, do not assume it.

## Binding carries

PREREG-1 sections 11 and 11.1. `prereg.md` is frozen and is never edited.
`knowledge/INDEX.md` is not written, regenerated or staged. CLAIM TIER TOY.
