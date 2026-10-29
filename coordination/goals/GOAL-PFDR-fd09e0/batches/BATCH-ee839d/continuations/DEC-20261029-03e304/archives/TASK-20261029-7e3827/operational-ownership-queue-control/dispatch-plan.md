# Dynamic Subagent Dispatch Plan

Fresh Q4-only software qualification with source-only exact80 native seal, at most one separately admitted new-host cache advice pass if needed, then separately admitted Q4; no scientific approval.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261029-6f4f28` | executor | queued | 80 | TASK-20261029-30f612, TASK-20261029-6cad2d | coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-6f4f28/report.md, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-6f4f28/owner-results-manifest.json, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-6f4f28/qualification-results.json, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-6f4f28/validation.json | coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/tasks/TASK-20261029-6f4f28 |

## Deferred or Blocked

- `TASK-20261029-947247`: dependency_not_completed:TASK-20261029-e276d7:queued
- `TASK-20261029-e276d7`: dependency_not_completed:TASK-20261029-6f4f28:queued, dependency_not_completed:TASK-20261029-e463ad:queued
- `TASK-20261029-e463ad`: dependency_not_completed:TASK-20261029-6f4f28:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261029-30f612`: released (owner `executor-native-q4prep-30f612`, epoch 1, expires 2026-10-29T17:48:50Z) -> ignored:queue_state_completed
- `TASK-20261029-6cad2d`: released (owner `coordinator-native-prep-snapshot-6cad2d`, epoch 1, expires 2026-10-29T17:18:05Z) -> ignored:queue_state_completed
- `TASK-20261029-9df840`: released (owner `coordinator-native-admission-snapshot-9df840`, epoch 1, expires 2026-10-29T17:00:49Z) -> ignored:queue_state_completed
- `TASK-20261029-bbd49b`: released (owner `coordinator-native-oomgate-bbd49b`, epoch 1, expires 2026-10-29T16:51:56Z) -> ignored:queue_state_completed

## Archives verified on CONTENT

These archives were verified against their declared `path_sha256`
rather than by a changed-path comparison. The content binding held
in every case below -- a mismatch would have failed. Entries with no
`verified_against` were checked at HEAD, which is the expected state
after a squash merge (see `ledger/corrections/CORR-20260802-a1f151.yaml`)
and is also what `content_first` asks for. An entry naming a commit was
checked in THAT tree, under `content_at_commit`, because its package
contains a record allowed to change after the archive.

- `TASK-20261029-6cad2d`: declared content_at_commit binding mode (5 path hashes verified at `86f4e6b86ceb`)
- `TASK-20261029-9df840`: declared content_at_commit binding mode (2 path hashes verified at `e6d1de8f1a38`)

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

Plan SHA-256: `4e568823c5c6a0b180155bce3a7bda332b367c8e5b7911dfd6c127193434b7ce`
