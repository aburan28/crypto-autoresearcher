# ECDLP-IDEA-115 — Source-labelled Ulrich–Chow complex

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_scoped_ulrich_single_map_source_length_floor`
- Top lane: `representation-changing`
- Evidence scale: immutable non-run theorem receipt at
  `ideas/artifacts/ECDLP-IDEA-115/ulrich_source_gate.md` and independent scope audit at
  `ideas/artifacts/ECDLP-IDEA-115/p1512_scoped_negative_audit.md`; no experiment ran
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a linear Chow complex, determinantal identity, kernel vector, valid relation, or toy descent is not an ECDLP break.

## Falsifiable hypothesis

The complete source-labelled elliptic relation incidence admits a target-independent Ulrich sheaf whose linear Chow complex has sub-rho size and whose specialized kernel or cokernel basis is biconditional with exact signed factor-base source tuples. Unlike a dense resultant, the linear complex would retain provenance and allow output-sensitive source recovery, full-rank relation collection, factor-log calibration, and blind descent with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The operation is **construct a source-labelled Ulrich sheaf and linear Chow complex whose specialized kernel vectors invert to exact elliptic sources**. This is representation-changing only if the complex is constructed from compact public equations, remains asymptotically smaller than the incidence degree, and supplies a canonical source inverse. A determinant alone, generic resultant matrix, quotient-algebra eigensolver, syzygy backend, or kernel annotated after sources are known is a duplicate/control.

The declared strict-Ulrich square-linear source-atom mechanism is rejected at a scoped
theorem boundary.
Ulrich/Chow complexes linearize incidence and can make a resultant determinantal, but
determinant degree and independent kernel multiplicity still reflect the full finite
fiber. This does not reject nonlinear target-specialized circuits or packed aggregates
whose separately charged splitter is not a kernel/cokernel atomizer; either would be a
new representation and require a new idea ID.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; `F` is target-independent with `B=N^beta`, and signed arity `m` is fixed.
2. The universal labelled relation incidence, including repeated points, signs, infinity, nonreduced fibers, and target parameter, has a public projective presentation of controlled degree.
3. It admits a target-independent Ulrich sheaf with a linear Chow/Tate complex constructible without enumerating `F^m` or solving the relation fiber.
4. Specialization at an output `R` yields kernel/cokernel atoms in exact bijection with signed factor-base tuples, with a public source inverse.
5. Matrix compression does not hide dense coefficients, source dictionaries, multiplicity blocks, or target-dependent reconstruction.
6. Sheaf construction, resolutions, matrix entries, specialization, kernels, source output, rank, factor logs, blind descent, verification, and peak memory are charged.

## Semantic fingerprint

`source_labelled_relation_incidence | Ulrich_sheaf | linear_Chow_Tate_complex | kernel_source_biconditional | blind_descent`

The removal test is a target-independent compact linear complex with exact source inversion and size below the relation degree. A dense resultant, generic syzygy solver, primitive-idempotent split after quotient construction, or relation-only determinant is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H644`, the nearest proposed non-Grobner high-arity decomposition sieve and its complete source-cost obligation.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1428-EXACT-SHARED-UNION-CONTROL`, where an exact balanced shared union object resolves incidences only after the full row-norm input is present.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the matching negative that aggregate shared norms do not recover ancestry or promote.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, whose source-complete transition polynomials become dense.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, whose exact local norm identity densifies under the composition needed for complete membership.

## Closest primary literature

- Eisenbud and Schreyer, with an appendix by Weyman, [Resultants and Chow forms via exterior syzygies](https://arxiv.org/abs/math/0111040), construct Chow forms and determinantal complexes from suitable sheaves; they do not give a compressed factor-base source inverse.
- Eisenbud and Schreyer, [Betti numbers of graded modules and cohomology of vector bundles](https://arxiv.org/abs/0712.1843), develop the surrounding linear-resolution framework; it does not remove finite-fiber degree or output.
- Buchweitz and Pavlov, [Moore Matrices and Ulrich Bundles on an Elliptic Curve](https://arxiv.org/abs/1511.05502), give determinantal normal forms and Ulrich bundles for plane cubics, not a source-labelled relation-fiber inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation incidence but no Ulrich source atomizer.

No checked primary source proves a sub-degree Ulrich/Chow representation with exact source kernels for generic prime-field elliptic relations. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, projective embedding, labelled incidence, Ulrich sheaf, resolution, Chow-complex convention, specialization, kernel normalization, source inverse, and exceptional-fiber policy.
2. Construct and independently verify the sheaf and linear complex without enumerating factor-base tuples; serialize every matrix and coefficient.
3. Specialize at a public `R`, compute every kernel/cokernel atom, invert each to exact signed members of `F`, and independently verify the elliptic sum.
4. Apply the frozen complex to known `R_j=[r_j]P`; retain verified rows until exactly `B+sigma` rows have rank `B`.
5. Solve all factor-base logarithms and independently verify every point/log pair.
6. Form fresh masked targets `R_t=Q+[t]P` and apply the identical specialization, kernel extraction, source inverse, and verification.
7. Substitute factor logs, subtract `t`, retain every multiplicity/ambiguity candidate, and accept only `[x]P=Q`.
8. Preserve construction failures, non-Ulrich cases, nonreduced kernels, missed/duplicate atoms, coefficient growth, rows, and candidates.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; sheaf/resolution plus factor-base construction time and memory be `N^a,N^a_m`; serialized complex size and working state be `N^c,N^c_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; complete specialization, kernel, source-inverse, and exact elliptic verification work be `N^k`; source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

