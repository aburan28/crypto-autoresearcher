# Dynamic Subagent Dispatch Plan

Snapshot the schema-repaired review retry capsule and obtain fresh independent Validator and Red Team verdicts before any design archive or execution authorization.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260809-6f34ac` | validator | queued | 3 | TASK-20260809-887e42 | coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-6f34ac/validation_report.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-6f34ac/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-6f34ac |
| `TASK-20260809-83623a` | red-team | queued | 3 | TASK-20260809-887e42 | coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-83623a/red_team_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-83623a/runtime-session-receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-83623a |

## Deferred or Blocked

- `TASK-20260809-1dfd9a`: dependency_not_completed:TASK-20260809-6f34ac:queued, dependency_not_completed:TASK-20260809-83623a:queued

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

Plan SHA-256: `80a11536da6d8afec2a7d6fd86d3c2a44f5f901b0a01abbeeba686aff73cc951`
