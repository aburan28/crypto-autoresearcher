# Dynamic Subagent Dispatch Plan

Execute the immutable fallback successors for the fully charged mechanism and verifiable-methodology screens, then independently review their verified snapshot before any ECDLP transition.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260721-007` | idea-generator | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-007/mechanism_frontier.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-007/novelty_matrix.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-007 |
| `TASK-20260721-008` | idea-generator | queued | 95 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008/methodology_frontier.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008/cost_audit.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-008 |

## Deferred or Blocked

- `TASK-20260721-009`: dependency_not_completed:TASK-20260721-007:queued, dependency_not_completed:TASK-20260721-008:queued
- `TASK-20260721-010`: dependency_not_completed:TASK-20260721-007:queued, dependency_not_completed:TASK-20260721-009:queued
- `TASK-20260721-011`: dependency_not_completed:TASK-20260721-008:queued, dependency_not_completed:TASK-20260721-009:queued
- `TASK-20260721-012`: dependency_not_completed:TASK-20260721-010:queued, dependency_not_completed:TASK-20260721-011:queued

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

Plan SHA-256: `7ca9eb76080246d4cb9a623f554238caa8c95f42fbbe241ffee842373009f3f7`
