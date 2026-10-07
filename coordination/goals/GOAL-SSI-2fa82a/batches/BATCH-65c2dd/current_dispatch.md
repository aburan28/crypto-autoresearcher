# Dynamic Subagent Dispatch Plan

Run one zero-experiment alternating EndRing-PKE candidate funnel: two independent candidates, immutable snapshot, joint-owned security evaluation, gap-fed revision, second review, and a scoped final report/ledger decision.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261007-b6c1ec` | red-team | queued | 40 | TASK-20261007-8ab26c, TASK-20261007-8116c4 | coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-b6c1ec/revision-review.yaml, coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-b6c1ec/review-attestation.yaml, coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-b6c1ec/runtime-session-receipt.json | coordination/design/TASK-20261007-9c36ba/reviews/TASK-20261007-b6c1ec |

## Deferred or Blocked

- `TASK-20261007-9c36ba`: dependency_not_completed:TASK-20261007-c47fc6:queued
- `TASK-20261007-c47fc6`: dependency_not_completed:TASK-20261007-b6c1ec:queued
- `TASK-20261007-e9b59b`: dependency_not_completed:TASK-20261007-b6c1ec:queued, dependency_not_completed:TASK-20261007-c47fc6:queued, dependency_not_completed:TASK-20261007-9c36ba:queued

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

Plan SHA-256: `f1c5805008e24c3ed049c9d0c60d1a1974fac65bf4fe80a9779960178b745d29`
