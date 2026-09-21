# Dynamic Subagent Dispatch Plan

Prepare fixed schemas and source interfaces for the approved symbolic trace-transfer audit; do not perform the audit in this queue.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260907-ec75b0` | executor | queued | 100 | - | experiments/EXP-CRYPTO-6505c6/implementation/symbolic-fixtures.yaml, experiments/EXP-CRYPTO-6505c6/implementation/obligation-matrix.yaml, experiments/EXP-CRYPTO-6505c6/implementation/certificate-schema.json, experiments/EXP-CRYPTO-6505c6/implementation/checker-specification.md, experiments/EXP-CRYPTO-6505c6/implementation/independent-check-plan.md, experiments/EXP-CRYPTO-6505c6/implementation/source-obligations.yaml, experiments/EXP-CRYPTO-6505c6/implementation/audit-interface.md, experiments/EXP-CRYPTO-6505c6/implementation/preparation-manifest.yaml, experiments/EXP-CRYPTO-6505c6/implementation/preparation-report.yaml | experiments/EXP-CRYPTO-6505c6/implementation/symbolic-fixtures.yaml, experiments/EXP-CRYPTO-6505c6/implementation/obligation-matrix.yaml, experiments/EXP-CRYPTO-6505c6/implementation/certificate-schema.json, experiments/EXP-CRYPTO-6505c6/implementation/checker-specification.md, experiments/EXP-CRYPTO-6505c6/implementation/independent-check-plan.md, experiments/EXP-CRYPTO-6505c6/implementation/source-obligations.yaml, experiments/EXP-CRYPTO-6505c6/implementation/audit-interface.md, experiments/EXP-CRYPTO-6505c6/implementation/preparation-manifest.yaml, experiments/EXP-CRYPTO-6505c6/implementation/preparation-report.yaml |

## Deferred or Blocked

- `TASK-20260907-2cb5eb`: dependency_not_completed:TASK-20260907-ec75b0:queued

## Dispatch Gates

- `claimed_tasks_are_not_offered_to_others`: passed
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

Plan SHA-256: `02d1cf6c4248be47a31bc2fe878b8fe76c93645f4cd674cc2f40601401496073`
