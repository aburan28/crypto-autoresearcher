# Dynamic Subagent Dispatch Plan

Run one zero-run basis-independent Trap_E interface funnel: propose two distinct candidates, evaluate T1-T5, feed one gap to one fresh proposal, re-evaluate, and stop.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261007-61dd3f` | idea-generator | queued | 100 | - | coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-61dd3f/candidate.md, coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-61dd3f/trap-interface.yaml, coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-61dd3f/proof-search-map.yaml, coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-61dd3f/provenance.yaml, ledger/proposals/IDEA-20261007-7625cc.yaml, ledger/hypotheses/H-SSI-125654.yaml | coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-61dd3f, ledger/proposals/IDEA-20261007-7625cc.yaml, ledger/hypotheses/H-SSI-125654.yaml |
| `TASK-20261007-6f5135` | idea-generator | queued | 100 | - | coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-6f5135/candidate.md, coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-6f5135/trap-interface.yaml, coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-6f5135/proof-search-map.yaml, coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-6f5135/provenance.yaml, ledger/proposals/IDEA-20261007-c5a097.yaml, ledger/hypotheses/H-SSI-c1352c.yaml | coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-6f5135, ledger/proposals/IDEA-20261007-c5a097.yaml, ledger/hypotheses/H-SSI-c1352c.yaml |

## Deferred or Blocked

- `TASK-20261007-06c0cd`: dependency_not_completed:TASK-20261007-ab8d2f:queued, dependency_not_completed:TASK-20261007-df7b77:queued, dependency_not_completed:TASK-20261007-70a40e:queued
- `TASK-20261007-3ba2ff`: dependency_not_completed:TASK-20261007-06c0cd:queued
- `TASK-20261007-4057bd`: dependency_not_completed:TASK-20261007-6f5135:queued, dependency_not_completed:TASK-20261007-61dd3f:queued
- `TASK-20261007-64221a`: dependency_not_completed:TASK-20261007-3ba2ff:queued, dependency_not_completed:TASK-20261007-6cd2cb:queued
- `TASK-20261007-6cd2cb`: dependency_not_completed:TASK-20261007-3ba2ff:queued
- `TASK-20261007-70a40e`: dependency_not_completed:TASK-20261007-6f5135:queued, dependency_not_completed:TASK-20261007-61dd3f:queued, dependency_not_completed:TASK-20261007-4057bd:queued
- `TASK-20261007-80466d`: dependency_not_completed:TASK-20261007-64221a:queued, dependency_not_completed:TASK-20261007-e2c5d4:queued, dependency_not_completed:TASK-20261007-b67a0f:queued
- `TASK-20261007-ab8d2f`: dependency_not_completed:TASK-20261007-6f5135:queued, dependency_not_completed:TASK-20261007-61dd3f:queued, dependency_not_completed:TASK-20261007-4057bd:queued
- `TASK-20261007-b67a0f`: dependency_not_completed:TASK-20261007-3ba2ff:queued, dependency_not_completed:TASK-20261007-6cd2cb:queued
- `TASK-20261007-d54864`: dependency_not_completed:TASK-20261007-80466d:queued
- `TASK-20261007-df7b77`: dependency_not_completed:TASK-20261007-6f5135:queued, dependency_not_completed:TASK-20261007-61dd3f:queued, dependency_not_completed:TASK-20261007-4057bd:queued
- `TASK-20261007-e2c5d4`: dependency_not_completed:TASK-20261007-3ba2ff:queued, dependency_not_completed:TASK-20261007-6cd2cb:queued
- `TASK-20261007-e9bc39`: dependency_not_completed:TASK-20261007-ab8d2f:queued, dependency_not_completed:TASK-20261007-df7b77:queued, dependency_not_completed:TASK-20261007-70a40e:queued, dependency_not_completed:TASK-20261007-06c0cd:queued, dependency_not_completed:TASK-20261007-64221a:queued, dependency_not_completed:TASK-20261007-e2c5d4:queued, dependency_not_completed:TASK-20261007-b67a0f:queued, dependency_not_completed:TASK-20261007-80466d:queued, dependency_not_completed:TASK-20261007-d54864:queued

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

Plan SHA-256: `8fea13885c793d1ade037aab2223be09210e47aa881543ba35b34a6b44a86c40`
