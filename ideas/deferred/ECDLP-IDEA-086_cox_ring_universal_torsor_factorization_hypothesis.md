# ECDLP-IDEA-086 — Cox-ring universal-torsor factorization

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `deferred_theorem_required`
- Top lane: `representation-changing`
- Evidence scale: no run; any future factorization preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a finitely generated Cox presentation, valid torsor lift, or correct toy factorization is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent marked elliptic-addition variety or universal family `X`
whose fixed-output incidence has dimension `m-1` and whose points encode output-marked
`m`-source relations. Its Cox total-coordinate ring `Cox(X)` is finitely generated at
sub-rho cost. Passing to the universal torsor makes the lifted relation equation
factorial: its homogeneous factorization splits into graded atoms with a public exact
inverse to the signed factor-base sources on the quotient. Those atoms yield `B+sigma`
full-rank relation rows and blind target descents with end-to-end time and memory
exponents below `1/2`.

## Mechanism-new operation

The operation is **lift the marked addition fiber to a factorial universal torsor, factor it into class-group-graded atoms, then invert the quotient map to exact source points**. It changes the representation before solving. A toric homogenization, same-field isogeny, genus-two/Prym transfer, solver substitution, factorization of an already explicit source polynomial, or public feature vector is a control. Survival requires finite generation, unique graded factorization up to explicitly resolved torsor units, and an exact quotient-source lift that does not materialize the relation incidence table.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; the target-independent factor base `F` has size `B=N^beta` and fixed relation arity `m`.
2. A fixed marked addition variety or universal family `X` represents the complete signed relation correspondence, including exceptional and boundary fibers.
3. `Cl(X)` is effectively computable and `Cox(X)` is finitely generated with a public homogeneous presentation smaller than the explicit `F^m` incidence object.
4. Relevant lifted fibers factor into graded atoms uniquely enough to recover every source index, sign, and multiplicity after quotienting by the grading torus.
5. The factorization and source inverse use no DLP labels, target-specific advice, or post-hoc selector.
6. Cox generators/relations, irrelevant ideal, torsor charts, units, quotient ambiguity, failed lifts, relation density, `B+sigma` rows, rank, factor logs, descent, candidate output, verification, and peak memory are fully charged.

## Semantic fingerprint

`marked_addition_variety | cox_total_coordinate_ring | universal_torsor_factorial_lift | graded_atom_factorization | exact_quotient_source_lift | blind_descent`

The candidate is representation-new only if factorial lifting removes the source ambiguity and dense incidence obstruction. A grading that merely tags an already known point or a Cox presentation as large as the source table receives no credit.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H008`, the nearest representation-changing Prym/genus-two transfer hypothesis; this candidate instead requires a factorial total-coordinate lift of the addition variety/family.
2. `ledger/FINDING-PF-IC-001.md` — imported `PO96`, the geometry-only saturation and principal-polarization gate that prevents a representation transfer from inheriting unproved source or cost claims.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-054`, the direct polarization-descent obstruction; a universal torsor must remove, not conceal, the quotient/source ambiguity.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier against compact public representations of prime-field relation structure.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where tested public feature spaces fail to contain factor logs; class-group gradings alone are therefore a control, not a scalar decoder.

## Closest primary literature

