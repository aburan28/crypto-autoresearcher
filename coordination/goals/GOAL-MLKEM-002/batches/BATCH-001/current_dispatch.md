# Dynamic Subagent Dispatch Plan

Repair the EXP-MLKEM-003 hardened gate with a baseline-invisible synthetic control and a mechanism-matched second implementation, then decide whether the incomplete ML-KEM re-encryption comparison class is isolated to the audited wolfSSL pre-fix routines or systemic, without key recovery, oracle construction, exploitation, or deployed-system interaction.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-919` | executor | queued | 90 | TASK-20260724-918 | experiments/EXP-MLKEM-004/source-lock.yaml, experiments/EXP-MLKEM-004/implementation.md, experiments/EXP-MLKEM-004/implementation/build_matrix.sh, experiments/EXP-MLKEM-004/implementation/multiclass_generator.py, experiments/EXP-MLKEM-004/implementation/synthetic_control.py, experiments/EXP-MLKEM-004/implementation/conformance_probe.c, experiments/EXP-MLKEM-004/implementation/decap_boundary_probe.c, experiments/EXP-MLKEM-004/implementation/run_experiment.py, experiments/EXP-MLKEM-004/analysis/second_implementation_selection.md, experiments/EXP-MLKEM-004/analysis/class_coverage_report.json, experiments/EXP-MLKEM-004/analysis/malformed_length_table.json, experiments/EXP-MLKEM-004/analysis/synthetic_control_report.json, experiments/EXP-MLKEM-004/vectors/README.md, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/manifest.yaml, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/command.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/environment.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/raw.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/summary.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/stdout.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-013/stderr.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/manifest.yaml, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/command.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/environment.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/raw.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/summary.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/stdout.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-014/stderr.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/manifest.yaml, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/command.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/environment.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/raw.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/summary.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/stdout.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-015/stderr.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/manifest.yaml, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/command.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/environment.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/raw.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/summary.json, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/stdout.txt, experiments/EXP-MLKEM-004/runs/RUN-MLKEM-016/stderr.txt, experiments/EXP-MLKEM-004/execution-report.yaml | experiments/EXP-MLKEM-004 |

## Deferred or Blocked

- `TASK-20260724-920`: dependency_not_completed:TASK-20260724-919:queued
- `TASK-20260724-921`: dependency_not_completed:TASK-20260724-919:queued, dependency_not_completed:TASK-20260724-920:queued
- `TASK-20260724-922`: dependency_not_completed:TASK-20260724-919:queued, dependency_not_completed:TASK-20260724-920:queued
- `TASK-20260724-923`: dependency_not_completed:TASK-20260724-921:queued, dependency_not_completed:TASK-20260724-922:queued

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

Plan SHA-256: `9b0c4974d613c1daef65c971bb9a3505691c5c4fd5ee56a1391b83a4312a6d62`
