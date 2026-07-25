# Dynamic Subagent Dispatch Plan

Scoped baseline derivation for revised IDEA-20260725-001: F_p2 vs F_p regime split, low-memory isogeny-graph collision-search definition or falsification, matched-baseline recommendation.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260725-505` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-002/tasks/TASK-20260725-505/derivation_note.md, coordination/goals/GOAL-SSI-001/batches/BATCH-002/tasks/TASK-20260725-505/baseline_recommendation.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-002/tasks/TASK-20260725-505 |

## Deferred or Blocked

- `TASK-20260725-506`: dependency_not_completed:TASK-20260725-505:queued
- `TASK-20260725-507`: dependency_not_completed:TASK-20260725-505:queued, dependency_not_completed:TASK-20260725-506:queued
- `TASK-20260725-508`: dependency_not_completed:TASK-20260725-507:queued

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

Plan SHA-256: `1a9b8517097fc03ed9accbf567508935ff630fd8ee8133ee98277f1bbdd6538c`
