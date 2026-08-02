# Dynamic Subagent Dispatch Plan

GOAL-P13-001 BATCH-004, the first UNCAPPED batch (DEC-20260802-fa3b26). Its primary objective is NC-3/NC-6: the first direct test of Heuristic 1's tail at the operating point, which multiplies all eighteen margin rows through P0 and has gone untested for three batches. Alongside it, three cheap items close out the c-programme honestly: NC2d-PROPER retires the FIRED FC-4 falsifier BY MEASUREMENT rather than by post-hoc restriction, NC2b-SLOPE is the only gate with power against assumption L1, and L2-WEIGHT prices the entry-weighted charging correction the red team raised against its own objection. A bibliographic subtask finally executes the baseline-constant retrieval named in three consecutive red-team reports and executed in none. This batch is opened on merits, NOT on available capacity: DEC-20260802-fa3b26 guard G-1 states that the absence of a cap is never a reason to continue. It is explicitly NOT an attempt at completion criterion 1, which remains unreachable by this method.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-4bd310` | executor | queued | 95 | TASK-20260802-56524a | experiments/EXP-HEUR-d640d9/implementation/heuristic_tail.py, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/manifest.yaml, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/raw-result.json, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/execution_report.yaml, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/stdout.txt, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/stderr.txt, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/stdout.log, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/stderr.log, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/command.txt, experiments/EXP-HEUR-d640d9/runs/RUN-HEUR-d640d9-a/environment.json | experiments/EXP-HEUR-d640d9/implementation, experiments/EXP-HEUR-d640d9/runs, coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-4bd310 |
| `TASK-20260802-459b18` | executor | queued | 90 | TASK-20260802-56524a | experiments/EXP-PEC-d7979c/implementation/closeout.py, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/manifest.yaml, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/raw-result.json, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/execution_report.yaml, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/stdout.txt, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/stderr.txt, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/stdout.log, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/stderr.log, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/command.txt, experiments/EXP-PEC-d7979c/runs/RUN-PEC-d7979c-a/environment.json | experiments/EXP-PEC-d7979c/implementation, experiments/EXP-PEC-d7979c/runs, coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-459b18 |
| `TASK-20260802-79a3cd` | idea-generator | queued | 85 | TASK-20260802-56524a | coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-79a3cd/baseline_constant_report.yaml, coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-79a3cd/retrieval_log.yaml | coordination/goals/GOAL-P13-001/batches/BATCH-004/tasks/TASK-20260802-79a3cd |

## Deferred or Blocked

- `TASK-20260802-375cd8`: dependency_not_completed:TASK-20260802-cd08cd:queued, dependency_not_completed:TASK-20260802-44c6a2:queued
- `TASK-20260802-44c6a2`: dependency_not_completed:TASK-20260802-4bd310:queued, dependency_not_completed:TASK-20260802-459b18:queued, dependency_not_completed:TASK-20260802-79a3cd:queued, dependency_not_completed:TASK-20260802-e83f4d:queued
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

Plan SHA-256: `31111b68afa262e88eeab8106632fe0671e4685de8d9f3165f5f70c0a5fa6afc`
