# Dynamic Subagent Dispatch Plan

F1: recompute Approximation 4.9's predicted Pwrong survival curve from the archived Carrier text and compare it against the archived measurement over the band the instrument actually resolved. Zero new sampling, no network dependence, no G6K run, no ML-KEM security claim. AGENTS.md rule 12 remains unmet and unwaived; F1 is chosen because it does not depend on that gate, and no record it governs may be treated as corrected in this batch.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-08f428` | validator | queued | 85 | TASK-20260802-8bae8e, TASK-20260802-7c4aee | coordination/goals/GOAL-MLKEM-003/batches/BATCH-009/tasks/TASK-20260802-08f428/validation_report.yaml, coordination/goals/GOAL-MLKEM-003/batches/BATCH-009/tasks/TASK-20260802-08f428/validation_notes.md | coordination/goals/GOAL-MLKEM-003/batches/BATCH-009/tasks/TASK-20260802-08f428 |

## Deferred or Blocked

- `TASK-20260802-43e5e4`: dependency_not_completed:TASK-20260802-08f428:queued

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

Plan SHA-256: `a023249668a2712d4f610e119345b2ffbc343dfd42ecd97a9b3dabb544505460`
