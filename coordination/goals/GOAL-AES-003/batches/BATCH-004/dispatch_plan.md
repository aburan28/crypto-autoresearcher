# Dynamic Subagent Dispatch Plan

BATCH-004 EXISTS TO RUN THE ONE MEASUREMENT THAT CAN FALSIFY THIS CAMPAIGN'S SCOPING RULE RATHER THAN ACCUMULATE AGREEMENT WITH IT. EV-AES-96257a OBS-B3-4: there is no decay control and no null arm for zero-entry matrices anywhere in this campaign -- every arm at r >= 6 uses AES MixColumns. Under M0 and M1 every fiber size is a multiple of 256; under AES MixColumns the histogram is Poisson-shaped with max_occ 12. If that fiber degeneracy forces n mod 8 = 0 independently of round count, the r=5 half of CORR-20260802-46b73b is measuring nothing. The BATCH-001 validator recorded this gap three batches ago, its attempt ABORTED on a singular matrix, and it was never refilled. Rank 1 fills it, in seconds of compute, with a verified non-singular zero-entry layer swept against a no-zero-entry control at the same round counts. Rank 2 supplies the positive control BATCH-003 rank 4 lacked. Rank 3 is the most interesting measurement left: the r=5 yoyo signal is the ONLY campaign result whose S-box dependence has never been measured, and if it too survives a random bijective S-box then NOTHING this campaign has found is specific to AES.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260803-6118b0` | coordinator | queued | 60 | TASK-20260803-fab2b8, TASK-20260803-cc92f0, TASK-20260803-ae3fcd | ledger/evidence/EV-AES-c66a80.yaml, ledger/decisions/DEC-20260803-baae70.yaml, coordination/goals/GOAL-AES-003/batches/BATCH-004/archives/TASK-20260803-6118b0/ledger-receipt.json, ledger/corrections/CORR-20260803-791ca7.yaml | ledger/evidence/EV-AES-c66a80.yaml, ledger/decisions/DEC-20260803-baae70.yaml, ledger/goals/GOAL-AES-003.yaml, coordination/goals/GOAL-AES-003/batches/BATCH-004/archives/TASK-20260803-6118b0, ledger/corrections/CORR-20260803-791ca7.yaml |

## Deferred or Blocked

None.

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

Plan SHA-256: `83b8911bfda2c2aee1598cc12d512437653ccd5e247a072a164427e2ce33963e`
