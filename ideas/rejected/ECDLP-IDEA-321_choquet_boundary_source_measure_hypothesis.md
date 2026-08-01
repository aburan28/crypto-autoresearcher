# ECDLP-IDEA-321 — Choquet-boundary source measure

## Status and claim labels

- Class: `convex_representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_choquet_measure_is_nonunique_and_extreme_dictionary_is_source_deck`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an extreme-point measure, valid relation, or toy decomposition is not an ECDLP break.

## Falsifiable hypothesis

A public convex lift sends each relation endpoint to a compact simplex whose Choquet boundary is canonically the signed factor deck, and its unique representing measure has sparse support that returns exact factors with complete exponents at most `0.45`.

## Mechanism-new operation

The screened operation is **lift the endpoint to a compact convex set, represent it by a boundary-supported Choquet measure, and read exact factor points from the measure's extreme support**. This is not merely linear programming: the conjectured gain is a canonical boundary measure on a simplex-like lift. In general Choquet representations are nonunique outside a simplex, and specifying the extreme boundary or point evaluation map is the source dictionary. It merges with IDEAs 104, 125, 143, 282, and 289.

## Assumptions

1. A target-independent real or nonarchimedean convex lift of finite-field endpoint data is canonical and scalar-blind.
2. The lifted feasible set is a compact simplex or has a unique relevant boundary measure.
3. Boundary extreme points map canonically and exactly to signed finite-field factor points on every stratum.
4. Lift precision, boundary construction, measure recovery, support output, relation density, rank, factor logs, descent, verification, and memory are charged.
5. The same lift and boundary inverse apply to fresh masked targets.

## Semantic fingerprint

`finite_field_endpoint_convex_lift | Choquet_boundary_measure | unique_sparse_extreme_support | exact_factor_point_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed batch source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-support boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the tested source-deck compression boundary.

## Closest primary literature

- Bishop and de Leeuw, [The representations of linear functionals by measures on sets of extreme points](https://doi.org/10.5802/aif.95), gives boundary-supported representing measures for supplied compact convex structures without guaranteeing a unique atomic source labelling.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), does not supply a simplex lift or exact boundary-to-point map.

No checked source constructs the required canonical finite-field convex lift, unique sparse measure, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed factor decks, convex lift, ambient topology/precision, boundary convention, measure normalization, masks, and verifier.
2. On known-log endpoints, build the lift without sources, recover a unique boundary measure, map its support to exact signed points, and verify every relation.
3. Collect independent rows, solve all factor-base logarithms, and independently verify them.
4. Apply the identical lift and measure inverse to fresh `Q+[t]P` endpoints with no source-labelled extreme list.
5. Substitute logs, remove masks, retain all measure/support ambiguity, and return scalar candidates.
6. Accept only `[x]P=Q`, charging lift, precision, boundary, optimization, support output, rank, factor logs, descent, verification, and peak memory.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one lift/measure/source inverse `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Precision, all extreme candidates, nonunique measures, and exact support certification are included. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Choquet theory represents points relative to a supplied compact convex set and boundary. Generic convex sets admit multiple representing measures; uniqueness requires simplex structure not provided by elliptic addition. A lift whose extreme points are already factor points includes the factor deck, while an aggregate lift has no canonical exact point-support inverse and may not even exist naturally over finite fields.

## Proof track

Prove a canonical scalar-blind lift, simplex/unique-measure theorem, exact all-strata boundary-to-point map, sub-rho construction and support recovery, sufficient rank, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Exhibit two boundary measures for one endpoint with different point supports, show that the extreme dictionary materializes the source deck, or prove lift/precision/output or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied finite simplices with planted vertices must recover their unique barycentric measures.
- Negative: nonsimplicial polytopes with equal points and different extreme decompositions must retain ambiguity.
- Baselines: IDEAs 104/125/143/282/289, P1434, Carathéodory enumeration, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a unique all-strata factor measure, 1,000 verified rows and 100 blind descents per large future toy size, and both complete exponents at most `0.45`.
- Falsify on one equal-endpoint/different-support measure pair, source-labelled extreme input, or lift/state/output or either exponent at least `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-321/choquet_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-321/nonunique_measure_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-321/independent_choquet_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-321/cost_analysis.md`

## Interpretation boundary

This is a scoped rejection of the stated Choquet source measure, not of convex methods. A correct measure representation, relation, or toy decomposition is not scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-321/choquet_source_theorem.md` proving a canonical simplex lift or an equal-endpoint/different-boundary-support collision.
