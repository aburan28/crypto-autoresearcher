# Dynamic Subagent Dispatch Plan

BATCH-004 EXISTS TO RUN THE ONE MEASUREMENT THAT CAN FALSIFY THIS CAMPAIGN'S SCOPING RULE RATHER THAN ACCUMULATE AGREEMENT WITH IT. EV-AES-96257a OBS-B3-4: there is no decay control and no null arm for zero-entry matrices anywhere in this campaign -- every arm at r >= 6 uses AES MixColumns. Under M0 and M1 every fiber size is a multiple of 256; under AES MixColumns the histogram is Poisson-shaped with max_occ 12. If that fiber degeneracy forces n mod 8 = 0 independently of round count, the r=5 half of CORR-20260802-46b73b is measuring nothing. The BATCH-001 validator recorded this gap three batches ago, its attempt ABORTED on a singular matrix, and it was never refilled. Rank 1 fills it, in seconds of compute, with a verified non-singular zero-entry layer swept against a no-zero-entry control at the same round counts. Rank 2 supplies the positive control BATCH-003 rank 4 lacked. Rank 3 is the most interesting measurement left: the r=5 yoyo signal is the ONLY campaign result whose S-box dependence has never been measured, and if it too survives a random bijective S-box then NOTHING this campaign has found is specific to AES.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260803-6ba122` | executor | queued | 100 | - | coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-6ba122/RESULTS.json, coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-6ba122/PREREGISTRATION.md, coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-6ba122/budget_stamps.jsonl | coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-6ba122 |
| `TASK-20260803-367b1b` | executor | queued | 95 | - | coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/RESULTS.json, coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/PREREGISTRATION.md, coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/budget_stamps.jsonl | coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b |

## Deferred or Blocked

- `TASK-20260803-6118b0`: dependency_not_completed:TASK-20260803-fab2b8:queued, dependency_not_completed:TASK-20260803-cc92f0:queued, dependency_not_completed:TASK-20260803-ae3fcd:queued
- `TASK-20260803-9b1482`: dependency_not_completed:TASK-20260803-6ba122:queued, dependency_not_completed:TASK-20260803-367b1b:queued
- `TASK-20260803-ae3fcd`: dependency_not_completed:TASK-20260803-fab2b8:queued, dependency_not_completed:TASK-20260803-cc92f0:queued
- `TASK-20260803-cc92f0`: dependency_not_completed:TASK-20260803-6ba122:queued, dependency_not_completed:TASK-20260803-367b1b:queued, dependency_not_completed:TASK-20260803-9b1482:queued
- `TASK-20260803-fab2b8`: dependency_not_completed:TASK-20260803-6ba122:queued, dependency_not_completed:TASK-20260803-367b1b:queued, dependency_not_completed:TASK-20260803-9b1482:queued

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

Plan SHA-256: `9d290f1bb9a29b53176a3ea74d69ff5cbe676839b3905b915ed06e91ed83e511`
