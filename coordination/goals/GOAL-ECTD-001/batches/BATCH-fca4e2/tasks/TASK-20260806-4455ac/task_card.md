# TASK-20260806-4455ac: Snapshot archive of the BATCH-fca4e2 run package

- **goal:** GOAL-ECTD-001
- **batch:** BATCH-fca4e2
- **role:** coordinator
- **state:** queued
- **priority:** 90
- **depends_on:** TASK-20260806-983eed
- **review_required:** False
- **archived_by:** TASK-20260806-4455ac (self; snapshot archives are terminal)

## Objective

Commit and verify the exact run package produced by TASK-20260806-983eed
(driver + both `RUN-ECTD-001-*` directories) before the independent validator
reads it. Runs alone; stages only the producer's declared artifact paths plus
this receipt.

## Completion gate

- Git verifies parent, paths, hashes, task ID, and reachable commit.
- The commit changes exactly the declared paths and no others.
- `archive.commit_sha` / `archive.parent_sha` are filled in only after the
  commit lands (never a commit's own SHA embedded within itself).
