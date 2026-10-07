# Dynamic Subagent Dispatch Plan

Run one zero-run basis-independent Trap_E interface funnel: propose two distinct candidates, evaluate T1-T5, feed one gap to one fresh proposal, re-evaluate, and stop.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261007-64221a` | validator | queued | 40 | TASK-20261007-3ba2ff, TASK-20261007-6cd2cb | coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-64221a/validation-report.yaml, coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-64221a/review-attestation.yaml | coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-64221a |
| `TASK-20261007-e2c5d4` | red-team | queued | 40 | TASK-20261007-3ba2ff, TASK-20261007-6cd2cb | coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-e2c5d4/red-team-report.yaml, coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-e2c5d4/review-attestation.yaml | coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-e2c5d4 |

## Deferred or Blocked

- `TASK-20261007-80466d`: dependency_not_completed:TASK-20261007-64221a:queued, dependency_not_completed:TASK-20261007-e2c5d4:queued, dependency_not_completed:TASK-20261007-b67a0f:queued
- `TASK-20261007-b67a0f`: concurrency_cap
- `TASK-20261007-d54864`: dependency_not_completed:TASK-20261007-80466d:queued
- `TASK-20261007-e9bc39`: dependency_not_completed:TASK-20261007-64221a:queued, dependency_not_completed:TASK-20261007-e2c5d4:queued, dependency_not_completed:TASK-20261007-b67a0f:queued, dependency_not_completed:TASK-20261007-80466d:queued, dependency_not_completed:TASK-20261007-d54864:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20261007-06c0cd`: released (owner `coordinator-ssi-trapdoor`, epoch 1, expires 2026-10-07T17:08:00Z) -> completed
- `TASK-20261007-3ba2ff`: released (owner `idea-endring-trap-c`, epoch 1, expires 2026-10-07T17:39:11Z) -> ignored:queue_state_completed
- `TASK-20261007-4057bd`: released (owner `coordinator-ssi-trapdoor`, epoch 1, expires 2026-10-07T16:46:54Z) -> ignored:queue_state_completed
- `TASK-20261007-61dd3f`: released (owner `idea-endring-trap-b`, epoch 1, expires 2026-10-07T17:19:39Z) -> ignored:queue_state_completed
- `TASK-20261007-6cd2cb`: live (owner `coordinator-ssi-trapdoor`, epoch 1, expires 2026-10-07T17:06:59Z) -> ignored:queue_state_completed
- `TASK-20261007-6f5135`: released (owner `idea-endring-trap-a`, epoch 1, expires 2026-10-07T17:19:37Z) -> ignored:queue_state_completed
- `TASK-20261007-70a40e`: released (owner `reviewer-endring-trap-t5`, epoch 1, expires 2026-10-07T17:18:30Z) -> completed
- `TASK-20261007-ab8d2f`: released (owner `validator-endring-trap`, epoch 1, expires 2026-10-07T17:29:58Z) -> completed
- `TASK-20261007-df7b77`: released (owner `redteam-endring-trap`, epoch 1, expires 2026-10-07T17:30:00Z) -> completed

## Archives verified on CONTENT

These archives were verified against their declared `path_sha256`
rather than by a changed-path comparison. The content binding held
in every case below -- a mismatch would have failed. Entries with no
`verified_against` were checked at HEAD, which is the expected state
after a squash merge (see `ledger/corrections/CORR-20260802-a1f151.yaml`)
and is also what `content_first` asks for. An entry naming a commit was
checked in THAT tree, under `content_at_commit`, because its package
contains a record allowed to change after the archive.

- `TASK-20261007-4057bd`: declared content_first binding mode (13 path hashes verified)
- `TASK-20261007-6cd2cb`: declared content_first binding mode (7 path hashes verified)

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

- `TASK-20261007-ab8d2f` (validator, completed):
  - `coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-ab8d2f/review-attestation.yaml`
  - `coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-ab8d2f/validation-report.yaml`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-ab8d2f --push`
- `TASK-20261007-df7b77` (red-team, completed):
  - `coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-df7b77/red-team-report.yaml`
  - `coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-df7b77/review-attestation.yaml`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-df7b77 --push`
- `TASK-20261007-70a40e` (reviewer, completed):
  - `coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-70a40e/review-attestation.yaml`
  - `coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-70a40e/t5-report.yaml`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-70a40e --push`
- `TASK-20261007-06c0cd` (coordinator, completed):
  - `coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-06c0cd/composition.yaml`
  - `coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-06c0cd/gap-packet.yaml`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-06c0cd --push`

Plan SHA-256: `c1fc9d4e7cf52aaf0565aa07d9791bdd38bb386d57c24c309c097bd89d64d947`
