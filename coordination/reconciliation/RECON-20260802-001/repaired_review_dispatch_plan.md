# Dynamic Subagent Dispatch Plan

Snapshot, execute, and archive separate exact-session Validator and Red Team reviews of the repaired 15-path reconciliation prescription. No merge, candidate materialization, experiment, or state change is authorized.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-995` | validator | queued | 100 | TASK-20260802-915 | coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-995/validation_report.yaml | coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-995 |
| `TASK-20260802-997` | red-team | queued | 100 | TASK-20260802-915 | coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-997/red_team_report.yaml | coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-997 |

## Deferred or Blocked

- `TASK-20260802-996`: dependency_not_completed:TASK-20260802-995:queued
- `TASK-20260802-998`: dependency_not_completed:TASK-20260802-997:queued

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

Plan SHA-256: `ae5d879f7dfad5cb0f028d971b1e06f07066559e699e2291617580d253ef82e6`
