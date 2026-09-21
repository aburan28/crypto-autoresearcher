# EXP-SGCP-EMBED-002 independent theory review v2

## Handoff: version-2 theory closeout

### Claim or task

Determine whether version 2 is mathematically defined and sufficiently frozen
for canonical execution.

### Status

`HYPOTHESIS`, `TOY-EVIDENCE`, and `MODEL-BOUND`; recommendation `REVISE`.
Canonical execution remains at zero runs.

### Assumptions

- The degree-two representative compiler is part of the tested construction.
- Coordinate-visible private preprocessing is charged audit state, not generic
  group computation or public attack advice.
- No test or curve-family sweep was run during this review.

### Evidence so far

- `R*(C)` is a well-defined finite optimization, and the source implements its
  primary and secondary objective order correctly.
- Conflict-graph independence iff full-union injectivity is a restricted
  theorem for the fixed downward-closed ideals used here. Every collision in a
  union is internal to one ideal or appears between two ideals. This does not
  automatically extend to closure rules that create new multi-maximum objects.
- The retention quantities obey
  `R(S) <= balanced_raw_final_support <= eight_fold_support <= q`, and version 2
  records both denominators.
- The construction is not representative-invariant. It selects the
  lexicographically first degree-two witness for each `2F` output. On the
  abstract group `Z/19Z` with indexed factor base `(2,7,12,17)`, selecting the
  least versus greatest colliding degree-two witness changes the full-cap
  optimum from `R*(19)=9` to `R*(19)=6`. Any result is therefore conditional on
  this representative compiler, not intrinsic to the factor base.
- The four-null statistic, duplicate-control rule, unresolved-cell denominator,
  and half-versus-three-quarter cap selection are not frozen. No family-level
  gate evaluator exists in the V2 source.
- The structured-generic interpretation is a finite coordinate-labelled
  partial-operation witness only. Additive expansion is descriptive; version 2
  proves no theorem connecting expansion or energy to fewer closure conflicts.

### Failure modes

- A measured family effect may be caused by the canonical representative
  compiler.
- Exact-only filtering may bias comparisons if unresolved cells cluster by
  family.
- Curve and Mobius provenance are not independently rederived.
- Exhaustive graph/direct-closure equivalence is tested only on the frozen B=4
  EC fixture and abstract small graphs.
- `source_recovery` does not specify and charge a label-to-source inversion
  interface.
- Nothing in scope establishes relations, rank, descent, a rho improvement, or
  cryptographic scaling.

### Next concrete action

Issue a no-run version-3 amendment freezing the representative compiler,
four-null statistic, unresolved denominator, and structured-generic/source
interface while requiring independent curve and predicate provenance.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/hypothesis.json`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/protocol-amendment-v2.json`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
