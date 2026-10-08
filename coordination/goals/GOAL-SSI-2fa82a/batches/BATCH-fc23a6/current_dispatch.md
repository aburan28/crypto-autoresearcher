# Dynamic Subagent Dispatch Plan

Run one zero-run public-binding EndRing interface funnel: propose two distinct candidates, evaluate T1-T5, feed at most one gap to one fresh proposal, re-evaluate, and stop.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261008-417e47` | validator | queued | 80 | TASK-20261008-ba8247, TASK-20261008-896b35, TASK-20261008-eb1230 | coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-417e47/candidate-a-review.yaml, coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-417e47/candidate-b-review.yaml | coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-417e47 |
| `TASK-20261008-5b590b` | red-team | queued | 80 | TASK-20261008-ba8247, TASK-20261008-896b35, TASK-20261008-eb1230 | coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-5b590b/candidate-a-review.yaml, coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-5b590b/candidate-b-review.yaml | coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-5b590b |

## Deferred or Blocked

- `TASK-20261008-0eba4e`: dependency_not_completed:TASK-20261008-7a3610:queued, dependency_not_completed:TASK-20261008-84054f:queued
- `TASK-20261008-2464ec`: dependency_not_completed:TASK-20261008-0eba4e:queued, dependency_not_completed:TASK-20261008-a6a7bb:queued, dependency_not_completed:TASK-20261008-dd1990:queued
- `TASK-20261008-2b605a`: dependency_not_completed:TASK-20261008-417e47:queued, dependency_not_completed:TASK-20261008-5b590b:queued, dependency_not_completed:TASK-20261008-f0f824:queued
- `TASK-20261008-46d7e4`: dependency_not_completed:TASK-20261008-2464ec:queued
- `TASK-20261008-4f85ee`: dependency_not_completed:TASK-20261008-417e47:queued, dependency_not_completed:TASK-20261008-5b590b:queued, dependency_not_completed:TASK-20261008-f0f824:queued, dependency_not_completed:TASK-20261008-2b605a:queued
- `TASK-20261008-7a3610`: dependency_not_completed:TASK-20261008-4f85ee:queued
- `TASK-20261008-84054f`: dependency_not_completed:TASK-20261008-7a3610:queued
- `TASK-20261008-a6a7bb`: dependency_not_completed:TASK-20261008-7a3610:queued, dependency_not_completed:TASK-20261008-84054f:queued
- `TASK-20261008-cdfe7f`: dependency_not_completed:TASK-20261008-46d7e4:queued
- `TASK-20261008-dd1990`: dependency_not_completed:TASK-20261008-7a3610:queued, dependency_not_completed:TASK-20261008-84054f:queued
- `TASK-20261008-f0f824`: concurrency_cap
- `TASK-20261008-fc652a`: dependency_not_completed:TASK-20261008-0eba4e:queued, dependency_not_completed:TASK-20261008-a6a7bb:queued, dependency_not_completed:TASK-20261008-dd1990:queued, dependency_not_completed:TASK-20261008-2464ec:queued, dependency_not_completed:TASK-20261008-46d7e4:queued, dependency_not_completed:TASK-20261008-cdfe7f:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261008-896b35`: released (owner `idea-endring-binding-b`, epoch 1, expires 2026-10-08T02:10:33Z) -> ignored:queue_state_completed
- `TASK-20261008-ba8247`: released (owner `idea-endring-binding-a`, epoch 1, expires 2026-10-08T02:10:31Z) -> ignored:queue_state_completed
- `TASK-20261008-eb1230`: live (owner `coordinator-ssi-public-binding`, epoch 1, expires 2026-10-08T01:55:11Z) -> ignored:queue_state_completed

## Archives verified on CONTENT

These archives were verified against their declared `path_sha256`
rather than by a changed-path comparison. The content binding held
in every case below -- a mismatch would have failed. Entries with no
`verified_against` were checked at HEAD, which is the expected state
after a squash merge (see `ledger/corrections/CORR-20260802-a1f151.yaml`)
and is also what `content_first` asks for. An entry naming a commit was
checked in THAT tree, under `content_at_commit`, because its package
contains a record allowed to change after the archive.

- `TASK-20261008-eb1230`: declared content_first binding mode (13 path hashes verified)

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

Plan SHA-256: `25ca74338c2ba8231780d8ef7bdd4c7fd30720bf9164ca943daa2461265a4534`
