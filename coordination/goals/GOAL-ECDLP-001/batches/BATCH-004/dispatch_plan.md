# Dynamic Subagent Dispatch Plan

Convert IDEA-20260726-001 into a formal hypothesis H-IC-001 and frozen experiment contract EXP-IC-001 measuring T_desc vs sqrt(N) and the multi-target IC amortization crossover K*. Snapshot, independently review, and ledger-archive. Authorize no implementation until the protocol passes review.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260726-001` | coordinator | queued | 100 | - | ledger/hypotheses/H-IC-001.yaml, experiments/EXP-IC-001/specification.yaml | ledger/hypotheses, experiments/EXP-IC-001 |

## Deferred or Blocked

- `TASK-20260726-002`: dependency_not_completed:TASK-20260726-001:queued
- `TASK-20260726-003`: dependency_not_completed:TASK-20260726-001:queued, dependency_not_completed:TASK-20260726-002:queued
- `TASK-20260726-004`: dependency_not_completed:TASK-20260726-003:queued

## Dispatch Gates

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

Plan SHA-256: `2ab8c11c58375adc23695bd11eb69917f6b128348cd5d05f0b848874e99ea77a`
