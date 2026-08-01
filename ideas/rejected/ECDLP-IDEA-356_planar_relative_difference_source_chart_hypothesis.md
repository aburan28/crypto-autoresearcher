# ECDLP-IDEA-356 — Planar relative-difference source chart

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `rejected_scoped_prime_order_to_additive_exponent_no_go`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a relative-difference-set identity is not an ECDLP break.

## Falsifiable hypothesis

Subgroup points admit a public planar-function chart whose unique relative differences decode elliptic pair complements and recursively return five exact signed sources with a bounded public correction.

## Mechanism-new operation

The screened operation is **embed points in a planar-function graph, use permutation derivatives for unique pair differences, and correct the chart defect while unranking sources**. It is distinct only if the chart intertwines elliptic addition or its exact defect correction is strictly smaller than the original pair-source relation.

Minimum-interface correction: unique direct unranking is unnecessary. A target-labelled, subset-stable exact complement-existence bit under arbitrary dyadic deck restrictions, with `O(log B)` charged derivative/defect queries, suffices to recover one tuple.

## Assumptions

1. A public chart maps the order-`N` subgroup into a planar-function domain without scalar indexing.
2. Planar derivative uniqueness transfers to elliptic pair sums.
3. Any nonhomomorphic defect has bounded fibers and exact sub-gate correction.
4. Restricted exact decisions cover signs, collisions, repeated points, singularities, and target updates, so bisection recovers one tuple.
5. Chart construction, tables, correction, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`public_curve_point_chart | planar_function_relative_difference_set | bounded_defect_exact_correction | subset_stable_exact_complement_decision | dyadic_source_bisection | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`; public coordinate families did not remove addition/source expansion.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; an exact source-resolving public partition remains the missing operation.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; arithmetic source-fibre generation must be constructed and charged.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; compact coordinate or phase structure did not imply exact nonlinear membership.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1434-GENERATIVE-RULE-POSITIVE-CONTROL`; compact additive source generation works only after scalar indices are supplied.

## Closest primary literature

- Dembowski and Ostrom, [Planes of order n with collineation groups of order n squared](https://doi.org/10.1007/BF01111042), is an early primary source for the planar-function construction and assumes the underlying additive geometry.
- Ma and Pott, [Relative difference sets, planar functions, and generalized Hadamard matrices](https://doi.org/10.1006/jabr.1995.1198), gives the explicit relative-difference-set connection; it does not construct an elliptic source chart.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies elliptic endpoint equations and no addition-compatible planar chart.

No checked source gives the stated chart or correction; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, chart, planar function, inverse, defect correction, masks, and verifier.
2. Encode all factor points and build only target-independent indexes.
3. Decide restricted known-log complements, exactly correct defects, bisect one tuple, and verify its relation.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Apply identical derivative queries and correction to fresh masked targets.
6. Recover sources, substitute logs, remove masks, and verify `[x]P=Q`.
7. Charge chart construction, derivatives, defect fibers, correction, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(1/5)` and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,1/5+delta+q-r+o,ell,delta_t+q+o+u,1/5)`

`mu=max(a_m,q_m,1/5+o,ell_m,u)`.

Require `0<=r<=o`, setup/state `<=B^(9/4)`, fresh query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time exponents are `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

The prime-order subgroup has order `N`, while the additive group of `F_q^2` has characteristic `p`. For `N!=p`, every additive homomorphism into that group is zero. If the characteristic is `N`, a faithful ambient representation has order at least `N` and requires scalar orientation. A nonhomomorphic chart loses the unique-difference implication; exact defect correction restores IDEA-027 or an explicit pair/source table.

## Proof track

Construct a nontrivial public addition-compatible chart or bounded exact defect theorem, then prove subset-stable exact decisions, bisection, and complete sub-gate costs.

## Disproof track

Prove the group-exponent zero-map dichotomy, find an unbounded defect fiber, or show correction encodes scalar labels or the pair-source relation.

## Positive and negative controls

- Positive: `F_q^+` with known coordinates and a standard planar-function graph.
- Negative: ordinary prime-order elliptic groups with `N!=p` and source-permuted charts.
- Baselines: IDEAs 027/064/134/165/167/340, P1434's known-index control, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a nontrivial addition-compatible chart, zero correction errors, 1,000 ranked rows, 100 blind descents, and complete gates at most `0.45`.
- Falsify on the exponent mismatch, one unbounded defect fiber, scalar-labelled construction, source-sized correction, or exponent at least `0.50`.
- A planar identity or valid known-coordinate control cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-356/group_exponent_chart_no_go.md`
- `ideas/artifacts/ECDLP-IDEA-356/defect_fiber_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-356/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-356/cost_analysis.md`

## Interpretation boundary

This is a scoped rejection of the proposed chart, not planar-function theory or arbitrary nonhomomorphic representations. All checks would be toy, heuristic, model-bound, and novelty-unverified. A correct identity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-356/group_exponent_chart_no_go.md` and prove the exponent dichotomy while isolating every nonhomomorphic defect rule left outside it.
