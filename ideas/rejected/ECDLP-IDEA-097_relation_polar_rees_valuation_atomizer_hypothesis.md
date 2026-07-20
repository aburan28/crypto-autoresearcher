# ECDLP-IDEA-097 — Relation-polar Rees-valuation atomizer

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_generic_etale_no_go`
- Top lane: `-`
- Evidence scale: semantic/theorem screen only; no run; any future computation would be `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct blowup, Rees valuation, branch label, relation, or toy descent is not an ECDLP break.

## Falsifiable hypothesis

Let `X -> Z` be a target-independent source-labelled-to-eliminated relation projection for signed `m`-term additions from a factor base `F` of size `B=N^beta`. Blow up and normalize the Rees algebra of the relative Jacobian ideal, equivalently the specified Fitting ideal of relative differentials, of this projection. The hypothesis is that the resulting divisorial valuations give a finite target-computable word that is biconditional with every exact factor-base source tuple, including generic all-distinct tuples, and that these words can produce `B+sigma` full-rank rows and blind target descents with complete time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **normalize the blowup of the relation projection's ramification-sensitive ideal and invert its Rees-valuation word to exact sources**. Unlike ECDLP-IDEA-085, the center is not a union of partial diagonals; it is the specified relative Jacobian/Fitting ideal defined from relative differentials. An independently defined polar ideal is outside this scoped formulation. Ordinary diagonal blowups, a Nash resolution with no source inverse, dense resultants, solver substitutions, or valuations attached after a tuple is known are controls.

The formulation is rejected after the theorem screen. On the generic all-distinct locus where a finite source projection is étale, the specified relative Jacobian/Fitting ideal is the unit ideal and its blowup is an isomorphism. Its Rees valuations therefore live on the branch/discriminant locus and cannot label generic accepted tuples. This unit-ideal claim does **not** apply automatically to an arbitrary polar ideal: a polar-center variant would need a versioned successor that specifies its ideal and separately proves both nontrivial generic support and a source inverse. Enlarging the present center until it distinguishes étale sheets requires source components or an equivalent source table, restoring the recorded obstruction.

## Assumptions

1. `E(F_p)` contains a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`; `F={F_1,...,F_B}` is deterministic, target-independent, sign-canonical, and has `B=N^beta`.
2. A fixed arity `m` and a finite source-labelled relation scheme `X` project to a compact eliminated state space `Z`, with all exceptional charts and multiplicities included.
3. A target-independent relative Jacobian/Fitting ideal `J` can be constructed without enumerating `F^m`, using factor logarithms, or seeing a target scalar; no unit-ideal conclusion is assumed for separately defined polar ideals.
4. The normalized blowup `Proj(overline{oplus_n J^n t^n})` has a finite ordered Rees-valuation alphabet covering generic all-distinct, repeated-source, ramified, and boundary branches.
5. Distinct signed source multisets have distinct public valuation words and a complete inverse recovers indices, signs, and multiplicities.
6. Rees-algebra construction, normalization, charts, branch failures, word output, source inversion, `B+sigma` rows, rank, factor-log solving, blind descent, ambiguity, verification, and peak memory are fully charged.

## Semantic fingerprint

`relation_projection_relative_Jacobian_Fitting_ideal | normalized_Rees_blowup | exceptional_branch_valuation_word | exact_source_biconditional | blind_descent`

The removal test is strict: a genuinely new operation must create source information on the generic étale all-distinct locus. Replacing partial diagonals by another ideal supported only on the discriminant, or adding source-labelled components to the center, is respectively ineffective or an explicit source table.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier that any compact relation-sensitive valuation must remove rather than rename.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1449`, the coordinate-expansion dry-cell boundary against treating an unexecuted compact feature map as evidence.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, where exact aggregate row norms still do not recover source ancestry or promote.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact sparse one-transition invariant becomes a dense quadratic object under composition.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the closest exact affine-pencil/secant control whose valid identities do not themselves atomize sources.

## Closest primary literature

