# Dynamic Subagent Dispatch Plan

Harden the EXP-MLKEM-002 conformance gate against its five surviving red-team objections and apply the hardened gate across wolfSSL pre-fix, wolfSSL post-fix, and at least one additional independent open-source ML-KEM implementation, to decide whether the incomplete re-encryption comparison class is isolated to the audited commits or systemic, without key recovery, oracle construction, exploitation, or deployed-system interaction.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-234` | coordinator | queued | 95 | TASK-20260724-233 | coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/archives/TASK-20260724-234/snapshot-receipt.json | coordination/goals/GOAL-MLKEM-001/batches/BATCH-006/archives/TASK-20260724-234 |

## Deferred or Blocked

- `TASK-20260724-235`: dependency_not_completed:TASK-20260724-234:queued
- `TASK-20260724-236`: dependency_not_completed:TASK-20260724-235:queued
- `TASK-20260724-237`: dependency_not_completed:TASK-20260724-235:queued, dependency_not_completed:TASK-20260724-236:queued
- `TASK-20260724-238`: dependency_not_completed:TASK-20260724-235:queued, dependency_not_completed:TASK-20260724-236:queued
- `TASK-20260724-239`: dependency_not_completed:TASK-20260724-237:queued, dependency_not_completed:TASK-20260724-238:queued

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

Plan SHA-256: `f36931daa8751812d066d34ff8c0cc5c51c133f20ea89b70c3585c2f385e9f1e`
