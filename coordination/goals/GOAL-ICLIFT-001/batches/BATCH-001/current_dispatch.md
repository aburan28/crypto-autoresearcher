# Dynamic Subagent Dispatch Plan

Close the two remaining open measurement routes on the index-calculus and lifting lines by exact counting: the never-executed EXP-FB3-001 factor-base geometry battery (RQ-FB3-001) and the unmeasurable-as-contracted EXP-XEDN-001 phase-2 xedni census, replaced by the frozen EXP-XEDN-002 exact census (RQ-XEDN-001). Every producer is independently validated and red-teamed before any status transition.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-232` | validator | queued | 76 | TASK-20260724-228, TASK-20260724-230 | coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-232/validation_report.yaml, coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-232/validation_notes.md | coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-232 |
| `TASK-20260724-233` | red-team | queued | 75 | TASK-20260724-228, TASK-20260724-230 | coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-233/red_team_report.yaml, coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-233/objections.md | coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-233 |
| `TASK-20260724-234` | validator | queued | 74 | TASK-20260724-229, TASK-20260724-231 | coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-234/validation_report.yaml, coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-234/validation_notes.md | coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-234 |

## Deferred or Blocked

- `TASK-20260724-235`: concurrency_cap
- `TASK-20260724-236`: dependency_not_completed:TASK-20260724-232:queued, dependency_not_completed:TASK-20260724-233:queued, dependency_not_completed:TASK-20260724-234:queued, dependency_not_completed:TASK-20260724-235:queued

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

Plan SHA-256: `495d583421309c179c2cefa44503c02c23d4303d3be76ae150ee4dad37f17ca3`
