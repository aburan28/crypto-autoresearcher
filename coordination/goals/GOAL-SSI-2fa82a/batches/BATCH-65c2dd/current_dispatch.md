# Dynamic Subagent Dispatch Plan

Run one zero-experiment alternating EndRing-PKE candidate funnel: two independent candidates, immutable snapshot, joint-owned security evaluation, gap-fed revision, second review, and a scoped final report/ledger decision.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261007-0ec6c3` | coordinator | queued | 90 | TASK-20261007-913665, TASK-20261007-61f3bc | coordination/design/TASK-20261007-9c36ba/archives/TASK-20261007-0ec6c3/snapshot-receipt.json | coordination/design/TASK-20261007-9c36ba/archives/TASK-20261007-0ec6c3 |

## Deferred or Blocked

- `TASK-20261007-385334`: dependency_not_completed:TASK-20261007-0ec6c3:queued
- `TASK-20261007-79e571`: dependency_not_completed:TASK-20261007-bc6c0f:queued, dependency_not_completed:TASK-20261007-385334:queued
- `TASK-20261007-8116c4`: dependency_not_completed:TASK-20261007-8ab26c:queued
- `TASK-20261007-8ab26c`: dependency_not_completed:TASK-20261007-79e571:queued
- `TASK-20261007-9c36ba`: dependency_not_completed:TASK-20261007-c47fc6:queued
- `TASK-20261007-b6c1ec`: dependency_not_completed:TASK-20261007-8ab26c:queued, dependency_not_completed:TASK-20261007-8116c4:queued
- `TASK-20261007-bc6c0f`: dependency_not_completed:TASK-20261007-0ec6c3:queued
- `TASK-20261007-c47fc6`: dependency_not_completed:TASK-20261007-b6c1ec:queued
- `TASK-20261007-e9b59b`: dependency_not_completed:TASK-20261007-bc6c0f:queued, dependency_not_completed:TASK-20261007-385334:queued, dependency_not_completed:TASK-20261007-79e571:queued, dependency_not_completed:TASK-20261007-b6c1ec:queued, dependency_not_completed:TASK-20261007-c47fc6:queued, dependency_not_completed:TASK-20261007-9c36ba:queued

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

- `TASK-20261007-913665` (idea-generator, completed):
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/candidate.md`
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/proof-search-map.yaml`
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/provenance.yaml`
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-913665/scheme-contract.yaml`
  - `ledger/hypotheses/H-SSI-fbe68d.yaml`
  - `ledger/proposals/IDEA-20261007-560bcb.yaml`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-913665 --push`
- `TASK-20261007-61f3bc` (idea-generator, completed):
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-61f3bc/candidate.md`
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-61f3bc/proof-search-map.yaml`
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-61f3bc/provenance.yaml`
  - `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-61f3bc/scheme-contract.yaml`
  - `ledger/hypotheses/H-SSI-3dad1f.yaml`
  - `ledger/proposals/IDEA-20261007-6553d5.yaml`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-61f3bc --push`

Plan SHA-256: `bd9589c72b8f0e8fd6cde271d49b0c0fa7ad01bf1c8afba2aa8be6961d3321c3`
