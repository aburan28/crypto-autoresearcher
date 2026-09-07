# Dynamic Subagent Dispatch Plan

Administrative recovery of the exact prior selected queue custody/schema defects; no scientific execution or status changes. Recover exact historical goal-head bytes from 93c6be1becda0a25254f7086502a2256e8cbbfe0 with expected hash 181b8ac53dbd575e35b59bbea1e67072e25c4f30eb36ab977ed7925269dfed9d; preserve reviews, EV and DEC bytes. Never restore historical goal over live head. Current pointer next_action remains zero-lattice instrument repair.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260907-376f68` | executor | queued | 100 | - | coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/tasks/TASK-20260907-376f68/preservation-package.json, coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/tasks/TASK-20260907-376f68/recovery-report.md | coordination/goals/GOAL-MLKEM-005/batches/BATCH-203eff/tasks/TASK-20260907-376f68 |

## Deferred or Blocked

- `TASK-20260907-848d71`: dependency_not_completed:TASK-20260907-376f68:queued
- `TASK-20260907-8c3306`: dependency_not_completed:TASK-20260907-376f68:queued, dependency_not_completed:TASK-20260907-848d71:queued
- `TASK-20260907-b1ccf9`: dependency_not_completed:TASK-20260907-8c3306:queued

## Dispatch Gates

- `claimed_tasks_are_not_offered_to_others`: passed
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

Plan SHA-256: `1dbe107e6b1200319da5a9d5ad9d54e2a75fcaa54d8f1e829b10a30bef3b9e64`
