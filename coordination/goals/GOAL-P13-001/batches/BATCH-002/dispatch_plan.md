# Dynamic Subagent Dispatch Plan

BATCH-002 DISPATCHES CONTROL NC-2 OF DEC-20260724-016 - THE HIGHEST-PRIORITY NEXT CONTROL OF GOAL-P13-001 - AS A SINGLE EXECUTOR CARD UNDER FROZEN EXPERIMENT CONTRACT EXP-SSI-002, PLUS THE STANDARD CHAIN (snapshot archive ALONE, validator and red team concurrently, ledger archive ALONE). THE CARD MEASURES THE TRUE PER-ENTRY TABLE-CONSTRUCTION COST OF ALGORITHM 1 OF THE FROZEN SOURCE - MODULAR POLYNOMIAL EVALUATION AND ROOT FINDING AND THE NON-BACKTRACKING FILTER AND TABLE INSERTION, ALL CHARGED - ACROSS A SWEEP OF EIGHT WELL-SEPARATED PRIMES p FROM ABOUT 2^20 TO ABOUT 2^40, AND FITS THE OVERHEAD EXPONENT c WITH A CONFIDENCE INTERVAL, RESIDUALS AND A GOODNESS-OF-FIT VERDICT, UNDER THREE SMOOTHNESS BOUNDS B, TWO IMPLEMENTATION VARIANTS, TWO SEEDING STRATEGIES, AND FIVE NAMED CONTROLS INCLUDING A MACHINE-CALIBRATION CONTROL AND A NULL CONTROL. THIS BATCH IS WHY THE CAMPAIGN EXISTS: DEC-20260724-016 RECORDS THAT THE NIST-I CONCRETE MARGIN (2.3 BITS) IS SMALLER THAN THE COST MODEL'S OWN IRREPRODUCIBILITY BAND (3.51 BITS), SO NEITHER `THREATENED` NOR `SAFE` IS AN HONEST OFFICIAL POSITION, AND NC-2 IS THE MEASUREMENT THAT DECIDES BETWEEN THEM. IT IS NOT AN ATTACK, NOT AN ATTACK IMPROVEMENT, NOT A BREAK, NOT A TEST OF HEURISTIC 1, AND NOT A PARAMETER RECOMMENDATION.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260731-001` | executor | queued | 100 | - | experiments/EXP-SSI-002/calibration_probe.py, experiments/EXP-SSI-002/fit_analysis.py, experiments/EXP-SSI-002/runs/RUN-SSI-002/manifest.yaml, experiments/EXP-SSI-002/runs/RUN-SSI-002/raw-timings.json, experiments/EXP-SSI-002/runs/RUN-SSI-002/summary.json, experiments/EXP-SSI-002/runs/RUN-SSI-002/fit_report.json, experiments/EXP-SSI-002/runs/RUN-SSI-002/controls.json, experiments/EXP-SSI-002/runs/RUN-SSI-002/execution_report.yaml, experiments/EXP-SSI-002/runs/RUN-SSI-002/sage_version.txt, experiments/EXP-SSI-002/runs/RUN-SSI-002/command.txt, experiments/EXP-SSI-002/runs/RUN-SSI-002/environment.json, experiments/EXP-SSI-002/runs/RUN-SSI-002/stdout.txt, experiments/EXP-SSI-002/runs/RUN-SSI-002/stderr.txt | experiments/EXP-SSI-002 |

## Deferred or Blocked

- `TASK-20260731-002`: dependency_not_completed:TASK-20260731-001:queued
- `TASK-20260731-003`: dependency_not_completed:TASK-20260731-001:queued, dependency_not_completed:TASK-20260731-002:queued
- `TASK-20260731-004`: dependency_not_completed:TASK-20260731-001:queued, dependency_not_completed:TASK-20260731-002:queued
- `TASK-20260731-005`: dependency_not_completed:TASK-20260731-003:queued, dependency_not_completed:TASK-20260731-004:queued

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

Plan SHA-256: `edb40b37e9dfaca5904b8f47d38b2ae1075ca08c0855d0260008f9378ac5f5be`
