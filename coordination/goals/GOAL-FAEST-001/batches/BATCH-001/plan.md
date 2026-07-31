# Dynamic Subagent Dispatch Plan

Open GOAL-FAEST-001 BATCH-001: obtain the Round-3 FAEST specification and reference implementation, file them as KN-LIT primary-source entries (the RQ-FAEST-001 constraint that no experiment be designed until the primary sources are filed), then run object-first ideation for RQ-FAEST-001 producing schema-complete IDEA-* proposals with the matched AES baseline cost written down. Proposals only: this batch creates no hypothesis, experiment, or evidence.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-001` | idea-generator | queued | 100 | - | knowledge/literature/KN-LIT-7617.md, knowledge/literature/KN-LIT-7618.md, knowledge/literature/KN-LIT-7619.md, knowledge/literature/KN-LIT-7620.md, coordination/goals/GOAL-FAEST-001/batches/BATCH-001/tasks/TASK-20260731-001/sources_note.md | knowledge/literature, coordination/goals/GOAL-FAEST-001/batches/BATCH-001/tasks/TASK-20260731-001 |

## Deferred or Blocked

- `TASK-20260731-002`: dependency_not_completed:TASK-20260731-001:queued
- `TASK-20260731-003`: dependency_not_completed:TASK-20260731-002:queued
- `TASK-20260731-004`: dependency_not_completed:TASK-20260731-003:queued
- `TASK-20260731-005`: dependency_not_completed:TASK-20260731-001:queued, dependency_not_completed:TASK-20260731-002:queued, dependency_not_completed:TASK-20260731-003:queued, dependency_not_completed:TASK-20260731-004:queued
- `TASK-20260731-006`: dependency_not_completed:TASK-20260731-005:queued

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

Plan SHA-256: `8a3e2360fcbd7264ee3800890aa8648c09f10d26c3fa4aafe44b547c38ac12e8`
