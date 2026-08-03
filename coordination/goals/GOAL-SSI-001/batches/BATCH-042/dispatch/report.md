# Dynamic Subagent Dispatch Plan

BATCH-042: advance QM-ERROR (f_union_ledger_partial) with a bounded zero-compute ledger/obligation step (tighten F-union from committed structure OR honest scoped pause/revisit); no reopening paused QM-STOPPING while REV unmet; no toy width; no fake-τ; no EXP-SSI-001; no clearance/breakthrough creep.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-139` | executor | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/qm_error_advancement.md, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/f_union_obligation_ledger.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/falsifiable_criteria.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/memory_map_status.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/classification.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/advancement_report.md, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/error_harness/__init__.py, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/error_harness/ledger_checks.py, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/error_harness/test_error.py, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/error_harness/run_harness.py, coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139/error_harness/harness_receipt.json | coordination/goals/GOAL-SSI-001/batches/BATCH-042/tasks/TASK-20260730-139 |

## Deferred or Blocked

- `TASK-20260730-140`: dependency_not_completed:TASK-20260730-139:queued
- `TASK-20260730-141`: dependency_not_completed:TASK-20260730-139:queued, dependency_not_completed:TASK-20260730-140:queued
- `TASK-20260730-142`: dependency_not_completed:TASK-20260730-141:queued

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

Plan SHA-256: `4c794eaba0f0843d532f4cc15cca7f79629b6e071b8525dd20017a7b65414c9b`
