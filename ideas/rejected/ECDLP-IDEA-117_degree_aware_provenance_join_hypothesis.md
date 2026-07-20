# ECDLP-IDEA-117 — Degree-aware provenance join

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `rejected_scoped_p1510_product_circuit_cubic_floor`
- Cohort: `20260717-f`
- Evidence scale: three immutable non-run theorem receipts at
  `ideas/artifacts/ECDLP-IDEA-117/fd_width_gate.md` and
  `ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md` and
  `ideas/artifacts/ECDLP-IDEA-117/p1511_scoped_negative_audit.md`; the last receipt
  preserves the independent synthetic replay; no experiment ran
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct join, exact five-point witness, valid relation,
  full-rank toy matrix, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Let `E(F_p)` contain a public prime-order subgroup `<P>` of order
`N=p^(1+o(1))`, let `Q=[x]P`, and let the sign-canonical, target-independent
factor base have size `B=L=N^ell`. P1510-style source-marked product circuits for serial
five-point Semaev incidence admit a factorized algebraic semijoin against the partitioned
`A_3` family. Without expanding the dense `A_2` coefficient vector, a
degree-`Theta(L^3)` union polynomial, all `L^2` surface pairs, or either explicit source
table, this semijoin returns only common endpoint factors and exact source jets with
complete source-query exponent `alpha<3/2`. It returns exact indices, signs, and
multiplicities for enough known random sums to produce `B+sigma` rows of rank `B`, and
the identical frozen semijoin supports blind descent of `Q+[t]P`. Fully charged circuit
construction, relation collection, sparse linear algebra, source output, blind descent,
verification, and peak memory have exponents below `1/2`.

## Mechanism-new operation

The proposed successor operation is **a factorized, source-marked algebraic semijoin on
P1510 product circuits that returns common endpoint factors together with Hasse-source
jets**. It must prune nonincidences inside the circuit representation and expose exact
source tuples without materializing `A_2`, `A_3`, a degree-`Theta(L^3)` polynomial, all
surface-pair queries, roots, or resultant tables. The incoming FD-width receipt already
shows that ordinary worst-case-optimal joining after relation construction is not this
operation.

Merely loading explicit Semaev relations into a database, replacing Z3 or Groebner with a
join engine, changing join order, adding an index to an `L^2` table, running dense
gcd/resultant input, invoking P1510 once per target, issuing all surface-pair queries, or
reporting only membership/counts is a duplicate or control. The mechanism is new only if
the factorized semijoin removes the recorded dense-state obstruction and retains exact
source jets through every common factor.

## Assumptions

1. `E,P,N,Q`, the fixed arity five, and a public factor base
   `F={F_1,...,F_B}` with `B=L=N^ell` are fixed before target queries.
2. Every oriented point, exceptional denominator branch, sign, repeated source, and point
   at infinity has an exact relational encoding and independent elliptic verifier.
3. The source-marked `A_2` and partitioned `A_3` objects are available as public
   P1510-style product circuits whose construction does not enumerate the explicit source
   tables; all circuit coefficients and source jets are charged.
4. The FD-width receipt's relational schema and the factorized-semijoin receipt's exact
   `Theta(L^3)` source-labelled leaf floor are accepted as scoped evidence for the
   declared P1510 product-circuit grammar.
5. Provenance returns all factor-base indices, signs, and multiplicities; an aggregate
   intermediate state without a source inverse is a failed query.
6. All setup, misses, heavy buckets, iterator construction, emitted tuples, duplicate
   suppression, linear algebra, target ambiguity, verification, and memory are charged.
7. Any finite evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`serial_S3_source_marked_product_circuits | P1510_Hasse_source_jets | factorized_algebraic_semijoin | common_endpoint_factor_output | no_dense_expansion_or_all_pair_queries | blind_descent`

