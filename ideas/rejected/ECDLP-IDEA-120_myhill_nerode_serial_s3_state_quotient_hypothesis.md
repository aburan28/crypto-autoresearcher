# ECDLP-IDEA-120 — Myhill-Nerode serial-S3 state quotient

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_state_width_barrier`
- Cohort: `20260717-f`
- Evidence scale: no run; any future quotient-width preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a canonical automaton, compact toy decision diagram,
  exact membership answer, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Encode sorted factor-base indices, signs, projective serial-S3 intermediates, target data,
and exceptional branches as a finite language. Two partial states are equivalent exactly
when they have the same target completions and the same source-provenance continuations.
For a public factor base `B=L=N^ell`, the canonical Myhill-Nerode quotient of this
language has width `W(L)=L^(w+o(1))` and can be constructed and queried with complete
source output exponent `alpha<3/2`, without visiting a dense `L^2` state/root surface.
Backtracking returns exact five-source tuples, supports `B+sigma` rows of rank `B`, all
verified factor logs, and blind `Q+[t]P` descent with time and memory below rho.

The record is rejected and merged at the state-width barrier: no current theorem shows a
subquadratic completion-equivalence quotient, and generic BDD/SAT/automaton replacement is
only a solver substitution.

## Mechanism-new operation

The proposed operation is **derive an algebraically certified completion-and-provenance
congruence for serial-S3 partial assignments, quotient by it canonically, and backtrack an
exact factor-base tuple from an accepting state**. Equivalence must preserve source labels
and all target completions, not merely a Boolean membership answer.

Trying a different BDD variable order, using an off-the-shelf knowledge compiler,
minimizing an explicitly enumerated automaton, replacing Z3 with a decision diagram, or
dropping provenance is a duplicate/control. The mechanism would be new only if an
algebraic congruence theorem proves and constructs a sub-`L^1.5` exact quotient before
dense states exist.

## Assumptions

1. `E(F_p)` contains public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, fixed arity five, and target-independent sign-canonical factor base
   `F={F_1,...,F_B}` with `B=L=N^ell`.
2. The word language encodes all source indices, signs, projective coordinates,
   exceptional denominators, repeated points, and the point at infinity exactly.
3. Completion equivalence is defined without hidden scalar labels and preserves the full
   multiset of source-provenance continuations.
4. The quotient can be constructed from algebraic invariants without enumerating all raw
   pair/triple states or all partial words.
5. Accepting-state backtracking returns every exact source tuple and independently
   verifies the elliptic sum.
6. Construction, variable ordering, transitions, quotient nodes, backpointers, emitted
   candidates, misses, rank, descent, verification, and bit memory are fully charged.
7. Any finite-size observation remains toy, heuristic, model-bound, and
   novelty-unverified.

## Semantic fingerprint

`serial_S3_source_language | completion_provenance_congruence | canonical_Myhill_Nerode_quotient | subquadratic_state_width | exact_accepting_path_unranking | blind_descent`

The load-bearing novelty is the algebraically proved completion/provenance quotient. A
small diagram after deleting source labels is an aggregate membership control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where bit-vector serial-S3
   membership times out; prequotienting semantics is distinct only if an independent
   state-width theorem exists.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1477`, where backward serial-S3
   state polynomials are dense and exceed the `L^1.5` gate; the quotient must merge these
   states while preserving exact sources.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, where exact transition
   composition creates a dense `L^2` state object; the proposed congruence must be built
   without first constructing that object.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which defines the complete
   five-term query, relation, linear-algebra, and descent exponent boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, where compact linear factor-log
   features fail; exact language equivalence is different from interpolation only if it
   retains endpoint provenance.

## Closest primary literature

