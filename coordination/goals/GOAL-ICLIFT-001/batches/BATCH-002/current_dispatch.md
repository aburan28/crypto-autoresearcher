# Dynamic Subagent Dispatch Plan

BATCH-002: decide whether max_|coeff| of Mordell-Weil relations among free-x integral sections of the frozen EXP-XEDN-002 family is bounded or grows with p — the cheapest control that can force withdrawal of DEC-20260724-008.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-239` | executor | queued | 90 | TASK-20260724-238 | experiments/EXP-XEDN-003/analysis.md, experiments/EXP-XEDN-003/execution-report.yaml | experiments/EXP-XEDN-003/implementation, experiments/EXP-XEDN-003/runs, experiments/EXP-XEDN-003/analysis.md, experiments/EXP-XEDN-003/execution-report.yaml |

## Deferred or Blocked

- `TASK-20260724-240`: dependency_not_completed:TASK-20260724-239:queued
- `TASK-20260724-241`: dependency_not_completed:TASK-20260724-239:queued, dependency_not_completed:TASK-20260724-240:queued
- `TASK-20260724-242`: dependency_not_completed:TASK-20260724-239:queued, dependency_not_completed:TASK-20260724-240:queued
- `TASK-20260724-243`: dependency_not_completed:TASK-20260724-241:queued, dependency_not_completed:TASK-20260724-242:queued

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

Plan SHA-256: `b65703c25fc62aac102f5ca75c789213e4639df5f6b9c0f3f74fa562a16c4b1b`
