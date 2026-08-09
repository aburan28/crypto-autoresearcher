# Dynamic Subagent Dispatch Plan

Refine the admitted SSI per-prime advice-frontier design and obtain fresh independent review before any execution authorization.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260809-950724` | red-team | queued | 3 | TASK-20260809-53689c, TASK-20260809-3c76a9 | coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724/red_team_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-950724 |
| `TASK-20260809-9f5850` | validator | queued | 3 | TASK-20260809-53689c, TASK-20260809-3c76a9 | coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-9f5850/validation_report.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-9f5850/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-6c960d/reviews/TASK-20260809-9f5850 |

## Deferred or Blocked

- `TASK-20260809-0c65c9`: dependency_not_completed:TASK-20260809-9f5850:queued, dependency_not_completed:TASK-20260809-950724:queued

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

Plan SHA-256: `e28ab3a3ccea433abe7726b63f8ba2c164185f4ccdf5e4f80978dcb728223bdd`
