# Dynamic Subagent Dispatch Plan

Harden the EXP-MLKEM-002 conformance gate against its five surviving red-team objections and apply the hardened gate across wolfSSL pre-fix, wolfSSL post-fix, and at least one additional independent open-source ML-KEM implementation, to decide whether the incomplete re-encryption comparison class is isolated to the audited commits or systemic, without key recovery, oracle construction, exploitation, or deployed-system interaction.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-235` | executor | queued | 90 | TASK-20260724-234 | experiments/EXP-MLKEM-003/source-lock.yaml, experiments/EXP-MLKEM-003/implementation.md, experiments/EXP-MLKEM-003/implementation/build_matrix.sh, experiments/EXP-MLKEM-003/implementation/multiclass_generator.py, experiments/EXP-MLKEM-003/implementation/conformance_probe.c, experiments/EXP-MLKEM-003/implementation/decap_boundary_probe.c, experiments/EXP-MLKEM-003/implementation/run_experiment.py, experiments/EXP-MLKEM-003/analysis/second_implementation_selection.md, experiments/EXP-MLKEM-003/analysis/class_coverage_report.json, experiments/EXP-MLKEM-003/analysis/malformed_length_table.json, experiments/EXP-MLKEM-003/vectors/README.md, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/manifest.yaml, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/command.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/environment.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/raw.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/summary.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/stdout.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-009/stderr.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/manifest.yaml, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/command.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/environment.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/raw.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/summary.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/stdout.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-010/stderr.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/manifest.yaml, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/command.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/environment.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/raw.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/summary.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/stdout.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-011/stderr.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/manifest.yaml, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/command.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/environment.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/raw.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/summary.json, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/stdout.txt, experiments/EXP-MLKEM-003/runs/RUN-MLKEM-012/stderr.txt, experiments/EXP-MLKEM-003/execution-report.yaml | experiments/EXP-MLKEM-003 |

## Deferred or Blocked

- `TASK-20260724-236`: dependency_not_completed:TASK-20260724-235:queued
- `TASK-20260724-237`: dependency_not_completed:TASK-20260724-235:queued, dependency_not_completed:TASK-20260724-236:queued
- `TASK-20260724-238`: dependency_not_completed:TASK-20260724-235:queued, dependency_not_completed:TASK-20260724-236:queued
- `TASK-20260724-239`: dependency_not_completed:TASK-20260724-237:queued, dependency_not_completed:TASK-20260724-238:queued

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

Plan SHA-256: `9fd72642b0793cc5e9df8d9d6b273409d47f60ea71afb40877bef711c637283d`
