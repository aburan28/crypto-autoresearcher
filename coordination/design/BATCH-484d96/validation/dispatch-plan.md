# Dynamic Subagent Dispatch Plan

Progress full pending-approval and open-idea objective without duplicating existing reserve design ownership; first new design is the CRT coverage calibration.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| none | - | - | - | - | - | - |

## Deferred or Blocked

None.

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260907-017550`: released (owner `coordinator-approval-design-20260907`, epoch 1, expires 2026-09-08T01:29:46Z) -> ignored:queue_state_completed
- `TASK-20260907-72aa15`: live (owner `coordinator-approval-design-20260907`, epoch 1, expires 2026-09-08T01:44:49Z) -> ignored:queue_state_completed
- `TASK-20260907-de5598`: released (owner `coordinator-approval-design-20260907`, epoch 1, expires 2026-09-08T01:36:50Z) -> ignored:queue_state_completed
- `TASK-20260907-f87818`: released (owner `coordinator-approval-design-20260907`, epoch 1, expires 2026-09-08T01:07:59Z) -> ignored:queue_state_completed

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

Plan SHA-256: `ff72bf04232c5c305f0ad253d8be7692b8ed74e559867ad44eeabd1f81570d00`
