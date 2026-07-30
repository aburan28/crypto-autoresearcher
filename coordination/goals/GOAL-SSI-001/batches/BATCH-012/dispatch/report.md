# Dynamic Subagent Dispatch Plan

BATCH-012: pin a concrete Peikert binary c-sieve simulator or reference-implementation control-flow artifact; extract transition kernel plus object-lifetime trace under FC0-R2; derive progress/tail bound; prove or refute finite Q/S/P/C; enumerate W/R/B/M_tail with deterministic concurrency; map failures to F; rerun C2/C3 and error-map audit. Zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-013` | idea-generator | queued | 100 | - | coordination/goals/GOAL-SSI-001/batches/BATCH-012/tasks/TASK-20260730-013/artifact_pin.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-012/tasks/TASK-20260730-013/process_extraction.md, coordination/goals/GOAL-SSI-001/batches/BATCH-012/tasks/TASK-20260730-013/joint_ledger.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-012/tasks/TASK-20260730-013/mutation_audit.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-012/tasks/TASK-20260730-013/classification.yaml | coordination/goals/GOAL-SSI-001/batches/BATCH-012/tasks/TASK-20260730-013 |

## Deferred or Blocked

- `TASK-20260730-014`: dependency_not_completed:TASK-20260730-013:queued
- `TASK-20260730-015`: dependency_not_completed:TASK-20260730-013:queued, dependency_not_completed:TASK-20260730-014:queued
- `TASK-20260730-016`: dependency_not_completed:TASK-20260730-015:queued

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

Plan SHA-256: `6ee0afa50a01120d889be432b564211c62f9e998aab12bd1eb8b9fda83419be5`
