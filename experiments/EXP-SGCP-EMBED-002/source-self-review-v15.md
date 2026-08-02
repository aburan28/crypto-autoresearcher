# EXP-SGCP-EMBED-002 V15 Source Self-Review

## Scope

This review covers the no-run V15 repair of output-path claim precision,
normalized-alias control coverage, current-state wording, and durable-artifact
inventory. It reviews no new mathematical evidence because V15 creates no
generated curve-family density row or canonical run.

## Routing and path policy

- Producer and verifier emit only V15; V1-V14 route to rejection before row
  semantics.
- Public writer, receipt-path, and status APIs invoke the path admission
  function internally.
- Output admission rejects an explicit `..` component before normalization.
- In-root `.` components and repeated separators are normalized aliases of one
  destination; raw spelling preservation or rejection is not claimed.
- The development root itself and every normalized outside-root destination are
  rejected; an absolute in-root destination follows the same containment rule.
- The descriptor walker repeats explicit parent-traversal rejection and opens
  the normalized root-relative parent chain with no-follow flags.
- Both deterministic final names are checked for absence before data creation;
  no-overwrite syscalls remain authoritative under races.

## Normalized-alias control

- One existing publication test now supplies a raw in-root path containing
  `./` and repeated separators.
- `output_path`, `publication_receipt_path`, and `publication_status` agree on
  the normalized destination.
- Publication through the raw alias succeeds, and the receipt binds the
  normalized development-root-relative path.
- Production and standalone validators attribute the same publication
  identifier to the normalized destination.
- A separate explicit `..` path is rejected by the writer, status function, and
  private descriptor walker, with no outside-root artifact.

## Retained publication behavior

- Each call samples a random 256-bit identifier.
- The receipt binds that identifier, destination basename, root-relative path,
  payload size and hash, protocol, experiment, and canonical self-digest.
- Exact-attempt reconciliation begins only after data publication completes and
  receipt publication is invoked.
- An ordinary synchronous exception returns accepted only if the final pair
  validates against the expected identifier and payload.
- A stale receipt blocks retry before replacement data is created.
- Simultaneous calls yield one no-overwrite winner, and the failed identifier is
  not attributed to the winning pair.
- A definite nonregular or wrong-size direct-write inode remains a hard failure.
- The standalone parser still shares no production status or canonicalization
  helper.

## Record repair

- The primary handoff and active ledger row identify the committed V14 review
  outcome and V15 implementation state.
- The durable inventory includes all four committed V7 implementation records.
- The specification preserves the complete V14 implementation, three exact
  reviews, provenance, and decision before listing V15 records.
- Historical review and decision files remain immutable.

## Mathematical and budget invariance

- No curve-grid, predicate, representative compiler, ordering, graph, cap,
  objective, gate, or threshold changed.
- The completed operation vector remains `480/112/336/218/4218`.
- No generated V15 curve-family density row, canonical matrix, runner, plan, or
  run is created or authorized.
- `maximum_runs=0` remains unchanged.

## Residual boundaries

- Random identifiers provide collision resistance, not a formal uniqueness
  theorem.
- `BaseException`, process termination, power loss, memory exhaustion, and
  hostile same-process code can prevent a success return after receipt commit.
- The unkeyed receipt does not authenticate against hostile same-user mutation.
- Sequential receipt and payload snapshots are not pair-atomic.
- A complete receipt is not proof that every durability syscall succeeded.
- The hard-link control does not establish support on the mounted development
  filesystem.
- CPU, wall time, peak RSS, allocator/parser memory, disk, I/O, cache traffic,
  and memory bandwidth remain external role costs.
- The structurally separate complete five-field oracle remains frozen-B4 only.

## Self-review result

`OBSERVATION`: source, test, contract, and inventory changes align the V15
record with the demonstrated path behavior without widening execution authority
or the mathematical claim. Fresh exact-commit theory, accounting, and red-team
review remains mandatory before launch-plan design. `maximum_runs=0`.
