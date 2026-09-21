# ECDLP-IDEA-085 — Wonderful-diagonal valuation atomizer

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_open_stratum_no_go`
- Top lane: `conservative` relative selection; contract retired from dispatch
- Evidence scale: no run; any future preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact valuation word, valid relation, or correct toy descent is not an ECDLP break.

## Falsifiable hypothesis

Let `E(F_p)` contain a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, let `F` be a target-independent factor base of size `B=N^beta`, and let `Z_R` be the `m`-source elliptic-addition incidence fiber with output `R`. Blowing up a frozen building set of partial diagonals in the universal relation-incidence space yields a wonderful model on which every proper-transform source branch has an exceptional-divisor valuation word. The hypothesis is that those words have an exact, scalar-blind inverse to factor-base source tuples and can be generated for `B+sigma` relations and a masked target with total time and peak-memory exponents strictly below `1/2`.

## Mechanism-new operation

The proposed operation is **read the ordered exceptional-divisor valuation word of a proper-transform relation branch and invert that word to its exact source tuple**. It is not a Cremona coordinate change, toric initial form, ordinary diagonal blowup, solver substitution, or post-hoc label on an already recovered tuple. Those are controls. The formulation is rejected: iterated blowups whose centers are partial diagonals are isomorphisms over the all-distinct open stratum, so a generic source tuple acquires no exceptional valuation word at all. A successor would need a genuinely non-diagonal mathematical operation and a new versioned idea ID.

## Assumptions

1. `E,P,N` and a sign-canonical factor base `F={F_1,...,F_B}` are public, with `B=N^beta` and fixed arity `m`.
2. The universal addition-incidence scheme and all partial-diagonal centers have finite-field models whose blowup order is public and target-independent.
3. Every valid factor-base tuple in `Z_R` reaches a proper-transform branch carrying a finite exceptional-valuation word, including tuples with no repeated coordinates.
4. Distinct signed source multisets have distinct words, and a public inverse recovers indices, signs, and multiplicities without discrete-log labels.
5. Building-set construction, charts, exceptional loci, failed fibers, source ambiguity, `B+sigma` row collection, rank, factor-log solving, blind descent, output, and peak memory are fully charged.
6. The same frozen model and inverse are used for randomized relation points and masked target points.

## Semantic fingerprint

`relation_incidence_Rees_algebra | wonderful_blowup_partial_diagonals | exceptional_valuation_atom_labels | proper_transform_source_inverse | blind_descent`

The removal test is exact and fails as written: the exceptional-valuation word cannot distinguish points over an open stratum on which the blowup map is an isomorphism. Merely resolving singularities or relabelling diagonal collisions is a duplicate/control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate barrier that a valuation word must remove rather than rename.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1447`, where ordered coordinate-energy features diagnose structure but provide no exact source inverse.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1449`, the coordinate-expansion matrix dry-cell boundary and a matched source-blind control.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the conditional `m`-ary relation-cost boundary that still charges membership, rows, rank, and descent.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where an exact one-transition subgroup norm composes to a dense quadratic resultant; the wonderful valuation must change that composition, not substitute another elimination backend.

## Closest primary literature

- Li, [Wonderful compactification of an arrangement of subvarieties](https://arxiv.org/abs/math/0611412), constructs wonderful models by iterated blowups; it does not give factor-base atom labels or an inverse from exceptional valuations.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the nearby elliptic relation-incidence equations, not the proposed birational atomizer.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic-group comparison boundary.

No checked source establishes an exceptional-valuation-to-source biconditional for elliptic addition fibers. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, signs, the universal output coordinate, partial-diagonal building set, blowup order, chart atlas, valuation-word order, and exceptional-fiber policy before seeing relation or target outcomes.
2. Construct the Rees algebras and wonderful model, pull back each addition-incidence fiber `Z_R`, and compute its proper transform without enumerating `F^m`.
3. For every returned branch, extract the ordered exceptional valuations, apply the proposed inverse, and independently verify that the recovered signed tuple lies in `F^m` and sums to `R`.
4. Sample known points `R_j=[r_j]P`; retain verified sparse rows `sum_i c_{j,i} log_P(F_i)=r_j (mod N)` until exactly `B+sigma` rows have been collected and the coefficient matrix has rank `B`.
5. Solve those rows for all factor logs, then independently verify every value by `[log_P(F_i)]P=F_i`.
6. Draw fresh masks `t`, set `R_t=Q+[t]P`, run the same frozen proper-transform valuation inverse, and emit every exact factor-base decomposition of each successful masked target.
7. Combine the verified factor logs to obtain candidates for `x+t`, subtract `t mod N` to unmask, and retain the complete ambiguity list.
8. Accept only a candidate `x` satisfying `[x]P=Q`; record failures and all rejected branches.

## Full rho/BSGS cost model

Pollard rho has expected time `N^(1/2+o(1))` and constant-state memory; BSGS has time and memory `N^(1/2+o(1))`. Let wonderful-model construction time/memory exponents be `w_t,w_m`, factor-base exponent be `beta`, reciprocal relation and target success probabilities be `N^delta,N^delta_t`, per-fiber proper-transform/valuation/inverse exponent be `k`, emitted source/word exponent be `o`, target ambiguity exponent be `a`, factor-log linear-algebra time/memory exponents be `ell,ell_m`, and let `sigma=N^o(1)`. The end-to-end time exponent is

`lambda=max(w_t, beta+delta+k+o, ell, delta_t+k+o+a, beta)`.

The peak-memory exponent is

`mu=max(w_m, beta+o, ell_m, a)`.

All building-set members, charts, Rees generators, proper-transform terms, rejected branches, `B+sigma` rows, source words, candidate output, and verification work are included. If a dense row or ancestry table is materialized, its full exponent replaces the sparse term. A claimed improvement requires both `lambda<1/2` and `mu<1/2`, not merely a cheap local valuation.

## Likely fatal obstruction

Partial diagonals record coordinate collisions, whereas a generic valid factor-base decomposition has `m` distinct source points and lies in the open configuration stratum. Blowing up the usual diagonal building set therefore gives that generic tuple no source-specific exceptional word. Adding centers that distinguish all proper-transform source branches can require the full intersection lattice or one center per relevant incidence component, exponential in the building set and effectively `Theta(B^m)`. Even then, proper transform preserves all generic tuples: resolution separates singular directions but does not compress their count. Thus the exact inverse is likely either false or an explicit source table with rho-or-worse time or memory.

## Proof track

Define the universal relation-incidence arrangement and prove that a target-independent finite building set covers every source branch. Then prove a bijection between exceptional-valuation words and exact signed factor-base tuples, give the inverse algorithm, and establish symbolic bounds `w_t,w_m,k,o,a,ell,ell_m<1/2` sufficient for `lambda,mu<1/2` through full relation collection and blind descent.

## Disproof track

Exhibit two distinct all-distinct source tuples with the same valuation word, prove that the open configuration stratum meets no discriminating exceptional divisor, or lower-bound the required building set/proper-transform output by `N^(1/2)` states. Any dependence of a blowup center or inverse on factor logs, the chosen target scalar, or a previously found tuple also disproves the mechanism as written.

## Positive and negative controls

- Published wonderful models for small subvariety arrangements with explicitly checkable nested sets.
- Planted arrangements whose exceptional chains encode known source labels and admit an exact inverse.
- A single diagonal blowup, a toric degeneration, and a Cremona transform matched for ambient dimension and arithmetic work.
- Source-blind collision partitions and forbidden tuple-indexed blowup centers.
- Exhaustive signed `F^m` truth on ordinary toy curves, including all-distinct and repeated-source tuples.
- Blind masked targets with the model frozen in advance, plus matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

No active promotion gate remains. The formulation is falsified by the generic
all-distinct open stratum: partial-diagonal blowups are isomorphisms there, so its points
have no source-specific exceptional valuation. A versioned successor would have to add a
genuinely non-diagonal, target-independent operation, prove a complete source
biconditional, and derive symbolic `lambda,mu<=0.45` before any toy run. It would then
require zero independently verified source or sum errors over 20 curves at each of four
increasing sizes, at least 1,000 independent rows, and 100 blind targets at each of the
two largest sizes, with upper 95% bounds for all complete time and memory exponents at
most `0.45`.

## Artifact plan

- Geometry and source-inverse theorem: `ideas/artifacts/ECDLP-IDEA-085/wonderful_source_inverse.md`
- Frozen building-set specification: `ideas/artifacts/ECDLP-IDEA-085/building_set.yaml`
- Prospective prototype: `ideas/artifacts/ECDLP-IDEA-085/valuation_atomizer.sage`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-085/verify_valuation_sources.py`
- Prospective run receipts: `ideas/artifacts/ECDLP-IDEA-085/runs/<run-id>/`
- Cost and gate analysis: `ideas/artifacts/ECDLP-IDEA-085/analysis.md`

## Interpretation boundary

This rejected formulation is toy, heuristic, model-bound, and novelty-unverified. The
open-stratum argument is a scoped no-go for partial-diagonal wonderful atomization, not a
general ECDLP result. Correct blowups, a valid valuation word on collision strata, a
resolved singularity, a verified relation, or a correct toy target descent is not
evidence of a below-rho improvement or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-085/wonderful_source_inverse.md` formalizing the open-stratum isomorphism and proving that partial-diagonal exceptional valuations cannot label generic all-distinct factor-base tuples.
