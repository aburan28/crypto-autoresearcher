# Dynamic Subagent Dispatch Plan

BATCH-013: bounded exact reachable-state analyzer for small sieve instances computing p(v1,v2) and searching for zero-progress witnesses, plus separate end-to-end recovery specification with W/R/B/M_tail and event F. Do not infer global tail from finite coverage. Zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-017` | executor | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/analyzer_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/analyzer_results.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/recovery_spec.md, coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/mutation_status.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-013/tasks/TASK-20260730-017 |

## Deferred or Blocked

- `TASK-20260730-018`: dependency_not_completed:TASK-20260730-017:queued
- `TASK-20260730-019`: dependency_not_completed:TASK-20260730-017:queued, dependency_not_completed:TASK-20260730-018:queued
- `TASK-20260730-020`: dependency_not_completed:TASK-20260730-019:queued

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

Plan SHA-256: `6e5e7276d4968fbc2136ff9653a76a080363b74c6fbddadfd947e4c0314a66b9`
