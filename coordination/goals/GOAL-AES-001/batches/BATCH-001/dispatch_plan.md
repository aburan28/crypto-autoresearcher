# Dynamic Subagent Dispatch Plan

Open the reduced-round AES campaign: generate object-first cryptanalytic candidates deduplicated against the known attack families, independently build the FIPS-197-pinned reduced-round-capable AES ground-truth harness that every later cryptanalytic claim must be certified against, and close the batch through independent validation and a verified ledger archive.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-601` | idea-generator | queued | 100 | - | coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-601/baseline_map.md, coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-601/candidate_report.yaml | coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-601 |
| `TASK-20260731-602` | executor | queued | 95 | - | coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/aes_reduced.py, coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/vector_check_receipt.json, coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602/run_record.md | coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602 |

## Deferred or Blocked

- `TASK-20260731-603`: dependency_not_completed:TASK-20260731-601:queued, dependency_not_completed:TASK-20260731-602:queued
- `TASK-20260731-604`: dependency_not_completed:TASK-20260731-601:queued, dependency_not_completed:TASK-20260731-602:queued, dependency_not_completed:TASK-20260731-603:queued
- `TASK-20260731-605`: dependency_not_completed:TASK-20260731-604:queued

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

Plan SHA-256: `a11965bbab876a6cae27b89bcaaaae78151504752c782a36e66950173c71830e`
