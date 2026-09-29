# Dynamic Subagent Dispatch Plan

Find a target-independent factor-base and corresponding exact point-decomposition representation with lower fully charged cost, potentially using SAT.

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

- `TASK-20260921-0205d6`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T00:01:22Z) -> ignored:queue_state_completed
- `TASK-20260921-0867e1`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T00:04:30Z) -> ignored:queue_state_completed
- `TASK-20260921-0f27d6`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-21T23:45:38Z) -> ignored:queue_state_completed
- `TASK-20260921-38dd45`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T00:32:31Z) -> ignored:queue_state_completed
- `TASK-20260921-4160c9`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T01:59:50Z) -> ignored:queue_state_completed
- `TASK-20260921-46605b`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T01:59:46Z) -> ignored:queue_state_completed
- `TASK-20260921-4d0d90`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T01:32:40Z) -> ignored:queue_state_completed
- `TASK-20260921-882eef`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T01:37:10Z) -> ignored:queue_state_completed
- `TASK-20260921-bacbdf`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-21T23:48:54Z) -> ignored:queue_state_completed
- `TASK-20260921-c2ce6d`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T02:23:03Z) -> ignored:queue_state_completed
- `TASK-20260921-c931a1`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T01:29:22Z) -> ignored:queue_state_completed
- `TASK-20260921-f7c8da`: released (owner `golden-factor-base-sat-control-20260921`, epoch 1, expires 2026-09-22T01:52:27Z) -> ignored:queue_state_completed

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260921-0205d6`: declared content_first binding mode (4 path hashes verified)
- `TASK-20260921-38dd45`: declared content_first binding mode (9 path hashes verified)
- `TASK-20260921-c931a1`: declared content_first binding mode (62 path hashes verified)
- `TASK-20260921-c2ce6d`: declared content_first binding mode (59 path hashes verified)

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

Plan SHA-256: `abdf93e7ef1fd497310893190c92e7a466d27fc1245921f3946127de87e5a579`
