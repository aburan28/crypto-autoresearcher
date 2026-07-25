# Dynamic Subagent Dispatch Plan

Specify and run EXP-MLKEM-005: library-facing adequacy probe plus preflight-or-widen second peer so the isolation-versus-systemic question is actually asked, without key recovery, oracle construction, exploitation, or deployed-system interaction.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-928` | validator | running | 80 | TASK-20260724-926, TASK-20260724-927 | coordination/goals/GOAL-MLKEM-002/batches/BATCH-002/tasks/TASK-20260724-928/validation_report.yaml, coordination/goals/GOAL-MLKEM-002/batches/BATCH-002/tasks/TASK-20260724-928/validation_notes.md | coordination/goals/GOAL-MLKEM-002/batches/BATCH-002/tasks/TASK-20260724-928 |
| `TASK-20260724-929` | red-team | running | 80 | TASK-20260724-926, TASK-20260724-927 | coordination/goals/GOAL-MLKEM-002/batches/BATCH-002/tasks/TASK-20260724-929/red_team_report.yaml, coordination/goals/GOAL-MLKEM-002/batches/BATCH-002/tasks/TASK-20260724-929/falsification_review.md | coordination/goals/GOAL-MLKEM-002/batches/BATCH-002/tasks/TASK-20260724-929 |

## Deferred or Blocked

- `TASK-20260724-930`: task_marked_blocked

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

Plan SHA-256: `21ae610fe320e3a612ece9876fa925aa77b11ac6f260e5377d2cf927b749e13f`
