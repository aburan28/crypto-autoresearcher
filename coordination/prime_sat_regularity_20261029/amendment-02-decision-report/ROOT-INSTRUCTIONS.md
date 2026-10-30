# Additive scope only

Apply queue-scope-amendment.json to the still-queued TASK-20261029-eb09c9 card: append the five paths to task write_scope/artifact_paths and to handoff write_scope/artifact_paths/deliverables; append constraints/completion gates. Leave the original canonical handoff, source task assignment, record IDs, prior archives and reviewer scopes unchanged. Publish this prospective amendment before claiming the ledger archive task. No new task is needed.

The existing source_task_ids already incorporates comparison review.md and its actual attestation into the archive's expected content union. Do not assign those source-owned files again to the archive task. The five added report/manifest files are owned directly by the archive. The exact expected union is in input-inventory-outline.json.

No canonical DEC, final report, final input manifest or verdict is written by this outline. Finalize only after actual comparison and the native independence check. The final ledger commit message must name TASK-20261029-eb09c9 and DEC-20261029-ce5c57; content_at_commit requires the actual first-parent and committed-content hashes for all eight paths.
