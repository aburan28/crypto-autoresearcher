# Dynamic Subagent Dispatch Plan

Snapshot and mechanically validate the narrow generated-artifact prescription that supersedes FIND-952-001. No merge, candidate tree, experiment, or research-state change is authorized.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-993` | executor | queued | 100 | TASK-20260802-992 | tools/check_reconciliation_generated_artifacts.py, tests/test_check_reconciliation_generated_artifacts.py, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-993/static_check_report.json, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-993/implementation_report.yaml | tools/check_reconciliation_generated_artifacts.py, tests/test_check_reconciliation_generated_artifacts.py, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-993 |

## Deferred or Blocked

- `TASK-20260802-994`: dependency_not_completed:TASK-20260802-993:queued

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

Plan SHA-256: `b6dd13b6d6750d20be1e0105ceed97b06b9bef59c899272ddcbca54476497fda`
