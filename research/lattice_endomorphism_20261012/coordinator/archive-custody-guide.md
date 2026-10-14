# Binding the four design snapshots to real published commits

The final `records.json` gives each lane's canonical paths, actual Generator artifact paths, source closure and IDs. Its `canonical_contract_archive_task_id` is the original bootstrap handoff's `snapshot_task_id`, preserving declared custody. The other input-archive ID remains an unused reservation. Generator task completion is based on the real Idea Generator report and checked artifact hashes; no independent review is recorded.

Copy the new RQ, H, approved specification, trial plan, Executor handoff and approval decision from the lane's Coordinator folder to their mapped canonical paths. Copy the Generator YAML unchanged to `ledger/proposals/<IDEA-ID>.yaml`; retain its original research proposal and exploration file as the Producer's declared artifacts. Copy the queue to the mapped package path. All driver, shared helper and test bytes must match the final source hashes. Create empty `amendments/` and `runs/` directories when materializing an experiment, without creating its allocated run directory before actual admission.

The initial archive uses `content_at_commit`: it verifies the declared bytes in its real published commit, whose parent and commit message are checked. For each lane, the exact archive set is the union of the archive task's `artifact_paths` and the Generator task's `artifact_paths`. These include the proposed source files and the canonical contract copies, driver/helper/test, handoff, approval decision and `input-archive-receipt.json`. The commit message must contain the initial archive task ID and every `archive.record_ids` entry.

Write the receipt before the API archive commit. It may contain `task_id`, `kind: snapshot`, `source_task_ids`, exact `artifact_paths`, `record_ids`, `binding_mode: content_at_commit`, the payload hashes and an explicit note that real commit and parent identity will be bound afterward in the queue. It must not embed its own future commit SHA or claim a fabricated commit. Calculate the receipt's own hash only after its bytes are finished; that hash belongs in the queue's `archive.path_sha256`, along with every other exact archive/source path.

After the API supplies the real archive commit C and first parent P, fill the queue archive task as follows:

```json
{
  "state": "completed",
  "archive": {
    "kind": "snapshot",
    "binding_mode": "content_at_commit",
    "source_task_ids": ["the actual Generator TASK ID"],
    "commit_sha": "actual full C",
    "parent_sha": "actual full P",
    "path_sha256": {"every archive/source path": "its SHA256 in C"},
    "record_ids": ["the existing exact IDs from the queue"]
  }
}
```

Preserve all existing scientific bindings and task IDs. Commit the completed queue binding after C: this is a separate custody update and does not require changing the trial plan, whose bytes bind the specification/source and task execution interface. The approval decision's `queue_sha256_at_readiness` intentionally records the inspected queue state; lifecycle completion is recorded by a later committed queue, rather than rewriting history.

Fetch/materialize the real branch so C resolves locally and is an ancestor of the branch HEAD. Run `research_dispatch.validate_queue(queue, repository_verifier=GitRepositoryVerifier(branch_checkout))`, or the existing `research_dispatch.py --ready-only --repo-root <branch_checkout>` against that queue. Its verifier checks C, P, commit message IDs and every archived byte. A Git object that is missing locally, a wrong branch HEAD, a missing receipt or a mismatched path hash is an infrastructure/custody failure; do not mark the snapshot complete or bypass it.

A ready Executor still needs the existing claim/owner/epoch and committed spec, plan, queue and source checks before the public run skill's canonical supervisor can launch. This Coordinator launched no scientific trial. The run snapshot and independent Reviewer/ledger tasks remain queued until actual outputs and review receipts exist. No future review decision was fabricated.
