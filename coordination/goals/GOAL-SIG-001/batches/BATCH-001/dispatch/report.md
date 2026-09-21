# Dynamic Subagent Dispatch Plan

Freeze D>=6 support-matched null re-derivation protocol (review-only) before new syzygy-cascade measurements.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260725-631` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SIG-001/batches/BATCH-001/tasks/TASK-20260725-631/d6_null_protocol.yaml, coordination/goals/GOAL-SIG-001/batches/BATCH-001/tasks/TASK-20260725-631/protocol_design_note.md | coordination/goals/GOAL-SIG-001/batches/BATCH-001/tasks/TASK-20260725-631 |

## Deferred or Blocked

- `TASK-20260725-632`: dependency_not_completed:TASK-20260725-631:queued
- `TASK-20260725-633`: dependency_not_completed:TASK-20260725-631:queued, dependency_not_completed:TASK-20260725-632:queued
- `TASK-20260725-634`: dependency_not_completed:TASK-20260725-633:queued

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

Plan SHA-256: `64b3390064b74a92f6aa6380bb26f032f35b8556a7f75e313f144270198aa4c8`