and

`mu=max(a_m,c_m,beta+o,ell_m,u)`.

All free-resolution terms, exterior maps, coefficients, multiplicity blocks, kernel bases, failed specializations, `B+sigma` rows, source output, and candidates are charged. A linear matrix whose dimension or coefficient payload equals the Chow degree enters `c` or `c_m` in full.

## Likely fatal obstruction

The Chow form records when a linear space meets the variety; linearization does not reduce the degree of that intersection. A source-biconditional specialized kernel must distinguish all accepted points of the finite fiber. Their multiplicity therefore appears as matrix dimension, kernel output, coefficient payload, or annotations. If the complex is smaller by aggregating points, its kernel is not an exact source inverse; splitting it restores the dense incidence object.

The immutable P1512 gate makes this obstruction exact for the declared
target-independent strict-Ulrich square-linear atomizer. At arity `t` with oriented
factor deck size `B`, the favorable unordered source cycle has length
`binomial(B+t-1,t)=Theta(B^t)` up to lower-order normalization deletions. For a
generically invertible `s x s` matrix of linear forms on the plane cubic, Smith normal
form and the determinant divisor give `3s>=sum_R nu_R=Theta(B^t)` whenever each source
is an independent kernel/cokernel atom. Thus `s=Omega(N^(t*beta))` for `B=N^beta`; the
smallest frozen contract arm has `t*beta=3*0.18=0.54`, already above rho. The independent
audit confines any multiterm extension to a separately proved noncancelling effective
homology degree with explicitly charged rank-twist payload.

## Proof track

Historic success would have required constructing the universal Ulrich sheaf and linear
complex, proving a complete kernel/source biconditional including exceptional fibers,
and proving `a,a_m,c,c_m,k,o,u,lambda,mu<=0.45` through rank, factor logs, and blind
descent. The cycle-length theorem gives strict-Ulrich payload exponent at least `0.54`
on every frozen arm, so this proof track fails for the declared representation.

## Disproof track

Show that no suitable Ulrich sheaf exists, exhibit a kernel atom mixing two sources,
prove matrix/coefficient/output size at least the generic relation degree, or lower-bound
complete time or memory by `N^(1/2)`. The P1512 receipts satisfy the size branch for a
target-independent strict-Ulrich square-linear map. A multiterm Chow/Tate extension
would require a separate proof that every exact source contributes noncancelling local
torsion in one effective homology degree and that the rank-twist payload is charged. A
source-annotated matrix or post-hoc kernel labelling also disproves the mechanism.

## Positive and negative controls

- Published determinantal varieties with explicit Ulrich sheaves and independently known Chow complexes.
- Planted zero-dimensional schemes whose kernel atoms have known point labels.
- The same schemes under ordinary dense resultants and quotient-algebra solvers.
- Source-labelled versus label-dropped complexes matched for degree and matrix payload.
- Exhaustive ordinary toy elliptic relation fibers including repeated and nonreduced cases.
- Blind masked targets with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

Historic promotion required a target-independent Ulrich sheaf, a kernel/source
biconditional, and symbolic `a,a_m,c,c_m,k,o,u,lambda,mu<=0.45` without a source table.
The declared mechanism is falsified because every frozen strict-Ulrich payload exponent
is at least `0.54`, so no run is admissible under this retired record. Any nonlinear,
multiterm, rectangular, or succinct target-specialized successor must preserve a complete
scalar-blind source inverse with every exponent below `1/2`, receive a new ID and
contract, and independently re-establish every
relation, rank, factor-log, blind-descent, time, output, and memory gate.

## Artifact plan

- Ulrich/source theorem gate: `ideas/artifacts/ECDLP-IDEA-115/ulrich_source_gate.md`
- Independent scoped-negative audit: `ideas/artifacts/ECDLP-IDEA-115/p1512_scoped_negative_audit.md`
- Prospective nonlinear-successor boundary: `ideas/artifacts/ECDLP-IDEA-115/nonlinear_successor_requirements.md`
- Frozen incidence/sheaf specification: `ideas/artifacts/ECDLP-IDEA-115/ulrich_complex_spec.yaml`
- Prospective complex constructor: `ideas/artifacts/ECDLP-IDEA-115/ulrich_chow.sage`
- Independent kernel/source verifier: `ideas/artifacts/ECDLP-IDEA-115/verify_ulrich_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-115/analysis.md`

## Interpretation boundary

This representation-changing proposal is rejected at a scoped, model-bound strict-Ulrich
single-map boundary and remains novelty-unverified. The theorem receipts close a
target-independent square-linear Chow/Ulrich atomizer whose independent kernel or
cokernel atoms invert directly to all sources. They do not close arbitrary nonlinear
target-specialized circuits, packed aggregates with a separately charged splitter,
weakly Ulrich or multiterm complexes with cancellation, rectangular Fitting encodings,
or succinct implicit operators. A valid Ulrich sheaf, linear complex, determinant,
source kernel, relation, or toy scalar is not evidence of a complete below-rho algorithm
or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-115/nonlinear_successor_requirements.md` freezing the requirements that any successor be constructed before source enumeration, use a target-specialized nonlinear representation rather than independent linear kernel atoms, expose an exact scalar-blind five-source inverse with payload `o(r^(5/2))`, and receive a new idea ID and contract.
