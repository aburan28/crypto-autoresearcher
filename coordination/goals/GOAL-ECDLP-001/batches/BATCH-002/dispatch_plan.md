# Dynamic Subagent Dispatch Plan

Create and independently review one bounded frontier-B certificate-contract revision; authorize no implementation or experiment.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260722-006` | idea-generator | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-006/certificate_contract.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-006/derivation_and_no_go.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-006 |

## Deferred or Blocked

- `TASK-20260722-007`: dependency_not_completed:TASK-20260722-006:queued
- `TASK-20260722-008`: dependency_not_completed:TASK-20260722-006:queued, dependency_not_completed:TASK-20260722-007:queued
- `TASK-20260722-009`: dependency_not_completed:TASK-20260722-008:queued

## Dispatch Gates

- `concurrency_cap_respected`: passed
- `all_selected_dependencies_completed`: passed
- `selected_write_scopes_do_not_overlap`: passed
- `archive_tasks_run_in_isolation`: passed
- `all_artifact_paths_are_exact_and_scoped`: passed
- `archive_artifact_coverage_complete`: passed
- `completed_archive_commits_verified`: passed
- `coordinator_only_promotes_research_status`: passed
- `terminal_noncompleted_tasks_do_not_unblock_successors`: passed
- `claim_relevant_tasks_have_independent_review`: passed

Plan SHA-256: `e4a928bf5219c407a20b0c7c6a344dbeab16fa1903af5e0fa690ebe93cd11fdc`