- Hassett and Tschinkel, [Universal torsors and Cox rings](https://arxiv.org/abs/math/0308182), studies equations of universal torsors on rational surfaces; it does not establish the required elliptic-addition variety/family or source decoder.
- Cox, [The homogeneous coordinate ring of a toric variety, with erratum](https://arxiv.org/abs/alg-geom/9210008), gives the toric total-coordinate ring and quotient construction; the marked relation variety/family is not assumed toric.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), provides the neighboring addition equations without a factorial torsor lift.

No checked source proves finite generation or graded-atom source recovery for this marked elliptic-addition space. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, the marked addition variety/family, compactification, divisor-class basis, Cox grading, irrelevant ideal, torsor quotient, unit normalization, and boundary policy.
2. Compute and independently verify a finite homogeneous presentation of `Cox(X)` and the universal-torsor charts without using source tuples or scalar labels as generators.
3. Lift a public fiber with output `R` to the torsor, factor its homogeneous coordinate/equation, normalize grading-torus associates, invert each surviving atom list to exact signed points of `F`, and verify their elliptic sum is `R`.
4. Apply the frozen lift to random known outputs `R_j=[r_j]P`; retain rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` verified rows have rank `B`.
5. Solve the relation system for every factor log and independently verify `[log_P(F_i)]P=F_i` for all `i`.
6. Choose fresh masks `t`, form `R_t=Q+[t]P`, and run the identical torsor lift, graded factorization, associate normalization, quotient-source inverse, and exact sum verification.
7. Combine verified factor logs to recover every candidate for `x+t`, subtract `t mod N` to unmask, and retain the entire ambiguity set.
8. Accept only `x` with `[x]P=Q`, preserving failed lifts, alternate torsor representatives, and rejected candidates.

## Full rho/BSGS cost model

Pollard rho requires expected `N^(1/2+o(1))` group operations with constant-state memory; BSGS has time and memory exponents `1/2`. Let Cox-presentation construction time/memory exponents be `c_t,c_m`, generator/relation-count exponent be `g`, factor-base exponent be `beta`, reciprocal relation/target success exponents be `delta,delta_t`, per-fiber lift/factor/quotient-inverse exponent be `f`, atom/source output exponent be `o`, unresolved torsor-orbit ambiguity exponent be `a`, linear-algebra time/memory exponents be `ell,ell_m`, and `sigma=N^o(1)`. Then

`lambda=max(c_t, g, beta+delta+f+o+a, ell, delta_t+f+o+a, beta)`

and

`mu=max(c_m, g, beta+o, ell_m, a)`.

The presentation, irrelevant ideal, all charts, factorization intermediates, units/associates, quotient fibers, rejected atoms, `B+sigma` rows, factor logs, candidate lists, and verification are charged. If finite generation needs `N^g` advice or quotient-source normalization enumerates an orbit, its complete time and storage enter the model. A local UFD speedup is insufficient unless both `lambda` and `mu` are below `1/2`.

## Likely fatal obstruction

The relevant compactified blowup/addition variety is unlikely to be a Mori dream space: the elliptic/Picard-zero contribution can make its Cox ring non-finitely generated, so there may be no finite factorial lift to compute. Even when a Cox ring is finitely generated, unique factorization in total coordinates is only up to the grading-torus action and concerns divisors/sections, not a unique tuple of quotient points. Different source tuples can have the same homogeneous product and quotient image. Retaining enough multigrading to distinguish them can make the Cox generators or quotient-source dictionary equal to the full dense incidence object.

## Proof track

Construct `X`, compute `Cl(X)`, prove that `X` is a Mori dream space with an explicit finite Cox presentation, and prove a biconditional between normalized graded factorizations and exact signed factor-base tuples. Then prove bounds on presentation size, factorization, orbit normalization, relation density, rank, descent, output, and memory that force `lambda,mu<1/2`.

## Disproof track

Prove non-finite generation, exhibit an infinite family of divisor classes needed by the relation fibers, find two distinct source tuples with the same normalized graded factorization, or show that the quotient-source inverse requires the explicit incidence table. Any source generator defined by its hidden factor log or any target-chosen Cox presentation also disproves the hypothesis.

## Positive and negative controls

- Toric varieties and rational surfaces with published finite Cox presentations and universal torsors.
- Planted factorial quotients whose homogeneous atoms have a known exact source inverse.
- The ordinary coordinate ring, toric homogenization, and same-field transfer matched for arithmetic work.
- A grading-only public-feature control and a forbidden source-indexed generator presentation.
- Exhaustive relation tuples on ordinary toy curves, including distinct tuples sharing divisor classes.
- Blind masked targets under a frozen torsor presentation, with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

The theorem gate requires a finite-generation proof, an explicit Cox presentation, a quotient-source biconditional on every chart, and symbolic `lambda,mu<=0.45`. A future toy preflight requires zero independently verified lift, source, sum, factor-log, or blind-descent errors on 20 curves at each of four increasing sizes, at least 1,000 independent rows, and 100 blind targets at each of the two largest sizes; upper 95% bounds for `c_t,c_m,g,o,a,lambda,mu` must be at most `0.45`. Falsify as written if finite generation fails, one normalized factorization has an independently reproduced source collision, or a lower 95% bound for presentation size, quotient ambiguity, `lambda`, or `mu` is at least `0.50`.

## Artifact plan

- Mori-dream and source-lift theorem: `ideas/artifacts/ECDLP-IDEA-086/mori_dream_source_lift_gate.md`
- Frozen Cox presentation: `ideas/artifacts/ECDLP-IDEA-086/cox_presentation.yaml`
- Prospective torsor factorizer: `ideas/artifacts/ECDLP-IDEA-086/torsor_factorization.sage`
- Independent quotient/source verifier: `ideas/artifacts/ECDLP-IDEA-086/verify_torsor_sources.py`
- Prospective run receipts: `ideas/artifacts/ECDLP-IDEA-086/runs/<run-id>/`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-086/analysis.md`

## Interpretation boundary

This deferred representation proposal is toy, heuristic, model-bound, and novelty-unverified. A finite presentation, factorial ring, correct quotient, valid atom factorization, or toy descent is not evidence of a generic scalar decoder, a below-rho result, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-086/mori_dream_source_lift_gate.md` computing the divisor-class/Cox finite-generation gate for the marked addition variety/family and proving either the normalized graded-atom source inverse or its quotient-collision obstruction.
