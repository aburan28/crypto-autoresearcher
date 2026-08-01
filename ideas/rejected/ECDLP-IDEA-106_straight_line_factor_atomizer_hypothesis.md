# ECDLP-IDEA-106 — Straight-line factor atomizer

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_solver_substitution`
- Evidence scale: no run; any circuit-factorization diagnostic is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: straight-line factorization and automatic differentiation are
  solver backends; they do not create a factor-to-point source inverse or remove relation
  density, rank, and blind descent.
- Breakthrough claim: **none**; a compact circuit, correct factorization, derivative, or
  toy relation is not an ECDLP break.

## Falsifiable hypothesis

Represent the target-conditioned Semaev/factor-base incidence polynomial by a short
straight-line program. The proposed claim is that black-box factorization splits this
circuit into source-labelled factors and that Baur-Strassen derivatives identify each
factor's factor-base atom at essentially the original circuit cost. If those atoms could
be emitted for `B+sigma` independent rows and masked targets with complete time and memory
exponents below `1/2`, the method would give an ECDLP path. The claim is rejected as a
solver substitution because algebraic factors are components of a polynomial, not the
individual point tuples in a zero-dimensional target fiber.

## Mechanism-new operation

The screened operation is **factor an implicit relation polynomial given by a
straight-line program, differentiate the factor circuit, and invert its factors to exact
factor-base source atoms**. Compact circuit evaluation, fast polynomial factorization,
reverse-mode differentiation, or an irreducible-component decomposition is a control.
For mechanism novelty the factorization would need a proved biconditional between factors
and signed source points before enumeration. No such operation is supplied, so the record
is rejected rather than admitted as another polynomial solver.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, fixed arity `m`, and factor base `F` of size `B=N^beta`.
2. The complete target relation predicate, including factor-base membership and all
   exceptional branches, has a straight-line program of sub-rho length and degree/height.
3. Black-box factorization works uniformly over the needed finite fields and returns
   factors without expanding an object of geometric degree comparable to the source fiber.
4. Factors and derivative values invert canonically to source indices, signs, and
   multiplicities without target-specific advice or known factor logs.
5. Circuit construction, degree, random evaluations, Hensel lifts, factor output,
   derivatives, failed targets, relation density, rank, descent, verification, and memory
   are fully charged.
6. Any diagnostic remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`implicit_Semaev_membership_SLP | black_box_polynomial_factorization | Baur_Strassen_derivative_circuit | claimed_factor_to_point_atom_inverse | full_relation_and_blind_descent`

The collision key is `compact equation representation + generic factorization backend +
missing source inverse`. An implementation speedup at fixed geometric degree is not a new
ECDLP mechanism.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`,
   where exact norm/resultant amortization loses row/source provenance.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, the nearest public arithmetic
   source-fiber generator and transposed join obligation.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, which requires a source generator,
   not merely a compact target polynomial.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact compact norm identity
   still lacks a source-resolving common-root algorithm below the cost gate.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate
   barrier that changing the solver representation does not remove.

## Closest primary literature

