# Dynamic Subagent Dispatch Plan

BATCH-018 EXECUTES APPROVED EXP-DS-001 v2 only (snapshot 65f3c82b; DEC-20260731-003; run_authorized true): implement+run bounded matrix with IDEA-20260731-011 null control, matched CTRL-RHO/CTRL-BSGS, HEUR-DS-1 sampling; snapshot-archive; independent Validator + Red Team; ledger EV-DS-001 + DEC-20260731-004 + GOAL checkpoint. Apply R-1 (F2 over S1 when any R<0.5 cell has R_null<0.9). TOY TIER. Do NOT execute v1. Do NOT alter H-IC-001/H-STR-002. No second amendment cycle.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-022` | executor | queued | 90 | - | experiments/EXP-DS-001/implementation/implementation.md, experiments/EXP-DS-001/implementation/ds001_driver.py, experiments/EXP-DS-001/implementation/verify_certificates.py, experiments/EXP-DS-001/runs/RUN-DS-001-impl/manifest.json, experiments/EXP-DS-001/runs/RUN-DS-001-impl/raw-result.json, experiments/EXP-DS-001/runs/RUN-DS-001-impl/stdout.txt, experiments/EXP-DS-001/runs/RUN-DS-001-impl/stderr.txt, experiments/EXP-DS-001/runs/RUN-DS-001-impl/command.txt, experiments/EXP-DS-001/runs/RUN-DS-001-impl/environment.json, experiments/EXP-DS-001/runs/RUN-DS-001-measure/manifest.json, experiments/EXP-DS-001/runs/RUN-DS-001-measure/raw-result.json, experiments/EXP-DS-001/runs/RUN-DS-001-measure/stdout.txt, experiments/EXP-DS-001/runs/RUN-DS-001-measure/stderr.txt, experiments/EXP-DS-001/runs/RUN-DS-001-measure/command.txt, experiments/EXP-DS-001/runs/RUN-DS-001-measure/environment.json, experiments/EXP-DS-001/runs/RUN-DS-001-heur/manifest.json, experiments/EXP-DS-001/runs/RUN-DS-001-heur/raw-result.json, experiments/EXP-DS-001/runs/RUN-DS-001-heur/stdout.txt, experiments/EXP-DS-001/runs/RUN-DS-001-heur/stderr.txt, experiments/EXP-DS-001/runs/RUN-DS-001-heur/command.txt, experiments/EXP-DS-001/runs/RUN-DS-001-heur/environment.json, experiments/EXP-DS-001/results/summary.json, experiments/EXP-DS-001/results/R_table.json, experiments/EXP-DS-001/results/HEUR_DS_1_report.json, experiments/EXP-DS-001/results/null_control_report.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-018/tasks/TASK-20260731-022/execution_report.yaml | experiments/EXP-DS-001/implementation, experiments/EXP-DS-001/runs, experiments/EXP-DS-001/results, coordination/goals/GOAL-ECDLP-001/batches/BATCH-018/tasks/TASK-20260731-022 |

## Deferred or Blocked

- `TASK-20260731-023`: dependency_not_completed:TASK-20260731-022:queued
- `TASK-20260731-024`: dependency_not_completed:TASK-20260731-022:queued, dependency_not_completed:TASK-20260731-023:queued
- `TASK-20260731-025`: dependency_not_completed:TASK-20260731-022:queued, dependency_not_completed:TASK-20260731-023:queued
- `TASK-20260731-026`: dependency_not_completed:TASK-20260731-024:queued, dependency_not_completed:TASK-20260731-025:queued

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

Plan SHA-256: `3afdc62542bbc3063283db403f1c4d966a561c0a2767c20a425c109fffda0d50`
