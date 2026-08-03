# EXP-SGCP-EMBED-002 V14 Source Self-Review

## Scope

This review covers the no-run V14 publication-attribution, containment,
direct-write, and control-independence changes. It reviews no new mathematical
evidence because V14 creates no generated curve-family density row or canonical
run.

## Routing and containment

- Producer and verifier emit only V14; V1-V13 route to rejection before row
  semantics.
- Public writer, receipt-path, and status APIs invoke the path admission
  function internally.
- Output admission rejects lexical dot components and normalized paths outside
  the development root.
- The descriptor walker independently rejects dot components and opens parent
  directories with no-follow flags.
- Both deterministic final names are checked for absence before data creation;
  no-overwrite syscalls remain authoritative under races.

## Attempt-bound publication

- Each call samples a random 256-bit identifier.
- The receipt binds that identifier, destination basename, root-relative path,
  payload size/hash, protocol, experiment, and canonical self-digest.
- Exact-attempt reconciliation begins only after data publication completed and
  receipt publication was invoked.
- An ordinary synchronous exception returns accepted only if the final pair
  validates against the expected identifier and payload.
- A reconciled result records
  `receipt_publication_exception_reconciled`; it does not invent a primitive
  method that the interrupted helper did not return.
- A stale receipt blocks retry before replacement data is created.
- Simultaneous calls can coexist as one winner and one failure, but the failed
  identifier is not attributed to the winning pair.

## Direct-write behavior

- Full write is followed by file fsync and inode inspection.
- A definite nonregular or wrong-size result raises and remains unaccepted.
- Metadata-access, file-fsync, and close errors can be warnings, but the outer
  writer still requires a fresh exact final-pair validation.
- Interrupted direct data is an orphan; interrupted or short direct receipt is
  invalid and never accepted.

## Controls

- A standalone parser shares no production status or canonicalization helper.
- Stale-receipt retry and two-thread same-destination attribution are checked.
- Lexical outside-root paths are rejected by public and private entry points.
- Rename, actual hard-link, and forced direct receipt commits followed by
  ordinary exceptions reconcile to the exact attempt.
- The actual `os.link` branch executes twice for a complete pair on a test-only
  hard-link-capable root.
- Actual hard-link temporary cleanup failure remains an accepted warning.
- A short direct receipt write is rejected by observed size mismatch and both
  validators.
- A validly re-signed different identifier is accepted by ordinary unkeyed
  status but rejected by exact-attempt reconciliation; wrong relative-path and
  weak-type bindings are rejected by both validators.
- Existing parent-symlink, payload-tamper, interrupted-write, race, no-overwrite,
  directory-fsync, state-lifecycle, accounting, and semantic controls remain.

## Residual boundaries

- Random identifiers give collision resistance, not a formal uniqueness
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

No known V14 source defect widens execution authority or the mathematical
claim. Fresh exact-commit theory, accounting, and red-team review remains
mandatory before launch-plan design. `maximum_runs=0`.
