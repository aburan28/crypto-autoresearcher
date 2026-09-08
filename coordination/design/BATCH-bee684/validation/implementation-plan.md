# Dynamic Subagent Dispatch Plan

Prepare fixed schemas and source interfaces for the approved known-reference recall study; do not perform the audit in this queue.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260907-da9b67` | executor | queued | 100 | - | experiments/EXP-CRYPTO-3759c6/implementation/corpus.py, experiments/EXP-CRYPTO-3759c6/implementation/queries.py, experiments/EXP-CRYPTO-3759c6/implementation/evaluate.py, experiments/EXP-CRYPTO-3759c6/implementation/controls.py, experiments/EXP-CRYPTO-3759c6/implementation/independent_checker.py, experiments/EXP-CRYPTO-3759c6/implementation/schemas.json, experiments/EXP-CRYPTO-3759c6/implementation/admission-template.json, experiments/EXP-CRYPTO-3759c6/implementation/label-rubric.md, experiments/EXP-CRYPTO-3759c6/implementation/implementation-manifest.yaml, experiments/EXP-CRYPTO-3759c6/implementation/preparation-report.yaml | experiments/EXP-CRYPTO-3759c6/implementation/corpus.py, experiments/EXP-CRYPTO-3759c6/implementation/queries.py, experiments/EXP-CRYPTO-3759c6/implementation/evaluate.py, experiments/EXP-CRYPTO-3759c6/implementation/controls.py, experiments/EXP-CRYPTO-3759c6/implementation/independent_checker.py, experiments/EXP-CRYPTO-3759c6/implementation/schemas.json, experiments/EXP-CRYPTO-3759c6/implementation/admission-template.json, experiments/EXP-CRYPTO-3759c6/implementation/label-rubric.md, experiments/EXP-CRYPTO-3759c6/implementation/implementation-manifest.yaml, experiments/EXP-CRYPTO-3759c6/implementation/preparation-report.yaml |

## Deferred or Blocked

- `TASK-20260907-c23402`: dependency_not_completed:TASK-20260907-da9b67:queued

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

Plan SHA-256: `68d8612dadbd190cdd7237d00c8e2d8592bb9b86758dc666894aa7e65e56c267`
