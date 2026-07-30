# Dynamic Subagent Dispatch Plan

BATCH-010: hash-addressed Peikert 2019/725 source integrity for Eq(4.1)/8L + one joint FC0-R2 stochastic resource-reconciliation worksheet for IDEA-20260729-001. Keep QUERY_MEMORY unreconciliation until control passes. Zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-005` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/source_manifest.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/peikert_2019_725_final.pdf, coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/extraction_transcript.md, coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/page_equation_mapping.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/reconciliation_worksheet.md, coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-010/tasks/TASK-20260730-005 |

## Deferred or Blocked

- `TASK-20260730-006`: dependency_not_completed:TASK-20260730-005:queued
- `TASK-20260730-007`: dependency_not_completed:TASK-20260730-005:queued, dependency_not_completed:TASK-20260730-006:queued
- `TASK-20260730-008`: dependency_not_completed:TASK-20260730-007:queued

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

Plan SHA-256: `01938ee8b8e410d3709d7963a5bca4008095e69faece777b2ae8a979f612295e`
