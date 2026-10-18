# Dynamic Subagent Dispatch Plan

One twelve-residue manifest, then a snapshot.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261012-e25b3e` | executor | queued | 10 | - | experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/manifest.yaml, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/raw-result.json, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/launch.json, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/execution-receipt.json, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/command.txt, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/environment.json, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/stdout.log, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/stderr.log, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/check.stdout.log, experiments/EXP-ECDLP-bfbe6f/runs/RUN-ECDLP-8f5190/check.stderr.log | experiments/EXP-ECDLP-bfbe6f/runs |

## Deferred or Blocked

- `TASK-20261012-9fd959`: dependency_not_completed:TASK-20261012-e25b3e:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261012-e25b3e`: released (owner `executor-ideas-20261018`, epoch 1, expires 2026-10-18T03:41:26Z) -> queued_scope_free

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

- `TASK-20261012-e25b3e` (executor): card sets fallback_allowed: false, but policy 'executor-mechanical' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261012-9fd959` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

Plan SHA-256: `bbe8931611659885813dcc8d3915097753b97bdec9eabf9bcc00080a8dd64d67`
