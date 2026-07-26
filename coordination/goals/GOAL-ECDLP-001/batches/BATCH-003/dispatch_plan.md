# Dynamic Subagent Dispatch Plan

Design one frozen, review-only toy validation protocol under certificate contract 1.0.0-review that pins a public fixture, a sealed schedule template, an independent verifier artifact hash, and the group-operation type vocabulary; snapshot it, independently review it, and ledger-archive the verdict and goal checkpoint. Authorize no implementation or experiment.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260725-001` | idea-generator | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-003/tasks/TASK-20260725-001/toy_validation_protocol.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-003/tasks/TASK-20260725-001/protocol_design_rationale.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-003/tasks/TASK-20260725-001 |

## Deferred or Blocked

- `TASK-20260725-002`: dependency_not_completed:TASK-20260725-001:queued
- `TASK-20260725-003`: dependency_not_completed:TASK-20260725-001:queued, dependency_not_completed:TASK-20260725-002:queued
- `TASK-20260725-004`: dependency_not_completed:TASK-20260725-003:queued

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

Plan SHA-256: `fbf519fa75b17f6833ecd85e1cfc54f178808ff2666a331b25e0acc4ae2f5b31`
