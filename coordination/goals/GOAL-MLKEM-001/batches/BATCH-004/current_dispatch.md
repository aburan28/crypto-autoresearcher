# Dynamic Subagent Dispatch Plan

Execute and independently validate the frozen EXP-MLKEM-001 Thorns exact-FIPS marginal audit without rare-event or n=256 testing.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260724-221` | executor | queued | 90 | TASK-20260724-220 | experiments/EXP-MLKEM-001/source-lock.yaml, experiments/EXP-MLKEM-001/implementation/fips_semantics.py, experiments/EXP-MLKEM-001/implementation/exact_dp.py, experiments/EXP-MLKEM-001/implementation/direct_enumerator.py, experiments/EXP-MLKEM-001/implementation/pinned_estimator_port.py, experiments/EXP-MLKEM-001/implementation/test_controls.py, experiments/EXP-MLKEM-001/analysis/ldp_lower_bound_repair.md, experiments/EXP-MLKEM-001/analysis/fips_output_coordinate_derivation.md, experiments/EXP-MLKEM-001/analysis/term_dependency_graph.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/manifest.yaml, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/command.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/environment.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/raw.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/summary.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/stdout.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-001/stderr.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/manifest.yaml, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/command.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/environment.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/raw.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/summary.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/stdout.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-002/stderr.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/manifest.yaml, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/command.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/environment.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/raw.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/summary.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/stdout.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-003/stderr.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/manifest.yaml, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/command.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/environment.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/raw.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/summary.json, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/stdout.txt, experiments/EXP-MLKEM-001/runs/RUN-MLKEM-004/stderr.txt, experiments/EXP-MLKEM-001/execution-report.yaml | experiments/EXP-MLKEM-001 |

## Deferred or Blocked

- `TASK-20260724-222`: dependency_not_completed:TASK-20260724-221:queued
- `TASK-20260724-223`: dependency_not_completed:TASK-20260724-221:queued, dependency_not_completed:TASK-20260724-222:queued
- `TASK-20260724-224`: dependency_not_completed:TASK-20260724-221:queued, dependency_not_completed:TASK-20260724-222:queued
- `TASK-20260724-225`: dependency_not_completed:TASK-20260724-223:queued, dependency_not_completed:TASK-20260724-224:queued

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

Plan SHA-256: `eea526bb38873c01259d198da3dcffee3e801e07050710744cddd096c785e5ab`
