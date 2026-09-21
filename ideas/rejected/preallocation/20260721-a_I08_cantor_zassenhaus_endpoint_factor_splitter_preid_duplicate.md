# Pre-ID duplicate draft — Cantor–Zassenhaus endpoint factor splitter

## Status and claim labels

- Prospect: `20260721-a-I08`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algebraic_factorization / high_risk / high-risk pre-ID screen.
- State: merged_rejected_explicit_polynomial_solver_and_endpoint_only_factors.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; polynomial factors, a relation, or scalar verification are not a breakthrough.

## Falsifiable hypothesis

Construct the target-labelled common-factor polynomial implicitly and apply Cantor–Zassenhaus equal-degree splitting so one factor identifies a restriction-stable source branch and supports complete relation collection and blind descent below rho/BSGS.

## Mechanism-new operation

Cantor–Zassenhaus uses random modular powers and polynomial gcds to split a supplied square-free equal-degree polynomial. It counts only if the target polynomial is endpoint-derived without a dense/source-sized object and each factor has a charged exact lift to signed occurrences; factoring an explicit polynomial is a solver control.

## Assumptions

1. A square-free target polynomial/circuit is built from public endpoints within the caps.
2. Equal-degree preprocessing and every gcd/power are charged in bit and field complexity.
3. Polynomial factors correspond biconditionally to restricted relation existence.
4. Roots/factors lift to all signed, repeated, and exceptional source occurrences.
5. Randomness is independent/recorded and state is reusable for blind targets.

## Semantic fingerprint

`public_target_common_factor_polynomial | Cantor_Zassenhaus_random_equal_degree_split | exact_restricted_factor_nontriviality | factor_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — common-factor semantics are known; compact construction/replay is open.
2. `ideas/rejected/ECDLP-IDEA-106_straight_line_factor_atomizer_hypothesis.md` — factorization needs a supplied compact source-complete circuit.
3. `ideas/rejected/ECDLP-IDEA-063_provenance_preserving_subresultant_forest_hypothesis.md` — gcd factors lose source provenance.
4. `ideas/deferred/ECDLP-IDEA-121_shared_bivariate_common_norm_hypothesis.md` — common norms remain circuit/state gated.
5. `ideas/rejected/ECDLP-IDEA-099_relative_galois_resolvent_block_intersection_hypothesis.md` — algebraic factors do not automatically return source blocks.

## Closest primary literature

- Cantor and Zassenhaus, [A new algorithm for factoring polynomials over finite fields](https://doi.org/10.1090/S0025-5718-1981-0606517-5), factors a supplied polynomial using modular powers and gcds.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not the compact target factor polynomial.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required compact source-faithful polynomial; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, polynomial representation, square-free/equal-degree rules, restrictions, signed strata, randomness, and verifier.
2. Construct only target-independent schema/advice within setup; do not amortize any target-labelled coefficients, circuit gates, materialization, or degree state.
3. For each known-log target, charge construction/materialization of its target-labelled polynomial or circuit to that target, then split/restrict, replay labelled signed points from a factor, verify the point sum, and record only verified rows.
4. Preserve failures/dependencies; collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `Q+[t]P`, split/replay, compute `x`, and verify `[x]P=Q`.
6. Charge polynomial construction, degree, square-free/equal-degree steps, powers, gcds, random retries, restrictions, replay, density, rank, logs, blind descent, bit time, and memory.

## Full rho/BSGS cost model

Let `a,a_m` charge only target-independent schema/advice. The construction, coefficient/circuit materialization, degree state, and memory of every target-labelled polynomial belong explicitly to per-target `q,q_m`, together with preprocessing, modular powers, gcds, retries, restrictions, and replay. With `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Cantor–Zassenhaus begins after the polynomial has been explicitly represented. P1553 R4's obstruction is constructing the target-labelled common factor and replaying sources without dense/source-sized state. Factorization is therefore a solver substitution; an endpoint factor can still combine many source occurrences without labels.

## Proof track

Construct a compact endpoint-only polynomial oracle accepted by a fully charged splitter, prove factor/restriction/source biconditionals and all-strata inversion, and meet complete exponents.

## Disproof track

Trace every coefficient/circuit gate and factor-to-source map; falsify if construction materializes dense/source state, if factors lack exact occurrence labels, or if randomized retries/costs exceed a cap.

## Positive and negative controls

- Positive: supplied square-free equal-degree polynomials with planted labelled factors and recorded randomness.
- Negative: irreducible, repeated-factor, high-degree dense, factor-collision, shuffled-source, empty-restriction, and blind-target cases.
- Baselines: generic gcd/factorization, SLP/subresultant/common-norm owners, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require compact endpoint-only construction, failure at most `2^-80`, exact factor/source biconditional, four increasing sizes, rank `d_FB` from at least `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on explicit dense/source state, unlabeled factors, a false decision, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i08_polynomial_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i08_factor_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i08_cost_analysis.md`

## Interpretation boundary

This rejects a solver transplant, not Cantor–Zassenhaus. Toy factors remain heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute factorization.
