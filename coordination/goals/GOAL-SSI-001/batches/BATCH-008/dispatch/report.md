# Dynamic Subagent Dispatch Plan

BATCH-008: revise CSIDH-COLLIMATION-FC0 against RT-20260729-003 O1-O5 and KN-TECH-051, then one zero-compute source-reconciliation derivation for IDEA-20260729-001. Cap at revised convention + three-way disposition; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260729-005` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-008/tasks/TASK-20260729-005/fc0_revision_note.md, coordination/goals/GOAL-SSI-001/batches/BATCH-008/tasks/TASK-20260729-005/derivation_note.md, coordination/goals/GOAL-SSI-001/batches/BATCH-008/tasks/TASK-20260729-005/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-008/tasks/TASK-20260729-005 |

## Deferred or Blocked

- `TASK-20260729-006`: dependency_not_completed:TASK-20260729-005:queued
- `TASK-20260729-007`: dependency_not_completed:TASK-20260729-005:queued, dependency_not_completed:TASK-20260729-006:queued
- `TASK-20260729-008`: dependency_not_completed:TASK-20260729-007:queued

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

Plan SHA-256: `aeea63ee0273b3b9a9e9c5f583e1e3be414f86ae52e4c8cde4cbd70691bd6325`
