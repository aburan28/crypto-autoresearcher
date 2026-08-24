# TASK-20260813-30cdca — SNAPSHOT ARCHIVE notarizing PREREG-4

    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            coordinator (archive, runs alone)
    policy          coordinator-orchestration-code     effort high
    state           queued
    depends_on      TASK-20260813-61dab8
    review_required false
    kind            snapshot
    sources         TASK-20260813-61dab8
    budget          1800 s, 2 GB, 1 run
    claim tier      TOY

## What this task must do

Commit `prereg.md` and a freshly computed `prereg_sha256.txt`, **alone**,
before any measuring task of this batch is dispatched. This is what makes
`PREREG-4`'s `RC-3` correction and part-(b) termination clause provably
prior to every number this batch produces.

## Completion gate (see dispatch_queue.json for the full text)

- The commit changes **exactly three paths**: `prereg.md`, `prereg_sha256.txt`,
  and this task's own `snapshot-receipt.json`. 0 extra, 0 missing.
- Verify — do not assume — that `prereg.md` is **not already committed**
  when this task starts, and that **zero** producer artifacts exist under
  `tasks/TASK-20260813-415c21` at this commit.
- The receipt rides inside its own commit with `commit_sha: null`; the real
  `commit_sha`/`parent_sha`/`path_sha256` are written into `dispatch_queue.json`'s
  `archive` block for this task **afterwards**.
- `origin/main` fetched and merged (never rebased) before the commit; base
  commit and merge outcome recorded in the receipt and commit message.
- Post-commit verifier run **before** the push; branch pushed; PR opened or
  refreshed naming `BATCH-7033ee` and `PREREG-4`.
- `knowledge/INDEX.md` is not written, regenerated or staged.

## Declared path set (3)

    archives/TASK-20260813-30cdca/snapshot-receipt.json
    tasks/TASK-20260813-61dab8/prereg.md
    tasks/TASK-20260813-61dab8/prereg_sha256.txt

## Blocks

No measuring task of this batch (`TASK-20260813-415c21`) may be dispatched
until this commit exists and the verifier has accepted it.
