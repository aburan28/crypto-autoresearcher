# Dynamic Subagent Dispatch Plan

GOAL-P13-001 BATCH-003 repairs the two defects that independent review found in BATCH-002 (DEC-20260802-8227b9), in the order the reviewers converged on. NC2b costs zero compute: recompute the overhead c with the fitted intercept restored, from values already stored in RUN-PEC-6be870-a, validated by the requirement that the corrected estimator return c_null ~ 0.77 for the run's own O(1)-per-entry null object rather than the ~0 the defective law returns. NC2a then removes the ell=101/103 definitional seam by extending IMPL-B over ell 103..211, so the primary response has one definition across the whole fitted range. A superseding contract EXP-PEC-49c773 replaces the defective extrapolation law of EXP-PEC-6be870; the superseded contract and its run are not edited. This batch does not re-open the concrete NIST-I question by itself and asserts no cryptographic-scale claim.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-8e00fe` | red-team | queued | 80 | TASK-20260802-63145a, TASK-20260802-18f85d | coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-8e00fe/red_team_report.yaml | coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-8e00fe |
| `TASK-20260802-c50ea2` | validator | queued | 80 | TASK-20260802-63145a, TASK-20260802-18f85d | coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-c50ea2/validation_report.yaml | coordination/goals/GOAL-P13-001/batches/BATCH-003/reviews/TASK-20260802-c50ea2 |

## Deferred or Blocked

- `TASK-20260802-c1f7c8`: dependency_not_completed:TASK-20260802-c50ea2:queued, dependency_not_completed:TASK-20260802-8e00fe:queued

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

Plan SHA-256: `566b6b358b7471fd90cca263e48128727ce08e5918e8d3a0e2dba350eb27d624`
