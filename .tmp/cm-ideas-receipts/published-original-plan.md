# Dynamic Subagent Dispatch Plan

File exactly five distinct, untested CM factor-base representation and defensive-assessment proposals under RQ-EQIC-8cb959; no mathematical execution or research-state transition.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| none | - | - | - | - | - | - |

## Deferred or Blocked

- `TASK-20260905-8b9222`: task_marked_blocked

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260905-1c36da`: released (owner `coordinator-cm-ideas-20260905`, epoch 2, expires 2026-09-05T17:25:48Z) -> ignored:queue_state_failed

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

Plan SHA-256: `b3e6b07973ba68b0850e16354ffdfaa245891e6b625c546e05b73bb7895ff62f`
