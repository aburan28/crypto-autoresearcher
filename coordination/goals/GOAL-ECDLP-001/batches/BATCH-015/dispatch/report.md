# Dynamic Subagent Dispatch Plan

BATCH-015 RT35-CTRL-1/2 probe; reopen execution question iff pre-registered falsification fires.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-003` | red-team | queued | 80 | TASK-20260730-001, TASK-20260730-002 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/tasks/TASK-20260730-003/red_team_report.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/tasks/TASK-20260730-003/falsification_review.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/tasks/TASK-20260730-003 |

## Deferred or Blocked

- `TASK-20260730-004`: dependency_not_completed:TASK-20260730-003:queued

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

Plan SHA-256: `86df48db21a3b1dcb92700b602fcd1b09241031c5278eac2e8f63e1dc2967b13`
