# Dynamic Subagent Dispatch Plan

Retain complete affine-plane membership and strong exact decomposition coverage before SAT comparison

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260921-5c43c7` | executor | running | 50 | TASK-20260921-aad852 | experiments/EXP-KIC-3df18c/code/search.cpp, experiments/EXP-KIC-3df18c/code/check.py, experiments/EXP-KIC-3df18c/code/runner.py, experiments/EXP-KIC-3df18c/code/README.md, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/manifest.yaml, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/source_closure.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/environment.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/controls.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/process_receipts.jsonl, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/geometry.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/plane_catalogue.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/base_scores.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/support_cache.bin, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/support_cache_manifest.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/selected.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/independent_replay.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/execution_report.md, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/raw_outputs.tar.gz, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/raw_manifest.json | experiments/EXP-KIC-3df18c/code/search.cpp, experiments/EXP-KIC-3df18c/code/check.py, experiments/EXP-KIC-3df18c/code/runner.py, experiments/EXP-KIC-3df18c/code/README.md, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/manifest.yaml, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/source_closure.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/environment.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/controls.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/process_receipts.jsonl, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/geometry.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/plane_catalogue.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/base_scores.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/support_cache.bin, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/support_cache_manifest.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/selected.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/independent_replay.json, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/execution_report.md, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/raw_outputs.tar.gz, experiments/EXP-KIC-3df18c/runs/RUN-KIC-234d11/raw_manifest.json |

## Deferred or Blocked

- `TASK-20260921-26ee4f`: dependency_not_completed:TASK-20260921-5c43c7:running
- `TASK-20260921-3cf8c0`: dependency_not_completed:TASK-20260921-a83eca:queued, dependency_not_completed:TASK-20260921-c1a993:queued
- `TASK-20260921-a83eca`: dependency_not_completed:TASK-20260921-26ee4f:queued
- `TASK-20260921-c1a993`: dependency_not_completed:TASK-20260921-26ee4f:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260921-5c43c7`: live (owner `admissible-affine-n19-20260921`, epoch 1, expires 2026-09-22T02:26:08Z) -> running_with_lease
- `TASK-20260921-aad852`: released (owner `admissible-affine-n19-20260921`, epoch 1, expires 2026-09-22T02:25:40Z) -> ignored:queue_state_completed

## Archives verified on CONTENT only

These archives' commit bindings could not be reached, so they were
verified against their declared `path_sha256` instead. The content
binding held in every case below -- a mismatch would have failed.
This is the expected state after a squash merge; see
`ledger/corrections/CORR-20260802-a1f151.yaml`.

- `TASK-20260921-aad852`: declared content_first binding mode (12 path hashes verified)

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

Plan SHA-256: `bbf67badad0410889c1ac1b5e953f3a8f96b97a88ea9b53b0afca0c60934ed11`
