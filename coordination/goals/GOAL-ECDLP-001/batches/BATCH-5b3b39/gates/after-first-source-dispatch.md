# Dynamic Subagent Dispatch Plan

Two fresh native metadata reproductions of unchanged three-output stage-0 instruments; preserve original invalid attempts and make no scientific status change.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261018-1ce66f` | coordinator | queued | 31 | TASK-20261018-39dae2 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-5b3b39/archives/TASK-20261018-1ce66f.json | coordination/goals/GOAL-ECDLP-001/batches/BATCH-5b3b39/archives/TASK-20261018-1ce66f.json |

## Deferred or Blocked

- `TASK-20261018-ca2f90`: dependency_not_completed:TASK-20261018-eeb8cc:queued
- `TASK-20261018-eeb8cc`: archive_requires_isolation:TASK-20261018-1ce66f

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261018-39dae2`: released (owner `executor-ideas-20261018`, epoch 1, expires 2026-10-18T05:46:52Z) -> completed

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

- `TASK-20261018-eeb8cc` (executor): card sets fallback_allowed: false, but policy 'executor-implementation' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-ca2f90` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.
- `TASK-20261018-1ce66f` (coordinator): card sets fallback_allowed: false, but policy 'coordinator-orchestration-code' binds on 'anthropic', which is not credentialed here (servable instead: local). A session run here will report fallback_used: true against a card that forbids it. Declare the binding on the card now, or record an inference_amendment, rather than amending after the work has run.

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

## Unlanded producer output

These declared artifacts exist in this working tree and are ABSENT
from `HEAD`. They exist on one machine. When it goes away they go with
it, which is what happened to two blind source reads and a completed
run on 2026-09-21 (`ledger/corrections/CORR-20260921-942a62.yaml`).

A running producer legitimately appears here, so this is a report and
not a gate. Land anything whose producer has already returned.

- `TASK-20261018-39dae2` (executor, completed):
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/RESULTS.md`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/check.stderr.log`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/check.stdout.log`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/command.txt`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/environment.json`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/execution-receipt.json`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/launch.json`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/legacy-execution.json`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/legacy-manifest.yaml`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/manifest.yaml`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/raw-result.json`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/stderr.log`
  - `experiments/EXP-ECDLP-5c8854/runs/RUN-ECDLP-67ed93/stdout.log`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261018-39dae2 --push`

Plan SHA-256: `5cefb728a54e777c8e2f2fefca383ed960d0c84eef285d5e2152cecaff2933d6`
