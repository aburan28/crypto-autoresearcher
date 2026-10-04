# Dynamic Subagent Dispatch Plan

Preserve the invalid opening archive, admit an additive repair, and create a content-first opening snapshot without releasing protocol design or mathematical execution.

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

- `TASK-20260824-c85718`: released (owner `coordinator-ecq-2`, epoch 2, expires 2026-08-30T23:04:30Z) -> ignored:queue_state_completed
- `TASK-20260831-234e80`: released (owner `coordinator-ecq-2`, epoch 1, expires 2026-08-31T16:46:43Z) -> ignored:queue_state_completed
- `TASK-20260831-46a7e5`: released (owner `coordinator-ecq-2`, epoch 1, expires 2026-08-31T17:05:22Z) -> ignored:queue_state_completed
- `TASK-20260831-5f39cb`: live (owner `coordinator-ecq-5`, epoch 1, expires 2026-09-02T02:43:27Z) -> ignored:queue_state_completed
- `TASK-20260831-b36a44`: released (owner `coordinator-ecq-5`, epoch 1, expires 2026-09-02T02:32:36Z) -> ignored:queue_state_completed
- `TASK-20260831-b83032`: released (owner `coordinator-ecq-5`, epoch 3, expires 2026-09-02T01:50:19Z) -> ignored:queue_state_completed
- `TASK-20260831-e24039`: released (owner `coordinator-ecq-5`, epoch 1, expires 2026-09-02T02:12:25Z) -> ignored:queue_state_completed
- `TASK-20260831-ea2561`: released (owner `coordinator-ecq-2`, epoch 1, expires 2026-08-31T17:16:44Z) -> ignored:queue_state_completed

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260824-861144`: declared content_first binding mode (11 path hashes verified)
- `TASK-20260824-32cf98`: declared content_first binding mode (3 path hashes verified)
- `TASK-20260831-2b729c`: declared content_first binding mode (6 path hashes verified)
- `TASK-20260831-f4ecd2`: declared content_first binding mode (3 path hashes verified)
- `TASK-20260831-8b9e45`: declared content_first binding mode (6 path hashes verified)

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

Plan SHA-256: `c5944115b77c6603ba3d4391a5c93fb1218676e5c8fec0e44969f6c440b801d8`
