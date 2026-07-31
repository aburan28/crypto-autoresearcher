# Dynamic Subagent Dispatch Plan

BATCH-018: produce stopping-law / joint Q/S/P/C control artifact for QM-STOPPING; keep QM-MEMORY-MAP / QM-ERROR open; retain FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED; do not equate BATCH-014; zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-045` | red-team | queued | 80 | TASK-20260730-043, TASK-20260730-044 | coordination/goals/GOAL-SSI-001/batches/BATCH-018/tasks/TASK-20260730-045/red_team_report.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-018/tasks/TASK-20260730-045/falsification_review.md | coordination/goals/GOAL-SSI-001/batches/BATCH-018/tasks/TASK-20260730-045 |

## Deferred or Blocked

- `TASK-20260730-046`: dependency_not_completed:TASK-20260730-045:queued

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

Plan SHA-256: `298a26b4eda6cb87b17acdaad8524f6ff7a01bdc67e2150109b10f73b17ee4cf`
