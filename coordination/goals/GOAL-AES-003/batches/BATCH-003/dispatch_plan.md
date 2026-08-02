# Dynamic Subagent Dispatch Plan

Execute GOAL-AES-003 BATCH-003 in the rank order DEC-20260802-b226fb fixed. RANK 1 IS THE SEGMENT-3 REVIEW: BATCH-002's two four-zero-matrix arms were run AFTER its reviewers were dispatched, so they are measured-but-unreviewed and carry no weight in EV-AES-d8a13e. Until they are independently re-executed, the r=5 half of the round-split scoping rule in CORR-20260802-46b73b rests on reviewed ANALYSIS rather than reviewed MEASUREMENT -- which is exactly why DEC-20260802-b226fb refused to promote that rule to a knowledge entry. RANK 2 is the cross-instrument anchor between BATCH-001's AES-NI engine and BATCH-002's software engine, the one unresolved confound that could invalidate every cross-batch comparison this campaign has made; their conventions were read across BY EYE and never anchored. RANK 4 finishes the hint-corruption coverage at slots t=1 and t=2, which BATCH-002's prefix-only corruption could not reach. A falsification on any of these is a legitimate outcome.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-4500d4` | executor | queued | 100 | - | coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-4500d4/RESULTS.json, coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-4500d4/PREREGISTRATION.md, coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-4500d4/budget_stamps.jsonl | coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-4500d4 |
| `TASK-20260802-447db8` | executor | queued | 95 | - | coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-447db8/RESULTS.json, coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-447db8/PREREGISTRATION.md, coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-447db8/budget_stamps.jsonl | coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-447db8 |

## Deferred or Blocked

- `TASK-20260802-4072e6`: dependency_not_completed:TASK-20260802-5baf79:queued, dependency_not_completed:TASK-20260802-fa1dcc:queued
- `TASK-20260802-5baf79`: dependency_not_completed:TASK-20260802-4500d4:queued, dependency_not_completed:TASK-20260802-447db8:queued, dependency_not_completed:TASK-20260802-d8a5ed:queued
- `TASK-20260802-d8a5ed`: dependency_not_completed:TASK-20260802-4500d4:queued, dependency_not_completed:TASK-20260802-447db8:queued
- `TASK-20260802-fa1dcc`: dependency_not_completed:TASK-20260802-4500d4:queued, dependency_not_completed:TASK-20260802-447db8:queued, dependency_not_completed:TASK-20260802-d8a5ed:queued

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

Plan SHA-256: `b13bd5208c45f4fb460deb72ea5b92c33e94ba84d6db5fd0b96170d021f1aa4e`
