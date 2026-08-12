# EXP-SGCP-EMBED-002 V13 Source Self-Review

## Scope

This review covers the no-run V13 changes to verifier-state lifecycle and
verification-output publication. It does not review new mathematical evidence
because V13 creates no generated curve-family density row or canonical run.

## State and routing

- `verify_document` creates one state per public call and restores the exact
  prior ContextVar token in `finally`.
- The state records its owner thread and is marked closed before restoration.
- Semantic helpers reject absent, wrong-permit, closed, and cross-thread state.
- The path worker rejects re-entry, and the large worker body requires the
  current invocation-local token.
- Nested public calls remain valid because each creates a new state and token.
- Same-thread hostile introspection or monkeypatching is not a security
  boundary.

## Publication

- Output parents are walked from the development root through no-follow
  directory descriptors.
- Temporary and final names are created with exclusive flags or no-replace
  publication primitives.
- Temporary names are fixed-length hashes plus random nonces rather than
  destination-name expansions.
- The data file alone is never accepted. A separate receipt binds destination,
  byte count, payload SHA-256, experiment, protocol, and its own digest.
- An interrupted direct data write becomes an unaccepted orphan.
- An interrupted direct receipt write becomes an unaccepted invalid receipt.
- A complete receipt is the logical content commit. Post-commit cleanup,
  fsync, stat, or close failures are returned as warnings and do not raise.
- Receipt validation uses descriptor-relative no-follow regular-file snapshots
  and exact canonical JSON, key, type, size, and digest checks.
- V13 tests force unsupported-publication responses. They do not establish a
  real-filesystem compatibility claim.

## Controls

- Successive, concurrent, and nested public calls reproduce isolated receipts.
- Escaping exceptions close inner state and restore outer context.
- Direct worker re-entry, copied-context cross-thread use, and stale copied
  contexts reject.
- Existing and race-created destinations are never overwritten.
- Data and receipt retries preserve prior bytes.
- Parent symlink traversal is rejected for output.
- Payload tampering invalidates an otherwise valid receipt.
- Forced direct-write interruptions classify data and receipt terminal states
  separately.
- Directory-fsync and hard-link temporary-cleanup failures after content
  publication return accepted results with structured warnings.

## Residual boundaries

- Receipt visibility and content integrity are not proof that every durability
  syscall succeeded.
- A future runner must preserve the publication result and warning vector,
  bind exact executed bytes and environment, enforce hard resource limits, and
  place artifacts in an immutable external store.
- Process kill, hardware failure, hostile same-process Python, and a hostile
  same-user filesystem actor are not solved by this module.
- CPU, wall time, peak RSS, allocator/parser memory, disk, I/O, cache traffic,
  and memory bandwidth remain external role costs.
- The structurally separate complete five-field oracle remains frozen-B4 only.

## Self-review result

No known V13 source defect currently widens execution authority or the
mathematical claim. Fresh exact-commit theory, accounting, and red-team review
is still mandatory before launch-plan design. `maximum_runs=0`.
