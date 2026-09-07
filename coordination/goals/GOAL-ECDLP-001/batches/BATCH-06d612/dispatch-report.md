# Dynamic Subagent Dispatch Plan

Execute the approved frozen contract EXP-ECDLP-a5f766 v2 (experiments/EXP-ECDLP-a5f766/approved-contract-v2.yaml, sha256 a81b1476...) exactly once under handoff TASK-20260906-b7628e; snapshot-archive the run package under TASK-20260906-cc73d8; then a committed-review-plan-gated independent validator + red-team round and Coordinator disposition. No scientific status change in this queue; disposition and any promotion belong to /review-evidence under Coordinator authority.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260907-6180fe` | red-team | queued | 4 | TASK-20260906-b7628e, TASK-20260906-cc73d8 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-06d612/reviews/TASK-20260907-6180fe | coordination/goals/GOAL-ECDLP-001/batches/BATCH-06d612/reviews/TASK-20260907-6180fe |

## Deferred or Blocked

- `TASK-20260907-bfd902`: dependency_not_completed:TASK-20260907-f9d7ef:queued, dependency_not_completed:TASK-20260907-6180fe:queued
- `TASK-20260907-f9d7ef`: concurrency_cap

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260906-b7628e`: expired (owner `executor-a5f766-run`, epoch 1, expires 2026-09-07T20:31:05Z) -> ignored:queue_state_completed

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260906-cc73d8`: declared content_first binding mode (28 path hashes verified)

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

Plan SHA-256: `64756307b3483d5133bd26a6070ba89c9268778b1091bc598147953804d7725a`
