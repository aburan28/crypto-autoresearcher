# Dynamic Subagent Dispatch Plan

Harden the EXP-MLKEM-002 conformance gate against its five surviving red-team objections and apply the hardened gate across wolfSSL pre-fix, wolfSSL post-fix, and at least one additional independent open-source ML-KEM implementation, to decide whether the incomplete re-encryption comparison class is isolated to the audited commits or systemic, without key recovery, oracle construction, exploitation, or deployed-system interaction.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-237` | validator | queued | 70 | TASK-20260724-235, TASK-20260724-236 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-237/validation_report.yaml, coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-237/validation_notes.md | coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-237 |
| `TASK-20260724-238` | red-team | queued | 70 | TASK-20260724-235, TASK-20260724-236 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-238/red_team_report.yaml, coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-238/falsification_review.md | coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/tasks/TASK-20260724-238 |

## Deferred or Blocked

- `TASK-20260724-239`: dependency_not_completed:TASK-20260724-237:queued, dependency_not_completed:TASK-20260724-238:queued

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

Plan SHA-256: `5eba3212445e37b396eea465995974422e9a34f66b725e461ee5323bdd9ad791`
