# TASK-20260731-111 — Open BATCH-026 (RC-26 fresh IT amend)

**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-026  
**Role:** coordinator  
**Decision:** DEC-20260731-029  
**Queue amend:** QUEUE-AMEND-20260731-015  
**Parent close:** DEC-20260731-028 / `1cb3c6c4` (BATCH-025 RC-25b non-execution)

## Disposition

Opened BATCH-026 under selected SG-ECDLP-002 / IDEA-20260731-008 / H-IT-001
for a fresh EXP-IT-001 protocol amendment **outside RC-25b**, discharging
B-5–B-8 while retaining discharged B-1. RC-26 one-cycle: REVISE after the
sole amend ⇒ design-path non-execution. No run. No Executor. No STR.
Structure-null-r2 Val/RT under DEC-027 left untouched (disjoint scope).

## Deliverables

| Path | Role |
|------|------|
| `ledger/decisions/DEC-20260731-029.yaml` | Batch-open decision |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/QUEUE-AMEND-20260731-015.md` | RC-26 cycle cap |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/tasks/TASK-20260731-111/task_report.md` | This report |

## Completion gate

- [x] DEC-029 and QUEUE-AMEND-015 filed
- [x] BATCH-026 open
- [x] No run

## Inference

- requested_policy: `coordinator-orchestration-code`
- resolved_model_id: `cursor-grok-4.5`
- fallback_used: true

## Next

TASK-20260731-112 author PA-IT-001-v3-rc26-b5-b8; TASK-113 snapshot; admit
TASK-114 independent re-review.
