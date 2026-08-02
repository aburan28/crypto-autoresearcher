# Dynamic Subagent Dispatch Plan

GOAL-P13-001 BATCH-003 repairs the two defects that independent review found in BATCH-002 (DEC-20260802-8227b9), in the order the reviewers converged on. NC2b costs zero compute: recompute the overhead c with the fitted intercept restored, from values already stored in RUN-PEC-6be870-a, validated by the requirement that the corrected estimator return c_null ~ 0.77 for the run's own O(1)-per-entry null object rather than the ~0 the defective law returns. NC2a then removes the ell=101/103 definitional seam by extending IMPL-B over ell 103..211, so the primary response has one definition across the whole fitted range. A superseding contract EXP-PEC-49c773 replaces the defective extrapolation law of EXP-PEC-6be870; the superseded contract and its run are not edited. This batch does not re-open the concrete NIST-I question by itself and asserts no cryptographic-scale claim.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-63145a` | executor | queued | 90 | TASK-20260802-b33bd4 | experiments/EXP-PEC-49c773/implementation/corrected_extrapolation.py, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/manifest.yaml, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/raw-result.json, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/execution_report.yaml, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/stdout.txt, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/stderr.txt, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/command.txt, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/environment.json, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/stdout.log, experiments/EXP-PEC-49c773/runs/RUN-PEC-49c773-a/stderr.log | experiments/EXP-PEC-49c773/implementation, experiments/EXP-PEC-49c773/runs, coordination/goals/GOAL-P13-001/batches/BATCH-003/tasks/TASK-20260802-63145a |

## Deferred or Blocked

- `TASK-20260802-18f85d`: dependency_not_completed:TASK-20260802-63145a:queued
- `TASK-20260802-8e00fe`: dependency_not_completed:TASK-20260802-63145a:queued, dependency_not_completed:TASK-20260802-18f85d:queued
- `TASK-20260802-c1f7c8`: dependency_not_completed:TASK-20260802-c50ea2:queued, dependency_not_completed:TASK-20260802-8e00fe:queued
- `TASK-20260802-c50ea2`: dependency_not_completed:TASK-20260802-63145a:queued, dependency_not_completed:TASK-20260802-18f85d:queued

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

Plan SHA-256: `1ae344023d5ad6d864283a75964e5057f1da8cfdef694730877d7bf410ae3216`
