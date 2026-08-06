# BATCH-122 Snapshot Receipt — TASK-20260805-009

**Goal:** GOAL-ECDLP-001
**Batch:** BATCH-122
**Archive task:** TASK-20260805-009
**Date:** 2026-08-05
**Base commit checked:** cursor/ecdlp-batch-120-continue @ 32a0d119e
**Main state fetched:** origin/main merged PR #178 (BATCH-120 content); branch
base was 61db44b66 merge-base; no new origin/main commits to merge during this batch.

## Snapshot contents

| Path | Task | Producer |
|---|---|---|
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-122/tasks/TASK-20260805-007/experiment_contract.md` | TASK-20260805-007 | coordinator (authoring) |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-122/tasks/TASK-20260805-008/ct_minimality_lemma.md` | TASK-20260805-008 | mathematical analyst via subagent |
| `ledger/hypotheses/H-MTBK-001.yaml` | TASK-20260805-009 | coordinator |
| `ledger/decisions/DEC-20260805-661790.yaml` | TASK-20260805-009 | coordinator |

## Provenance notes

- TASK-20260805-007 dispatched to a `general` subagent; it returned no artifact.
  The contract was authored by the Coordinator session (disclosed in DEC). Model:
  deepseek-v4-flash-free, policy coordinator-orchestration-code.
- TASK-20260805-008 dispatched to a `general` subagent; it returned the lemma in-band
  and the file was verified on disk (22,402 bytes, 362 lines).
- H-MTBK-001 renamed at allocation-check time from H-MT-BKK-001 (pattern violation:
  area codes are letters-only); all references in the batch and decision updated.

## Reading state

- Working tree was dirty with unrelated modifications at batch start? No — started
  from 32a0d119e clean.
- No main synchronization required this batch.