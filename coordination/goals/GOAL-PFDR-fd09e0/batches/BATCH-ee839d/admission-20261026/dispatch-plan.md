# Dynamic Subagent Dispatch Plan

Native implementation handoff, independent interface review and archives only; exact24 scientific cells stay unrun.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261026-589ad5` | executor | queued | 100 | - | coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/report.md, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/diagram.svg, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/report.typ, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/report.pdf, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/owner-source-manifest.json, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/compatibility-map.json, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/prospective-packet.json, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/trialplan.json, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/transfer-assessment.md, coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5/validation.json | coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-ee839d/tasks/TASK-20261026-589ad5 |

## Deferred or Blocked

- `TASK-20261026-022037`: dependency_not_completed:TASK-20261026-971954:queued, dependency_not_completed:TASK-20261026-391e68:queued, dependency_not_completed:TASK-20261026-e48b18:queued
- `TASK-20261026-391e68`: dependency_not_completed:TASK-20261026-589ad5:queued, dependency_not_completed:TASK-20261026-971954:queued
- `TASK-20261026-971954`: dependency_not_completed:TASK-20261026-589ad5:queued
- `TASK-20261026-9fec07`: dependency_not_completed:TASK-20261026-391e68:queued, dependency_not_completed:TASK-20261026-e48b18:queued, dependency_not_completed:TASK-20261026-022037:queued
- `TASK-20261026-e48b18`: dependency_not_completed:TASK-20261026-589ad5:queued, dependency_not_completed:TASK-20261026-971954:queued

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

- `TASK-20261026-971954` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261026-022037` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261026-9fec07` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

Plan SHA-256: `f53594a53de9ff7206969b48fae49e4e11f6174cbf902ed8ec87949031371c4e`
