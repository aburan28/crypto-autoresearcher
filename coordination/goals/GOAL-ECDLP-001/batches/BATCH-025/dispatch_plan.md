# Dynamic Subagent Dispatch Plan

BATCH-025 structure-null-r2 after APPROVED b27db960: run snapshotted; Val+RT; ledger EV-DS-008/DEC-20260731-028. Toy ceiling. No EXP-IT launder. No STR.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-100` | validator | running | 70 | TASK-20260731-098, TASK-20260731-099 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-100/validation_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-100 |
| `TASK-20260731-101` | red-team | running | 70 | TASK-20260731-098, TASK-20260731-099 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-101/red_team_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-101 |

## Deferred or Blocked

- `TASK-20260731-102`: dependency_not_completed:TASK-20260731-100:running, dependency_not_completed:TASK-20260731-101:running

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

Plan SHA-256: `3e3d02bb1d0cf6e4d5a3386424d4ecb7f9a308c92955c800e4c7762cc94fc993`
