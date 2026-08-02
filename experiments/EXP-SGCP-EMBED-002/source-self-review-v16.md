# EXP-SGCP-EMBED-002 V16 Source Self-Review

## Scope

This review covers the no-run V16 repair of the POSIX-anchor claim, lexical path
control, accepted raw-alias attribution, contract title, current-state records,
and unittest-discover scope. It reviews no new mathematical evidence because
V16 creates no generated curve-family density row or canonical run.

## Routing and version consistency

- Producer and verifier emit only V16; V1-V15 route to rejection before row
  semantics.
- Contract title, specification version, ledger version, producer protocol, and
  verifier protocol all identify version 16.
- Public generated-curve and legacy-row construction remain disabled, and
  public density-row construction admits only the exact frozen p=19, B=4
  control.

## Lexical path policy

- Public writer, receipt-path, and status APIs invoke output admission
  internally.
- Output admission rejects the distinct POSIX `//` anchor and any explicit
  `..` component before absolute normalization.
- Ordinary `.` components and internal repeated separators are normalized
  aliases.
- Three or more leading separators collapse to the ordinary POSIX root anchor
  on the controlled runtime, then undergo normal containment.
- The development root itself and every normalized outside-root destination are
  rejected; an absolute in-root destination follows the same containment rule.
- The descriptor walker independently repeats anchor, parent-traversal, root,
  and containment checks and opens the normalized root-relative parent chain
  with no-follow flags.

## Controls

- One table-driven focused method covers absolute, dot, internal-double,
  three-leading, combined raw-alias, exact leading-double, parent-traversal,
  root, and outside spellings.
- Every admitted spelling maps to one destination and receipt path.
- Publication occurs through the combined raw alias.
- Production and standalone status receive every admitted spelling after
  publication and must attribute the exact winning identifier.
- Public admission, receipt path, production status, standalone status, writer,
  and private descriptor walker all reject the lexical negative cases.
- Existing production controls continue to reject a symlinked parent; the
  standalone parser retains its disclosed non-race boundary.

## Record and test-scope repair

- V15 implementation, all three exact reviews, provenance, and decision are
  present in the required and durable inventories.
- The live handoff and active ledger record V15 as reviewed `REVISE` and V16 as
  the current no-run successor.
- The broad regression evidence is named repository-wide unittest-discover
  scope. It does not claim collection of module-level pytest-style tests.

## Mathematical and budget invariance

- No curve-grid, predicate, representative compiler, ordering, graph, cap,
  objective, gate, or threshold changed.
- The completed operation vector remains `480/112/336/218/4218`.
- No generated V16 curve-family density row, canonical matrix, runner, plan, or
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
- Module-level pytest-style tests are outside the recorded unittest-discover
  result unless separately executed and preserved.

## Self-review result

`OBSERVATION`: source, controls, and governance records now distinguish the
POSIX `//` anchor from admitted normalized aliases without widening execution
authority or the mathematical claim. Fresh exact-commit theory, accounting, and
red-team review remains mandatory before launch-plan design. `maximum_runs=0`.
