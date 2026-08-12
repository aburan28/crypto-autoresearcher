# Pre-ID duplicate draft — Nesterov accelerated source relaxation

## Status and claim labels

- Prospect: `20260721-d-L11`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: optimization_algorithm / high-risk / high-risk pre-ID screen.
- State: merged_rejected_approximate_relaxation_and_missing_exact_rounding.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; objective convergence, a rounded relation, or verified tuple is not an ECDLP result.

## Falsifiable hypothesis

Construct a smooth convex endpoint relaxation whose minimizers are uniformly separated exactly at signed relation sources, use Nesterov momentum to reach the correct basin under restrictions, round to occurrences, and complete factor logs plus blind target descent below rho and BSGS.

## Mechanism-new operation

The native operation combines a gradient step with an extrapolated momentum point to obtain an `O(1/k^2)` objective-gap rate for a supplied smooth convex problem. It counts only if the relaxation, gradients, exact margin, and rounding section are endpoint-derived and relation-biconditional; accelerating a supplied approximate objective is a control.

## Assumptions

1. Public endpoint data defines a smooth convex objective without source-sized features or scalar labels.
2. Valid relation fibres correspond exactly to minimizers with a uniform public separation margin.
3. Momentum remains stable under finite-field embedding, restrictions, rounding, and exceptional strata.
4. A rounded minimizer returns one occurrence-distinct signed tuple with charged precision/ambiguity.
5. The same target-independent objective serves relation collection and fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_convex_relation_relaxation | Nesterov_extrapolated_gradient_acceleration | exact_margin_restricted_minimizer | minimizer_rounding_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact zero-safe predicate, replay, and descent frontier.
2. `ideas/rejected/preallocation/20260719-d_D09_frank_wolfe_source_convex_hull_preid_duplicate.md` — convex optimization starts from supplied atoms and only approximates membership.
3. `ideas/rejected/preallocation/20260719-d_D06_randomized_kaczmarz_source_projection_preid_duplicate.md` — iterative projection assumes an explicit source system and does not create exact support.
4. `ideas/rejected/preallocation/20260721-c_K08_goemans_williamson_source_rounding_preid_duplicate.md` — approximate relaxation plus rounding lacks zero integrality gap and source incidence.
5. `ideas/rejected/preallocation/20260721-b_J12_remez_minimax_endpoint_indicator_preid_duplicate.md` — approximation needs a supplied function oracle and exact margin to become a decision procedure.

## Closest primary literature

- Nesterov, [A method of solving a convex programming problem with convergence rate O(1/k^2)](https://www.mathnet.ru/eng/dan46009), proves accelerated objective convergence for a supplied smooth convex problem.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations without a convex exact-source relaxation.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), gives the generic baseline.

No checked source constructs the exact-margin relaxation or noncircular signed occurrence rounding; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, embedding/objective/precision, and independent point verifier.
2. Construct and certify the endpoint-derived convex objective, gradient oracle, condition/margin bounds, and rounding map without source enumeration or scalar labels.
3. For each known-log target, solve at most `5 ceil(log_2 B)+O(1)` restrictions to certified precision, round `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, round/replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge objective/feature construction, gradient evaluations, precision, conditioning, momentum restarts, restrictions, rounding/repair, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge relaxation/oracle setup in `a,a_m`, restricted optimization/rounding in `q,q_m`, and outputs/ambiguity/repair in `o,u`. With `B=N^beta`, `beta=1/5`, `delta,delta_t,r,ell,ell_m` as usual, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50`.

## Likely fatal obstruction

Accelerated objective convergence does not imply exact discrete support recovery. A convex hull contains mixtures of many invalid source assignments, and no public uniform integrality margin is known. Exact rounding/repair is the original source oracle; conditioning and bit precision can erase iteration gains even before density, rank, and descent are charged.

## Proof track

Construct a source-free convex formulation with a proved uniform integrality/separation margin, exact all-strata rounding, restriction stability, and full bit-complexity exponents below the gates.

## Disproof track

Find fractional minimizers, vanishing margins, or rounding collisions; trace gradient features and repair; falsify on source advice, one false decision, precision beyond caps, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied strongly convex objectives with planted integral minimizers and certified margins.
- Negative: flat fractional faces, near-tied invalid minimizers, adversarial conditioning, empty restrictions, and fresh targets.
- Baselines: gradient descent, Frank-Wolfe, Kaczmarz, SDP rounding, Remez, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only objective construction, four increasing sizes, zero false decisions, a proved margin, exact replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps including bit complexity, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on one fractional/false rounding, source-sized features, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l11_margin_rounding_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l11_nesterov_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l11_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only accelerated-relaxation transplant, not Nesterov acceleration for supplied convex problems. Every finite convergence trace remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
