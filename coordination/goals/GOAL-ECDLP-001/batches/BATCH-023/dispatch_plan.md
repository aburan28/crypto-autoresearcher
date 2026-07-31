# Dynamic Subagent Dispatch Plan

BATCH-023 residual plant-contrastive control under SG-ECDLP-001: author PA-DS-001-v2-ctrl-plant-contrast (CTRL-PLANT-CONTRASTIVE-F2) requiring plant-OFF fail ∧ plant-ON pass (RT070-B2/RT047-B3); one RC-23 review cycle; Executor RUN-DS-001-ctrl-plant-contrast only if APPROVED; Val+RT; ledger EV-DS-007/DEC-20260731-019. Deferred: CI-IDENTITY, SPARSE-P-SUCCESS. Toy claim ceiling. No full 54-cell matrix. No v1. Do not edit theater-r2 or rejected BATCH-021 freeze. Do not alter H-IC-001/H-STR-002. Do not reopen STR. No H-DS-001 support. Ignore unauthorized RUN-DS-001-ctrl-theater. Leave FAEST/XEDN alone. No push.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-078` | validator | queued | 70 | TASK-20260731-076, TASK-20260731-077 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/reviews/TASK-20260731-078/validation_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/reviews/TASK-20260731-078 |
| `TASK-20260731-079` | red-team | queued | 70 | TASK-20260731-076, TASK-20260731-077 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/reviews/TASK-20260731-079/red_team_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-023/reviews/TASK-20260731-079 |

## Deferred or Blocked

- `TASK-20260731-080`: dependency_not_completed:TASK-20260731-078:queued, dependency_not_completed:TASK-20260731-079:queued

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

Plan SHA-256: `b57d64d141d35f9aa1e7fb2152172f8aa2c92e646b41203c76457571ad0c605e`
