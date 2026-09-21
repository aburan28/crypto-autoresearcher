# Implementation, version 3a, source repair v4

Status: mathematical specification GO and source repair v4 read-only GO. The
reviewed source is ready for a Git freeze; no canonical certificate or
verification run exists.

The coordinate-only builder emits separately hashed public-model and charged
private-audit sections. The independent verifier reconstructs the curve,
controls, rows, scalar predicates, and index-based model without importing the
builder. A third implementation, `verify_sgcp_scalar_index.py`, independently
reconstructs P2 in scalar-index representation and is an acceptance gate for
candidate universes, conflicts, outcomes, winners, retention, and accounting.

## Repair boundary

- Locked generator and verifier modes use exact stdout JSON, isolated Python,
  no child Git query, no descendants, and predecessor raw-result linkage.
- Runner mode preserves the exact planned `sys.argv[0]` token; the frozen-plan
  fixture rejects a relative-versus-absolute receipt mismatch.
- The verifier binds the external runner manifest/receipt interval, argv,
  launch commits, and raw-result hash. Direct file modes remain development
  tools and are not the proposed canonical execution path.
- Private rows preserve literal target-to-input-pair maps and counts,
  degree-two identity witnesses, per-row operation attribution, and
  self-inclusive fixed-point canonical byte counts.
- Distinct balanced candidates and raw balanced parent pairs have separate
  density ratios.
- Scalar-material checks are explicitly syntactic and bounded. The verifier
  does not claim to exclude general covert encoding.
- Builder wall time and Python-object deep size are self-reported diagnostics;
  locked runner limits and receipts are separate evidence.

## Execution boundary

`specification.json` contains a two-run hash-bound proposal:

1. `RUN-SGCP-EMBED-001`: locked five-bit generator.
2. `RUN-SGCP-EMBED-002`: locked verifier over the committed predecessor
   `raw-result.json`.

The specification remains `review_required` and `approved_by` is null. Merely
having an execution plan does not authorize either run.

Development repair v4 passed the focused suite `22/22`, repository suite
`62/62`, exact frozen-plan no-descendant role composition, schema validation,
and all 16 proposed protocol hashes. Exact commands and hashes are in
`development-test-log-v4.md`.

## Claim boundary

This is a five-bit implementation preflight for one structured-group candidate.
It does not measure relation generation, relation-matrix rank, linear algebra,
individual logarithms, preprocessing crossover, or an exponent below rho.
