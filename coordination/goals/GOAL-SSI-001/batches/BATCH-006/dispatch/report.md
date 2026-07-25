# Dynamic Subagent Dispatch Plan

SQI-FS-T0 sufficiency derivation for IDEA-20260725-003: Kani/Petit necessary-condition check; three-way disposition; zero curve compute.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260725-521` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-006/tasks/TASK-20260725-521/derivation_note.md, coordination/goals/GOAL-SSI-001/batches/BATCH-006/tasks/TASK-20260725-521/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-006/tasks/TASK-20260725-521 |

## Deferred or Blocked

- `TASK-20260725-522`: dependency_not_completed:TASK-20260725-521:queued
- `TASK-20260725-523`: dependency_not_completed:TASK-20260725-521:queued, dependency_not_completed:TASK-20260725-522:queued
- `TASK-20260725-524`: dependency_not_completed:TASK-20260725-523:queued

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

Plan SHA-256: `fa7458fed5c1e7a01e4c823338e074ebbb2607e202780f5082369405fa6e0389`
