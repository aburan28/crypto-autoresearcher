# Dynamic Subagent Dispatch Plan

With zero runs, construct or exactly obstruct one prescribed-degree unique-isogeny EigenX-v2 KEM/PKE, its IND-CCA syntax, and its correctly directed attacker-to-complete-EndRing reduction; keep authenticated old CEST only as a non-EndRing control.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261013-311565` | idea-generator | queued | 1 | - | coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-311565/reduction-boundary.yaml, coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-311565/cost-adversarial-view.yaml, coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-311565/authenticated-cest-control.yaml | coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-311565 |
| `TASK-20261013-613c4e` | idea-generator | queued | 1 | - | coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-613c4e/candidate.md, coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-613c4e/scheme-contract.yaml, coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-613c4e/source-overlap.yaml | coordination/design/TASK-20261013-0348f3/tasks/TASK-20261013-613c4e |

## Deferred or Blocked

- `TASK-20261013-0ec69e`: dependency_not_completed:TASK-20261013-a7be35:queued, dependency_not_completed:TASK-20261013-26410a:queued
- `TASK-20261013-1dd311`: dependency_not_completed:TASK-20261013-613c4e:queued, dependency_not_completed:TASK-20261013-311565:queued
- `TASK-20261013-26410a`: dependency_not_completed:TASK-20261013-a7be35:queued
- `TASK-20261013-37ee89`: dependency_not_completed:TASK-20261013-613c4e:queued, dependency_not_completed:TASK-20261013-311565:queued, dependency_not_completed:TASK-20261013-1dd311:queued
- `TASK-20261013-460f4d`: dependency_not_completed:TASK-20261013-613c4e:queued, dependency_not_completed:TASK-20261013-311565:queued, dependency_not_completed:TASK-20261013-1dd311:queued
- `TASK-20261013-5f8b99`: dependency_not_completed:TASK-20261013-613c4e:queued, dependency_not_completed:TASK-20261013-311565:queued, dependency_not_completed:TASK-20261013-1dd311:queued
- `TASK-20261013-8361f9`: dependency_not_completed:TASK-20261013-613c4e:queued, dependency_not_completed:TASK-20261013-311565:queued, dependency_not_completed:TASK-20261013-1dd311:queued
- `TASK-20261013-8a6d75`: dependency_not_completed:TASK-20261013-613c4e:queued, dependency_not_completed:TASK-20261013-311565:queued, dependency_not_completed:TASK-20261013-1dd311:queued
- `TASK-20261013-a7be35`: dependency_not_completed:TASK-20261013-1dd311:queued, dependency_not_completed:TASK-20261013-460f4d:queued, dependency_not_completed:TASK-20261013-8361f9:queued, dependency_not_completed:TASK-20261013-37ee89:queued, dependency_not_completed:TASK-20261013-8a6d75:queued, dependency_not_completed:TASK-20261013-5f8b99:queued
- `TASK-20261013-d00f55`: dependency_not_completed:TASK-20261013-460f4d:queued, dependency_not_completed:TASK-20261013-8361f9:queued, dependency_not_completed:TASK-20261013-37ee89:queued, dependency_not_completed:TASK-20261013-8a6d75:queued, dependency_not_completed:TASK-20261013-5f8b99:queued, dependency_not_completed:TASK-20261013-a7be35:queued, dependency_not_completed:TASK-20261013-26410a:queued, dependency_not_completed:TASK-20261013-0ec69e:queued

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

- `TASK-20261013-613c4e` (idea-generator): card sets fallback_allowed: false, but policy 'research-deep' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-311565` (idea-generator): card sets fallback_allowed: false, but policy 'research-deep' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-1dd311` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-460f4d` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-8361f9` (red-team): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-37ee89` (validator): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-8a6d75` (red-team): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-5f8b99` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-a7be35` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-26410a` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-0ec69e` (reviewer): card sets fallback_allowed: false, but policy 'review-adversarial' binds on 'anthropic', which is not credentialed here -- and NO backend bound to this policy is credentialed here, so the only route is the runtime-native binding permitted by core rule 16. A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261013-d00f55` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

Plan SHA-256: `339a1247eac0ea976746fbd7a395205150c57b59a3ef323cd01a7da7e693a93e`
