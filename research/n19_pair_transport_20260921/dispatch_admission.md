# Dynamic Subagent Dispatch Plan

Complete orbit-canonical native pair lookup with exact inverse witness transport and test cold exact-three decomposition cost against a same-binary expanded pair table.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260921-b18d1a` | executor | running | 50 | TASK-20260921-4d18d0 | experiments/EXP-KIC-7bcef8/code/native.cpp, experiments/EXP-KIC-7bcef8/code/checker.py, experiments/EXP-KIC-7bcef8/code/runner.py, experiments/EXP-KIC-7bcef8/code/analyze.py, experiments/EXP-KIC-7bcef8/code/README.md, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/source_closure.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/build_receipt.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/environment.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/base_manifest.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/case_manifest.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/native_controls.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/control_tables.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/control_membership.bin, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/control_queries.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/control_receipt.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/independent_replay.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/checker_receipt.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/benchmark_receipts.jsonl, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/analysis.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/manifest.yaml, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/command.txt, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/stdout.log, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/stderr.log, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/raw-result.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/raw_outputs.tar.gz, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/raw_manifest.json, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e/execution_report.md | experiments/EXP-KIC-7bcef8/code, experiments/EXP-KIC-7bcef8/runs/RUN-KIC-278e3e |

## Deferred or Blocked

- `TASK-20260921-0350df`: dependency_not_completed:TASK-20260921-d0f343:queued, dependency_not_completed:TASK-20260921-b18d1a:running
- `TASK-20260921-7fb07f`: dependency_not_completed:TASK-20260921-0350df:queued, dependency_not_completed:TASK-20260921-c6dbe6:queued
- `TASK-20260921-c6dbe6`: dependency_not_completed:TASK-20260921-d0f343:queued, dependency_not_completed:TASK-20260921-b18d1a:running
- `TASK-20260921-d0f343`: dependency_not_completed:TASK-20260921-b18d1a:running

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260921-4d18d0`: released (owner `n19-pair-transport-20260921`, epoch 1, expires 2026-09-22T05:26:31Z) -> ignored:queue_state_completed
- `TASK-20260921-b18d1a`: live (owner `n19-pair-transport-20260921`, epoch 1, expires 2026-09-22T05:26:34Z) -> running_with_lease

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260921-4d18d0`: declared content_first binding mode (20 path hashes verified)

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

Plan SHA-256: `ee96828829700a6fa3a79ecd39b88763d29cf614bd5af20b3c017b10b2977425`
