# Dynamic Subagent Dispatch Plan

GOAL-P13-001 BATCH-002 executes red-team next-control NC-2 (DEC-20260724-016), the single deciding measurement for the concrete NIST-I question left INCONCLUSIVE by BATCH-001: the true per-entry cost of Algorithm 1's table construction, which paper Section 4.1 assumes to be exactly one F_{p^2}-operation. The batch freezes an experiment contract (EXP-PEC-6be870) and the Panny proof-of-concept source named by NC-2, runs one bounded Executor measurement at p ~ 2^40 with pre-registered null-object and instrument-fidelity controls, and closes with independent Validator and Red Team review before a ledger archive. The batch measures a toy-scale exponent and states an explicit extrapolation law; it does not claim a cryptographic-scale result and does not by itself promote or reject H-P13-001.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-b31c7f` | executor | queued | 90 | TASK-20260802-df7df5 | experiments/EXP-PEC-6be870/implementation/per_entry_cost.py, experiments/EXP-PEC-6be870/runs/RUN-PEC-6be870-a/manifest.yaml, experiments/EXP-PEC-6be870/runs/RUN-PEC-6be870-a/raw-result.json, experiments/EXP-PEC-6be870/runs/RUN-PEC-6be870-a/execution_report.yaml, experiments/EXP-PEC-6be870/runs/RUN-PEC-6be870-a/stdout.txt, experiments/EXP-PEC-6be870/runs/RUN-PEC-6be870-a/stderr.txt | experiments/EXP-PEC-6be870/implementation, experiments/EXP-PEC-6be870/runs, coordination/goals/GOAL-P13-001/batches/BATCH-002/tasks/TASK-20260802-b31c7f |

## Deferred or Blocked

- `TASK-20260802-96d908`: dependency_not_completed:TASK-20260802-b31c7f:queued, dependency_not_completed:TASK-20260802-ca5bdc:queued
- `TASK-20260802-9ade2e`: dependency_not_completed:TASK-20260802-b31c7f:queued, dependency_not_completed:TASK-20260802-ca5bdc:queued
- `TASK-20260802-ca5bdc`: dependency_not_completed:TASK-20260802-b31c7f:queued
- `TASK-20260802-e804d1`: dependency_not_completed:TASK-20260802-9ade2e:queued, dependency_not_completed:TASK-20260802-96d908:queued

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

Plan SHA-256: `07fcf15c88968e2cef45401cdf0a90692917a2f236def64981cbba9503e0088c`
