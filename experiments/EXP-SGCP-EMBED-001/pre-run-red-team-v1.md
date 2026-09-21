# Pre-run red-team: SGCP-EMBED-001 v1

Date: 2026-07-17

Execution state: no canonical certificate, relation collection, ECDLP run, or
performance run was launched.

## Handoff: v1 specification counterexamples

### Claim or task

Determine whether the v1 formal-multiset construction and five-bit preflight
were sufficiently precise for implementation approval.

### Status

NEGATIVE RESULT

The order-ideal embedding lemma survives, but the v1 P2 search universe,
degree-two policy, optimizer certificate, controls, and final-boundary wording
were not sufficiently specified. This is a specification negative, not a
negative result for structured-label embeddings or ECDLP decomposition.

### Assumptions

- Labels are exactly the `q` EC points, one label per point.
- Formal factors are multisets and may repeat.
- The registered fixture is `p=19`, `a=2`, `b=9`, `q=23`.
- Review was read-only and performed before any canonical experiment run.

### Evidence so far

- If `M` is a finite downward-closed multiset family containing the empty
  multiset and factor-base singletons, and EC evaluation is injective on `M`,
  the union-defined partial operation is a sufficient structured-label
  construction. The theorem still needs the pinned-paper wording checked for
  repeated primes and all identity cases.
- At `B=6`, forcing every canonical degree-two witness is already infeasible:
  `(0,3) + (3,17) = (4,10)`. The degree-two formal product collides with a
  required singleton.
- At `B=8`, empty plus eight singletons plus sixteen canonical degree-two
  products gives 25 formal objects in a group of order 23, so injectivity is
  impossible before any degree-four choice.
- The v1 canonical-only P2 universe is not a maximum over balanced witnesses.
  With
  `F=((0,3),(0,16),(3,2),(3,17),(4,9),(4,10),(5,7),(5,12))`, output `(6,3)`
  has canonical multiset `(0,0,0,4)`, whose closure collides because `(0,4)`
  evaluates to singleton `F[2]=(3,2)`. Alternate witness `(1,6,6,6)` has the
  same output and an injective full closure.
- Relative final-support retention can conceal low absolute group coverage.
  At 12 bits with `B=4`, at most 35 degree-four multisets yield at most 630
  unordered pair sums against `q=2129`.

### Failure modes

- `D2` was ambiguous between all canonical degree-two nodes, forced
  submultisets, and separately selected nodes.
- "Max retention" over one canonical witness per output discarded feasible
  alternates.
- Retained output count and retained source-witness count were redundant in
  the canonical universe.
- The optimizer record did not bind the complete candidate universe or prove
  exact optimality independently.
- No direct `A4 x A4` star edge is testable, but absence of equivalent advice
  was overclaimed while audit metrics themselves materialized final sums.
- Negative controls could fail several predicates at once, so a first-error
  result did not isolate the intended gate.
- Random-control repetitions in the full contract conflicted with the
  one-instance implementation preflight.

### Next concrete action

Revise the contract to v2 before any canonical run: define `D2` as only the
submultisets forced by selected degree-four maxima, optimize over every distinct
balanced degree-four formal multiset, report absolute and relative final
support separately, separate public-model and private-audit artifacts, and add
fixed isolated regressions for the counterexamples above.

### Artifact paths

- `notes/sgcp_embed_001_contract_20260717.md`
- `experiments/EXP-SGCP-EMBED-001/contract.md`
- `experiments/EXP-SGCP-EMBED-001/specification.json`
- `experiments/EXP-SGCP-EMBED-001/pre-run-red-team-v1.md`
