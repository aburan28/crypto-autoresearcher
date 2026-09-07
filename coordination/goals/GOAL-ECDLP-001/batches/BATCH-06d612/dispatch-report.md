# Dynamic Subagent Dispatch Plan

Execute the approved frozen contract EXP-ECDLP-a5f766 v2 (experiments/EXP-ECDLP-a5f766/approved-contract-v2.yaml, sha256 a81b1476...) exactly once under handoff TASK-20260906-b7628e; snapshot-archive the run package under TASK-20260906-cc73d8; then a committed-review-plan-gated independent validator + red-team round and Coordinator disposition. No scientific status change in this queue; disposition and any promotion belong to /review-evidence under Coordinator authority.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260906-b7628e` | executor | queued | 1 | - | experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e | experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e |

## Deferred or Blocked

- `TASK-20260906-cc73d8`: dependency_not_completed:TASK-20260906-b7628e:queued
- `TASK-20260907-6180fe`: dependency_not_completed:TASK-20260906-b7628e:queued, dependency_not_completed:TASK-20260906-cc73d8:queued
- `TASK-20260907-bfd902`: dependency_not_completed:TASK-20260907-f9d7ef:queued, dependency_not_completed:TASK-20260907-6180fe:queued
- `TASK-20260907-f9d7ef`: dependency_not_completed:TASK-20260906-b7628e:queued, dependency_not_completed:TASK-20260906-cc73d8:queued

## Expired Leases

These tasks are still `running` in the queue, but their lease expired
before `--now` -- their write_scope is no longer treated as held, so a
queued successor over the same scope was admitted instead. The task
itself is untouched: a Coordinator still records the actual terminal
state (most likely `failed`) the next time the queue is edited.
An entry marked `claim` is an expired write-once claim instead: the task
stays queued and is offered again; claim it at the next epoch.

- `TASK-20260906-b7628e` (executor, claim by `executor-a5f766-run`, expired 2026-09-07T20:31:05Z): experiments/EXP-ECDLP-a5f766/execution/TASK-20260906-b7628e

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260906-b7628e`: expired (owner `executor-a5f766-run`, epoch 1, expires 2026-09-07T20:31:05Z) -> queued_after_expiry

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

Plan SHA-256: `902aee0fc81eb9aa0569e5403dee90078a1616c3a25400e2f17d249a2365bdab`
