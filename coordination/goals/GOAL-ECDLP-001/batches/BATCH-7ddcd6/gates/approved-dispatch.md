# Dynamic Subagent Dispatch Plan

Four fresh metadata-compatible replays of unchanged stage-0 ECDLP worksheets; preserve every original invalid attempt and make no scientific status change.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261018-f4abf9` | executor | queued | 13 | - | experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/launch.json, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/execution-receipt.json, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/command.txt, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/environment.json, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/stdout.log, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/stderr.log, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/check.stdout.log, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/check.stderr.log, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/manifest.yaml, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/raw-result.json, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/legacy-manifest.yaml, experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe/legacy-execution.json | experiments/EXP-ECDLP-5d6ec1/runs/RUN-ECDLP-6671fe |

## Deferred or Blocked

- `TASK-20261018-529622`: dependency_not_completed:TASK-20261018-9661ac:queued
- `TASK-20261018-744219`: concurrency_cap
- `TASK-20261018-9661ac`: concurrency_cap
- `TASK-20261018-da8a5f`: dependency_not_completed:TASK-20261018-f4abf9:queued
- `TASK-20261018-e0ee60`: concurrency_cap
- `TASK-20261018-e909e2`: dependency_not_completed:TASK-20261018-e0ee60:queued
- `TASK-20261018-ef2d22`: dependency_not_completed:TASK-20261018-744219:queued

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

- `TASK-20261018-744219` (executor): card sets fallback_allowed: false, but policy 'executor-implementation' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-ef2d22` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-e0ee60` (executor): card sets fallback_allowed: false, but policy 'executor-implementation' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-e909e2` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-9661ac` (executor): card sets fallback_allowed: false, but policy 'executor-implementation' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-529622` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-f4abf9` (executor): card sets fallback_allowed: false, but policy 'executor-implementation' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-da8a5f` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

Plan SHA-256: `3515a15048056de1c754b6fbbb2f23ee70162a3bf6052ab87fb1e23a556aa9d7`
