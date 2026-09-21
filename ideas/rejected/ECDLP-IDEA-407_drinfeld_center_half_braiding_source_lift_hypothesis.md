# ECDLP-IDEA-407 — Drinfeld-center half-braiding source lift

## Status and claim labels

- Class: `monoidal_center_source_lift`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_monoidal_category_encodes_incidence_and_center_data_forget_occurrence_labels`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct center, half-braiding, or modular datum is not an ECDLP break.

## Falsifiable hypothesis

A target-independent monoidal category of partial elliptic relations has a compact Drinfeld center whose half-braidings separate all signed factor occurrences, so decomposing an endpoint central object and forgetting back to the source category canonically returns a relation and fresh-target descent.

## Mechanism-new operation

The screened operation is **form the monoidal category of partial correspondences, compute its Drinfeld center of objects with coherent half-braidings, split an endpoint object into central simples, and invert the forgetful image to exact factor occurrences**. The proposed primitive is categorical centering, not a character-table or fusion-solver substitution.

## Assumptions

1. Objects, morphisms, tensor product, associators, and duals are endpoint-constructible without source enumeration.
2. The center and its simple/half-braiding data have subgate size and exact finite-field arithmetic.
3. Central decomposition retains occurrence labels, signs, repetitions, and pairing across restrictions.
4. The forgetful inverse is canonical rather than an isomorphism class or gauge choice.
5. Category construction, center, half-braidings, decomposition, inverse, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`partial_relation_monoidal_category | Drinfeld_center_construction | coherent_half_braiding_simple_split | central_object_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; endpoint objects must return exact restricted sources.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; a source-labelled category is charged as advice.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; modular or central transforms must compress the complete state.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; coherent phase and orientation remain charged.
5. `inputs/ledger_inventory.json` — imported `P1479`; every restriction must reuse the same categorical data.

## Closest primary literature

- Joyal and Street, [Braided tensor categories](https://doi.org/10.1006/aima.1993.1055), develops braided/central categorical structure from supplied monoidal categories.
- Müger, [From subfactors to categories and topology II](https://arxiv.org/abs/math/0111205), studies the Drinfeld center and its simple objects for supplied tensor categories.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives relation equations without a compact monoidal source category.

No checked source constructs the proposed elliptic category and occurrence-faithful center inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, category, tensor/associator data, center convention, simple decomposition, restrictions, and verifier.
2. Construct target-independent category and center within `B^(9/4+o(1))` without one object or morphism per source tuple or transition.
3. For known-log targets, form the endpoint central object, restrict it, split it, invert one summand to an occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging zero objects, gauge/isomorphism ambiguity, output, and dependent rows; solve factor logs.
5. Apply the unchanged center and inverse to fresh scalar-blind `Q+[t]P` targets.
6. Substitute factor logs, remove `t`, retain all categorical/gauge branches, and verify `[x]P=Q`.
7. Charge category/center construction, half-braidings, decomposition, inverse, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

The Drinfeld center begins with a supplied monoidal category and coherent tensor data. A category whose simples or morphisms distinguish factor occurrences already materializes the source alphabet. Central objects and modular data normally classify isomorphism/orbit types, while the forgetful functor has no canonical inverse to labelled representatives. This meets IDEAs 072, 108, 127, 183, 225, and 305 at the category-versus-occurrence boundary.

## Proof track

Construct a compact endpoint-only monoidal category, prove a bounded center with restriction-stable occurrence separation and canonical inverse, and certify `lambda,mu<=0.45`.

## Disproof track

Show one object/morphism/half-braiding encodes source incidence, exhibit equal central data with different occurrences, or prove category/center state above the caps.

## Positive and negative controls

- Positive: supplied finite fusion categories with known centers, simples, and labelled forgetful images must replay exactly.
- Negative: gauge-equivalent half-braidings, equal central characters with distinct simples, relabelled source objects, signed strata, restrictions, and blind targets.
- Baselines: IDEAs 072/108/127/183/225/305, explicit source categories, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only compact category, exact central occurrence inverse, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing morphism, equal-center/different-source collision, noncanonical inverse, cap violation, or either exponent at least `0.50`.
- A correct toy center computation is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-407/drinfeld_center_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-407/half_braiding_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-407/restricted_central_lift_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-407/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic Drinfeld-center route, not center theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; categorical correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-407/drinfeld_center_source_obligations.md` and classify every object, morphism, tensor datum, half-braiding, simple label, and inverse by endpoint versus source dependence.
