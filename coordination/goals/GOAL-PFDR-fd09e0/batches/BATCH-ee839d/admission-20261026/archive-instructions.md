# Isolated admission archive

Owner: parent Coordinator control plane, TASK-20261026-d85844. This is a
new bootstrap admission archive, separate from completed initial archive50b7bd.
No agent launch or new scientific dependency is introduced.

1. Freeze archive-paths.json. Confirm its exact source files and actual claim
   exist. Create the declared admission-packet-receipt.json using schema
   crypto.autoresearch.archive_receipt.v1, kind snapshot, binding_mode
   content_at_commit, goal/batch/task IDs, actual parent SHA, declared_paths,
   record_ids and SHA256 of every source path except the receipt itself.
   Set commit_sha:null with the established no-self-reference note.
2. Stage only declared_paths. Commit once, naming TASK-20261026-d85844,
   DEC-20261026-610781 and TASK-20261026-589ad5. Never stage initial receipt,
   original handoffs, contract, owner source, private credentials or other work.
3. Verify actual parent, exact changed-path set and every Git blob against
   the receipt. Record commit SHA and receipt's own SHA256 in the separately
   declared admission-publication-verification.json after commit; publish
   that verification subsequently. No receipt may hash itself.
4. Push current branch and update stacked PR2594. Record actual publication
   before native Executor dispatch. Required hosted checks/feature-base merge
   limits remain; publication is not successful merge or scientific evidence.
5. Parent rechecks live goal claim, Conductor lease/epoch/both owner scopes,
   then invokes exact native gpt-6.1-sol/high Executor under original card and
   additive log-scope decision. Zero scientific calls remain binding.