- Nerode,
  [Linear Automaton Transformations](https://doi.org/10.1090/S0002-9939-1958-0135681-9),
  supplies the completion-equivalence foundation for canonical automaton states; it does
  not bound the elliptic source-language index.
- Bryant,
  [Graph-Based Algorithms for Boolean Function Manipulation](https://doi.org/10.1109/TC.1986.1676819),
  develops reduced ordered decision diagrams and explicitly leaves exponential worst-case
  size possible; it does not establish a compact Semaev representation.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the exact algebraic language whose source-preserving quotient is at issue.

No checked source proves subquadratic Myhill-Nerode width for serial-S3 source incidence.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B=L`, bit/projective encoding, source-word order, exceptional cases,
   completion equivalence, algebraic state invariants, quotient construction, and
   independent exhaustive truth.
2. Prove the congruence biconditional and construct the target-independent canonical
   quotient with source backpointers without visiting `A_2`, `A_3`, or an `L^2` state
   table.
3. For known public `R_j=[r_j]P`, specialize only the target terminals, traverse accepting
   quotient paths, unrank exact source tuples, and independently verify every signed sum;
   preserve all misses, duplicate paths, and ambiguities.
4. Collect exactly `B+sigma` verified source rows whose coefficient matrix has rank `B`
   modulo `N`; Boolean acceptance without an exact tuple does not count.
5. Solve all factor-base logarithms and independently verify
   `[log_P(F_i)]P=F_i` for every factor-base point.
6. Freeze the quotient, choose fresh public masks `t`, and apply the identical terminal
   specialization and source unranking to blind targets `Q+[t]P`.
7. Substitute verified factor logs, subtract `t`, enumerate every accepting-path scalar
   candidate, and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Set `B=L=N^ell`. Let quotient construction cost
`L^(s+o(1))` time and `L^(s_m+o(1))` peak memory; let canonical width be
`W=L^(w+o(1))`. Let one complete target query, accepting-path traversal, source
backtracking, all candidate output, and verification cost `L^(alpha+o(1))` time and
`L^(m_q+o(1))` memory. Necessarily `s>=w`; if transitions or backpointers require
`L^c` output, then `s,alpha`, or memory includes `c` rather than treating it as free.

Under the P1476 support model `pi=min(1,L^5/N)`, sparse-regime relation and descent costs
are

`T_rel=N*L^(alpha-4+o(1))`

and

`T_desc=N*L^(alpha-5+o(1))`.

Dense-regime costs are `L^(1+alpha+o(1))` and `L^(alpha+o(1))`. Sparse linear algebra
costs `L^(2+o(1))` time and at least `L^(1+o(1))` memory. Quotient nodes, transitions,
source backpointers, `B+sigma` rows, factor logs, and accepting paths are all charged
output/storage.

The sparse-regime exponents are

`lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)`

and

`mu=max(s_m*ell,w*ell,m_q*ell,ell)`.

As in P1476, `alpha<=1` conditionally gives optimized time `2/(6-alpha)`; for
`1<alpha<3/2`, `ell=1/5` gives `max(2/5,(1+alpha)/5)<1/2`. A width or query lower bound
`Omega(L^2)` gives `alpha>=2` or comparable construction cost and destroys this gate.

## Likely fatal obstruction

Distinct partial source words can reach the same projective intermediate while admitting
different endpoint continuations, so source provenance refines rather than compresses the
state space. Communication-style fooling sets may force `Omega(L^2)` inequivalent states
for every variable ordering. Computing exact equivalence can itself require enumerating
all completions, making quotient construction the original membership problem.

## Proof track

Define the source language and prove an algebraic finite-index congruence, sub-`L^1.5`
construction/query bounds, exact accepting-path unranking, and the complete seven-step
rank, factor-log, blind-descent, output, and memory model.

## Disproof track

Construct an `Omega(L^2)` completion/provenance fooling set, show that every useful merge
loses source labels, prove quotient minimization requires dense completion enumeration, or
derive full time or peak-memory exponent at least `1/2`.

## Positive and negative controls

- Positive automaton control: planted regular languages with known compact canonical
  quotients and exact labelled-path unranking.
- Positive EC control: exhaustive tiny serial-S3 truth with blinded source indices and all
  exceptional branches.
- Negative width control: equality/disjointness-style languages with known large
  completion-equivalence index.
- Mechanism controls: Z3 bit-vectors, generic BDD variable-order sweeps, SAT/Groebner,
  explicit state minimization, P1478 resultants, and membership-only diagrams.
- Leakage control: permute source labels while preserving all intermediate state values;
  provenance must follow the permutation.
- Baseline control: matched Pollard rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

The rejected lane cannot reopen without a theorem proving the complete
completion/provenance congruence and symbolic `lambda,mu<=0.45`. A future toy preflight
must cover at least 20 ordinary curves per size across four increasing sizes, exhaustive
truth through 18 bits, at least `1,000` verified relations and `100` blind descents at
each of the two largest sizes, exactly `B+sigma` retained rows of rank `B`, zero source
errors, and upper 95% bounds `lambda<=0.45` and `mu<=0.45` including construction,
transitions, backpointers, output, and bit memory. Falsify on one stable provenance merge
error or if a fooling-set/proved/lower-95% bound gives `w>=2`, `alpha>=3/2`,
`lambda>=0.50`, or `mu>=0.50`.

## Artifact plan

- Quotient-width theorem gate: `ideas/artifacts/ECDLP-IDEA-120/state_quotient_gate.md`
- Frozen source language: `ideas/artifacts/ECDLP-IDEA-120/source_language.yaml`
- Prospective quotient builder: `ideas/artifacts/ECDLP-IDEA-120/build_quotient.py`
- Independent path/source verifier: `ideas/artifacts/ECDLP-IDEA-120/verify_paths.sage`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-120/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-120/analysis.md`

## Interpretation boundary

This merged/rejected record is toy, heuristic, model-bound, and novelty-unverified. A
canonical quotient, compact toy diagram, exact membership answer, valid relation, full
toy rank, verified factor log, or recovered toy scalar is not a better-than-rho result.
Without a proved source-preserving width collapse and complete blind descent, the state
width barrier remains controlling.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-120/state_quotient_gate.md` proving either a source-provenance Myhill-Nerode quotient constructible and queryable below `L^1.5` or an explicit `Omega(L^2)` completion-equivalence fooling set for the serial-S3 language.
