# Dynamic Subagent Dispatch Plan

Fresh Q4-only software qualification with source-only exact80 native seal, at most one separately admitted new-host cache advice pass if needed, then separately admitted Q4; no scientific approval.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261029-bbd49b` | coordinator | queued | 100 | - | coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/admission/TASK-20261029-30f612/preparation-admission.json | coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/continuations/DEC-20261029-03e304/admission/TASK-20261029-30f612/preparation-admission.json |

## Deferred or Blocked

- `TASK-20261029-30f612`: dependency_not_completed:TASK-20261029-9df840:queued
- `TASK-20261029-6cad2d`: dependency_not_completed:TASK-20261029-30f612:queued
- `TASK-20261029-6f4f28`: task_marked_blocked
- `TASK-20261029-947247`: dependency_not_completed:TASK-20261029-e276d7:queued
- `TASK-20261029-9df840`: dependency_not_completed:TASK-20261029-bbd49b:queued
- `TASK-20261029-e276d7`: dependency_not_completed:TASK-20261029-6f4f28:blocked, dependency_not_completed:TASK-20261029-e463ad:queued, dependency_not_completed:TASK-20261029-30f612:queued, dependency_not_completed:TASK-20261029-6cad2d:queued
- `TASK-20261029-e463ad`: dependency_not_completed:TASK-20261029-6f4f28:blocked

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261029-30f612`: live (owner `executor-native-q4prep-30f612`, epoch 1, expires 2026-10-29T17:48:50Z) -> ignored:dependencies_incomplete_from_this_view:TASK-20261029-9df840

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

Plan SHA-256: `ee39e06242abcb9137bbcde72695e8f2ce46659ddfd7837d68549fb496562588`
