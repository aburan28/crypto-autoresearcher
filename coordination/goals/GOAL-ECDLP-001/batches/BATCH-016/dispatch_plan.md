# Dynamic Subagent Dispatch Plan

BATCH-016 DISPATCHES CTRL-RT034-A ALONE - THE MUTATION TEST OF CTRL-4 - AS A SINGLE EXECUTOR CARD, PLUS THE STANDARD ARCHIVE-AND-REVIEW CHAIN (snapshot archive ALONE, two independent reviews concurrently, ledger archive ALONE), AND NOTHING ELSE. THE CARD RE-RUNS THE CTRL-4 ASSERTION - THE SAME CHECKER CODE, COPIED VERBATIM FROM THE COMMITTED BATCH-015 PROBE DRIVER, NOT A FRESH REIMPLEMENTATION - AGAINST THREE DELIBERATELY BROKEN INPUTS AND REQUIRES IT TO FAIL ON EACH: (1) a zeta3 that is not a cube root of unity; (2) a factor base with one element of one complete block replaced by an unrelated on-curve x; (3) a factor base with two blocks' contents interleaved. CASE (1)'s OUTCOME IS PRE-STATED, IS ALREADY THE FINDING OF THE TASK-20260730-034 RED TEAM, AND IS NOT A PREDICTION TO BE SCORED OR A RESULT TO BE RE-RECORDED. CASES (2) AND (3) MUST FAIL; IF EITHER PASSES, THE CHECKER IS BROKEN AS WELL AS VACUOUS, WHICH IS STRICTLY WORSE AND IS INFORMATION NOBODY CURRENTLY HAS. THIS BATCH MEASURES AN INSTRUMENT, NOT THE OBJECT. NO CLOSURE, NO ALPHA, NO LADDER, NO DRIVER, NO RANK, NO DISPLACEMENT RANK, NO MISALIGNMENT SET AND NO COST QUANTITY OF ANY KIND IS COMPUTED. IT IS NOT AN ATTACK, NOT AN ATTACK IMPROVEMENT, NOT A CRYPTANALYTIC RESULT, NOT A CLOSURE, AND NOT A TEST OF H-STR-002's MECHANISM.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20260730-036` | executor | queued | 100 | - | coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/mutation_driver.py, coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/command.txt, coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/environment.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/stdout.log, coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/stderr.log, coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/mutation_probe.json, coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/mutation_manifest.json | coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation |

## Deferred or Blocked

- `TASK-20260730-037`: dependency_not_completed:TASK-20260730-036:queued
- `TASK-20260730-038`: dependency_not_completed:TASK-20260730-037:queued
- `TASK-20260730-039`: dependency_not_completed:TASK-20260730-037:queued
- `TASK-20260730-040`: dependency_not_completed:TASK-20260730-038:queued, dependency_not_completed:TASK-20260730-039:queued

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

Plan SHA-256: `301efa989770966a94de2dca09ab7075ccfac65ca30ce43114ae41a395bd3a9e`
