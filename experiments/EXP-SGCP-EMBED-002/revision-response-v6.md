# EXP-SGCP-EMBED-002 revision response v6

## Scope

V6 repairs the snapshot-binding, registered-admission, fail-fast semantics,
resource-reservation, phase-receipt, standalone-transcript, and gate-control
findings from independent V5 review. It creates no curve-family row, canonical
matrix, runner, launch plan, or execution authorization.

## Finding closure

| V5 finding | V6 response |
|---|---|
| Parsed bytes and receipted bytes could differ | The verifier opens one no-follow regular file, reads it once into an immutable byte snapshot, computes SHA-256 directly from the final snapshot, and parses those same bytes. A regression changes the path after snapshotting and proves that parsing and the receipt remain bound to the original bytes. |
| Nonregular and changing inputs bypassed file intent | Directories and symlinks fail before JSON parsing. File identity, size, mtime, and ctime are compared before and after the read, and a size mismatch is invalid. |
| Unbounded curve bits reached prime enumeration | Every row is checked against the frozen fixture or the fixed `(bits,seed)` canonical registry before curve provenance work. Registered generated curves are independently derived from source-owned bit sizes and seeds without following an input draw count. |
| B=64 admitted enormous degree-eight expansion | V6 admits only the preregistered `B in {4,6,8}`. Expansion and graph upper bounds are reserved before semantics. |
| Invalid document envelopes still ran every row | Scope, canonical flag, interpretation, parameters, row count, row schemas/types/digests, exact grid, curves, caps, node caps, and resource reservation must all pass before `_verify_density_row_unchecked` is called. Seven- and twelve-row frozen amplification fixtures make zero semantic row calls. |
| Static check lists overclaimed execution | Receipts contain an ordered phase/status ledger. `independent_checks` is generated only from phases with status `passed`. Budget failure claims no parse; parse failure claims no shape; schema failure claims no type; envelope failure claims no row preflight or semantics. |
| Replay followed an input-controlled cap | The source freezes 100000 replay nodes per frozen cap and 2000000 per canonical cap. Direct rows require an explicit registered scope. Every cap must also fit the trusted primary limit. |
| Aggregate verifier work was not bound | Before semantics, V6 reserves separate limits for curve draws, expansion cells, graph cells, replay nodes, primary nodes, both replay caches, both primary caches, retained-model calls, and retained-model cells. An aggregate replay mutation is rejected before row semantics. |
| Duplicate-null fixture could not detect deduplication | The registered control is `[8,8,10,12]`, with multiset median 9 and deduplicated median 10. Hand-derived comparison counts prove multiplicity is retained. |
| Collapse boundaries were incomplete | Exact `1/10` does not collapse; three below-threshold strata do; two collapsing coordinate families do not produce document-level COLLAPSE; all three do. Existing 17/18, 18/24, two/three-strata, and cross-cap controls remain. |
| Standalone oracle followed emitted curve, B, and caps and compared aggregates | The oracle hardcodes only the registered frozen constants, independently derives q and caps, and compares complete factor-base, representative, rejection, conflict, graph, selected-mask, formal-family, constrained-label, edge, source-table, digest, axiom, and cap-winner transcripts. |

## Claim boundary

The mathematical candidate is unchanged. V6 improves the integrity and
resource totality of the finite verifier but adds no evidence that a coordinate
predicate beats a hash-ranked control. The only constructed density row remains
the frozen p=19, B=4 implementation fixture.

The resource receipt is a combinatorial worst-case reservation plus selected
actual counters. It is not a CPU, wall-time, peak-RSS, byte-traffic, or field-
operation authorization. Those resources remain obligations of any future
separately reviewed plan.

Even a future complete PASS would remain `TOY-EVIDENCE`, `MODEL-BOUND`, and
`NOVELTY-UNVERIFIED`. It would not establish relation yield, matrix rank,
target descent, fixed-curve preprocessing advantage, a fitted exponent, a rho
improvement, or an ECDLP break.

## Next action

Freeze exact hashes for V6, validate the records and ledger, commit one exact
snapshot, and request fresh read-only theory, accounting, and red-team review.
Keep `maximum_runs=0`. Do not design a launch plan unless all three reviewers
explicitly authorize that separate design step.
