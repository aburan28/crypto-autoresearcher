# ECDLP-IDEA-122 — Maltsev few-subpowers addition CSP

## Status and claim labels

- Class: `constraint-algebra`
- Risk band: `conservative`
- State: `rejected_factor_base_breaks_required_maltsev_invariance`
- Evidence scale: structural preflight only; no experiment ran
- Scale labels: any prospective run would be `toy`; all complexity claims are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; polynomial CSP propagation, a valid relation, or a correct toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The recursive elliptic addition relation together with factor-base membership admits a public Maltsev polymorphism and a few-subpowers generating-set representation, allowing all five-source solutions for a target to be propagated and decoded without enumerating pair or triple states. The hypothesis is falsified if the frozen factor-base predicate is not invariant under the same Maltsev term or if compact subpower generators do not invert to exact sources.

## Mechanism-new operation

The proposed operation is **factor-base-preserving Maltsev closure with exact source decoding**: compile the projective addition chain as a finite-domain CSP, maintain compact generators for every projected solution relation, and reconstruct signed source tuples by the Maltsev term `m(x,y,z)=x-y+z`. This would differ from a solver substitution only if one proves invariance of every curve, addition, sign, infinity, and factor-base constraint and charges the complete generator-to-source expansion.

The preflight rejects the declared operation by an exact coset theorem, not merely a genericity argument. If a nonempty subset `A` of an abelian group is closed under `m(x,y,z)=x-y+z`, then for any `a in A`, the translate `A-a` contains zero and is closed under subtraction and addition, hence is a subgroup; therefore `A` is a coset. In the prime-order group `<P>`, `A` is consequently a singleton or the whole group. A factor base of size `B=N^(1/5+o(1))` can be neither. Dropping its unary constraint solves a different dense group relation and is only a control.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and target-independent factor base `F` of size `B=N^beta`.
2. The five-source recursive addition chain has a complete projective finite-domain encoding including signs, infinity, repeated points, and denominator-zero cases.
3. One public Maltsev term preserves the graph of addition and every unary factor-base predicate used at all five leaves.
4. Powers of the resulting constraint algebra have polynomial-size generating sets constructible without enumerating `F^2`, `F^3`, or relation fibers.
5. Generator membership and extension yield every exact signed source tuple with multiplicity, not only satisfiability or a relation certificate.
6. Compilation, generator growth, propagation, branching, source output, relation collection, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`projective_addition_CSP | factor_base_preserving_Maltsev_term | few_subpowers_generators | exact_tuple_extension | blind_descent`

The removal test is simultaneous Maltsev invariance of addition and factor-base membership plus a charged exact source inverse. A generic SAT/SMT/Grobner backend, altered encoding, parameter change, post-hoc source table, or satisfiability-only certificate is a duplicate or control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H640`, which leaves explicit sign/orientation constraints or a genuinely different symbolic backend open; a Maltsev algebra would qualify only with a proved invariant language.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H641`, where symbolic `S5` or a different factor-base generator is the surviving branch after tested decompositions; few-subpowers must change the algebra, not the solver name.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H675`, which asks whether coordinate predicates and recursive addition features induce exact source-resolving structure; the Maltsev preservation test is the precise version here.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1416-EXPLICIT-S3-NO-PROMOTION`, which closes tested interval, residue, rational-map, composition, union, and hash bases under enumeration but not an actually invariant CSP language.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1480`, where a bit-vector serial-`S3` compilation times out and fails the completeness gates; changing to CSP algorithms helps only if the missing polymorphism theorem holds.

## Closest primary literature

- Bulatov and Dalmau, [A Simple Algorithm for Maltsev Constraints](https://doi.org/10.1137/050628957), give a polynomial algorithm for constraint languages already invariant under a Maltsev operation; they do not show that sparse elliptic factor bases have that invariance.
- Idziak, Markovic, McKenzie, Valeriote, and Willard, [Tractability and Learnability Arising from Algebras with Few Subpowers](https://doi.org/10.1137/090775646), develop the compact-subpower criterion; it does not supply a source-biconditional elliptic encoding.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), provides the neighboring addition relations but no Maltsev-preserved factor-base language.

No checked primary source proves the conjunction required here. Novelty remains unverified, and the generic sparse-factor-base version is structurally rejected.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, the five signed leaves, projective addition constraints, repeated/infinity policies, and a candidate Maltsev term.
2. Prove preservation of every basic constraint, especially unary membership in `F`, by exhaustive symbolic identities rather than sampled tuples.
3. Construct few-subpowers generators for target fibers without enumerating pair/triple states, and extend them to every exact signed five-source tuple.
4. Independently verify each tuple by curve membership, factor-base membership, and elliptic addition; preserve duplicates and missed multiplicities.
5. Query known multiples `[r_j]P` until `B+sigma` verified rows have rank `B`, charging every failed fiber and generator expansion.
6. Solve factor-base logarithms and independently verify every point/log pair.
7. Apply the identical blind CSP to `Q+[t]P`, substitute factor logs, subtract `t`, and retain all candidates.
8. Accept only `[x]P=Q` and report complete time, memory, generator, output, rank, factor-log, and descent receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant-state memory; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; CSP compilation time/memory be `N^a,N^a_m`; maximum few-subpowers generator construction and state be `N^s,N^s_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; propagation, source extension, and exact verification per query be `N^k`; source and target ambiguity exponents be `o,u`; and factor-log linear-algebra time/memory be `N^ell,N^ell_m`. Then

