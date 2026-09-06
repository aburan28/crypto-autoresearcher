# Isolated successor recovery

An expired lease ends scheduling ownership, not necessarily a process. An
unobservable process must not create a permanent veto on an entire research
goal. Recovery preserves both facts: **runtime unknown; isolated successor
permitted only by explicit, bounded Coordinator authority**.

This is a prospective recovery procedure, not a rewrite of any historical
decision, task status, claim, or result. A task-specific decision that forbids
continuation must be explicitly superseded by a new Coordinator decision.

## Method: observe once, authorize, isolate, revalidate, reconcile

1. **Observe once.** Refresh task-relevant refs and perform one read-only
   inspection, capped at 600 seconds. Read the claim/release overlay, queue
   diagnostic, declared output paths and any already available runtime binding.
   A known handle may be inspected; an unknown handle stays unknown. No repeated
   preparation packets or requests for the same unavailable identifier.
2. **Choose a disposition.** Completed attempts go to output/archive
   verification. Live leases retain their owner; this alone is not a verified
   process wait. Expired, noncompleted attempts go to a Coordinator successor
   decision. Missing/malformed ownership needs explicit Coordinator disposition;
   the automated admission gate below does not guess. A queue-schema failure is
   a reason to create a valid successor queue, not to rewrite the predecessor.
3. **Authorize the exact successor.** Allocate/check fresh IDs. Preserve the
   original questions, controls and scientific limits. Record a quantitative
   execution/resource budget, the cost of possible duplicate computation, and
   why the next task ranks ahead of doing nothing. Explicitly supersede any
   decision that made the missing runtime handle mandatory. Bind approval to
   the successor contract, predecessor queue, observed claim epoch/owner,
   successor session and both worktrees. Archive/publish the decision through
   the normal Coordinator lifecycle. An assessment is not approval.
4. **Isolate.** Use a distinct worktree and fresh repository-relative output
   namespace, including archive outputs. Never reuse predecessor output paths,
   release as the predecessor's owner, kill an unidentified process, or mark it
   failed/completed. A lease epoch fences bookkeeping, not arbitrary filesystem
   writes by a native process. Isolation reduces accidental collisions; it is
   not a security boundary against a process that ignores its write scope.
5. **Revalidate immediately before launch.** Render the valid successor queue
   using the dispatcher. It verifies pinned approval/source bytes, disjoint
   paths, budgets/session and the current predecessor claim overlay. A new
   claim, completed release, or late output stops admission for reconciliation.
   Publish the successor's own claim before launch; read back its actual
   runtime binding promptly. Do not reuse an expired successor attempt's
   output paths. A further attempt receives a new successor decision and ID.
6. **Reconcile late returns.** Keep original outputs in their original namespace.
   Late files are neither deleted nor silently substituted into the successor
   archive. Compare independently attributed outputs, archive each actual
   attempt, and let the Coordinator resolve conflicting evidence. No scientific
   status changes follow from expiry, recovery, or a passing admission gate.

The inspection cap is procedural: the read-only assessor does not launch or
terminate inspection processes. The dispatcher is an admission check, not an
execution monitor or a distributed lock. Recheck after publication and before
launch; git ref discovery cannot eliminate races with unfetched remote writers.

## Read-only assessment

```sh
python3 tools/task_recovery.py PATH/dispatch_queue.json TASK-YYYYMMDD-xxxxxx --repo .
```

The JSON output keeps `lease_status`, `runtime_status`, `queue_diagnostic`,
`next_action`, and `dispatch_authorized` separate. It always reports runtime as
unknown because this tool does not query a process. A `runtime_handle_hint` is
only a pointer. It never writes claims, queues or evidence records. Save an
assessment only under an explicitly assigned administrative archive scope.

## Dispatcher contract (opt-in, version 1)

Put a `recovery` object on the successor producer card, not on the predecessor.
Legacy queues without this object retain their previous behavior. All ordinary
dependency, handoff, archive, review and concurrency gates still apply.

```json
{
  "mode": "isolated_successor_v1",
  "predecessor_task_id": "TASK-YYYYMMDD-xxxxxx",
  "predecessor_epoch": 1,
  "predecessor_owner": "original-owner",
  "predecessor_queue": {
    "path": "coordination/old/dispatch_queue.json",
    "commit": "FULL_40_HEX_COMMIT",
    "sha256": "SHA256_OF_EXACT_FILE_BYTES"
  },
  "predecessor_worktree": "/absolute/original/worktree",
  "successor_worktree": "/absolute/isolated/worktree",
  "session": "ACTUAL_SUCCESSOR_SESSION_IDENTIFIER",
  "supersedes_decision_ids": ["DEC-YYYYMMDD-xxxxxx"],
  "decision": {
    "path": "ledger/decisions/DEC-YYYYMMDD-yyyyyy.yaml",
    "commit": "FULL_40_HEX_COMMIT",
    "sha256": "SHA256_OF_EXACT_FILE_BYTES"
  }
}
```

The committed decision is an ordinary `coordinator_decision` with
`decided_by: coordinator`, `decision: approve | revise`, the normal ledger
fields, and a `recovery_authorization` mapping containing:

- `predecessor_task_id`, `successor_task_id`;
- `predecessor_epoch`, `predecessor_owner`;
- `predecessor_queue_sha256`;
- `successor_contract_sha256` from `tools.task_recovery.contract_sha256(task)`;
- `predecessor_worktree`, `successor_worktree`, `session`;
- `allow_unknown_runtime: true`;
- `supersedes_decision_ids`, matching the explicit decision supersessions.

Contract hashing canonicalizes read/write scopes and excludes only `recovery`,
`state`, `lease`, and `receipt`. Budgets, objective, inputs, outputs, dependencies
and review requirements remain bound. The approval must be a regular Git blob
in a reachable commit and match current worktree bytes. This verifies a declared
Coordinator decision, not a cryptographic authentication of a human or model.
Normal authority, archive and publication duties remain mandatory.

For queued or running successors, the dispatcher scans predecessor claims across available
refs even with `--claims off`. It refuses a changed owner/epoch, live/completed
claim, predecessor output in either declared worktree, existing successor
output on a queued successor, overlapping queue/archive scope, missing session, unbounded resource
budget, changed approval, or missing explicit clock in the Python API. The CLI
supplies a clock when none is given. Terminal/blocked cards retain the
fixed approval checks without requiring the predecessor to remain expired.
Running cards may have partial successor outputs; a changed predecessor still
requires reconciliation. A refusal is never an instruction to kill a process.

The gate does not prove that the recorded session is live; launch control must
verify its binding. It does not search arbitrary private logs or every machine
for late outputs. Declared paths and fetched refs define its observable scope.

## Regression boundary

`python3 -m unittest tools.test_task_recovery tools.test_goal_lanes tools.test_research_dispatch`

The tests include the original failure shape: expired claim, null session,
invalid predecessor `read_scope`, no terminal proof. A separately approved,
valid isolated successor can be selected without repairing/releasing the old
task. Negative controls reject live claims, stale approvals, changed epochs,
path overlap/escape, missing binding, late original files and partial successor
outputs. Existing claim/release fencing tests remain unchanged.