The load-bearing operation was the hypothesized sub-`L^1.5` factorized source semijoin. A fast
membership bit, count, ordinary join over supplied relations, or dense circuit expansion
does not satisfy the fingerprint.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which supplies the exact
   `alpha<3/2` five-term membership boundary that the provenance join must meet.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where materialized backward
   `A_3` state polynomials exceed that boundary; the proposed join must avoid them.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, whose exact one-transition
   primitive composes into a dense quadratic resultant; the now-rejected P1510 circuit
   route likewise retains source-labelled pair leaves before the semijoin.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where bit-vector serial-S3 solving
   times out; the factorized product-circuit spelling is a backend change unless it
   reduces the pre-leaf representation, which this record does not.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1473`, where pair membership is
   exact and fast but the full graph work remains near `q`; this proposal must extend to
   complete five-source output and factor-log descent.

## Closest primary literature

- Ngo, Porat, Re, and Rudra,
  [Worst-case Optimal Join Algorithms](https://doi.org/10.1145/2213556.2213565),
  construct join algorithms meeting fractional-cover output bounds; they do not prove a
  favorable bound or implicit neighbor iterator for elliptic addition incidence.
- Abo Khamis, Ngo, and Suciu,
  [Computing Join Queries with Functional Dependencies](https://doi.org/10.1145/2902251.2902289),
  turn polymatroid bounds with functional dependencies and degree information into join
  algorithms; they do not establish the required Semaev closed-set lattice or provenance
  width collapse.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the algebraic addition constraints and source obligation, not this proposed
  join factorization.

No checked source proves a source-labelled elliptic join of exponent below `3/2`.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B=L,m=5`, relational schemas, exceptional branches, source-marked
   product circuits, factorized-semijoin contract, and independent source verifier.
2. Construct and prove the common-factor/source-jet semijoin without materializing
   `A_2`, `A_3`, a degree-`Theta(L^3)` polynomial, all `L^2` surface pairs, or an
   equivalent dense state object.
3. For public known random scalars `r_j`, query `R_j=[r_j]P`; return exact source tuples,
   verify each signed sum on `E`, and preserve every miss, duplicate, ambiguity, and
   iterator/output record.
4. Collect exactly `B+sigma` verified sparse source rows whose coefficient matrix has
   rank `B` modulo `N`; membership-only or dependent rows do not count.
5. Solve all factor-base logarithms and independently verify
   `[log_P(F_i)]P=F_i` for every `F_i`.
6. Freeze all join state, choose fresh public masks `t`, and apply the identical query to
   blind targets `Q+[t]P`, without target-specific indices or scalar advice.
7. Substitute verified factor logs, subtract `t`, retain every ambiguity candidate, and
   accept only `x` satisfying `[x]P=Q` on the original curve.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory.
BSGS costs `N^(1/2+o(1))` time and `N^(1/2+o(1))` stored group elements. Let
`B=L=N^ell`. Let complete target-independent join setup cost `L^(s+o(1))` time and
`L^(s_m+o(1))` peak memory. Let one complete source query, including implicit iteration,
provenance, all emitted candidates, duplicate suppression, and verification, cost
`L^(alpha+o(1))` time and `L^(m_q+o(1))` peak memory. If a query writes `L^z` tuples,
then by definition `alpha>=z` and memory or streaming-output accounting includes `z`.

Under the P1476 random-support model, query success probability is
`pi=min(1,L^5/N)`. In the sparse regime `L^5<N`, collecting `Theta(L)` independent rows
costs

`T_rel=N*L^(alpha-4+o(1))`,

and one blind descent costs

`T_desc=N*L^(alpha-5+o(1))`.

In the dense regime these become `L^(1+alpha+o(1))` and `L^(alpha+o(1))`.
Sparse Wiedemann/Lanczos is charged `L^(2+o(1))` time and at least `L^(1+o(1))`
memory, while the `B+sigma` fixed-width rows and factor logs contribute `L^(1+o(1))`
output/storage.

Thus the sparse-regime time exponent is

`lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)`,

and peak-memory exponent is

`mu=max(s_m*ell,m_q*ell,ell)`.

For `alpha<=1`, balancing relation collection and linear algebra gives the conditional
P1476 exponent `2/(6-alpha)`; for `1<alpha<3/2`, `ell=1/5` gives
`max(2/5,(1+alpha)/5)<1/2`. Every join key, degree partition, failed iterator branch,
source tuple, and target candidate is included; an explicit `L^2` relation/index build
uses its actual construction time and bit memory.

## Likely fatal obstruction

The relevant addition relations are not supplied as small database tables. Constructing
the neighbor iterators needed by a worst-case-optimal join may itself enumerate all
`L^2` pairs. The valid algebraic functional dependencies may also leave fractional or
submodular width at least two, while retaining source provenance can destroy projected
degree savings. In that case the join is only a renamed meet-in-the-middle/resultant
solver and has `alpha>=2`, which misses the P1476 gate.