- Duarte, Jeffries, and Nunez-Betancourt, [Nash blowups of toric varieties in prime characteristic](https://arxiv.org/abs/2208.05599), identifies a prime-characteristic logarithmic Jacobian ideal whose blowup realizes the Nash blowup in the toric setting; it does not give branch-to-factor-base source inversion.
- Heinzer and Kim, [The Rees Valuations of Complete Ideals in a Regular Local Ring](https://arxiv.org/abs/1404.1524), studies when complete ideals have one or several Rees valuations; it does not make those valuations labels for generic sheets of an elliptic relation projection.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring relation projection but not the proposed non-diagonal atomizer.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic square-root comparison boundary.

No checked primary source establishes a Rees-valuation/source biconditional on generic elliptic-addition fibers. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, the labelled relation scheme `X`, eliminated state space `Z`, projection, ideal `J`, normalization order, chart atlas, valuation ordering, source inverse, and exceptional-fiber policy.
2. Construct and independently check the Rees algebra and normalized blowup without enumerating the source fiber; for a public output `R`, compute every returned valuation word.
3. Apply the proposed inverse to each word and independently verify every recovered signed point is in `F`, including sign and multiplicity, and that its elliptic sum equals `R`.
4. For known random outputs `R_j=[r_j]P`, retain verified sparse rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have been collected and their coefficient matrix has rank `B`.
5. Solve for all factor-base logarithms and independently verify `[log_P(F_i)]P=F_i` for every `i`.
6. Choose fresh masks `t`, form blind descent targets `R_t=Q+[t]P`, and apply the identical frozen blowup, valuation-word extraction, source inverse, and sum verification.
7. Substitute verified factor logs to recover every candidate for `x+t`, subtract `t mod N`, retain the full ambiguity set, and accept only `x` satisfying `[x]P=Q`.
8. Preserve empty fibers, branch-only words, source collisions, rejected candidates, and all charged intermediate sizes.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` with constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let `B=N^beta`; Rees-ideal/blowup construction time and memory be `N^a,N^am`; normalization/chart state be `N^g`; reciprocal relation and target success probabilities be `N^delta,N^delta_t`; per-fiber valuation computation and inverse be `N^k`; emitted word/source and ambiguity exponents be `o` and `u`; and factor-log linear-algebra time and memory be `N^ell,N^ell_m`. The complete time exponent is

`lambda=max(a,g,beta+delta+k+o,ell,delta_t+k+o+u,beta)`,

and the peak-memory exponent is

`mu=max(am,g,beta+o,ell_m,u)`.

All ideal generators, integral closures, affine charts, exceptional divisors, branch tests, failed fibers, `B+sigma` rows, source words, output candidates, and verification are charged. If source-sensitive centers, normalization, or the word dictionary has one state per relation branch, its full exponent enters `g`, `o`, or `mu`. Promotion would require both `lambda<1/2` and `mu<1/2`; a cheap valuation on a sparse discriminant does not count.

## Likely fatal obstruction

For a generically separable finite source projection, the relative differentials vanish and the specified Fitting/Jacobian ideal is invertible on the étale locus. Its blowup and normalization therefore change only ramified fibers. Generic all-distinct factor-base tuples lie on separate étale sheets with no exceptional valuation distinguishing them. This is not a no-go theorem for every ideal called "polar": any different polar center must be analyzed from its exact definition. For the present center, a refinement by closures of the étale sheets must already distinguish source components, so its generators or charts encode the dense incidence object it was meant to compress.

## Proof track

Construct the exact finite projection and prove that a target-independent non-unit ideal has normalized Rees valuations on a positive-density generic all-distinct locus. Prove a bijection between finite words and exact signed factor-base tuples, give a scalar-blind inverse, and bound ideal construction, normalization, output, relation collection, rank, factor logs, blind descent, and memory so that `lambda,mu<1/2`.

## Disproof track

Prove the projection is étale over the generic accepted all-distinct locus and that the specified relative Jacobian/Fitting ideal is the unit ideal there; exhibit two distinct source sheets with identical valuation data; or prove any discriminating refinement needs one generator/chart per source component. Any tuple-indexed center, factor-log-labelled valuation, or target-scalar-dependent normalization also disproves the mechanism. A result about an unrelated polar ideal neither proves nor disproves this scoped formulation without an explicit comparison of the two ideals.

## Positive and negative controls

- Published toric Nash-blowup and complete-ideal examples with independently calculable Rees valuations.
- A planted ramified finite cover whose exceptional valuations genuinely distinguish its known branches.
- The same cover restricted to an étale open set, where the blowup must return no branch-specific exceptional labels.
- ECDLP-IDEA-085 partial-diagonal blowups, dense elimination, and source-indexed centers matched for arithmetic work.
- Exhaustive ordinary toy-curve relation fibers split into all-distinct, repeated-source, ramified, and boundary strata.
- Blind masked targets under a frozen construction, with complete candidate output and matched rho/BSGS accounting.

## Quantitative promotion and falsification gates

No active promotion gate remains for this rejected formulation. A versioned successor must first prove nontrivial source-biconditional valuations on a positive-density all-distinct open set without source-labelled centers and derive symbolic `a,am,g,o,u,lambda,mu<=0.45`. Any later toy preflight would require zero independently verified word/source/sum/factor-log/descent errors over 20 curves at each of four increasing sizes, at least 1,000 independent rows, and 100 blind descents at each of the two largest sizes. Falsify after one reproduced pair of distinct source sheets with identical valuation data, proof that the ideal is invertible on the accepted open locus, or a lower 95% bound `>=0.50` for construction, source output, complete time, or memory.

## Artifact plan

- Generic-etale no-go proof: `ideas/artifacts/ECDLP-IDEA-097/generic_etale_rees_no_go.md`
- Frozen projection and ideal specification: `ideas/artifacts/ECDLP-IDEA-097/relation_polar_spec.yaml`
- Prospective valuation prototype: `ideas/artifacts/ECDLP-IDEA-097/relation_polar_rees.sage`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-097/verify_rees_sources.py`
- Complete cost analysis: `ideas/artifacts/ECDLP-IDEA-097/analysis.md`
- Any future receipts: `ideas/artifacts/ECDLP-IDEA-097/runs/<run-id>/`

## Interpretation boundary

This rejected representation-changing record is toy, heuristic, model-bound, and novelty-unverified. The étale-locus argument is a scoped no-go for the specified relative Jacobian/Fitting Rees atomization, not for arbitrary polar ideals and not a general ECDLP impossibility. A valid ideal, normalized blowup, exceptional valuation, exact ramified-branch label, relation, or correct toy scalar is not evidence of a below-rho algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-097/generic_etale_rees_no_go.md` proving that the specified relative Jacobian/Fitting ideal is invertible on the generic all-distinct étale relation locus and therefore yields no source-specific Rees valuations there, without extending the claim to arbitrary polar ideals.
