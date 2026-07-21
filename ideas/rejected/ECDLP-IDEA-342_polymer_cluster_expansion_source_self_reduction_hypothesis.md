# ECDLP-IDEA-342 — Polymer cluster-expansion source self-reduction

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_cluster_expansion_requires_completion_activities_and_returns_marginals`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; convergence of a partition-function expansion or approximate marginal is not an ECDLP break.

## Falsifiable hypothesis

The endpoint-conditioned exact-source fibre has a public sparse polymer representation satisfying a uniform cluster-expansion criterion, and coefficient-complete conditional ratios can pin one signed factor at a time with exact self-reduction inside the P1553 bounds.

## Mechanism-new operation

The screened operation is **rewrite compatible partial-source corrections as polymers, evaluate convergent connected-cluster weights, and use exact conditional partition-function ratios to self-reduce to a factor tuple**. It is distinct only if polymer activities are computable from the endpoint without completion counts. Otherwise it merges with IDEAs 079, 104, 147, 200, 240, 316, and 332: the conditional activity is the missing source router and the expansion returns aggregate marginals.

## Assumptions

1. A target-independent polymer alphabet and incompatibility graph are generated without enumerating source completions.
2. Either a certified integer/complex lift of every activity satisfies a uniform analytic Kotecký–Preiss absolute-convergence bound with height and precision charged, or a formal exact expansion is used with no analytic convergence claim.
3. Any reduction back to the finite field and every truncation are coefficient-complete for zero/nonzero decisions; no approximate sign or positivity surrogate is used.
4. Conditional ratios pin every signed, repeated, infinity, and ambiguous source stratum exactly.
5. Alphabet construction, activities, clusters, truncation, output, rank, logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_source_polymers | sparse_incompatibility_graph | convergent_connected_cluster_expansion | exact_conditional_ratio_self_reduction | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic batch generator and transposed-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, where exact ancestry prevents lossless compression.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition cost floor.

## Closest primary literature

- Kotecký and Preiss, [Cluster expansion for abstract polymer models](https://doi.org/10.1007/BF01211762), proves convergence for supplied polymer activities and incompatibilities; it does not construct elliptic completion weights.
- Patel and Regts, [Deterministic polynomial-time approximation algorithms for partition functions and graph polynomials](https://doi.org/10.1137/16M1101003), is the nearby algorithmic zero-free/cluster-expansion control and remains approximate outside coefficient-complete regimes.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the endpoint constraint rather than polymer activities or exact conditional ratios.

No checked source supplies the claimed source-free activities and exact self-reduction; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, polymer grammar, incompatibility graph, activities, truncation, pinning order, masks, and verifier.
2. Construct activities for known-log endpoints without source lists or completion oracles.
3. Evaluate exact conditional ratios, pin every source tuple, and verify every group relation.
4. Collect at least `B` independent rows, solve factor logs, and independently verify them.
5. Repeat the identical expansion and pinning order on fresh scalar-blind masked targets.
6. Substitute factor logs, remove masks, preserve all zero/ambiguous branches, and verify `[x]P=Q`.
7. Charge construction, clusters, coefficient growth, pinning queries, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, expansion query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every polymer, incompatibility, coefficient bit, lift height, precision bit, cluster, conditional query, and output is charged; `0<=r<=o`. Promotion requires all complete exponents at most `0.45` and fresh-target work at most `0.25`. Pollard rho has expected time exponent `0.50` with negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

A useful polymer activity is the number or weight of source completions after fixing a partial tuple, exactly the missing endpoint router. Generic relation fibres are not in a proven zero-free/high-temperature regime, and finite fields have no native analytic absolute value to which the cited Kotecký–Preiss error bound directly applies. A charged lift still needs exact reduction; approximate marginals cannot certify exact zeros or point labels, while coefficient-complete expansion restores the full cluster/source deck.

## Proof track

Construct public activities, prove uniform convergence and coefficient-complete truncation, prove exact all-strata self-reduction, and derive setup/query and complete exponents below the frozen gates.

## Disproof track

Show any activity evaluates a completion count, violate the convergence criterion on preregistered controls, produce an approximate-ratio source error, or charge cluster/state growth to `B^3` or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied sparse polymer models with exact rational activities and unique planted configurations must self-reduce correctly.
- Negative: equal-partition-function models with different supports, source-permuted activities, and approximate marginals must not emit preferred elliptic factors.
- Baselines: IDEAs 079/104/147/200/240/316/332, explicit completion counting, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a source-free activity theorem, certified exact ratios, zero source errors, 1,000 verified rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify if activities require completion counts, convergence fails, one pinning branch is approximate or lost, state reaches `B^3`, or either exponent reaches `0.50`.
- A convergent approximate partition function is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-342/polymer_activity_input_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-342/convergence_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-342/conditional_ratio_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-342/cost_analysis.md`

## Interpretation boundary

This rejects the proposed exact elliptic polymer self-reduction, not cluster expansions. All finite checks would be toy; scaling is heuristic and model-bound; novelty is unverified. Approximate counting, convergence, or a valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-342/polymer_activity_input_receipt.md` expanding one proposed activity and marking every term that queries a hidden completion or source edge.
