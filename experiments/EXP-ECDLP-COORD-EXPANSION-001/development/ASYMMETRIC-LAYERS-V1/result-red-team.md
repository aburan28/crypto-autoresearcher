# Independent Red-Team Review: Asymmetric Layers V1

## Handoff: `2A+3R` adversarial interpretation

### Claim or task

Determine whether the scalar cyclic support result supports a credible
coordinate ECDLP path.

### Status

`REVISE`.

Review pinned to commit
`10214c603a8b7d6869c0b457c2f96b9235456982`. Hashes match, the three
targeted tests pass, and deterministic replay matches after excluding wall
time. The tests check occupancy, disjointness, and support only; they do not
check point witnesses or relations.

### Strongest positive signal

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`: median scalar support remains
`0.405–0.464` while `|2A|=5–17` across eight increasing prime cyclic orders.
This is consistent with the imposed occupancy model.

A read-only auxiliary probe using first witnesses found full rank only after
accounting for the exact typed kernel. This is a feasibility check, not
coordinate evidence.

### Main objections

1. Every fixed `2A+3R` row has the deterministic kernel
   `(3*1_A,-2*1_R)`.
2. The implementation stores support keys without canonical witnesses and
   does not execute point-only queries.
3. The design uses more columns than its homogeneous comparator and does not
   reduce the total compiler.
4. The optimizer minimizes column count under formal occupancy, not complete
   attack cost.
5. Reported scaling is largely imposed by the optimizer and is toy-scale.
6. Cardinalities omit payload bytes and bandwidth; the sampler incurs
   avoidable `O(q)` Python memory.
7. Existing exact translation-profile results rule out the natural complete
   low-dimensional linear quotient; nonlinear and target-restricted routes
   remain open.

### Clean counterexample

Replace progression A with a coordinate-matched random unknown-log set.
Generically `|2A|` becomes `Theta(q^(1/2))`, destroying the advertised scan.
If only public group progressions retain small doubling, progression
structure is the mechanism and must be represented with its exact unknown-log
semantics.

### Next concrete action

Test coordinate R with point-keyed witnesses, public unknown-offset A,
quotient rank, multiple-witness selection, held-out descent, deep bytes,
construction operations, and materialized/same-advice generic baselines.

