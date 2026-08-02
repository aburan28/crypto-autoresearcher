# Dynamic Subagent Dispatch Plan

BATCH-027 RUN THE MEASUREMENT. Everything the measurement needs already exists, is frozen, is hash-bound and has been independently reviewed, and NONE OF IT IS REBUILT, RE-FROZEN OR RE-REVIEWED. experiments/EXP-LPF-001/specification.yaml is UNFAULTED at sha256 0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda, frozen at ba1567ee; experiments/EXP-LPF-001/reading_rule_v2.yaml (RR-LPF-2) is the READING RULE OF RECORD at sha256 b633eaf1837ec876ffb7a52bdc6450baba8b1bb4d253dce3d8f3e6e13a7de328, frozen at 9515f6a1, PASSED on substance at TASK-20260801-068; experiments/EXP-LPF-001/reading_rule.yaml (RR-LPF-1) is IMMUTABLE at sha256 8bcb196fa620503c736da307281325d17bb3dc8b0299407b24b584067c979f1d and appears in no write scope; RUN-LPF-001-calib at snapshot 104d32fa is ADMISSIBLE at 68950136 verified factorizations and is REUSED WITHOUT RE-EXECUTION; the RUN-LPF-001-plantz package at snapshot aaf7672c is ADMISSIBLE with its manifest defect superseded by manifest_v2.yaml and registered in tools/run_supersession_registry.yaml; lpf001_driver.py at DRIVER_SHA256 786aeb0550d75fa3d0785aefbe50b121a24cacae584a4cadd79902c464722d65 is UNMODIFIED and binds. THE CHAIN IS SHORT AND DELIBERATELY SO - authorize, REVIEW THE UNREVIEWED TOOL CHANGE THAT REMOVED THE BATCH-026 BLOCKER, record the approval determination, RUN RUN-LPF-001-measure ONCE, snapshot it before anyone reads it, validate and red-team it independently of each other, then file EV-LPF-001 plus the close decision plus the H-LPF-001 status record plus the GOAL checkpoint in one isolated ledger commit. NO NEW EXPERIMENT ID, NO NEW HYPOTHESIS, NO NEW CONTRACT, NO NEW CALIBRATION, NO NEW READING RULE, NO NEW DRIVER AND NO NEW DISCIPLINE. Toy claim ceiling. NO search, NO cost measurement, NO timing decision variable, NO R, NO exponent. Do not edit any file under experiments/EXP-SMTH-001/, experiments/EXP-DS-001/, experiments/EXP-EQD-001/ or experiments/EXP-DEP-001/. Do not alter H-LPF-001 except along the branch RR-LPF-2 assigns at the close, and do not alter H-SMTH-001, H-DS-001, H-EQD-001, H-DEP-001, H-IC-001 or H-STR-002. Leave FAEST and XEDN alone.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260801-079` | executor | queued | 88 | TASK-20260801-078 | experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/manifest.yaml, experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/raw-result.json, experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/command.txt, experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/environment.json, experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/stdout.log, experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/stderr.log, experiments/EXP-LPF-001/runs/RUN-LPF-001-measure/git_status_prerun.txt, experiments/EXP-LPF-001/results/measure/LPF_report.json, experiments/EXP-LPF-001/results/measure/absolute_comparison.json, experiments/EXP-LPF-001/results/measure/relative_band_comparison.json, experiments/EXP-LPF-001/results/measure/deviation_certificate.json, experiments/EXP-LPF-001/results/measure/factorization_verification.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-027/tasks/TASK-20260801-079/execution_report.yaml | experiments/EXP-LPF-001/runs/RUN-LPF-001-measure, experiments/EXP-LPF-001/results/measure, coordination/goals/GOAL-ECDLP-001/batches/BATCH-027/tasks/TASK-20260801-079 |

## Deferred or Blocked

- `TASK-20260801-080`: dependency_not_completed:TASK-20260801-079:queued
- `TASK-20260801-081`: dependency_not_completed:TASK-20260801-080:queued, dependency_not_completed:TASK-20260801-079:queued
- `TASK-20260801-082`: dependency_not_completed:TASK-20260801-080:queued, dependency_not_completed:TASK-20260801-079:queued
- `TASK-20260801-083`: dependency_not_completed:TASK-20260801-080:queued, dependency_not_completed:TASK-20260801-081:queued, dependency_not_completed:TASK-20260801-082:queued

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

Plan SHA-256: `a1cdc219f8f20d50f62a6df8b25f367cf9c69ac925f4ef66100e597c4530dc12`
