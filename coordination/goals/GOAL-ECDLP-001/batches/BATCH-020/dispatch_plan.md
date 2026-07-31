# Dynamic Subagent Dispatch Plan

BATCH-020 CTRL-RT025-UNPLANTED: author PA-DS-001-v2-ctrl-unplanted (single cell bits=20,B=64,m=4,seed=101; unplanted; live /4 plant); one RC-20 review cycle; Executor RUN-DS-001-ctrl-unplanted only if APPROVED; Val+RT; ledger EV-DS-003/DEC-20260731-011. Toy claim ceiling. No full 54-cell matrix. No v1. Do not alter H-IC-001/H-STR-002. Leave FAEST/XEDN alone.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-046` | validator | queued | 70 | TASK-20260731-044, TASK-20260731-045 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/reviews/TASK-20260731-046/validation_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/reviews/TASK-20260731-046 |
| `TASK-20260731-047` | red-team | queued | 70 | TASK-20260731-044, TASK-20260731-045 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/reviews/TASK-20260731-047/red_team_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/reviews/TASK-20260731-047 |

## Deferred or Blocked

- `TASK-20260731-048`: dependency_not_completed:TASK-20260731-046:queued, dependency_not_completed:TASK-20260731-047:queued

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

Plan SHA-256: `0ab8646ad3b46e97bb0823d7fb9f6eac8c4b874ea3f6b68252942abf2c766a6f`
