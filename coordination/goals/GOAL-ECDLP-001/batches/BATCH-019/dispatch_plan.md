# Dynamic Subagent Dispatch Plan

BATCH-019 SCOPED REPAIR: archive the working-tree EXP-DS-001 relations=200 package (specification.v2.yaml only) under new task IDs; independent Validator + Red Team on the new snapshot only; ledger superseding EV/DEC if warranted. Toy claim ceiling. Do not reuse TASK-022..026. Do not execute v1. Do not alter H-IC-001/H-STR-002. Leave FAEST/XEDN/KN-FIND-010 alone. BATCH-018 remains completed_inconclusive at 33a1f6ae until superseded.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-037` | validator | queued | 85 | TASK-20260731-035, TASK-20260731-036 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-019/reviews/TASK-20260731-037/validation_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-019/reviews/TASK-20260731-037 |
| `TASK-20260731-038` | red-team | queued | 85 | TASK-20260731-035, TASK-20260731-036 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-019/reviews/TASK-20260731-038/red_team_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-019/reviews/TASK-20260731-038 |

## Deferred or Blocked

- `TASK-20260731-039`: dependency_not_completed:TASK-20260731-037:queued, dependency_not_completed:TASK-20260731-038:queued

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

Plan SHA-256: `fae158bef603947ffbf04873c0e46806f4f6a8a00adad69b45dc867e6f43074d`
