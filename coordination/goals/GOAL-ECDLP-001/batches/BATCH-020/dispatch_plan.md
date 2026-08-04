# Dynamic Subagent Dispatch Plan

BATCH-020 CTRL-RT025-UNPLANTED: author PA-DS-001-v2-ctrl-unplanted (single cell bits=20,B=64,m=4,seed=101; unplanted; live /4 plant); one RC-20 review cycle; Executor RUN-DS-001-ctrl-unplanted only if APPROVED; Val+RT; ledger EV-DS-648/DEC-20260731-020. Toy claim ceiling. No full 54-cell matrix. No v1. Do not alter H-IC-001/H-STR-002. Leave FAEST/XEDN alone.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-044` | executor | queued | 80 | TASK-20260731-043 | experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/manifest.json, experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/raw-result.json, experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/stdout.txt, experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/stderr.txt, experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/command.txt, experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/environment.json, experiments/EXP-DS-001/results/ctrl_unplanted/summary.json, experiments/EXP-DS-001/results/ctrl_unplanted/R_cell.json, experiments/EXP-DS-001/results/ctrl_unplanted/null_control_report.json, experiments/EXP-DS-001/results/ctrl_unplanted/live_plant_report.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/tasks/TASK-20260731-044/execution_report.yaml, experiments/EXP-DS-001/implementation/ds001_driver.py | experiments/EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted, experiments/EXP-DS-001/results/ctrl_unplanted, experiments/EXP-DS-001/implementation, coordination/goals/GOAL-ECDLP-001/batches/BATCH-020/tasks/TASK-20260731-044 |

## Deferred or Blocked

- `TASK-20260731-045`: dependency_not_completed:TASK-20260731-044:queued
- `TASK-20260731-046`: dependency_not_completed:TASK-20260731-044:queued, dependency_not_completed:TASK-20260731-045:queued
- `TASK-20260731-047`: dependency_not_completed:TASK-20260731-044:queued, dependency_not_completed:TASK-20260731-045:queued
- `TASK-20260731-048`: dependency_not_completed:TASK-20260731-045:queued, dependency_not_completed:TASK-20260731-046:queued, dependency_not_completed:TASK-20260731-047:queued

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

Plan SHA-256: `b12c6ed414585e8c2ec84fcfad8b2f2fb238054eeb780f61c007116a26506bad`
