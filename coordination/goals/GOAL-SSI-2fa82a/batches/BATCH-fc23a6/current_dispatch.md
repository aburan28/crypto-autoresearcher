# Dynamic Subagent Dispatch Plan

Run one zero-run public-binding EndRing interface funnel: propose two distinct candidates, evaluate T1-T5, feed at most one gap to one fresh proposal, re-evaluate, and stop.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| `TASK-20261008-896b35` | idea-generator | queued | 100 | - | coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-896b35/candidate.md, coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-896b35/binding-interface.yaml, coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-896b35/proof-search-map.yaml, coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-896b35/provenance.yaml, ledger/proposals/IDEA-20261008-71a5ca.yaml, ledger/hypotheses/H-SSI-68351d.yaml | coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-896b35, ledger/proposals/IDEA-20261008-71a5ca.yaml, ledger/hypotheses/H-SSI-68351d.yaml |
| `TASK-20261008-ba8247` | idea-generator | queued | 100 | - | coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-ba8247/candidate.md, coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-ba8247/binding-interface.yaml, coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-ba8247/proof-search-map.yaml, coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-ba8247/provenance.yaml, ledger/proposals/IDEA-20261008-305a07.yaml, ledger/hypotheses/H-SSI-0e38a2.yaml | coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-ba8247, ledger/proposals/IDEA-20261008-305a07.yaml, ledger/hypotheses/H-SSI-0e38a2.yaml |

## Deferred or Blocked

- `TASK-20261008-0eba4e`: dependency_not_completed:TASK-20261008-7a3610:queued, dependency_not_completed:TASK-20261008-84054f:queued
- `TASK-20261008-2464ec`: dependency_not_completed:TASK-20261008-0eba4e:queued, dependency_not_completed:TASK-20261008-a6a7bb:queued, dependency_not_completed:TASK-20261008-dd1990:queued
- `TASK-20261008-2b605a`: dependency_not_completed:TASK-20261008-417e47:queued, dependency_not_completed:TASK-20261008-5b590b:queued, dependency_not_completed:TASK-20261008-f0f824:queued
- `TASK-20261008-417e47`: dependency_not_completed:TASK-20261008-ba8247:queued, dependency_not_completed:TASK-20261008-896b35:queued, dependency_not_completed:TASK-20261008-eb1230:queued
- `TASK-20261008-46d7e4`: dependency_not_completed:TASK-20261008-2464ec:queued
- `TASK-20261008-4f85ee`: dependency_not_completed:TASK-20261008-417e47:queued, dependency_not_completed:TASK-20261008-5b590b:queued, dependency_not_completed:TASK-20261008-f0f824:queued, dependency_not_completed:TASK-20261008-2b605a:queued
- `TASK-20261008-5b590b`: dependency_not_completed:TASK-20261008-ba8247:queued, dependency_not_completed:TASK-20261008-896b35:queued, dependency_not_completed:TASK-20261008-eb1230:queued
- `TASK-20261008-7a3610`: dependency_not_completed:TASK-20261008-4f85ee:queued
- `TASK-20261008-84054f`: dependency_not_completed:TASK-20261008-7a3610:queued
- `TASK-20261008-a6a7bb`: dependency_not_completed:TASK-20261008-7a3610:queued, dependency_not_completed:TASK-20261008-84054f:queued
- `TASK-20261008-cdfe7f`: dependency_not_completed:TASK-20261008-46d7e4:queued
- `TASK-20261008-dd1990`: dependency_not_completed:TASK-20261008-7a3610:queued, dependency_not_completed:TASK-20261008-84054f:queued
- `TASK-20261008-eb1230`: dependency_not_completed:TASK-20261008-ba8247:queued, dependency_not_completed:TASK-20261008-896b35:queued
- `TASK-20261008-f0f824`: dependency_not_completed:TASK-20261008-ba8247:queued, dependency_not_completed:TASK-20261008-896b35:queued, dependency_not_completed:TASK-20261008-eb1230:queued
- `TASK-20261008-fc652a`: dependency_not_completed:TASK-20261008-0eba4e:queued, dependency_not_completed:TASK-20261008-a6a7bb:queued, dependency_not_completed:TASK-20261008-dd1990:queued, dependency_not_completed:TASK-20261008-2464ec:queued, dependency_not_completed:TASK-20261008-46d7e4:queued, dependency_not_completed:TASK-20261008-cdfe7f:queued

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

Plan SHA-256: `019fc42c9fc7c0c9c4fe20b56dac45d61c2b930fb197df2e47adab28a3dfc137`
