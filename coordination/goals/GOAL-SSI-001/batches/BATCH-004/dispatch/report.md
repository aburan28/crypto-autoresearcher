# Dynamic Subagent Dispatch Plan

Revised IDEA-20260725-002 derivation: tightened public-input model (CGL/path-finding + independently published alpha); charged Cl-vectorization vs KN-TECH-050; three-way disposition.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260725-515` | red-team | queued | 80 | TASK-20260725-513, TASK-20260725-514 | coordination/goals/GOAL-SSI-001/batches/BATCH-004/tasks/TASK-20260725-515/red_team_report.yaml, coordination/goals/GOAL-SSI-001/batches/BATCH-004/tasks/TASK-20260725-515/falsification_review.md | coordination/goals/GOAL-SSI-001/batches/BATCH-004/tasks/TASK-20260725-515 |

## Deferred or Blocked

- `TASK-20260725-516`: dependency_not_completed:TASK-20260725-515:queued

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

Plan SHA-256: `490d9bd904cf1877355c876e89fe09d639d383924ce107cdc5bfe69996895000`
