# ECDLP-IDEA-348 — Frieze–Kannan cut-decomposition source router

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_cut_approximation_hides_rare_exact_relations_in_residual`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an accurate cut approximation or valid routed relation is not an ECDLP break.

## Falsifiable hypothesis

The implicit pair-incidence matrix of complementary partial sums has a short public Frieze–Kannan cut decomposition whose rectangles route every exact relation source, including the residual, to a sub-gate exact peeling procedure.

## Mechanism-new operation

Use the convention that a valid relation entry is `1`. The screened operation is **replace the hidden pair-incidence matrix by a weak-regularity sum of cut rectangles, route candidate sources through those rectangles, and exactly peel the residual**. It is distinct only if the decomposition and residual oracle are built without materializing pair incidences and if rare relation entries cannot hide in the approximation error. Otherwise it is a rectangle/table partition or aggregate approximation control.

## Assumptions

1. Cut queries and rectangle witnesses are evaluated from public coordinates without enumerating the pair matrix.
2. Every exact relation source lies in an explicitly routed rectangle or an exactly searchable small residual.
3. Approximation error cannot erase rare `1` relation entries, introduce false sources, or merge provenance.
4. Rectangle overlap, singular, repeated, infinity, signed, and ambiguous strata are exact.
5. Decomposition construction, routing, residual peeling, output, rank, logs, blind descent, and memory are charged.

## Semantic fingerprint

`pair_incidence_matrix | Frieze_Kannan_cut_decomposition | rectangle_candidate_router | exact_residual_source_peeling | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where a compact linear view does not report sources.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the missing nonlinear full-phase composition boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the exact all-strata source-faithfulness obligation.
4. `inputs/ledger_inventory.json` — imported `P1478`, the compact transition and dense-composition boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where lossless compact routing restores source-labelled edges.

## Closest primary literature

- Frieze and Kannan, [Quick approximation to matrices and applications](https://doi.org/10.1007/s004930050052), proves weak-regularity approximations in cut norm; it does not preserve every rare relation entry or hidden source.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies exact endpoint equations but no cut-query or exact residual oracle.

No checked source supplies an exact source-faithful cut router; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, implicit incidence definition, cut oracle, decomposition rule, residual peeler, and verifier.
2. Build the decomposition for known-log relation collection without materializing pair incidences.
3. Route rectangles, peel the complete residual, recover exact tuples, replay them, and verify relations.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Rebuild or update the identical representation for fresh scalar-blind masked targets.
6. Recover target tuples, substitute logs, remove masks, retain ambiguity, and verify `[x]P=Q`.
7. Charge cut queries, rectangles, routing, residual work, output, rank, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, routed query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every cut query, stored rectangle, overlap, residual entry, output tuple, and bit is charged; `0<=r<=o`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`. Promotion requires complete exponents at most `0.45`.

## Likely fatal obstruction

Cut decomposition controls aggregate rectangle error, not exact rare entries. A valid `1` relation entry can sit entirely in the residual while the approximation remains excellent. Making rectangles disjoint and source-exact restores a labelled incidence partition; searching every residual or materializing its witnesses recovers the same pair-table and source-state costs already recorded by the rectangle and tensor controls.

## Proof track

Give a sub-gate cut oracle, prove every exact `1` relation entry is routed with source labels or lies in a bounded exactly peelable residual, cover all strata, and derive complete `lambda,mu<=0.45`.

## Disproof track

Construct two matrices indistinguishable within the stored cut-error tolerance but differing at a relation entry, reduce a cut query to pair enumeration, show exact residual peeling materializes the incidence deck, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive: explicit low-cut-rank matrices with planted source-labelled `1` relation rectangles must route and replay all sources.
- Negative: matrices indistinguishable within the stored cut-error tolerance but with distinct singleton relation entries, source-permuted rectangles, and adversarial residuals must expose the approximation's ambiguity.
- Baselines: IDEAs 135/141, binary partitions, explicit pair tables, P1553 contractions, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact all-strata relation-entry recall, zero false provenance, a proved bounded residual, 1,000 ranked rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on one hidden residual `1` relation entry, one false source, a materialized pair deck, an unbounded residual, or either exponent at least `0.50`.
- Small cut error or a routed valid relation is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-348/cut_oracle_spec.md`
- `ideas/artifacts/ECDLP-IDEA-348/cut_error_relation_adversaries.json`
- `ideas/artifacts/ECDLP-IDEA-348/residual_peeling_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-348/cost_analysis.md`

## Interpretation boundary

This rejects the proposed exact cut router, not weak regularity. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Approximation accuracy or relation validity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-348/cut_error_relation_adversaries.json` with two incidence matrices indistinguishable within one stored cut-error tolerance but differing at a valid relation entry.
