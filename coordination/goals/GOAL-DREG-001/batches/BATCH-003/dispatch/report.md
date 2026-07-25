# Dynamic Subagent Dispatch Plan

Freeze CTRL-B support-restricted null rank protocol (review-only) before any new D6 measurement.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260725-691` | red-team | queued | 80 | TASK-20260725-689, TASK-20260725-690 | coordination/goals/GOAL-DREG-001/batches/BATCH-003/tasks/TASK-20260725-691/red_team_report.yaml, coordination/goals/GOAL-DREG-001/batches/BATCH-003/tasks/TASK-20260725-691/falsification_review.md | coordination/goals/GOAL-DREG-001/batches/BATCH-003/tasks/TASK-20260725-691 |

## Deferred or Blocked

- `TASK-20260725-692`: dependency_not_completed:TASK-20260725-691:queued

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

Plan SHA-256: `c138f2043bd323c48aafc0d0988d9b7461f4c860102c301f530284ca013799f0`
