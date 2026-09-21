# Dynamic Subagent Dispatch Plan

Continue cold-start single-target IC against matchedrho under the96-child approvedpublicsyntheticprotocol

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260921-a78926` | coordinator | queued | 50 | TASK-20260921-362caa | research/cold_single_ic_20260921/source_snapshot.tar.gz, research/cold_single_ic_20260921/source_origin.json, research/cold_single_ic_20260921/coordinator_handoff.json, research/cold_single_ic_20260921/id_allocation.json, research/cold_single_ic_20260921/build_preparation/receipt.json, research/cold_single_ic_20260921/build_preparation/progress.json, research/cold_single_ic_20260921/build_preparation/resolve.stdout, research/cold_single_ic_20260921/build_preparation/resolve.stderr, research/cold_single_ic_20260921/build_preparation/build.stdout, research/cold_single_ic_20260921/build_preparation/build.stderr, research/cold_single_ic_20260921/build_preparation/tests.stdout, research/cold_single_ic_20260921/build_preparation/tests.stderr, research/cold_single_ic_20260921/build_preparation/tests_receipt.json, research/cold_single_ic_20260921/source/Cargo.lock, research/cold_single_ic_20260921/snapshot_receipt.json, research/cold_single_ic_20260921/measurement_admission.json, research/cold_single_ic_20260921/implementation_resolutions.json, research/cold_single_ic_20260921/inference_amendment.json, research/cold_single_ic_20260921/task_model_bindings.yaml, research/cold_single_ic_20260921/task_model_policies.yaml, research/cold_single_ic_20260921/inference_resolution.json, research/cold_single_ic_20260921/executor_transition.json, research/cold_single_ic_20260921/premeasurement_cost_accounting.json, research/cold_single_ic_20260921/conformance_attempt3_admission.json, research/cold_single_ic_20260921/hardware_fairness_amendment.json, research/cold_single_ic_20260921/common_arm_port.patch, research/cold_single_ic_20260921/source_arm_origin.json, research/cold_single_ic_20260921/source_arm_snapshot.tar.gz, research/cold_single_ic_20260921/arm_build/progress.json, research/cold_single_ic_20260921/arm_build/receipt.json, research/cold_single_ic_20260921/arm_build/verification.json, research/cold_single_ic_20260921/arm_build/build.stdout, research/cold_single_ic_20260921/arm_build/build.stderr, research/cold_single_ic_20260921/arm_build/tests.stdout, research/cold_single_ic_20260921/arm_build/tests.stderr, research/cold_single_ic_20260921/conformance_path_resolution.json, research/cold_single_ic_20260921/duplicate_parent_launch_event.json | research/cold_single_ic_20260921/source_snapshot.tar.gz, research/cold_single_ic_20260921/source_origin.json, research/cold_single_ic_20260921/coordinator_handoff.json, research/cold_single_ic_20260921/id_allocation.json, research/cold_single_ic_20260921/build_preparation/receipt.json, research/cold_single_ic_20260921/build_preparation/progress.json, research/cold_single_ic_20260921/build_preparation/resolve.stdout, research/cold_single_ic_20260921/build_preparation/resolve.stderr, research/cold_single_ic_20260921/build_preparation/build.stdout, research/cold_single_ic_20260921/build_preparation/build.stderr, research/cold_single_ic_20260921/build_preparation/tests.stdout, research/cold_single_ic_20260921/build_preparation/tests.stderr, research/cold_single_ic_20260921/build_preparation/tests_receipt.json, research/cold_single_ic_20260921/source/Cargo.lock, research/cold_single_ic_20260921/snapshot_receipt.json, research/cold_single_ic_20260921/measurement_admission.json, research/cold_single_ic_20260921/implementation_resolutions.json, research/cold_single_ic_20260921/inference_amendment.json, research/cold_single_ic_20260921/task_model_bindings.yaml, research/cold_single_ic_20260921/task_model_policies.yaml, research/cold_single_ic_20260921/inference_resolution.json, research/cold_single_ic_20260921/executor_transition.json, research/cold_single_ic_20260921/premeasurement_cost_accounting.json, research/cold_single_ic_20260921/conformance_attempt3_admission.json, research/cold_single_ic_20260921/hardware_fairness_amendment.json, research/cold_single_ic_20260921/common_arm_port.patch, research/cold_single_ic_20260921/source_arm_origin.json, research/cold_single_ic_20260921/source_arm_snapshot.tar.gz, research/cold_single_ic_20260921/arm_build/progress.json, research/cold_single_ic_20260921/arm_build/receipt.json, research/cold_single_ic_20260921/arm_build/verification.json, research/cold_single_ic_20260921/arm_build/build.stdout, research/cold_single_ic_20260921/arm_build/build.stderr, research/cold_single_ic_20260921/arm_build/tests.stdout, research/cold_single_ic_20260921/arm_build/tests.stderr, research/cold_single_ic_20260921/conformance_path_resolution.json, research/cold_single_ic_20260921/duplicate_parent_launch_event.json |

## Deferred or Blocked

- `TASK-20260921-6ae79e`: dependency_not_completed:TASK-20260921-a78926:queued
- `TASK-20260921-d86664`: dependency_not_completed:TASK-20260921-6ae79e:queued, dependency_not_completed:TASK-20260921-a78926:queued

## Claims (write-once, tools/goal_lanes.py)

A `live` claim is another session's hold on that task's write_scope:
it is listed under Ready Tasks as `running` so you do not start it.
Start only Ready Tasks whose `claim` is null, and claim them first.

- `TASK-20260921-362caa`: released (owner `cold-single-ic-control-20260921`, epoch 1, expires 2026-09-21T17:50:33Z) -> ignored:queue_state_completed

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

Plan SHA-256: `a6c69c970c71d1115c2954b31936118454891d0ef5191d891691bfc75b94d2f5`
