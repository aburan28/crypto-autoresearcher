# EXP-SGCP-EMBED-002 V18 Source Self-Review

## Scope

This review covers the no-run V18 repair of CLI output ingress, the
`__fspath__` side-effect boundary, historical-evidence qualification,
current-state assertions, and the exact-Git-entry review surface. It reviews no
new mathematical evidence because V18 creates zero generated V18 curve-family
density rows and zero canonical runs.

## Routing and version consistency

- Producer and verifier emit only V18; V1-V17 route to rejection before row
  semantics.
- Contract title, specification version, ledger version, producer protocol,
  and verifier protocol identify version 18.
- Public generated-curve and legacy-row construction remain disabled, and
  public density-row construction admits only the exact frozen p=19, B=4
  control.

## CLI and raw-path boundary

- Verifier and producer parsers retain `--output` as the exact Python-decoded
  string and do not construct `Path` during parsing.
- Verifier `main` preflights output admission before input verification.
- The same admitted decoded string reaches the writer.
- Terminal `/` and terminal `/.` survive parsing and reject before verifier
  work, writer invocation, or parent creation.
- Raw argv bytes, shell decoding, operating-system decoding, and Python's argv
  decoding are outside the claim.
- Exact `str`, `pathlib.Path`, and custom exact-string `os.PathLike` remain
  admitted under normalized development-root containment.
- Bytes, byte-valued path-like objects, string subclasses, unsupported/null
  objects, empty strings, embedded NUL, relative strings, terminal forms,
  explicit `..`, exact leading `//`, root, and outside paths remain rejected.
- Three-or-more leading separators collapse to the ordinary root anchor only
  on the controlled POSIX runtime.

## Callback-effect boundary

- `os.fspath` may execute arbitrary caller `__fspath__` code before its return
  value can be classified.
- A string-valued control creates a caller marker and then admits a separate
  destination without verifier creation.
- A byte-valued control creates its own candidate and then rejects by exact
  return type.
- The verifier-created no-destination statement begins after `os.fspath`
  returns and applies to inert rejected inputs. Caller-created callback effects
  are explicitly outside it.

## Review-surface manifest

- Exact repository paths include the constitution, README, roadmap, build
  metadata, ledgers, all three role contracts, lifecycle/evidence rules,
  shared record definitions, and inherited SGCP controls.
- Exact flat-directory selectors cover one-level schema JSON, harness Python,
  and test Python files.
- The static experiment rule covers `.md`, `.json`, and `.py` files except
  generated directories, sidecars, and five future V18 review/closeout outputs.
- Four exact historical development paths are included despite the general
  development-directory exclusion.
- Selected paths must be ASCII without ASCII controls. Every selected entry
  must be a regular nonexecutable `100644 blob`.
- Sorted records are encoded as `mode NUL type NUL raw-path NUL`. The manifest
  hashes entry metadata only and predicts no commit or tree.
- The exact reviewed Git commit and tree bind all selected blob bytes.

## Historical and current authority

- The four historical files preserve 17 historical V1 development rows and one
  historical development run manifest.
- V18 creates and authorizes zero generated V18 curve-family density rows and
  zero canonical runs.
- `maximum_runs=0`; launch-plan design and execution remain unauthorized.

## Mathematical and accounting invariance

- No curve-grid, predicate, representative compiler, ordering, graph, cap,
  objective, gate, threshold, reservation formula, or operation vector changed.
- The completed operation vector remains `480/112/336/218/4218`.
- No relation-generation, rank, linear-algebra, target-descent,
  preprocessing-crossover, rho, exponent, deployment, or ECDLP claim is added.

## Residual boundaries

- Arbitrary same-process callbacks and monkeypatching are not sandboxed.
- Random identifiers provide collision resistance, not a formal uniqueness
  theorem.
- `BaseException`, process termination, power loss, memory exhaustion, and
  hostile same-process code can prevent a success return after receipt commit.
- The unkeyed receipt does not authenticate against hostile same-user mutation.
- Sequential receipt and payload snapshots are not pair-atomic.
- A complete receipt is not proof that every durability syscall succeeded.
- CPU, wall time, peak RSS, allocator/parser memory, disk, I/O, cache traffic,
  and memory bandwidth remain external role costs.
- The structurally separate complete five-field oracle remains frozen-B4 only.
- Module-level pytest-style tests remain outside unittest-discover unless a
  separate pytest run is recorded.

## Self-review result

`OBSERVATION`: V18 closes the identified CLI-coercion and review-entry
specification gaps without widening the mathematical claim or execution
authority. Fresh exact-commit theory, accounting, and red-team review remains
mandatory before launch-plan design. `maximum_runs=0`.
