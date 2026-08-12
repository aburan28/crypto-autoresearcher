# P1511 Sparse Batch Relation-Incidence Contract

Status: `preregistered_derivation_gate`. Execution and claim promotion remain
evidence-gated.

## Objective

Test whether P1510's source-coded marked-resultant algebra can be extended from
one complete two-step endpoint surface to a source-complete batch extractor for
five-term factor-base relations with total work below the Pollard-rho boundary.

For factor-base size `r` and ordinary prime-order fixtures with
`q = Theta(r^5)`, a passing relation campaign needs `Theta(r)` independent rows
in `O(r^beta polylog r)` work for a proved `beta < 5/2`. P1510 alone does not
meet this requirement: its explicit output has `Theta(r^2)` coefficients per
target, so materializing it for `Theta(r)` targets is already `Theta(r^3)`.

This is a relation-collection derivation gate. It is not blind target descent,
an end-to-end ECDLP algorithm, a Pollard-rho improvement, or a Shoup-bound
break.

## Frozen Inputs

- P1490 exact rational-selector relation and descent control, including its
  independently verified pair/triple baseline;
- P1491 soft-linear supplied-endpoint predicate and independently verified
  candidate-supply floor;
- P1509 local source-coded Hasse section and independent audit;
- P1510 contract, producer, result, note, independent audit, and derivation;
- the P1511-active focus queue, generated plan, and readable report, which
  must be hash-frozen before any execution phase.

Every input hash must be recorded in the producer result. Any changed input
requires a versioned successor contract.

## Exact Relation Object

For each frozen public target

```text
R_t = a_t G + b_t Q,
```

emit complete signed source rows for every accepted identity

```text
R_t = P_i1 + P_i2 + P_i3 + P_i4 + P_i5,
```

where every `P_ij` is a public signed factor-base point. Canonicalization must
retain repeated indices, signs, target coefficients `(a_t,b_t)`, and enough
information to replay the elliptic identity without a discrete-log oracle.

The intended incidence is the intersection of the target-dependent two-step
support `A2(R_t)` and the target-independent three-step support `A3`. P1510's
15 marked components may encode the `A2` side. A passing construction must
also give an exact source section for the `A3` side and for the intersection.

## Phase 0: Sparse Compiler Derivation

Before relation fixtures run, freeze one explicit algorithm that returns only
accepted incidence rows without materializing either of these complete objects:

- all `Theta(r^2)` P1510 endpoint coefficients for every target;
- the `Theta(r^3)` signed or canonical `A3` source table;
- a dense target-by-endpoint incidence matrix;
- one P1491 pointwise query for every explicit `A2` or `A3` candidate.

The derivation must state:

1. the exact summation-polynomial, FFE, resultant, subresultant, multipoint,
   sparse-factor, or module identity used to filter nonincidences before output;
2. an iff proof between nonzero output rows and complete five-term relations;
3. a public source lift for every surviving row, including multiplicities,
   repeated factors, vertical pairs, returns, and exceptional charts;
4. every preprocessing, unsuccessful target, factorization, gcd, sort, lookup,
   rank, and verification cost;
5. peak coefficient and source state;
6. a recurrence proving total exponent `beta < 5/2` for enough rows to reach
   full factor-log-plus-challenge rank.

A call to P1510 once per target is an exact control, not a passing algorithm.
Likewise, fast arithmetic applied to a dense degree-`Theta(r^3)` polynomial
does not change its output floor.

If no concrete sparse identity and source-lift biconditional can be derived,
record `REVISE` or a scoped negative before a scaling campaign. Wall-time fits
cannot replace the recurrence.

## Public Targets And Fixtures

Freeze target coefficients `(a_t,b_t)` by domain-separated hashes before any
source construction. Use:

- all four P1490 ordinary prime-order fixtures and their frozen target panels;
- the L16 and L32 density extensions as diagnostics only;
- at least two held-out generated ordinary prime-order fixtures per new size;
- planted degree-one, degree-two, repeated-source, vertical-pair, return, and
  no-relation controls;
- matched random-list and random-group incidence controls with identical list
  sizes and output counts.

The candidate lane must not use the verifier-held challenge scalar or select
targets after viewing relation sources.

## Relation And Rank Gates

For each fixture record target attempts, accepted and rejected candidates,
deduplicated rows, row rank, factor-column coverage, source replays, and every
operation count. Promotion requires:

- zero false rows and zero missed rows against the exhaustive oracle at every
  size where exhaustive replay is feasible;
- full factor-log-plus-challenge rank on frozen non-planted targets;
- exact challenge recovery only in the verifier lane;
- a proved total exponent below `5/2` in `r`, including the number of attempts
  required for enough independent rows;
- peak state below `r^(5/2)` up to polylogarithmic factors;
- no hidden advice, post-hoc target selection, or verifier source table on the
  candidate path.

Finite-size full rank is correctness evidence only. It cannot promote a lane
whose proved cost is `Theta(r^3)=Theta(q^(3/5))` or worse.

## Charged Controls

- P1490 explicit `A2/A3` pair-triple meet-in-the-middle baseline;
- P1491 supplied-endpoint pointwise predicate;
- P1510 complete 15-component compiler run independently for each target;
- dense product-polynomial and gcd intersection controls;
- explicit endpoint factorization and source opening;
- source-free endpoint hits, which must not enter relation rank;
- planted and matched-random incidence systems;
- Pollard rho at exponent `1/2` in `q` and `5/2` in `r`.

## Budget

Phase 0 is limited to 7,200 wall-clock seconds, 8 aggregate CPU-hours, 8 GiB
peak memory, and 12 runs. A later exact scaling phase requires a reviewed
versioned approval and its own resource ceiling.

## Independent Audit

The audit must not import candidate helpers. It must rebuild public targets and
factor-base points, replay every emitted row, compare complete small-fixture
incidences with the explicit oracle, recompute rank and charged cost, and reject
mutations to a source index, sign, target coefficient, multiplicity, operation
count, trust manifest, and claimed exponent recurrence.

## Decision Rule

Record a scoped positive relation compiler only if Phase 0 supplies an exact
source-complete sparse incidence algorithm and the frozen campaign validates
full rank with proved total exponent `beta < 5/2`. Record a scoped negative if
complete candidate supply or source opening necessarily emits `Omega(r^3)`
state/work on this representation. Record `inconclusive` or `REVISE` for an
implementation failure, incomplete source semantics, finite-size scaling
without a proof, or an uncharged factorization/rank stage.

Even a positive P1511 result would authorize only separately frozen blind
descent and end-to-end accounting. The campaign's generic sub-rho/Shoup claim
remains `not_attempted`.
