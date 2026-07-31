# Dynamic Subagent Dispatch Plan

BATCH-025 RC-25b after TASK-105 REVISE / TASK-106 NOT APPROVED (DEC-20260731-026 / QUEUE-AMEND-20260731-014): one protocol_amendment discharging B-1–B-4 on EXP-IT-001 / H-IT-001; freeze snapshot; independent re-review. No Executor until APPROVED. Structure-null-r2 deferred (DEC-025 superseded for execution). H-DS-001 analyzed. Toy ceiling. No STR. No push.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-107` | coordinator | queued | 100 | TASK-20260731-106 | experiments/EXP-IT-001/specification.v2.yaml, experiments/EXP-IT-001/amendments/PA-IT-001-v2-rc25b-b1-b4.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/tasks/TASK-20260731-107/task_report.md | experiments/EXP-IT-001/specification.v2.yaml, experiments/EXP-IT-001/amendments, coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/tasks/TASK-20260731-107, ledger/hypotheses/H-IT-001.yaml |

## Deferred or Blocked

- `TASK-20260731-108`: dependency_not_completed:TASK-20260731-107:queued
- `TASK-20260731-109`: dependency_not_completed:TASK-20260731-108:queued
- `TASK-20260731-110`: dependency_not_completed:TASK-20260731-109:queued

## Dispatch Gates

- `concurrency_cap_respected`: passed
- `all_selected_dependencies_completed`: passed
- `selected_write_scopes_do_not_overlap`: passed
- `archive_tasks_run_in_isolation`: passed
- `all_artifact_paths_are_exact_and_scoped`: passed
- `archive_artifact_coverage_complete`: passed
- `completed_archive_commits_verified`: passed
- `archive_tasks_are_coordinator_owned`: passed
- `terminal_noncompleted_tasks_do_not_unblock_successors`: passed
- `claim_relevant_tasks_have_independent_review`: passed

Plan SHA-256: `38a28e1589b48a76844f286fd821c0ea0d682ca6bde43c53d8031d0bd31cc338`
