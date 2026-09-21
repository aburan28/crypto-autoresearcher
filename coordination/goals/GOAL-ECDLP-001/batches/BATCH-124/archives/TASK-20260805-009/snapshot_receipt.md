# BATCH-124 Snapshot Receipt — TASK-20260805-009

**Goal:** GOAL-ECDLP-001
**Batch:** BATCH-124
**Archive task:** TASK-20260805-009
**Date:** 2026-08-05
**Base commit checked:** 6581dc365 (cursor/ecdlp-batch-120-continue)

## Snapshot contents

| Path | Task | Producer |
|---|---|---|
| `experiments/EXP-MTBK-306bdb/code/run_mtbk_smoke.py` (v2) | TASK-20260805-013 | coordinator |
| `experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-smoke/*` (v2) | TASK-20260805-013 | coordinator |
| `experiments/EXP-MTBK-306bdb/execution-report.yaml` (v2) | TASK-20260805-013 | coordinator |
| `experiments/EXP-MTBK-306bdb/specification.yaml` (status update) | TASK-20260805-013 | coordinator |
| `knowledge/findings/KN-FIND-982fdf.md` | TASK-20260805-013 | coordinator |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-124/tasks/TASK-20260805-014/y_sign_oracle.md` | TASK-20260805-014 | coordinator |
| `ledger/decisions/DEC-20260805-d4b182.yaml` | TASK-20260805-009 | coordinator |

## Key numbers (v2 smoke)

- theorem_index_test: gamma_empirical 0.49997 vs lb 0.5; speedup_empirical
  1.99988 vs 2.0 (m=3, B=230, 200k trials). Smoke gate PASSED.
- y-sign probe: sign-positives 26218 of (N-1)/2 = 26219 at p=52721 -> sign
  oracle is a half-curve selector, never a factor base.

## Provenance notes

- Executor/validator subagents returned empty (BATCH-120..124 pattern);
  coordinator authored and ran the v2 driver and the probe. Disclosed in
  execution-report.yaml and DEC.
- KN-FIND-982fdf promotion relies on the qualified-accept review
  (TASK-20260805-011) referenced in review_refs.

## Reading state

- No new origin/main commits to merge during this batch (fetch pack errors on
  this volume are an infra issue; merge base verified up to date).