# Dynamic Subagent Dispatch Plan

BATCH-026 EXP-LPF-001 REPAIR AND MEASURE. Carry the RTB-054-1 mechanical repair and the RTB-054-2 and RTB-054-6 corrections into a SUPERSEDING reading rule RR-LPF-2, and then FINALLY REACH THE MEASUREMENT ARM against the EXISTING ADMISSIBLE calibration. NO NEW EXPERIMENT ID, NO NEW HYPOTHESIS, NO NEW CONTRACT, NO NEW CALIBRATION AND NO NEW DRIVER. experiments/EXP-LPF-001/specification.yaml is UNFAULTED and UNCHANGED at sha256 0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda; experiments/EXP-LPF-001/reading_rule.yaml carrying RR-LPF-1 is IMMUTABLE and is NOT edited; RUN-LPF-001-calib at snapshot 104d32faff09207740f980be3c7dc8faa3642110 is ADMISSIBLE and is REUSED WITHOUT RE-EXECUTION; lpf001_driver.py at DRIVER_SHA256 786aeb0550d75fa3d0785aefbe50b121a24cacae584a4cadd79902c464722d65 is UNMODIFIED and binds. FIRST regenerate the planted-Z tail arrays that RTB-054-2 showed were missing from the archive, by an AUXILIARY script that IMPORTS the unmodified driver, touching no real object and requiring no factorization, and ARCHIVE THEM AS MACHINE-READABLE ARRAYS; validate that package independently; THEN author RR-LPF-2 under a FOUR-CHANGE CAP - moving_rungs regenerated MECHANICALLY from LPF_movement_beyond_noise_flag, D1 restated as structural for OBJ-PLANT-ROUGH only plus a MEASURED near-disjointness for OBJ-PLANT-SMOOTH, V8 restated to match, and the RTB-054-6 LIMB B headroom declaration ADDED - with EVERYTHING ELSE COPIED; snapshot it; review it independently against FIVE named duties with the attainability and perturbation-movement duties RE-RUN FROM SCRATCH because a regenerated moving_rungs changes what is certified; approval snapshot; RUN-LPF-001-measure only if APPROVED; snapshot; Validator and Red Team; ledger EV-LPF-001 + close decision + H-LPF-001 status + GOAL checkpoint. Toy claim ceiling. NO search, NO cost measurement, NO timing decision variable, NO R, NO exponent. Do not edit any file under experiments/EXP-SMTH-001/, experiments/EXP-DS-001/, experiments/EXP-EQD-001/ or experiments/EXP-DEP-001/. Do not alter H-SMTH-001, H-DS-001, H-EQD-001, H-DEP-001, H-IC-001 or H-STR-002. Leave FAEST and XEDN alone.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260801-068` | reviewer | queued | 82 | TASK-20260801-067 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068/contract_review.yaml, coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068/attainability_check.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068/anti_tuning_check.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068/alternative_class_check.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068/perturbation_movement_check.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068/supersession_diff_check.md | coordination/goals/GOAL-ECDLP-001/batches/BATCH-026/reviews/TASK-20260801-068 |

## Deferred or Blocked

- `TASK-20260801-069`: dependency_not_completed:TASK-20260801-068:queued
- `TASK-20260801-070`: dependency_not_completed:TASK-20260801-069:queued
- `TASK-20260801-071`: dependency_not_completed:TASK-20260801-070:queued
- `TASK-20260801-072`: dependency_not_completed:TASK-20260801-071:queued, dependency_not_completed:TASK-20260801-070:queued
- `TASK-20260801-073`: dependency_not_completed:TASK-20260801-071:queued, dependency_not_completed:TASK-20260801-070:queued
- `TASK-20260801-074`: dependency_not_completed:TASK-20260801-071:queued, dependency_not_completed:TASK-20260801-072:queued, dependency_not_completed:TASK-20260801-073:queued

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

Plan SHA-256: `2629f112987bfdab012a7b0287c73b5afd432d7faceceea2e0e62af4ff38845b`
