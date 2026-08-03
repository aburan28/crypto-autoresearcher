# Dynamic Subagent Dispatch Plan

BATCH-003 CTRL-B: pin the exact GENUINE (support-independent) degree-6 deficit in [1931, 17947] by exact GF(2) rank of the null Macaulay matrix restricted to sem's 174035-column support at n=12, D=6, seed=2026.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260726-DREG-CTRLB-P1` | executor | queued | 90 | - | experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/manifest.yaml, experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/raw-result.json | experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6 |

## Deferred or Blocked

- `TASK-20260726-DREG-CTRLB-LEDGER`: dependency_not_completed:TASK-20260726-DREG-CTRLB-VAL:queued, dependency_not_completed:TASK-20260726-DREG-CTRLB-RT:queued
- `TASK-20260726-DREG-CTRLB-RT`: dependency_not_completed:TASK-20260726-DREG-CTRLB-P1:queued, dependency_not_completed:TASK-20260726-DREG-CTRLB-SNAP:queued
- `TASK-20260726-DREG-CTRLB-SNAP`: dependency_not_completed:TASK-20260726-DREG-CTRLB-P1:queued
- `TASK-20260726-DREG-CTRLB-VAL`: dependency_not_completed:TASK-20260726-DREG-CTRLB-P1:queued, dependency_not_completed:TASK-20260726-DREG-CTRLB-SNAP:queued

## Dispatch Gates

- `concurrency_cap_respected`: passed
- `all_selected_dependencies_completed`: passed
- `selected_write_scopes_do_not_overlap`: passed
- `archive_tasks_run_in_isolation`: passed
- `all_artifact_paths_are_exact_and_scoped`: passed
- `archive_artifact_coverage_complete`: passed
- `completed_archive_commits_verified`: passed
- `coordinator_only_promotes_research_status`: passed
- `terminal_noncompleted_tasks_do_not_unblock_successors`: passed
- `claim_relevant_tasks_have_independent_review`: passed

Plan SHA-256: `cf724678208f1c97f63e79949cc42d7b50366edc389eeed497a5c048ff757bd6`
