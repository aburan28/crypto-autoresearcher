# Dynamic Subagent Dispatch Plan

BATCH-014 DISPATCHES DEFER-BATCH009-001's EXP-STR-004 REPLICATION AND NOTHING ELSE. It freezes, independently reviews before execution, executes, snapshots, independently reviews twice after execution, and ledger-archives ONE bounded toy-scale CURVE-COMPUTE experiment: the two-arm B-sweep that DEC-20260727-009's next action specifies - arm A-prime (the phi-invariant factor base with the line-303/304 dedup and zero-filter DISABLED) and arm E-prime (a phi-free closure emitting each sigma-orbit once and never suppressing) - measured at fourteen NAMED (curve, B, m) cells so that the independence-of-B content of H-STR-002's claim is tested rather than assumed. THIS IS THE FIRST BATCH IN FOUR THAT TOUCHES THE RESEARCH QUESTION RATHER THAN THE INSTRUMENT, and that is the whole of its ambition: it can discharge a replication obligation and settle or leave unadjudicated an instrument question at toy tier. IT IS NOT AN ATTACK, NOT AN ATTACK IMPROVEMENT AND NOT A TEST OF H-STR-002's MECHANISM.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260729-040` | coordinator | queued | 100 | - | experiments/EXP-STR-004/specification.yaml, experiments/EXP-STR-004/derivation_note.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/tasks/TASK-20260729-040/feasibility_table.md | experiments/EXP-STR-004/specification.yaml, experiments/EXP-STR-004/derivation_note.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-014/tasks/TASK-20260729-040 |

## Deferred or Blocked

- `TASK-20260729-041`: dependency_not_completed:TASK-20260729-040:queued
- `TASK-20260729-042`: dependency_not_completed:TASK-20260729-040:queued, dependency_not_completed:TASK-20260729-041:queued
- `TASK-20260729-043`: dependency_not_completed:TASK-20260729-042:queued
- `TASK-20260729-044`: dependency_not_completed:TASK-20260729-042:queued, dependency_not_completed:TASK-20260729-043:queued
- `TASK-20260729-045`: dependency_not_completed:TASK-20260729-044:queued
- `TASK-20260729-046`: dependency_not_completed:TASK-20260729-045:queued
- `TASK-20260729-047`: dependency_not_completed:TASK-20260729-045:queued
- `TASK-20260729-048`: dependency_not_completed:TASK-20260729-046:queued, dependency_not_completed:TASK-20260729-047:queued

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

Plan SHA-256: `17598f20671f082c76d76b48b82b82f83cd08c1f5c801312cc4d86b3cd7403e4`