The first immutable receipt verifies this obstruction for explicit A2/A3 and dense
P1510 coefficient routes. The second proves that the exact proposed factorized grammar
instantiates `Theta(L^3)` constant-size source-labelled leaves before gcd, factorization,
rank, or descent. On `N=Theta(L^5)`, that setup has exponent `3/5`, above rho's `1/2`.
The independent audit receipt replays the deterministic control over `F_65537` for
`L in {4,6,8,12,16,24,32}` and reproduces the `L^3` leaves and degrees, gcd degree `L`,
planted-source recovery, and growing leaf/rho ratio `sqrt(L)`. It also scopes `Theta(L^3)`
to generation, traffic, or explicit serialization rather than an unconditional peak-memory
floor. This is a scoped no-go for the declared P1510 product-circuit representation, not
for an arbitrary pre-leaf or target-uniform representation.

## Proof track

The proof track would require a factorized source-marked P1510 semijoin with total setup
below `L^2.5`, query exponent below `L^1.5`, exact common factors and source jets, and the
seven-step rank/descent path. The two receipts and independent replay show that the
declared grammar already has `Theta(L^3)` setup input, so this proof track fails.

## Disproof track

For the declared P1510 product-circuit grammar, prove a `Theta(L^3)` source-labelled leaf
or degree floor before semijoin work and independently replay the planted common-factor
control. Both obligations are now satisfied. No lower bound is claimed for arbitrary
succinct circuits or a representation acting before P1510 leaf emission.

## Positive and negative controls

- Positive join control: Loomis-Whitney and bounded-degree synthetic joins with planted
  provenance and independently known optimal output bounds.
- Positive EC control: exhaustive tiny factor bases with all five-source tuples and exact
  exceptional-branch verification.
- Negative width control: matched random incidence relations having the same cardinality
  and degree marginals but no extra functional dependency.
- Mechanism controls: explicit `A_2/A_3` tables, P1478 resultants, generic Z3/Groebner,
  ordinary meet-in-the-middle, and join-order-only variants.
- Leakage control: permute factor-base labels while preserving aggregate state values;
  exact provenance must follow the permutation without scalar labels.
- Baseline control: matched Pollard rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

The declared mechanism is falsified because its proved setup exponent is `3/5>=0.50`;
no run is admissible under this retired record. Historic promotion would have required a
source-jet biconditional, zero provenance errors, `alpha<3/2`, and upper 95% bounds
`lambda,mu<=0.45` across the complete relation/rank/blind-descent pipeline. Any succinct,
target-uniform object constructed before P1510 leaf emission must receive a new idea ID,
new fingerprint, and new contract rather than weakening this negative boundary.

## Artifact plan

- FD-width theorem gate: `ideas/artifacts/ECDLP-IDEA-117/fd_width_gate.md`
- Factorized-semijoin scoped-negative receipt: `ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md`
- Independent scoped-negative audit: `ideas/artifacts/ECDLP-IDEA-117/p1511_scoped_negative_audit.md`
- Prospective successor boundary: `ideas/artifacts/ECDLP-IDEA-117/preleaf_successor_requirements.md`
- Frozen relational schema: `ideas/artifacts/ECDLP-IDEA-117/join_schema.yaml`
- Prospective join implementation: `ideas/artifacts/ECDLP-IDEA-117/provenance_join.py`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-117/verify_sources.sage`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-117/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-117/analysis.md`

## Interpretation boundary

This record is rejected at a scoped, model-bound boundary and remains
novelty-unverified. The immutable receipts and independent replay close ordinary explicit
joins, dense P1510 composition, and the declared source-labelled P1510 product-circuit
semijoin. They do not close every factorized algebraic representation. Correct join
output, an FD identity, exact membership, a valid relation, full toy rank, verified
factor logs, or a recovered toy scalar does not establish better-than-rho ECDLP. A
pre-leaf representation change is a new hypothesis, not promotion of this record.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-117/preleaf_successor_requirements.md` freezing the requirements that any successor act before pair-resultant leaf emission, provide a target-uniform source-biconditional object of size `o(r^(5/2))`, retain an exact five-source inverse, and receive a new idea ID and contract.
