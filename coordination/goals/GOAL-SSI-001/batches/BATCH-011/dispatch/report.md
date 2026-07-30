# Dynamic Subagent Dispatch Plan

BATCH-011: FC0-R2 joint stopping-law and global-liveness control for IDEA-20260729-001. Either exhibit a source-compatible finite joint additive ledger with instantiated global memory schedule and common operational error metric, or reconfirm FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED with named blockers. Optional ePrint PDF re-fetch. Zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-009` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-011/tasks/TASK-20260730-009/stopping_liveness_control.md, coordination/goals/GOAL-SSI-001/batches/BATCH-011/tasks/TASK-20260730-009/joint_ledger.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-011/tasks/TASK-20260730-009/eprint_fetch_attempt.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-011/tasks/TASK-20260730-009/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-011/tasks/TASK-20260730-009 |

## Deferred or Blocked

- `TASK-20260730-010`: dependency_not_completed:TASK-20260730-009:queued
- `TASK-20260730-011`: dependency_not_completed:TASK-20260730-009:queued, dependency_not_completed:TASK-20260730-010:queued
- `TASK-20260730-012`: dependency_not_completed:TASK-20260730-011:queued

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

Plan SHA-256: `b2dadd1fce85ecffa91ce1f610364364c5c925358d455e1506faaeb535637486`
