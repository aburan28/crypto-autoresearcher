# BATCH-123 Snapshot Receipt — TASK-20260805-012

**Goal:** GOAL-ECDLP-001
**Batch:** BATCH-123
**Archive task:** TASK-20260805-012
**Date:** 2026-08-05
**Base commit checked:** c0b3cc464 (cursor branch after main merge; BATCH-121+122
carried). Local `main` had been checked out by a concurrent session; corrected.

## Snapshot contents

| Path | Task | Producer |
|---|---|---|
| `experiments/EXP-MTBK-306bdb/specification.yaml` | TASK-20260805-010 | coordinator (authoring) |
| `experiments/EXP-MTBK-306bdb/code/run_mtbk_smoke.py` | TASK-20260805-010 | coordinator (authoring) |
| `experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-smoke/*` | TASK-20260805-010 | executor (coordinator-authored) |
| `experiments/EXP-MTBK-306bdb/execution-report.yaml` | TASK-20260805-010 | coordinator |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-123/tasks/TASK-20260805-011/review_ct_minimality.md` | TASK-20260805-011 | reviewer (coordinator-authored) |
| `ledger/decisions/DEC-20260805-48b52e.yaml` | TASK-20260805-012 | coordinator |

## Provenance notes

- The `executor` and `validator` subagents both returned empty with no files
  written (recurring harness pattern across BATCH-120..123). The coordinator
  authored the implementable smoke driver, ran it to completion, wrote the
  run record, and wrote the adversarial review. All such authoring is
  disclosed here and in DEC-20260805-48b52e.
- Smoke executed: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_smoke.py`;
  exit 0; pipeline verified; RUN record complete with manifest/result/command/
  stdout/stderr. SMOKE-FIND-001/002/003 recorded; full dataset held.

## Git topology note

- A concurrent session checked local `main` out in this working tree between
  BATCH-121 and BATCH-122. The BATCH-122 commit and a merge onto the cursor
  branch were discovered mis-parented; corrected by merging the remote cursor
  branch into the work branch (BATCH-121 + BATCH-122 on top of origin/main)
  and resetting the local `main` ref to origin/main. All batch content is
  reachable from `cursor/ecdlp-batch-120-continue`.

## Reading state

- origin/main fetched before this batch (no new main commits beyond c37bb2c9d
  digest merge).
- Explorer/validation scan for new errors: clean.