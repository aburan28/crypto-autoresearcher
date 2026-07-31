# Dynamic Subagent Dispatch Plan

BATCH-025 restore executable structure-null-r2 under SG-ECDLP-001 (DEC-20260731-025 supersedes DEC-024 pivot race): PA-DS-001-v2-ctrl-structure-null-r2 / CTRL-NULL-OBJECT-STRUCTURE-DIRECTION-R2 encoding R_null>=0.9 structure credit (RT079-B3/RT070-B3); one RC-25 review cycle; Executor only if APPROVED; Val+RT; ledger EV-DS-008/DEC-20260731-026. Do not edit abandoned BATCH-024 stubs. Do not launder EXP-IT-001/H-IT-001. Deferred CI/SPARSE. Toy ceiling. No STR. No push.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-096` | reviewer | running | 80 | TASK-20260731-095 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-096/contract_review.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-096/derivation_check.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-025/reviews/TASK-20260731-096 |

## Deferred or Blocked

- `TASK-20260731-097`: dependency_not_completed:TASK-20260731-096:running
- `TASK-20260731-098`: dependency_not_completed:TASK-20260731-097:queued
- `TASK-20260731-099`: dependency_not_completed:TASK-20260731-098:queued
- `TASK-20260731-100`: dependency_not_completed:TASK-20260731-098:queued, dependency_not_completed:TASK-20260731-099:queued
- `TASK-20260731-101`: dependency_not_completed:TASK-20260731-098:queued, dependency_not_completed:TASK-20260731-099:queued
- `TASK-20260731-102`: dependency_not_completed:TASK-20260731-099:queued, dependency_not_completed:TASK-20260731-100:queued, dependency_not_completed:TASK-20260731-101:queued

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

Plan SHA-256: `820ba6b813bb6ad574673abbe16b9673b353570de3fa9e04e8ae80f93f1713c4`
