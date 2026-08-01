# Dynamic Subagent Dispatch Plan

Carry the independent review and ledger close of RUN-DS-001-ctrl-unplanted, which BATCH-020 cannot carry because its TASK-20260731-045 archive is permanently unbindable (CORR-20260731-010). The run package is already committed and immutable at 61cd52621e0a53669cee8f30af145f8193838362; this batch binds the reviews to that commit rather than to an archive receipt. IT AUTHORIZES NO RUN and re-runs nothing. Its primary target is the producer-authored instrument.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260801-001` | validator | queued | 80 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/reviews/TASK-20260801-001/validation_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/reviews/TASK-20260801-001 |
| `TASK-20260801-002` | red-team | queued | 80 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/reviews/TASK-20260801-002/red_team_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-021/reviews/TASK-20260801-002 |

## Deferred or Blocked

- `TASK-20260801-003`: dependency_not_completed:TASK-20260801-001:queued, dependency_not_completed:TASK-20260801-002:queued

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

Plan SHA-256: `327abd4f39864c3148217ea996f244acb296295d28e01eb60ca3715264e51002`
