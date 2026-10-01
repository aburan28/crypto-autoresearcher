# Dynamic Subagent Dispatch Plan

Continue cold-start single-target IC against matchedrho under the96-child approvedpublicsyntheticprotocol

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260921-362caa` | executor | queued | 50 | TASK-20260921-8efef1 | research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/runner.py, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/analyze.py, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/source_closure.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/candidate.patch, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/candidate_source.tar.gz, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/build_toolchain.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/runner_preflight.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/case_manifest.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/processes.jsonl, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/raw_processes.tar.gz, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/calibration_selection.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/analysis.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/analysis.md, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/environment.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/execution_receipt.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/artifact_manifest.json, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/custody/binaries.tar.gz, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/custody/Cargo.lock, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/custody/dependencies.tar.gz, research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed/raw_processes_manifest.json | research/cold_single_ic_20260921/artifacts/RUN-KIC-e3dbed, research/cold_single_ic_20260921/source_allocation |

## Deferred or Blocked

- `TASK-20260921-6ae79e`: dependency_not_completed:TASK-20260921-362caa:queued, dependency_not_completed:TASK-20260921-a78926:queued
- `TASK-20260921-a78926`: dependency_not_completed:TASK-20260921-362caa:queued
- `TASK-20260921-d86664`: dependency_not_completed:TASK-20260921-6ae79e:queued, dependency_not_completed:TASK-20260921-a78926:queued

## Dispatch Gates

- `claimed_tasks_are_not_offered_to_others`: passed
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

Plan SHA-256: `3187253a9695c4d57b656aeee62b336ccb285a6cbcf1f7a3b1f7096d9255673d`
