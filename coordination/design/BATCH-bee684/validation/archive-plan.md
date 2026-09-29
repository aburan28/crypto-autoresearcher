# Dynamic Subagent Dispatch Plan

Continue full pending-experiment approval and open-idea conversion objective with one ranked corrected ECC mechanism.

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

- `TASK-20260907-9d7e6a`: live (owner `coordinator-recall-archive`, epoch 1, expires 2026-09-08T06:28:03Z) -> ignored:queue_state_completed
- `TASK-20260907-b1a59b`: released (owner `coordinator-integrity-recall`, epoch 1, expires 2026-09-08T05:02:08Z) -> ignored:queue_state_completed

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

Plan SHA-256: `8bfd73d9bbc00daca1a449c10cf56230d217b64b903b040e374768434128e43b`
