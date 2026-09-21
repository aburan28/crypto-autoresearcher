# Dynamic Subagent Dispatch Plan

Independently review the complete SDEG counter protocol and reach a Coordinator approval or concrete revision disposition.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260908-ece27b` | validator | queued | 100 | TASK-20260908-5cdfb7 | coordination/design/BATCH-c2a2b6/reviews/TASK-20260908-ece27b/runtime-session-receipt.json, coordination/design/BATCH-c2a2b6/reviews/TASK-20260908-ece27b/review.yaml, coordination/design/BATCH-c2a2b6/reviews/TASK-20260908-ece27b/delivery-receipt.json | coordination/design/BATCH-c2a2b6/reviews/TASK-20260908-ece27b/runtime-session-receipt.json, coordination/design/BATCH-c2a2b6/reviews/TASK-20260908-ece27b/review.yaml, coordination/design/BATCH-c2a2b6/reviews/TASK-20260908-ece27b/delivery-receipt.json |

## Deferred or Blocked

- `TASK-20260908-020fc1`: concurrency_cap
- `TASK-20260908-1ca5e8`: dependency_not_completed:TASK-20260908-ece27b:queued
- `TASK-20260908-40e722`: dependency_not_completed:TASK-20260908-1ca5e8:queued
- `TASK-20260908-686ab3`: dependency_not_completed:TASK-20260908-40e722:queued, dependency_not_completed:TASK-20260908-ab0e84:queued, dependency_not_completed:TASK-20260908-020fc1:queued, dependency_not_completed:TASK-20260908-69a17c:queued, dependency_not_completed:TASK-20260908-7d435c:queued
- `TASK-20260908-69a17c`: concurrency_cap
- `TASK-20260908-7d435c`: dependency_not_completed:TASK-20260908-40e722:queued, dependency_not_completed:TASK-20260908-ab0e84:queued, dependency_not_completed:TASK-20260908-020fc1:queued, dependency_not_completed:TASK-20260908-69a17c:queued
- `TASK-20260908-ab0e84`: concurrency_cap

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260908-5cdfb7`: live (owner `coordinator-sdeg-review-binding-archive`, epoch 1, expires 2026-09-08T17:25:37Z) -> ignored:queue_state_completed
- `TASK-20260908-f2c006`: released (owner `coordinator-sdeg-review-binding`, epoch 1, expires 2026-09-08T17:15:41Z) -> ignored:queue_state_completed

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

Plan SHA-256: `a1c4362a6a42145bc81a18051e0020997e5ee8672bcecc1f82fdb67848a847cf`
