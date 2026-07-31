# Dynamic Subagent Dispatch Plan

BATCH-019: bounded FC0 lifetime/Verify spike against CollimationSieve@6f9188e4 or explicit host-gap certificate for QM-MEMORY-MAP / QM-ERROR; keep QM-STOPPING open; retain FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED; do not equate BATCH-014; zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-047` | executor | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-019/tasks/TASK-20260730-047/spike_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-019/tasks/TASK-20260730-047/host_gap_or_impl_status.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-019/tasks/TASK-20260730-047/lifetime_verify_attempt.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-019/tasks/TASK-20260730-047/mutation_status.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-019/tasks/TASK-20260730-047/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-019/tasks/TASK-20260730-047 |

## Deferred or Blocked

- `TASK-20260730-048`: dependency_not_completed:TASK-20260730-047:queued
- `TASK-20260730-049`: dependency_not_completed:TASK-20260730-047:queued, dependency_not_completed:TASK-20260730-048:queued
- `TASK-20260730-050`: dependency_not_completed:TASK-20260730-049:queued

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

Plan SHA-256: `f8528af731463b2340917fdc9673a44ea5f54768b2fc6a4f8fca8373eb9f4701`