- Kaltofen,
  [Factorization of polynomials given by straight-line programs](https://kaltofen.math.ncsu.edu/bibliography/89/Ka89_slpfac.pdf),
  establishes polynomial factorization in compact arithmetic-circuit representation; it
  does not make irreducible factors correspond to elliptic source tuples.
- Baur and Strassen,
  [The complexity of partial derivatives](https://doi.org/10.1016/0304-3975(83)90110-X),
  shows that derivatives of a straight-line computation can be obtained within a constant
  factor of evaluation complexity; it does not supply factor-base orientation.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the relation equations and requires actual bounded/source solutions.

These sources establish compact polynomial computation, factorization, and efficient
derivatives, not the claimed factor-to-point atom inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the circuit grammar, membership encoding, factorization field,
   randomization, exceptional-branch policy, and exhaustive source truth.
2. Build and independently verify a target-parametric straight-line program without
   enumerating `F^m` or embedding factor logs in constants.
3. For known outputs `R_j=[r_j]P`, specialize and factor the circuit, differentiate its
   factors, invert every accepted factor to exact signed points in `F`, and verify the sum.
4. Preserve irreducible factors with no source inverse, repeated factors, failed lifts,
   misses, duplicate rows, and dependencies; collect `B+sigma` verified rows of rank `B`.
5. Solve and independently verify every factor-base logarithm modulo `N`.
6. Freeze the circuit/factorization protocol and apply it unchanged to masked blind
   targets `Q+[t]P`, retaining every factor and source ambiguity.
7. Substitute factor logs, unmask all candidates, and accept only after checking
   `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`. Let straight-line-circuit construction
take `N^(a+o(1))` time and `N^(a_m+o(1))` peak memory; let materializing the circuit,
degree metadata, and coefficient-height data take `N^(h+o(1))` time and
`N^(h_m+o(1))` memory. Let a complete factorization/derivative/source-inversion attempt,
excluding written output, take `N^(q+o(1))` time and `N^(q_m+o(1))` working memory. Let
the complete factor list have exponent `f`, the exact source tuples emitted per accepted
fiber have exponent `o`, and the residual scalar ambiguity per emitted target source have
exponent `u`; their explicit output requires the corresponding time and storage. Let the
reciprocal accepted-relation and target densities be `N^delta` and `N^delta_t`. Let
sparse linear algebra take `N^(ell+o(1))` time and `N^(ell_m+o(1))` memory, with
`ell>=2beta` absent proved structure. Finally, let verification of one emitted
tuple/candidate take `N^(v+o(1))` time and `N^(v_m+o(1))` working memory.

The complete time exponent is

`lambda=max(a,h,beta+delta+q+f+o+v,ell,delta_t+q+f+o+u+v)`,

and the complete peak-memory exponent is

`mu=max(a_m,h_m,q_m,ell_m,beta,f+o+u,v_m)`.

Thus the circuit state, factor workspace and factor list, source output, target ambiguity,
linear-algebra state, and verifier workspace are all explicit. Geometric degree, all
random evaluations, specializations, Hensel data, failed inversions, emitted sources, and
verification are charged. Polynomial time in a geometric degree of `N^(1/2)` or more
does not beat rho.

## Likely fatal obstruction

The target relation polynomial may be irreducible even though its zero set contains many
point tuples. Factoring the equation then yields no tuple atoms. For a zero-dimensional
specialization, primitive idempotents or linear factors appear only after constructing a
splitting algebra whose length is the number of solutions. Derivatives describe local
geometry of already represented factors; they do not orient an atom to a factor-base
index. Thus the geometric degree, factor output, or source inverse restores the original
solver and enumeration cost.

## Proof track

A versioned successor must prove a target-uniform factor/source biconditional, bound
circuit degree and complete factor output below rho, and establish the seven-step
factor-log and blind-descent path with `lambda,mu<1/2`. Faster factorization alone does not
satisfy this obligation.

## Disproof track

Show the generic incidence polynomial is irreducible, exhibit one factor containing
multiple source tuples, prove source splitting requires the full relation algebra, show
derivatives are invariant under source-label permutation, or derive complete
time/output/memory exponent at least `1/2`.

## Positive and negative controls

- Positive circuit control: planted products of linear factors given by short
  straight-line programs with independently known atoms.
- Positive derivative control: Baur-Strassen gradients checked against symbolic
  derivatives on tiny circuits.
- Negative geometry control: irreducible polynomials with many finite-field zeros.
- Mechanism controls: Gröbner, resultant, and black-box factorization backends on identical
  relation systems, all charged by geometric degree and source output.
- Leakage control: permute factor-base labels while preserving the circuit polynomial.
- Baseline control: matched Pollard-rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

No promotion gate remains for this solver-substitution record. A mechanism-new successor
would require a proved factor/source biconditional, zero source errors on exhaustive
ordinary curves through 18 bits, at least `1,000` verified rows and `100` blind descents
at each of the two largest sizes, fresh rank at least `0.8B`, and upper 95% bounds
`lambda,mu<=0.45` under the complete formulas above. Falsify as written if one
irreducible factor contains distinct source tuples, factorization returns only
components, source inversion has lower 95%
exponent at least `0.50`, or every complete arm has `lambda>=0.50`.

## Artifact plan

- Rejection proof: `ideas/artifacts/ECDLP-IDEA-106/factorization_solver_merge.md`
- Circuit specification: `ideas/artifacts/ECDLP-IDEA-106/relation_slp.yaml`
- Diagnostic factorizer: `ideas/artifacts/ECDLP-IDEA-106/slp_factorizer.sage`
- Independent source checker: `ideas/artifacts/ECDLP-IDEA-106/verify_factor_sources.py`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-106/analysis.md`
- Any diagnostic receipts: `ideas/artifacts/ECDLP-IDEA-106/runs/<run-id>/`

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. Compact
evaluation, correct factorization, fast derivatives, valid relations, or a toy scalar do
not establish a better-than-rho algorithm. A source-labelled factor inverse and complete
descent remain absent.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-106/factorization_solver_merge.md` proving that straight-line factorization decomposes polynomial components rather than factor-base tuples and that derivative circuits do not restore source orientation.
