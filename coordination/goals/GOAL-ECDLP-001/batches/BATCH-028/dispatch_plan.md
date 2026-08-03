# Dynamic Subagent Dispatch Plan

BATCH-028 bounded toy Executor for EXP-IT-001 v3 under SG-ECDLP-002 / IDEA-20260731-008 after DEC-034 APPROVED. IDEA-011 null + planted-path + matched rho/BSGS + HEUR-ISO-1. Snapshot then Val+RT then ledger EV-IT-001/DEC-036. BATCH-026 CI TASK-115 left alone (disjoint). Toy. No STR. No v1/v2. No push.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-127` | executor | running | 80 | TASK-20260731-126 | experiments/EXP-IT-001/runs/RUN-IT-001-bounded-toy/manifest.json, experiments/EXP-IT-001/runs/RUN-IT-001-bounded-toy/raw-result.json, experiments/EXP-IT-001/results/summary.json, experiments/EXP-IT-001/results/HEUR_ISO_1_report.json, experiments/EXP-IT-001/results/transfer_gate_report.json, experiments/EXP-IT-001/results/concrete_cost_table.json, experiments/EXP-IT-001/results/null_it_isogeny_transfer_report.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-028/tasks/TASK-20260731-127/execution_report.yaml | experiments/EXP-IT-001/implementation, experiments/EXP-IT-001/runs, experiments/EXP-IT-001/results, coordination/goals/GOAL-ECDLP-001/batches/BATCH-028/tasks/TASK-20260731-127 |

## Deferred or Blocked

- `TASK-20260731-128`: dependency_not_completed:TASK-20260731-127:running
- `TASK-20260731-129`: dependency_not_completed:TASK-20260731-127:running, dependency_not_completed:TASK-20260731-128:queued
- `TASK-20260731-130`: dependency_not_completed:TASK-20260731-127:running, dependency_not_completed:TASK-20260731-128:queued
- `TASK-20260731-131`: dependency_not_completed:TASK-20260731-128:queued, dependency_not_completed:TASK-20260731-129:queued, dependency_not_completed:TASK-20260731-130:queued

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

Plan SHA-256: `d4103db6554439f7e13de531018ea5080a4b6135327be6008790e54676a47797`
