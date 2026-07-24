# Dynamic Subagent Dispatch Plan

Produce the first admissible full-column d_reg datum past the D=5 wall (D6-at-n=12, now valid) plus the gap(n)=d_reg-d_ff ladder n=12,15,18 (>=3 seeds), null-controlled, toward the H-DREG-001 degree-axis decision.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260721-DREG-N12D6-P1` | executor | queued | 90 | - | experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/manifest.yaml, experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/raw-result.json | experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6 |

## Deferred or Blocked

- `TASK-20260721-DREG-N12D6-LEDGER-C2`: dependency_not_completed:TASK-20260721-DREG-N12D6-VAL-R1:queued, dependency_not_completed:TASK-20260721-DREG-N12D6-RT-R1:queued
- `TASK-20260721-DREG-N12D6-RT-R1`: dependency_not_completed:TASK-20260721-DREG-N12D6-P1:queued, dependency_not_completed:TASK-20260721-DREG-N12D6-SNAP-C1:queued
- `TASK-20260721-DREG-N12D6-SNAP-C1`: dependency_not_completed:TASK-20260721-DREG-N12D6-P1:queued
- `TASK-20260721-DREG-N12D6-VAL-R1`: dependency_not_completed:TASK-20260721-DREG-N12D6-P1:queued, dependency_not_completed:TASK-20260721-DREG-N12D6-SNAP-C1:queued

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

Plan SHA-256: `e475a1c5300a2099667aabe68aceafbaa3b3d750820db8bb9b5fde03c7eab3fc`
