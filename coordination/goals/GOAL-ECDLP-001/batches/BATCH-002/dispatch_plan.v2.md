# Dynamic Subagent Dispatch Plan

Execute the immutable authorized-fallback successor for one bounded frontier-B certificate-contract revision, then preserve the existing snapshot and independent-review gates; authorize no implementation or experiment.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260722-012` | idea-generator | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-012/certificate_contract.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-012/derivation_and_no_go.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-012 |

## Deferred or Blocked

- `TASK-20260722-013`: dependency_not_completed:TASK-20260722-012:queued
- `TASK-20260722-014`: dependency_not_completed:TASK-20260722-012:queued, dependency_not_completed:TASK-20260722-013:queued
- `TASK-20260722-015`: dependency_not_completed:TASK-20260722-014:queued

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

Plan SHA-256: `e722bc5a0528cb8a956dba67f6ccaab2b92d08e4817f1c8da3f23cdd7bbfe069`
