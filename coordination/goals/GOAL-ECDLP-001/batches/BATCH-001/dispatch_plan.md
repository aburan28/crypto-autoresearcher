# Dynamic Subagent Dispatch Plan

Novelty-screen one fully charged attack-mechanism lane and one verifiable-methodology lane, then independently review survivors before any ECDLP claim or experiment is promoted.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260721-001` | idea-generator | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-001/mechanism_frontier.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-001/novelty_matrix.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-001 |
| `TASK-20260721-002` | idea-generator | queued | 95 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-002/methodology_frontier.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-002/cost_audit.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-001/tasks/TASK-20260721-002 |

## Deferred or Blocked

- `TASK-20260721-003`: dependency_not_completed:TASK-20260721-001:queued, dependency_not_completed:TASK-20260721-002:queued
- `TASK-20260721-004`: dependency_not_completed:TASK-20260721-001:queued, dependency_not_completed:TASK-20260721-003:queued
- `TASK-20260721-005`: dependency_not_completed:TASK-20260721-002:queued, dependency_not_completed:TASK-20260721-003:queued
- `TASK-20260721-006`: dependency_not_completed:TASK-20260721-004:queued, dependency_not_completed:TASK-20260721-005:queued

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

Plan SHA-256: `c50db0e6f68af175d2669bd793f3332f4bc980073aa253d0ea15d011977ebc61`
