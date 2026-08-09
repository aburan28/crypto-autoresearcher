# Dynamic Subagent Dispatch Plan

Repair the remaining SSI advice-frontier design gaps and obtain fresh independent review before any execution authorization.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260809-2ded5b` | red-team | queued | 3 | TASK-20260809-c58735, TASK-20260809-f1c4fa | coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b/red_team_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-2ded5b |
| `TASK-20260809-4492f4` | validator | queued | 3 | TASK-20260809-c58735, TASK-20260809-f1c4fa | coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-4492f4/validation_report.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-4492f4/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-6554d6/reviews/TASK-20260809-4492f4 |

## Deferred or Blocked

- `TASK-20260809-7fbbb0`: dependency_not_completed:TASK-20260809-4492f4:queued, dependency_not_completed:TASK-20260809-2ded5b:queued

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

Plan SHA-256: `b31174d0b810fa78b58c29e046cfe3140a4cf62738c10a980a63836ed2ee5a42`
