# Dynamic Subagent Dispatch Plan

Close the two remaining open measurement routes on the index-calculus and lifting lines by exact counting: the never-executed EXP-FB3-001 factor-base geometry battery (RQ-FB3-001) and the unmeasurable-as-contracted EXP-XEDN-001 phase-2 xedni census, replaced by the frozen EXP-XEDN-002 exact census (RQ-XEDN-001). Every producer is independently validated and red-teamed before any status transition.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-228` | executor | queued | 90 | TASK-20260724-227 | experiments/EXP-FB3-001/analysis.md, experiments/EXP-FB3-001/conservation.md, experiments/EXP-FB3-001/execution-report.yaml | experiments/EXP-FB3-001/implementation, experiments/EXP-FB3-001/runs, experiments/EXP-FB3-001/analysis.md, experiments/EXP-FB3-001/conservation.md, experiments/EXP-FB3-001/execution-report.yaml |
| `TASK-20260724-229` | executor | queued | 90 | TASK-20260724-227 | experiments/EXP-XEDN-002/analysis.md, experiments/EXP-XEDN-002/derivation.md, experiments/EXP-XEDN-002/execution-report.yaml | experiments/EXP-XEDN-002/implementation, experiments/EXP-XEDN-002/runs, experiments/EXP-XEDN-002/analysis.md, experiments/EXP-XEDN-002/derivation.md, experiments/EXP-XEDN-002/execution-report.yaml |

## Deferred or Blocked

- `TASK-20260724-230`: dependency_not_completed:TASK-20260724-228:queued
- `TASK-20260724-231`: dependency_not_completed:TASK-20260724-229:queued
- `TASK-20260724-232`: dependency_not_completed:TASK-20260724-228:queued, dependency_not_completed:TASK-20260724-230:queued
- `TASK-20260724-233`: dependency_not_completed:TASK-20260724-228:queued, dependency_not_completed:TASK-20260724-230:queued
- `TASK-20260724-234`: dependency_not_completed:TASK-20260724-229:queued, dependency_not_completed:TASK-20260724-231:queued
- `TASK-20260724-235`: dependency_not_completed:TASK-20260724-229:queued, dependency_not_completed:TASK-20260724-231:queued
- `TASK-20260724-236`: dependency_not_completed:TASK-20260724-232:queued, dependency_not_completed:TASK-20260724-233:queued, dependency_not_completed:TASK-20260724-234:queued, dependency_not_completed:TASK-20260724-235:queued

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

Plan SHA-256: `ac01da89006de764cd6f246bad2782a6baa83f1d4945ea6e1460068bd4c5d740`
