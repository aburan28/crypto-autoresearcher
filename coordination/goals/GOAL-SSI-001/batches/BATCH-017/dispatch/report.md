# Dynamic Subagent Dispatch Plan

BATCH-017: implement recovery and object-lifetime tracing gate for QM-MEMORY-MAP / QM-ERROR (component-to-F maps, W/R/B/M_tail lifetime); retain FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED; keep QM-STOPPING open; do not equate BATCH-014; zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-039` | executor | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039/lifetime_trace.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039/component_to_F_map.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039/gate_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039/mutation_status.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-017/tasks/TASK-20260730-039 |

## Deferred or Blocked

- `TASK-20260730-040`: dependency_not_completed:TASK-20260730-039:queued
- `TASK-20260730-041`: dependency_not_completed:TASK-20260730-039:queued, dependency_not_completed:TASK-20260730-040:queued
- `TASK-20260730-042`: dependency_not_completed:TASK-20260730-041:queued

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

Plan SHA-256: `a627d799a3235774a553dda6685d2a0852b8894e666312a5037f13099494dbe6`