`lambda=max(a,s,beta+delta+k+o,ell,delta_t+k+o+u,beta)`

`mu=max(a_m,s_m,beta+o,ell_m,u)`.

The exponent model charges construction of the full constraint language, all generators, failed branches, source tuples, `B+sigma` rows, factor logs, and blind descent. Polynomial time in an explicitly listed domain of size `N` is not automatically sub-rho.

## Likely fatal obstruction

Maltsev tractability is a property of the complete constraint language. Although the elliptic group operation itself has a Maltsev term, closure of a nonempty factor base `A` under `X-Y+Z` forces `A-a` to be a subgroup. Because `<P>` has prime order, the only possibilities are `|A|=1` and `|A|=N`; the required `|A|=N^(1/5+o(1))` is impossible. Taking the Maltsev closure therefore expands a nontrivial sparse factor base to the whole subgroup and destroys relation density; encoding membership outside the invariant language restores arbitrary CSP difficulty or an explicit source table. Even an invariant satisfiability representation would still need a complete output-sensitive tuple inverse.

## Proof track

Historic survival would require a nontrivial factor-base family of size `N^beta` preserved by the same Maltsev term as elliptic addition, polynomial-size subpower generators, a complete source-extension theorem, and `lambda,mu<=0.45` through blind descent. The coset theorem makes the preservation premise impossible at `beta=1/5` in a prime-order group, so this proof track is closed unless a different algebra and operation change the mathematical object under a new ID.

## Disproof track

Apply the coset theorem to show that a nonempty Maltsev-closed `F` in `<P>` has size `1` or `N`, contradicting `B=N^(1/5+o(1))`; alternatively prove any proposed different Maltsev term fails an addition constraint, or lower-bound generator/source output at `N^(1/2)`. The coset-size contradiction is already a decisive rejection for the declared group-term mechanism.

## Positive and negative controls

- Linear equations over a finite abelian group with the full group as domain, where `x-y+z` is a genuine Maltsev positive control.
- A planted coset factor base closed under the term, kept explicitly toy and compared with a size-matched random sparse factor base.
- Frozen coordinate, interval, residue, and matched-hash factor bases from the ledger, with exhaustive closure counterexamples.
- The same projective addition CSP without unary factor-base constraints to show that solving the dense group relation is not source descent.
- Bit-vector `P1480`, SAT, and direct enumeration controls with identical output and memory charging.
- Blind known-log targets and independent tuple/scalar verification.

## Quantitative promotion and falsification gates

This record is rejected for the frozen generic sparse factor-base setting. Historic promotion would have required exact symbolic invariance, generator size and construction exponents at most `0.45`, `100%` exhaustive toy source recall, zero false tuples, and complete `lambda,mu<=0.45` accounting. One preservation counterexample, a closure hull larger than `N^0.45`, any source table, missed tuple, or time/memory exponent at least `0.5` falsifies the mechanism.

## Artifact plan

- Preservation theorem/counterexample plan: `ideas/artifacts/ECDLP-IDEA-122/maltsev_preservation_gate.md`
- Prospective toy language fixture: `ideas/artifacts/ECDLP-IDEA-122/csp_fixture.json`
- Prospective closure checker: `ideas/artifacts/ECDLP-IDEA-122/check_polymorphism.py`
- Prospective independent source verifier: `ideas/artifacts/ECDLP-IDEA-122/verify_sources.py`
- Complete cost worksheet: `ideas/artifacts/ECDLP-IDEA-122/cost_analysis.md`

These are prospective paths only; no artifact or experiment was created.

## Interpretation boundary

This is a rejected, novelty-unverified structural preflight. Its hypothetical complexity is heuristic and model-bound; any evidence would begin at toy scale. The rejection closes only the declared factor-base-preserving Maltsev/few-subpowers operation for generic sparse public factor bases. It does not prove general ECDLP hardness, and satisfiability or a valid relation would not be a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-122/maltsev_preservation_gate.md` with a symbolic preservation proof obligation and one exhaustive generic-factor-base counterexample family, then keep the idea rejected unless a new closed factor-base algebra survives without exceeding the `0.45` cost gates.
