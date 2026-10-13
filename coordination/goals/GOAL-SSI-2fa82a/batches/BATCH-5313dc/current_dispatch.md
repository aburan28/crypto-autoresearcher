# Dynamic Subagent Dispatch Plan

With zero runs, construct or exactly obstruct one EigenX-v3 Ring-Witness CCA PKE using polynomial-time R_CER, relation-specific external-instance DXWE/XWE, and Naor--Yung plus simulation-sound NIZK, with every non-EndRing assumption separate.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261013-172e43` | red-team | queued | 3 | TASK-20261013-46b108, TASK-20261013-2b203f | coordination/design/TASK-20261013-451ecb/reviews/TASK-20261013-172e43/review.yaml | coordination/design/TASK-20261013-451ecb/reviews/TASK-20261013-172e43 |
| `TASK-20261013-7b385a` | reviewer | queued | 3 | TASK-20261013-46b108, TASK-20261013-2b203f | coordination/design/TASK-20261013-451ecb/reviews/TASK-20261013-7b385a/review.yaml | coordination/design/TASK-20261013-451ecb/reviews/TASK-20261013-7b385a |

## Deferred or Blocked

- `TASK-20261013-5d2db8`: dependency_not_completed:TASK-20261013-836352:queued
- `TASK-20261013-836352`: dependency_not_completed:TASK-20261013-8c1d9b:queued, dependency_not_completed:TASK-20261013-172e43:queued, dependency_not_completed:TASK-20261013-dd9b7c:queued, dependency_not_completed:TASK-20261013-9117c2:queued, dependency_not_completed:TASK-20261013-7b385a:queued
- `TASK-20261013-8c1d9b`: concurrency_cap
- `TASK-20261013-9117c2`: concurrency_cap
- `TASK-20261013-a43ec4`: dependency_not_completed:TASK-20261013-836352:queued, dependency_not_completed:TASK-20261013-5d2db8:queued
- `TASK-20261013-b7b5fa`: dependency_not_completed:TASK-20261013-8c1d9b:queued, dependency_not_completed:TASK-20261013-172e43:queued, dependency_not_completed:TASK-20261013-dd9b7c:queued, dependency_not_completed:TASK-20261013-9117c2:queued, dependency_not_completed:TASK-20261013-7b385a:queued, dependency_not_completed:TASK-20261013-836352:queued, dependency_not_completed:TASK-20261013-5d2db8:queued, dependency_not_completed:TASK-20261013-a43ec4:queued
- `TASK-20261013-dd9b7c`: concurrency_cap

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261013-2b203f`: released (owner `coordinator-eigenx-v3`, epoch 1, expires 2026-10-13T16:13:41Z) -> ignored:queue_state_completed
- `TASK-20261013-46b108`: released (owner `coordinator-eigenx-v3`, epoch 1, expires 2026-10-13T17:10:30Z) -> ignored:queue_state_completed

## Archives verified on CONTENT

These archives were verified against their declared `path_sha256`
rather than by a changed-path comparison. The content binding held
in every case below -- a mismatch would have failed. Entries with no
`verified_against` were checked at HEAD, which is the expected state
after a squash merge (see `ledger/corrections/CORR-20260802-a1f151.yaml`)
and is also what `content_first` asks for. An entry naming a commit was
checked in THAT tree, under `content_at_commit`, because its package
contains a record allowed to change after the archive.

- `TASK-20261013-2b203f`: declared content_first binding mode (5 path hashes verified)

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

- `TASK-20261013-8c1d9b` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-172e43` (red-team): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-dd9b7c` (validator): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-9117c2` (red-team): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-7b385a` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-836352` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-5d2db8` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-a43ec4` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-b7b5fa` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

Plan SHA-256: `aa4abe3e3e5242791e4d6ee107eccb90ac262160d2c93c4eae6bac90cb8c1a80`
