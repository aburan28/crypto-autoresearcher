# ECDLP-IDEA-361 — Robust sunflower-core source router

## Status and claim labels

- Class: `combinatorial`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_set_family_requires_explicit_source_labels`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; finding a sunflower core or color pattern is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-defined family of bounded-size relation-source sets has a robust sunflower core whose restricted petal-color state decides exact family nonemptiness for source bisection with sub-source-size state and query cost.

## Mechanism-new operation

The screened operation is **construct an implicit set family from endpoint constraints, extract a robust sunflower core, and use petal-color signatures as exact nonemptiness decisions under dyadic source restrictions**. It is distinct only if the family is never explicitly enumerated and restrictions preserve exact endpoints rather than aggregate overlap types.

Minimum-interface correction: petal colors need not directly identify labels. A target-labelled, subset-stable exact family-nonemptiness bit under arbitrary dyadic deck restrictions, with `O(log B)` charged core queries, suffices to recover one signed tuple.

## Assumptions

1. Relation-source sets are represented by an endpoint-only membership/rank oracle.
2. A robust sunflower theorem applies with quantitative constants below the gates.
3. Restricted core/color state preserves exact family nonemptiness, so bisection recovers one signed tuple rather than only a dense subfamily.
4. Target updates, repeated points, signs, and all exceptional source strata preserve the routing rule.
5. Family-oracle construction, core extraction, coloring, inverse routing, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`endpoint_relation_set_family | robust_sunflower_core_extraction | subset_stable_exact_family_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-040`; set-family transfer preserved aggregate overlaps but not exact source transport.
2. `inputs/ledger_inventory.json` — imported `ECFG-H552`; a compact endpoint-conditioned source-family representation remains hypothetical.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; quotienting source families without an exact source section leaves the central circuit obligation.
4. `inputs/ledger_inventory.json` — imported `ECFG-P867`; motif recurrence is a supplied toy relation-lane control, not a complete source router.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-989`; selector or filter structure did not remove source generation and target-descent costs.

## Closest primary literature

- Alweiss, Lovett, Wu, and Zhang, [Improved bounds for the sunflower lemma](https://doi.org/10.4007/annals.2021.194.3.5), proves existence bounds for sunflowers in explicit set systems; it does not build an implicit labelled witness router.
- Naslund and Sawin, [Upper bounds for sunflower-free sets](https://doi.org/10.1017/fms.2017.12), gives algebraic bounds for set families rather than endpoint-only enumeration or source inversion.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies a relation predicate but not a compact source-set oracle.

No checked source supplies the implicit family oracle and exact source router; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, endpoint-defined set family, core/petal conventions, color inverse, masks, and verifier.
2. Construct target-independent core state or a bounded target update without listing relation-source sets.
3. Query restricted exact family nonemptiness for known-log targets, bisect one signed tuple, and replay its relation.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Apply the unchanged core/color router to fresh masked targets.
6. Substitute logs, remove masks, retain ambiguity, and verify `[x]P=Q`.
7. Charge family-oracle construction, sunflower extraction, coloring, tuple output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(beta)`, `beta=1/5`, and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `a` charges the family oracle, core, and colors, `q` includes target routing plus restriction updates, `o` is exact source output, and `u` is residual ambiguity. Require `0<=r<=o`, setup/state `<=B^(9/4)`, fresh query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time are exponent `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

Sunflower theorems reason about an already specified set family. This is the same information-flow boundary as IDEA-200's hypergraph containers: the structural theorem consumes the edge/family oracle and does not locate a rare endpoint edge. Explicit relation sets are the source witnesses the route is meant to avoid; no subset-stable endpoint decision is supplied below the gates. Moreover, disjoint petals do not imply linearly independent relation rows or fresh-target coverage, so rank and descent can still collapse after paying family construction.

## Proof track

Construct an endpoint-only membership/rank oracle, prove robust-core subset-stable exact decisions plus bisection for every stratum, and derive complete sub-gate costs.

## Disproof track

Show family materialization is necessary, find equal-color/different-source tuples, or demonstrate that core extraction preserves no rank or target-descent advantage.

## Positive and negative controls

- Positive: a supplied labelled set family with a planted core and explicit petal dictionary.
- Negative: point-label permutations preserving the unlabelled sunflower and color statistics but changing exact relations.
- Baselines: IDEAs 090/143/200/248/328, P867, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only family oracle, subset-stable exact decisions plus charged bisection, zero source errors, 1,000 independent rows, 100 blind descents, and complete exponents at most `0.45`.
- Falsify on explicit family enumeration, a label-permutation family whose every public color correction or section exceeds the gates, rank collapse after all bounded corrections, incomplete target coverage, or complete exponent at least `0.50`.
- A sunflower bound, planted core, or toy motif recurrence is insufficient.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-361/implicit_family_and_core_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-361/point_label_permutation_controls.json`
- `ideas/artifacts/ECDLP-IDEA-361/rank_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-361/cost_analysis.md`

## Interpretation boundary

This rejects the implicit exact-source router, not sunflower theory. All prospective checks are toy, heuristic, model-bound, and novelty-unverified. A combinatorial core is not a breakthrough.

## Exactly one next executable action

1. Define `ideas/artifacts/ECDLP-IDEA-361/implicit_family_and_core_obligations.md` as an endpoint-only subset-stable exact family-nonemptiness specification that never exposes the relation-set list and charges every bisection query.
