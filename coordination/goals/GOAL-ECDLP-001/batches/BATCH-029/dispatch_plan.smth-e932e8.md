# Dynamic Subagent Dispatch Plan

Settle the BATCH-028 calibration question with the two cheap arms both reviewers independently converged on, and do it under the approval gate BATCH-028 did not have. ARM 1, THE NULL-SCALING ARM: enlarge only the null at CELL-16 by 8x -- if D = 0.004808 is sampling noise it must decay as n^(-1/2), and if it does not the separation is real and the stricter one-sample calibration wins. ARM 2, THE SUPPORT-MATCHED NULL: BATCH-028 found all 130816 discriminants square, so the treatment occupies half the support the null samples and no decision rule noticed. THE STRUCTURAL CHANGE IS TASK-20260802-e2f66c, A COORDINATOR APPROVAL TASK BETWEEN FREEZE AND EXECUTION, whose determination the executor must READ AND HALT ON. BATCH-028's contract ran with approved_by: null and self-declared evidence_eligible: true; here the contract carries NO self-declaration of standing at all, because eligibility is a determination made outside the artifact. Either arm can falsify BATCH-028's headline in minutes of compute, and that is a legitimate and expected outcome.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-979fae` | executor | queued | 100 | - | experiments/EXP-SMTH-e932e8/specification.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-029/tasks/TASK-20260802-979fae/freeze_receipt.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-029/tasks/TASK-20260802-979fae/budget_stamps.jsonl | coordination/goals/GOAL-ECDLP-001/batches/BATCH-029/tasks/TASK-20260802-979fae, experiments/EXP-SMTH-e932e8 |

## Deferred or Blocked

- `TASK-20260802-1839a9`: dependency_not_completed:TASK-20260802-979fae:queued, dependency_not_completed:TASK-20260802-e2f66c:queued, dependency_not_completed:TASK-20260802-2bf627:queued, dependency_not_completed:TASK-20260802-8c84fe:queued
- `TASK-20260802-2bf627`: dependency_not_completed:TASK-20260802-979fae:queued, dependency_not_completed:TASK-20260802-e2f66c:queued
- `TASK-20260802-3949e8`: dependency_not_completed:TASK-20260802-1839a9:queued, dependency_not_completed:TASK-20260802-ee4276:queued
- `TASK-20260802-8c84fe`: dependency_not_completed:TASK-20260802-979fae:queued, dependency_not_completed:TASK-20260802-e2f66c:queued, dependency_not_completed:TASK-20260802-2bf627:queued
- `TASK-20260802-e2f66c`: dependency_not_completed:TASK-20260802-979fae:queued
- `TASK-20260802-ee4276`: dependency_not_completed:TASK-20260802-979fae:queued, dependency_not_completed:TASK-20260802-e2f66c:queued, dependency_not_completed:TASK-20260802-2bf627:queued, dependency_not_completed:TASK-20260802-8c84fe:queued

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

Plan SHA-256: `199ebc317ac888b0b4faba3b22f56e82a4218fafe9f4b9001a993e542ea12117`
