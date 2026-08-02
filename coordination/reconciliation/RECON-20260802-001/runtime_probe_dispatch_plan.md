# Dynamic Subagent Dispatch Plan

Snapshot the Coordinator-approved, session-scoped Codex runtime-provenance probe protocol before any implementation begins. This is harness tooling, not ECDLP evidence or an inference amendment.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-966` | executor | queued | 100 | TASK-20260802-965 | orchestration/adapter/codex_runtime.py, orchestration/adapter/cli.py, orchestration/adapter/config.py, tests/test_codex_runtime_probe.py, docs/inference-backends.md, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-966/implementation_report.yaml | orchestration/adapter/codex_runtime.py, orchestration/adapter/cli.py, orchestration/adapter/config.py, tests/test_codex_runtime_probe.py, docs/inference-backends.md, coordination/reconciliation/RECON-20260802-001/tasks/TASK-20260802-966 |

## Deferred or Blocked

- `TASK-20260802-967`: dependency_not_completed:TASK-20260802-966:queued

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

Plan SHA-256: `e72bc46b26d13afd1f337729751f16f6a501545f784e2586e7dc10fc827f9a0f`
