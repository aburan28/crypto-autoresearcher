# Dynamic Subagent Dispatch Plan

Execute and independently validate the frozen EXP-MLKEM-001 Thorns exact-FIPS marginal audit without rare-event or n=256 testing.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-223` | validator | queued | 70 | TASK-20260724-221, TASK-20260724-222 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-004/tasks/TASK-20260724-223/validation_report.yaml, coordination/goals/GOAL-MLKEM-001/batches/BATCH-004/tasks/TASK-20260724-223/validation_notes.md | coordination/goals/GOAL-MLKEM-001/batches/BATCH-004/tasks/TASK-20260724-223 |
| `TASK-20260724-224` | reviewer | queued | 70 | TASK-20260724-221, TASK-20260724-222 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-004/tasks/TASK-20260724-224/review_report.yaml, coordination/goals/GOAL-MLKEM-001/batches/BATCH-004/tasks/TASK-20260724-224/technical_review.md | coordination/goals/GOAL-MLKEM-001/batches/BATCH-004/tasks/TASK-20260724-224 |

## Deferred or Blocked

- `TASK-20260724-225`: dependency_not_completed:TASK-20260724-223:queued, dependency_not_completed:TASK-20260724-224:queued

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

Plan SHA-256: `2c61c3342b53982f06f2ce06da465cd4d35ad6b3a16a57fa086992fe8c4f738c`
