# Dynamic Subagent Dispatch Plan

Determine whether the accepted orbit-canonical pair representation saves total cold-job cost when its table is reused acrossmanypointdecomposition queries, including a largerfinitebase.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260922-89d6e6` | executor | queued | 50 | TASK-20260922-01282b | experiments/EXP-KIC-d9c828/code/native.cpp, experiments/EXP-KIC-d9c828/code/checker.py, experiments/EXP-KIC-d9c828/code/runner.py, experiments/EXP-KIC-d9c828/code/analyze.py, experiments/EXP-KIC-d9c828/code/README.md, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/source_closure.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/build_receipt.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/environment.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/case_manifest.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/native_controls.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/bases.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/public_panels.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/oracle_metadata.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/pair_tables.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/control_queries.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/control_receipt.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/independent_replay.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/checker_receipt.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/benchmark_receipts.jsonl, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/analysis.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/manifest.yaml, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/command.txt, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/stdout.log, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/stderr.log, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/raw-result.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/raw_outputs.tar.gz, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/raw_manifest.json, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/execution_report.md | experiments/EXP-KIC-d9c828/code, experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9 |

## Deferred or Blocked

- `TASK-20260922-546d42`: dependency_not_completed:TASK-20260922-89d6e6:queued
- `TASK-20260922-a0c874`: dependency_not_completed:TASK-20260922-546d42:queued, dependency_not_completed:TASK-20260922-89d6e6:queued
- `TASK-20260922-a5ab4c`: dependency_not_completed:TASK-20260922-546d42:queued, dependency_not_completed:TASK-20260922-89d6e6:queued
- `TASK-20260922-c067b4`: dependency_not_completed:TASK-20260922-a0c874:queued, dependency_not_completed:TASK-20260922-a5ab4c:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260922-01282b`: released (owner `pair-reuse-20260922`, epoch 1, expires 2026-09-23T00:52:42Z) -> ignored:queue_state_completed

## Archives verified on CONTENT

These archives were verified against their declared `path_sha256`
rather than by a changed-path comparison. The content binding held
in every case below -- a mismatch would have failed. Entries with no
`verified_against` were checked at HEAD, which is the expected state
after a squash merge (see `ledger/corrections/CORR-20260802-a1f151.yaml`)
and is also what `content_first` asks for. An entry naming a commit was
checked in THAT tree, under `content_at_commit`, because its package
contains a record allowed to change after the archive.

- `TASK-20260922-01282b`: declared content_first binding mode (19 path hashes verified)

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

Plan SHA-256: `9723d270964d21b7940d51704a6e575222c602f65951347d3f03fa4d05086536`
