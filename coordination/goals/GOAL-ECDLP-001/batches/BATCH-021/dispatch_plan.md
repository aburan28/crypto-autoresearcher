# Dynamic Subagent Dispatch Plan

Object-first, ledger-wide, primary-literature-checked ECDLP ideation after an empty focused rerank; preserve the full pre-ID cohort and independently audit semantic novelty before allocating any IDEA id.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260801-005` | idea-generator | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/tasks/TASK-20260801-005/idea_cohort.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/tasks/TASK-20260801-005/semantic_dedup.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/tasks/TASK-20260801-005 |

## Deferred or Blocked

- `TASK-20260801-006`: dependency_not_completed:TASK-20260801-005:queued
- `TASK-20260801-007`: dependency_not_completed:TASK-20260801-005:queued, dependency_not_completed:TASK-20260801-006:queued
- `TASK-20260801-008`: dependency_not_completed:TASK-20260801-007:queued

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

Plan SHA-256: `0314177cee6106345df9e0d6abdabe1c9295de0225b86ca757fac2266ff94f36`
