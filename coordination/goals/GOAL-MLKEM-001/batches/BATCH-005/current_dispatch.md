# Dynamic Subagent Dispatch Plan

Execute and independently challenge the frozen EXP-MLKEM-002 direct comparison-primitive conformance audit on exact pre-fix and post-fix wolfSSL ML-KEM commits, without key recovery, oracle construction, or deployed-system interaction.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-230` | validator | queued | 70 | TASK-20260724-228, TASK-20260724-229 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-230/validation_report.yaml, coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-230/validation_notes.md | coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-230 |
| `TASK-20260724-231` | red-team | queued | 70 | TASK-20260724-228, TASK-20260724-229 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-231/red_team_report.yaml, coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-231/falsification_review.md | coordination/goals/GOAL-MLKEM-001/batches/BATCH-005/tasks/TASK-20260724-231 |

## Deferred or Blocked

- `TASK-20260724-232`: dependency_not_completed:TASK-20260724-230:queued, dependency_not_completed:TASK-20260724-231:queued

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

Plan SHA-256: `ac0b10c08a2c09d8ecce2fa515d88e9a1e2f42f9939208afdbfb0402dceed513`
