# ECDLP-IDEA-357 — Exterior-algebraic shifted source complex

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_noninvertible_source_complex_transform`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a shifted complex or preserved Betti number is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation simplicial complex has an endpoint-derived exterior generic initial ideal whose restricted shifted complex decides exact face nonemptiness inside the P1553 gates.

## Mechanism-new operation

The screened operation is **take the exterior generic initial ideal of the source relation complex, update it under source-deck restrictions, and decide exact accepted-face nonemptiness**. It is distinct only if the shifted ideal is built without the face list and restrictions preserve exact support rather than only aggregate Hilbert data.

Minimum-interface correction: a canonical facet inverse is unnecessary. A target-labelled, subset-stable exact face-existence bit under arbitrary dyadic deck restrictions, with `O(log B)` charged ideal updates, suffices to recover one facet.

## Assumptions

1. The relation complex and exterior ideal are constructed directly from endpoint equations.
2. Generic shifting compresses rather than merely rearranges degree-five faces.
3. Restricted shifted state preserves exact zero-versus-nonzero, so bisection recovers one factor-labelled facet without an ancestry dictionary.
4. Target updates and all source strata preserve the inverse.
5. Ideal construction, basis change, facets, inverse, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`endpoint_relation_simplicial_complex | exterior_generic_initial_ideal | strongly_stable_shifted_facets | subset_stable_exact_face_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the endpoint-derived exact source complex or circuit is the missing operation.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public arithmetic source-fibre generation remains unresolved.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless source ancestry survives exact transformations.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; transformed exact source state remained full rank.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; exact source terminals retain the witness surface.

## Closest primary literature

- Aramova, Herzog, and Hibi, [Shifting operations and graded Betti numbers](https://doi.org/10.1023/A:1011238406374), defines algebraic shifting and studies Hilbert/Betti information; it does not give pointwise facet inversion.
- Hibi and Murai, [Algebraic shifting and graded Betti numbers](https://arxiv.org/abs/math/0503685), studies aggregate graded behavior rather than labelled source ancestry.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives a relation predicate rather than its compact face ideal.

The checked generic-initial constructions use an infinite-field generic change of basis, with some Betti comparisons stated in characteristic zero. No checked source provides an `F_p`-native constructor, a charged extension/descent substitute, or subset-stable endpoint-only decisions; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, relation complex, exterior algebra, generic basis rule, inverse, masks, and verifier.
2. Construct target-independent shifted state or a bounded target update without enumerating faces.
3. Query restricted accepted-face existence for known-log targets, bisect to one facet, and replay the tuple.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Repeat the identical construction and inverse on fresh masked targets.
6. Substitute logs, remove masks, retain ambiguity, and verify `[x]P=Q`.
7. Charge face/ideal construction, basis state, shifted facets, inverse ancestry, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(1/5)` and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,1/5+delta+q-r+o,ell,delta_t+q+o+u,1/5)`

`mu=max(a_m,q_m,1/5+o,ell_m,u)`.

Require `0<=r<=o`, setup/state `<=B^(9/4)`, query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time are exponent `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

Algebraic shifting starts from the face ideal, whose endpoint-only construction is already unsupplied, and preserves aggregate f/Hilbert data rather than exact restricted support. Degree-five source monomials can total `Theta(B^5)`. Noninvertibility of a generic-initial degeneration rules out a direct facet lift but is not alone fatal to a decision route. The audited exact restricted-support updater either materializes the face ideal or retains source-sized basis/ancestry; no bounded correction is constructed.

## Proof track

Construct the shifted ideal from endpoint equations, prove subset-stable exact face decisions plus bisection on all strata, and derive complete sub-gate costs.

## Disproof track

Find a restricted-complex family with identical available shifted state but different exact face nonemptiness and no sub-gate correction, prove face-ideal materialization is necessary, or show restriction updates need source-sized basis/ancestry state.

## Positive and negative controls

- Positive: a supplied small shellable complex with a known facet dictionary.
- Negative: differently labelled complexes with identical shifted ideals and Hilbert functions.
- Baselines: IDEAs 073/098/151/234/346, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only constructor, subset-stable exact face decisions plus charged bisection, zero source errors, 1,000 rows, 100 blind descents, and complete gates at most `0.45`.
- Falsify on an equal-shift/different-source family whose every public correction or facet section exceeds the gates, required face materialization, source-sized basis lift, or exponent at least `0.50`.
- A preserved Hilbert function, Betti number, or toy facet cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-357/shift_noninjectivity_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-357/equal_shift_source_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-357/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-357/cost_analysis.md`

## Interpretation boundary

This rejects the source-invertible adaptation, not algebraic shifting. All checks would be toy, heuristic, model-bound, and novelty-unverified. Aggregate preservation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-357/equal_shift_source_collisions.json` with source-labelled toy complexes whose unrestricted shifts agree but whose dyadically restricted exact face-nonemptiness answers differ, then charge any correction.
