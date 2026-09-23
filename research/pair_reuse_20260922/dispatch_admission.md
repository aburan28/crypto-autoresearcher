# Dynamic Subagent Dispatch Plan

Determine whether the accepted orbit-canonical pair representation saves total cold-job cost when its table is reused acrossmanypointdecomposition queries, including a largerfinitebase.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260922-a0c874` | validator | running | 50 | TASK-20260922-546d42, TASK-20260922-89d6e6 | research/pair_reuse_20260922/review/source_report.yaml, research/pair_reuse_20260922/review/source_rederive.py | research/pair_reuse_20260922/review/source_report.yaml, research/pair_reuse_20260922/review/source_rederive.py |
| `TASK-20260922-a5ab4c` | validator | running | 50 | TASK-20260922-546d42, TASK-20260922-89d6e6 | research/pair_reuse_20260922/review/blind_report.yaml, research/pair_reuse_20260922/review/blind_rederive.py, research/pair_reuse_20260922/review/blind_results.json | research/pair_reuse_20260922/review/blind_report.yaml, research/pair_reuse_20260922/review/blind_rederive.py, research/pair_reuse_20260922/review/blind_results.json |

## Deferred or Blocked

- `TASK-20260922-c067b4`: dependency_not_completed:TASK-20260922-a0c874:running, dependency_not_completed:TASK-20260922-a5ab4c:running

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260922-01282b`: released (owner `pair-reuse-20260922`, epoch 1, expires 2026-09-23T00:52:42Z) -> ignored:queue_state_completed
- `TASK-20260922-546d42`: released (owner `pair-reuse-20260922`, epoch 1, expires 2026-09-23T02:10:27Z) -> ignored:queue_state_completed
- `TASK-20260922-89d6e6`: released (owner `pair-reuse-20260922`, epoch 2, expires 2026-09-23T03:09:36Z) -> ignored:queue_state_completed
- `TASK-20260922-a0c874`: live (owner `pair-reuse-20260922`, epoch 1, expires 2026-09-23T03:14:03Z) -> running_with_lease
- `TASK-20260922-a5ab4c`: live (owner `pair-reuse-20260922`, epoch 1, expires 2026-09-23T03:14:32Z) -> running_with_lease

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
- `TASK-20260922-546d42`: declared content_first binding mode (112 path hashes verified)

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

Plan SHA-256: `9818c17e5b3ee995625ac2ca6ba743fc6145b4819aa48c01b6dcc2ed860abe05`
