# TASK-20260813-d63082 — SNAPSHOT ARCHIVE that NOTARIZES PREREG-5

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-94e686
    review_required false
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What it must do

Notarize `PREREG-5` ALONE, before any measuring task of `BATCH-a6fab5` is
dispatched: commit `prereg.md` and a freshly computed `prereg_sha256.txt`,
and nothing else, so §2.2's operational definition and §2.6's termination
clause are provably prior to every number this batch produces. Verify —
never assume — that `prereg.md` is absent at this commit's parent and that
zero producer artifacts exist anywhere under `tasks/TASK-20260813-c0ec71` at
this commit. The receipt carries `commit_sha: null` and rides inside its own
commit; the real sha/parent go into `dispatch_queue.json`'s archive block
afterwards. Fetch and MERGE `origin/main` (never rebase) before committing;
record the base and outcome. Run the post-commit verifier BEFORE the push;
push and open/refresh the PR naming `BATCH-a6fab5` and `PREREG-5`.

## Absolute constraint

**NO MEASURING TASK OF THIS BATCH MAY BE DISPATCHED UNTIL THIS COMMIT EXISTS
AND THE VERIFIER HAS ACCEPTED IT.** Do not edit `prereg.md`. Stage paths
explicitly; never `git add -A` in this batch.

## Artifacts — THREE PATHS DECLARED (this task's own two + PREREG-5)

    archives/TASK-20260813-d63082/snapshot-receipt.json   (own)
    tasks/TASK-20260813-94e686/prereg_sha256.txt            (own)
    tasks/TASK-20260813-94e686/prereg.md                    (source, already written)
