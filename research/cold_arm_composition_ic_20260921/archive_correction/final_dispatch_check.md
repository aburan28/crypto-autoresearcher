# Dynamic Subagent Dispatch Plan

Test combined cold-start IC improvements against existing and equally strengthened rho on a fixed fresh four-arm panel.

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

- `TASK-20260921-1bd94f`: released (owner `cold-single-ic-control-20260921`, epoch 1, expires 2026-09-21T22:58:18Z) -> ignored:queue_state_completed
- `TASK-20260921-7bbc5d`: released (owner `cold-single-ic-control-20260921`, epoch 1, expires 2026-09-21T22:44:54Z) -> ignored:queue_state_completed
- `TASK-20260921-95474b`: live (owner `cold-single-ic-control-20260921`, epoch 1, expires 2026-09-21T23:27:06Z) -> ignored:queue_state_completed
- `TASK-20260921-b5b7ec`: released (owner `cold-single-ic-control-20260921`, epoch 1, expires 2026-09-21T22:02:03Z) -> ignored:queue_state_completed

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260921-7bbc5d`: declared content_first binding mode (84 path hashes verified)
- `TASK-20260921-95474b`: declared content_first binding mode (27 path hashes verified)

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

Plan SHA-256: `343691def09a594da5c7263cf8cbf7279316437651afc638b378ef38f2a8b023`
