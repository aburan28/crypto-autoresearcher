# Dynamic Subagent Dispatch Plan

BATCH-028 MEASURES THE YARDSTICK. It executes RT082-CTRL-1, the instance-variance control, which is the single next_action recorded at the BATCH-027 close (DEC-20260801-014) and is also the frozen disposition of RR-LPF-2 branch L-4 - the replication at a DIFFERENT curve instance per cell. THE OBJECT OF THIS BATCH IS OBJ-RT082-1 AND NOTHING ELSE. OBJ-NULL-UNIF is 130816 iid draws whose 200-replicate sd matches sqrt(p(1-p)/n) to about 8 percent at every powered rung; OBJ-REAL IS NOT A SAMPLE - the frozen specification says so - and its 130816 values are determined by 512 factor-base x-coordinates each appearing in 511 pairs, n = C(512,2) = 130816 exactly. The scale that actually fluctuates, ACROSS CURVE INSTANCES, was never measured because there is one instance per cell. IT CUTS BOTH WAYS AND THAT IS WHY IT IS DECISIVE - if the between-instance sd exceeds the iid sd, the one BATCH-027 reject is noise AND the nine non-rejections are nearly vacuous; if it is below, both are stronger. The published detection-floor table of EV-LPF-001 - u=2 plus or minus 1.7 percent, u=3 plus or minus 4.5, u=4 plus or minus 13, u=5 plus or minus 39 - could be right by a factor of ONE or wrong by a factor of about SIXTEEN, and nothing in the campaign currently distinguishes those. EVERYTHING UPSTREAM IS REVIEWED, HASH-BOUND AND IS NOT REBUILT OR RE-REVIEWED - the specification at sha256 0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda frozen at ba1567ee, RR-LPF-2 at b633eaf1837ec876ffb7a52bdc6450baba8b1bb4d253dce3d8f3e6e13a7de328 frozen at 9515f6a1, RR-LPF-1 at 8bcb196fa620503c736da307281325d17bb3dc8b0299407b24b584067c979f1d, the driver at DRIVER_SHA256 786aeb0550d75fa3d0785aefbe50b121a24cacae584a4cadd79902c464722d65, the calibration ADMISSIBLE at snapshot 104d32fa, the plant-Z package ADMISSIBLE at snapshot aaf7672c. THE CHAIN IS SHORT AND DELIBERATELY SO - author and freeze a control contract and a control reading rule BEFORE ANY DATUM, review it independently, record the approval, run RUN-LPF-001-ivr ONCE at k = 20 fresh curve instances per cell, snapshot it before anyone reads it, validate and red-team it independently of each other, then file EV-IVR-001 plus the close decision plus the GOAL checkpoint in one isolated ledger commit. NO NEW EXPERIMENT ID, NO NEW HYPOTHESIS, NO HYPOTHESIS TRANSITION OF ANY KIND. Toy claim ceiling. Do not edit experiments/EXP-LPF-001/specification.yaml, reading_rule.yaml, reading_rule_v2.yaml, implementation/lpf001_driver.py, any existing run package, any review file or any prior ledger record. Do not alter H-LPF-001 or any other hypothesis. Do not edit any file under experiments/EXP-SMTH-001/, experiments/EXP-DS-001/, experiments/EXP-EQD-001/ or experiments/EXP-DEP-001/. Leave FAEST and XEDN alone.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260802-003` | executor | queued | 92 | TASK-20260802-002 | experiments/EXP-LPF-001/control_ivr/control_specification.yaml, experiments/EXP-LPF-001/control_ivr/reading_rule_ivr.yaml, experiments/EXP-LPF-001/control_ivr/implementation/ivr001_driver.py, experiments/EXP-LPF-001/control_ivr/implementation.md, coordination/goals/GOAL-ECDLP-001/batches/BATCH-028/tasks/TASK-20260802-003/contract_report.yaml | experiments/EXP-LPF-001/control_ivr, coordination/goals/GOAL-ECDLP-001/batches/BATCH-028/tasks/TASK-20260802-003 |

## Deferred or Blocked

- `TASK-20260802-004`: dependency_not_completed:TASK-20260802-003:queued
- `TASK-20260802-005`: dependency_not_completed:TASK-20260802-004:queued
- `TASK-20260802-006`: dependency_not_completed:TASK-20260802-005:queued
- `TASK-20260802-007`: dependency_not_completed:TASK-20260802-006:queued
- `TASK-20260802-008`: dependency_not_completed:TASK-20260802-007:queued
- `TASK-20260802-009`: dependency_not_completed:TASK-20260802-008:queued, dependency_not_completed:TASK-20260802-007:queued
- `TASK-20260802-010`: dependency_not_completed:TASK-20260802-008:queued, dependency_not_completed:TASK-20260802-007:queued
- `TASK-20260802-011`: dependency_not_completed:TASK-20260802-008:queued, dependency_not_completed:TASK-20260802-009:queued, dependency_not_completed:TASK-20260802-010:queued

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

Plan SHA-256: `e011939c783acb70f614f033c2ea69b0cece6d35f2a665180e79e4f384e46f41`
