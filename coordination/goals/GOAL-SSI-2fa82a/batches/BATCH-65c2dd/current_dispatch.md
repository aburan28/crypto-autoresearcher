# Dynamic Subagent Dispatch Plan

Run one zero-experiment alternating EndRing-PKE candidate funnel: two independent candidates, immutable snapshot, joint-owned security evaluation, gap-fed revision, second review, and a scoped final report/ledger decision.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261007-e9b59b` | coordinator | queued | 10 | TASK-20261007-bc6c0f, TASK-20261007-385334, TASK-20261007-79e571, TASK-20261007-b6c1ec, TASK-20261007-c47fc6, TASK-20261007-9c36ba | coordination/design/TASK-20261007-9c36ba/archives/TASK-20261007-e9b59b/ledger-receipt.json, ledger/evidence/EV-SSI-e454e0.yaml, ledger/decisions/DEC-20261007-43afbd.yaml, ledger/goals/GOAL-SSI-2fa82a/checkpoints/BATCH-65c2dd.yaml | coordination/design/TASK-20261007-9c36ba/archives/TASK-20261007-e9b59b, ledger/evidence/EV-SSI-e454e0.yaml, ledger/decisions/DEC-20261007-43afbd.yaml, ledger/goals/GOAL-SSI-2fa82a/checkpoints/BATCH-65c2dd.yaml |

## Deferred or Blocked

None.

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

- `TASK-20261007-9c36ba` (coordinator, completed):
  - `research/ssi-endring-pke/2026-10-07-candidate-funnel/funnel-flow.svg`
  - `research/ssi-endring-pke/2026-10-07-candidate-funnel/report.md`
  - `research/ssi-endring-pke/2026-10-07-candidate-funnel/report.pdf`
  - remedy: `python3 tools/producer_landing.py <queue> TASK-20261007-9c36ba --push`

Plan SHA-256: `3f0491a984a02ee3da3c82885225659876972b63d8d53deb8d5de3956fdda4ae`
