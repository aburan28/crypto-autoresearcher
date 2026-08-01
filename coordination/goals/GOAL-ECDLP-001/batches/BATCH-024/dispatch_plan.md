# Dynamic Subagent Dispatch Plan

BATCH-024 EXP-DEP-001 (RT049-CTRL-1): measure the DETECTION POWER of the exact statistic family and the exact archived thresholds of EXP-EQD-001 against deviations that preserve BOTH fibre-invariant marginals BIT-IDENTICALLY and move ONLY the dependence between e_1 and e_2. CALIBRATION FIRST. Author the frozen contract and H-DEP-001; snapshot so ALT-CLASS-DEP-1, THR-DEP-1, DET-DEP-1, CERT-DEP-1, ATS-DEP-1, the three plant families, the three ladders, rho_star, eps_star and the whole branch structure are hash-bound before any datum exists; author the driver COMPLETE including the unexecuted measurement entry point and run RUN-DEP-001-calib on NULL AND PLANT-MACHINERY OBJECTS ONLY; snapshot the driver sha256 and the calibration package; INDEPENDENTLY VALIDATE THAT CALIBRATION PACKAGE, including the mandatory marginal bit-identity check, before anything is frozen against it; freeze reading_rule.yaml and ATTAIN-RR-DEP-1 with measured numbers; snapshot the rule; one independent review whose THREE NAMED DUTIES are the attainability check, the ATS-DEP-1 anti-tuning check and the ALTERNATIVE-CLASS check, each with its own deliverable file; approval snapshot; RUN-DEP-001-measure only if APPROVED; snapshot; Validator and Red Team; ledger EV-DEP-001 + the SUPERSEDING record EV-EQD-002 + close decision + H-DEP-001 status + GOAL checkpoint. Toy claim ceiling. NO smoothness, NO factorization, NO Dickman model, NO search, NO timing decision variable, NO cost identity, NO R. This characterizes an INSTRUMENT; it is not a second measurement of the deterministic factor base, it is NOT a replication of EV-EQD-001 because the curve instances are deliberately the same, and it is NOT a validation or refutation of HEUR-DS-1 in either direction. Do not edit any file under experiments/EXP-EQD-001/, experiments/EXP-DS-001/ or experiments/EXP-SMTH-001/. Do not alter H-EQD-001, H-DS-001, H-SMTH-001, H-IC-001 or H-STR-002. Leave FAEST and XEDN alone.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260801-037` | validator | queued | 92 | TASK-20260801-035, TASK-20260801-036 | coordination/goals/GOAL-ECDLP-001/batches/BATCH-024/reviews/TASK-20260801-037/calibration_validation_report.yaml | coordination/goals/GOAL-ECDLP-001/batches/BATCH-024/reviews/TASK-20260801-037 |

## Deferred or Blocked

- `TASK-20260801-038`: dependency_not_completed:TASK-20260801-037:queued
- `TASK-20260801-039`: dependency_not_completed:TASK-20260801-038:queued
- `TASK-20260801-040`: dependency_not_completed:TASK-20260801-039:queued
- `TASK-20260801-041`: dependency_not_completed:TASK-20260801-040:queued
- `TASK-20260801-042`: dependency_not_completed:TASK-20260801-041:queued
- `TASK-20260801-043`: dependency_not_completed:TASK-20260801-042:queued
- `TASK-20260801-044`: dependency_not_completed:TASK-20260801-042:queued, dependency_not_completed:TASK-20260801-043:queued
- `TASK-20260801-045`: dependency_not_completed:TASK-20260801-042:queued, dependency_not_completed:TASK-20260801-043:queued
- `TASK-20260801-046`: dependency_not_completed:TASK-20260801-037:queued, dependency_not_completed:TASK-20260801-043:queued, dependency_not_completed:TASK-20260801-044:queued, dependency_not_completed:TASK-20260801-045:queued

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

Plan SHA-256: `900314c92845f667bbdc37eb9b1404747d91481684495bac21eae3d090b7f3e2`
