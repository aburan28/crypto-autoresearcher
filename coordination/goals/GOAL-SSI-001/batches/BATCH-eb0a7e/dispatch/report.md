# Dynamic Subagent Dispatch Plan

Localize the EXP-WESOVOW-001 van Oorschot-Wiener anchor defect at its source and recompute the vOW-versus-Delfs-Galbraith comparison under the corrected charging law, from committed inputs only, without editing any frozen contract or committed run artifact. Producer, isolated snapshot archive, independent Validator review, isolated ledger archive. This batch measures nothing new: it is arithmetic on already-committed literals plus code reading.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260824-dd5b5c` | executor | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/defect_localization.md, coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/corrected_charging.py, coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/recomputed_table.json, coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/control_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/anchor_sensitivity.md | coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c |

## Deferred or Blocked

- `TASK-20260824-52f6d0`: dependency_not_completed:TASK-20260824-5b150a:queued
- `TASK-20260824-5b150a`: dependency_not_completed:TASK-20260824-dd5b5c:queued, dependency_not_completed:TASK-20260824-e8f6b7:queued
- `TASK-20260824-e8f6b7`: dependency_not_completed:TASK-20260824-dd5b5c:queued

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

Plan SHA-256: `294fe47e2afd195819fe2f99ba9688162cfb9735420d4d6e84070804aca4e4cb`
