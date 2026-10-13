# Dynamic Subagent Dispatch Plan

With zero scientific runs, test at most three public adaptive-OneEnd coverage interfaces and independently audit whether any surviving bridge repairs the correctly directed EigenX/CEST-to-EndRing reduction and all six PKE obligations.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261013-3e1698` | red-team | queued | 3 | TASK-20261013-a9f4e6, TASK-20261013-ca4c9a, TASK-20261013-83d718 | coordination/design/TASK-20261013-ba3742/reviews/TASK-20261013-3e1698/review.yaml | coordination/design/TASK-20261013-ba3742/reviews/TASK-20261013-3e1698 |
| `TASK-20261013-794750` | validator | queued | 3 | TASK-20261013-a9f4e6, TASK-20261013-ca4c9a, TASK-20261013-83d718 | coordination/design/TASK-20261013-ba3742/reviews/TASK-20261013-794750/review.yaml | coordination/design/TASK-20261013-ba3742/reviews/TASK-20261013-794750 |

## Deferred or Blocked

- `TASK-20261013-56cb4b`: dependency_not_completed:TASK-20261013-a6dbb9:queued, dependency_not_completed:TASK-20261013-7ddb22:queued
- `TASK-20261013-7ddb22`: dependency_not_completed:TASK-20261013-a6dbb9:queued
- `TASK-20261013-a6dbb9`: dependency_not_completed:TASK-20261013-794750:queued, dependency_not_completed:TASK-20261013-f41a55:queued, dependency_not_completed:TASK-20261013-3e1698:queued
- `TASK-20261013-c882b8`: dependency_not_completed:TASK-20261013-794750:queued, dependency_not_completed:TASK-20261013-f41a55:queued, dependency_not_completed:TASK-20261013-3e1698:queued, dependency_not_completed:TASK-20261013-a6dbb9:queued, dependency_not_completed:TASK-20261013-7ddb22:queued, dependency_not_completed:TASK-20261013-56cb4b:queued
- `TASK-20261013-f41a55`: concurrency_cap

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261013-83d718`: live (owner `coordinator-eigenx-snapshot`, epoch 1, expires 2026-10-13T04:00:14Z) -> ignored:queue_state_completed
- `TASK-20261013-a9f4e6`: released (owner `eigenx-bridge-producer`, epoch 1, expires 2026-10-13T04:49:53Z) -> completed
- `TASK-20261013-ca4c9a`: released (owner `eigenx-scheme-producer`, epoch 1, expires 2026-10-13T04:50:00Z) -> completed

## Archives verified on CONTENT

These archives were verified against their declared `path_sha256`
rather than by a changed-path comparison. The content binding held
in every case below -- a mismatch would have failed. Entries with no
`verified_against` were checked at HEAD, which is the expected state
after a squash merge (see `ledger/corrections/CORR-20260802-a1f151.yaml`)
and is also what `content_first` asks for. An entry naming a commit was
checked in THAT tree, under `content_at_commit`, because its package
contains a record allowed to change after the archive.

- `TASK-20261013-83d718`: declared content_first binding mode (7 path hashes verified)

## Inference Advisories (ADVISORY -- these do not block dispatch)

Each card below sets `fallback_allowed: false` while its policy binds to a backend
this machine has no credentials for. That is not a safeguard here, it is a claim the
dispatch will break: the returning session reports `fallback_used: true` against a
card that forbade it, and the card gets amended AFTER the work ran. Declare the
binding on the card now, or record an `inference_amendment`.

AN ADVISORY IS NOT PERMISSION. It does not authorize a substitution -- only a
Coordinator `inference_amendment` on the card does, and a card carrying one is not
listed. A `degradable: false` policy is listed too, with a different remedy: moving
to a binding that fully meets its floor is fine, degrading it is not, and if nothing
meets the floor the CLAIM stays un-promoted while the campaign stays active.

- `TASK-20261013-794750` (validator): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-f41a55` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-3e1698` (red-team): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-a6dbb9` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-7ddb22` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-56cb4b` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-c882b8` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

Plan SHA-256: `ee53361e462514b857b0aff9e5fc9975be834306df8623b5d7c5e539a33d3695`
