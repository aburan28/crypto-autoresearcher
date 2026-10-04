# Dynamic Subagent Dispatch Plan

Test whether complete-admissible affine-plane membership reduces cold SAT/XOR point-decomposition cost compared with a strong same-domain encoding on a fixed stratified N19 panel.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260921-52008f` | executor | running | 50 | TASK-20260921-fabea6 | experiments/EXP-KIC-c3c732/code/field.py, experiments/EXP-KIC-c3c732/code/circuits.py, experiments/EXP-KIC-c3c732/code/worker.py, experiments/EXP-KIC-c3c732/code/runner.py, experiments/EXP-KIC-c3c732/code/checker.py, experiments/EXP-KIC-c3c732/code/tests.py, experiments/EXP-KIC-c3c732/code/native.cpp, experiments/EXP-KIC-c3c732/code/README.md, experiments/EXP-KIC-c3c732/code/analyze.py, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/manifest.yaml, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/command.txt, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/environment.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/stdout.log, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/stderr.log, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/raw-result.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/source_closure.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/build_receipt.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/solver_dependency_manifest.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/solver_snapshot_regular.tar.gz, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/base_manifest.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/case_manifest.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/native_controls.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/control_receipts.jsonl, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/science_receipts.jsonl, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/cnf_xor_model_manifest.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/model_group_replay.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/analysis.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/raw_outputs.tar.gz, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/raw_manifest.json, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34/execution_report.md | experiments/EXP-KIC-c3c732/code, experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34 |

## Deferred or Blocked

- `TASK-20260921-0ce27e`: dependency_not_completed:TASK-20260921-52008f:running
- `TASK-20260921-447fa1`: dependency_not_completed:TASK-20260921-0ce27e:queued
- `TASK-20260921-538005`: dependency_not_completed:TASK-20260921-0ce27e:queued
- `TASK-20260921-8a1a92`: dependency_not_completed:TASK-20260921-538005:queued, dependency_not_completed:TASK-20260921-447fa1:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260921-52008f`: live (owner `n19-affine-sat-20260921`, epoch 1, expires 2026-09-22T03:15:19Z) -> running_with_lease
- `TASK-20260921-fabea6`: released (owner `n19-affine-sat-20260921`, epoch 1, expires 2026-09-22T03:14:39Z) -> ignored:queue_state_completed

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260921-fabea6`: declared content_first binding mode (12 path hashes verified)

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

Plan SHA-256: `fa7758b16dbd992ca2a4eb3b61ad15ca6ba7ff3b35ec0af4ef64371871009b9e`
