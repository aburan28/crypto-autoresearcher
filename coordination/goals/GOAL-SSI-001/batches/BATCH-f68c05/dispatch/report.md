# Dynamic Subagent Dispatch Plan

Refresh and independently review the closed-list classical per-prime OneEnd advice-frontier derivation before authorizing any Stage 0/1 execution.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260809-099b4d` | red-team | queued | 3 | TASK-20260809-9990b8 | coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/reviews/TASK-20260809-099b4d/red_team_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/reviews/TASK-20260809-099b4d/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/reviews/TASK-20260809-099b4d |
| `TASK-20260809-69d1f1` | validator | queued | 3 | TASK-20260809-9990b8 | coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/reviews/TASK-20260809-69d1f1/validation_report.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/reviews/TASK-20260809-69d1f1/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/reviews/TASK-20260809-69d1f1 |

## Deferred or Blocked

- `TASK-20260809-7e85ad`: dependency_not_completed:TASK-20260809-69d1f1:queued, dependency_not_completed:TASK-20260809-099b4d:queued

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

Plan SHA-256: `cb94ae506ad64235e9c297f92d5173117404074f75febaaa86d75d5e7bf03ed5`
