# Dynamic Subagent Dispatch Plan

GOAL-P13-001 BATCH-004, the first UNCAPPED batch (DEC-20260802-fa3b26). Its primary objective is NC-3/NC-6: the first direct test of Heuristic 1's tail at the operating point, which multiplies all eighteen margin rows through P0 and has gone untested for three batches. Alongside it, three cheap items close out the c-programme honestly: NC2d-PROPER retires the FIRED FC-4 falsifier BY MEASUREMENT rather than by post-hoc restriction, NC2b-SLOPE is the only gate with power against assumption L1, and L2-WEIGHT prices the entry-weighted charging correction the red team raised against its own objection. A bibliographic subtask finally executes the baseline-constant retrieval named in three consecutive red-team reports and executed in none. This batch is opened on merits, NOT on available capacity: DEC-20260802-fa3b26 guard G-1 states that the absence of a cap is never a reason to continue. It is explicitly NOT an attempt at completion criterion 1, which remains unreachable by this method.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-0a794b` | coordinator | queued | 99 | TASK-20260802-baaeb1 | experiments/EXP-HEUR-d640d9/specification.yaml, experiments/EXP-PEC-d7979c/specification.yaml, coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-0a794b/opening_report.md | experiments/EXP-HEUR-d640d9/specification.yaml, experiments/EXP-PEC-d7979c/specification.yaml, coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-0a794b |

## Deferred or Blocked

- `TASK-20260802-375cd8`: dependency_not_completed:TASK-20260802-cd08cd:queued, dependency_not_completed:TASK-20260802-44c6a2:queued
- `TASK-20260802-44c6a2`: dependency_not_completed:TASK-20260802-4bd310:queued, dependency_not_completed:TASK-20260802-459b18:queued, dependency_not_completed:TASK-20260802-79a3cd:queued, dependency_not_completed:TASK-20260802-e83f4d:queued
- `TASK-20260802-459b18`: dependency_not_completed:TASK-20260802-56524a:queued
- `TASK-20260802-4bd310`: dependency_not_completed:TASK-20260802-56524a:queued
- `TASK-20260802-56524a`: dependency_not_completed:TASK-20260802-0a794b:queued
- `TASK-20260802-79a3cd`: dependency_not_completed:TASK-20260802-56524a:queued
- `TASK-20260802-cd08cd`: dependency_not_completed:TASK-20260802-4bd310:queued, dependency_not_completed:TASK-20260802-459b18:queued, dependency_not_completed:TASK-20260802-79a3cd:queued, dependency_not_completed:TASK-20260802-e83f4d:queued
- `TASK-20260802-e83f4d`: dependency_not_completed:TASK-20260802-4bd310:queued, dependency_not_completed:TASK-20260802-459b18:queued, dependency_not_completed:TASK-20260802-79a3cd:queued

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

Plan SHA-256: `a72157cc10077d43caa6caf6d2229e2c5d4ef47f5e84a2760137ba330f0f7822`
