# Dynamic Subagent Dispatch Plan

Execute the GOAL-AES-001 BATCH-002 plan reranked on the committed DEC-20260731-003 checkpoint: (1) archive the two durable negative facts recomputed in BATCH-001 as a standalone, independently verifiable derivation note -- the artifact that must precede any decision relying on it -- and perform object-first ideation on the one exponent-relevant residual BATCH-001 left open, cross-column / super-box-level objects at the 2-round 32-bit super-box where ShiftRows sits on the outside; (2) repair harness defects H-1 and H-3 in a superseding BATCH-002 package, with H-2 recorded; (3) run GATE-601-B only, limited to its three self-contained yields with every struck literature comparison removed; then close the batch through independent three-way validation and a verified ledger archive that promotes KN-FIND-012 if and only if the derivation note survives review.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-701` | idea-generator | queued | 100 | - | coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701/derivation_note_column_local_obstructions.md, coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701/verify_derivation.py, coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701/candidate_report.yaml | coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-701 |
| `TASK-20260731-702` | executor | queued | 95 | - | coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702/mutation_control_v2.py, coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702/repair_receipt.json, coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702/repair_report.md | coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702 |
| `TASK-20260731-703` | executor | queued | 90 | - | coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703/gate_601b_impl.c, coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703/gate_601b_results.json, coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703/run_record.md | coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703 |

## Deferred or Blocked

- `TASK-20260731-704`: dependency_not_completed:TASK-20260731-701:queued, dependency_not_completed:TASK-20260731-702:queued, dependency_not_completed:TASK-20260731-703:queued
- `TASK-20260731-705`: dependency_not_completed:TASK-20260731-701:queued, dependency_not_completed:TASK-20260731-702:queued, dependency_not_completed:TASK-20260731-703:queued, dependency_not_completed:TASK-20260731-704:queued
- `TASK-20260731-706`: dependency_not_completed:TASK-20260731-705:queued

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

Plan SHA-256: `4262fa7804da87f95dc13547f91ed0611af5e455033f796265a9389c5a244452`
