# Dynamic Subagent Dispatch Plan

Snapshot and implement the externally bound, non-authorizing historical-index repair for RECON-20260802-001. No candidate, merge, ECDLP experiment, BATCH-031, or research-state transition is authorized.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260803-003` | executor | queued | 100 | TASK-20260803-002 | tools/author_reconciliation_history.py, tools/check_reconciliation_generated_artifacts.py, tools/research_dispatch.py, tests/test_author_reconciliation_history.py, tests/test_check_reconciliation_generated_artifacts.py, tests/test_research_dispatch.py, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-003/source_occurrence_table.json, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-003/reference_occurrence_table.json, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-003/static_check_report.json, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-003/implementation_report.yaml | tools/author_reconciliation_history.py, tools/check_reconciliation_generated_artifacts.py, tools/research_dispatch.py, tests/test_author_reconciliation_history.py, tests/test_check_reconciliation_generated_artifacts.py, tests/test_research_dispatch.py, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260803-003 |

## Deferred or Blocked

- `TASK-20260803-004`: task_marked_blocked

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

Plan SHA-256: `4de95d1eaa04357d2a5e06706d13d5db84ea10893e58f79d279cb565324f01b6`
