# Dynamic Subagent Dispatch Plan

BATCH-017: implement recovery and object-lifetime tracing gate for QM-MEMORY-MAP / QM-ERROR (component-to-F maps, W/R/B/M_tail lifetime); retain FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED; keep QM-STOPPING open; do not equate BATCH-014; zero curve compute; no numeric security/breakthrough/completion; do not reopen closed IDEA-20260725-001/002/003.

## Ready Tasks

| ID | Role | State | Priority | Dependencies | Artifacts | Write scope |
|---|---|---|---:|---|---|---|
| none | - | - | - | - | - | - |

## Deferred or Blocked

None.

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

Plan SHA-256: `2bac2b76c11cc52bd714c04dab3aa0560748e1805a879b5b700409b4e2d93a3a`
