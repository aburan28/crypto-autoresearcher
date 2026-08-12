# Pre-ID duplicate draft — Beck–Teboulle mirror source descent

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_gradient_and_mirror_geometry`.
- Class/risk: algorithm / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; objective convergence, a valid relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, public endpoints induce a convex source objective and a
target-independent mirror map matched to elliptic source geometry. Mirror descent reaches an
exact signed occurrence for relations and 100 fresh blind targets with complete time and memory
exponents at most `0.45`.

## Mechanism-new operation

Mirror descent takes subgradient steps in dual coordinates and maps back through a Bregman
proximal geometry. It counts only if endpoint-only gradients and the mirror map are available
without source incidence, and the minimizer exactly replays signs and occurrences under arbitrary
restrictions. Replacing Euclidean descent after a source objective exists is a solver control.

## Assumptions

1. A public convex objective has minima exactly at valid signed source tuples and nowhere else.
2. Gradients/subgradients and prox steps require no source catalogue or decomposition oracle.
3. The mirror map is target-independent, efficiently invertible, and exact on all strata.
4. Iteration, precision, and workspace caps hold despite rare fibres and restrictions.
5. The final point is integral and has a charged exact occurrence inverse for blind targets.

## Semantic fingerprint

`public_endpoint_convex_source_objective | bregman_mirror_subgradient_steps | exact_integral_source_minimizer | charged_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-d_L11_nesterov_accelerated_source_relaxation_preid_duplicate.md` — first-order acceleration assumes the objective and gradients.
2. `ideas/rejected/preallocation/20260719-d_D09_frank_wolfe_source_convex_hull_preid_duplicate.md` — convex optimization begins from a source polytope and oracle.
3. `ideas/rejected/preallocation/20260719-b_B03_sinkhorn_knopp_source_coupling_preid_duplicate.md` — alternative geometry preserves only a continuous aggregate.
4. `ideas/rejected/preallocation/20260722-d_Q06_cousot_abstract_source_fixpoint_preid_duplicate.md` — iterative abstraction can merge rare nonempty and empty states.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted source return remains the owner.

## Closest primary literature

- Beck and Teboulle, [Mirror Descent and Nonlinear Projected Subgradient Methods for Convex Optimization](https://doi.org/10.1016/S0167-6377(02)00231-6), analyzes mirror descent for a supplied convex problem.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not give the exact convex objective or mirror map.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison.

No checked source proves the required exact objective, gap, or inverse; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, objective, mirror map, gradients, steps, precision, tie rule, restrictions, strata, and verifier.
2. Build target-independent objective/mirror state inside `B^(9/4+o(1))`, rejecting source rows, labelled training, or hidden decomposition calls.
3. For each known-log target, run exact mirror descent, replay signed occurrences, and verify the elliptic sum.
4. Collect at least `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs.
5. Reuse identical state for 100 fresh masked targets, recover points, subtract masks, and verify every scalar.
6. Charge objective/gradient construction, prox inversions, steps, precision, failures, rounding, output, rank, logs, bits, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal densities
`N^delta,N^delta_t`; gradient/prox/query work `N^q,N^q_m`; rank credit `N^r`;
output `N^o`; ambiguity `N^u`; and factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS remain exponent `0.50`.

## Likely fatal obstruction

The exact source objective and subgradients encode the missing predicate. Natural relaxations
have fractional minima and smooth away singleton fibres. A mirror map changes geometry but not
information; exact rounding or conditioning restores source enumeration.

## Proof track

Prove endpoint-only convexity, a restriction-uniform integral gap, efficient exact mirror/prox
maps, subcap convergence, and signed inversion through full logs and blind descent.

## Disproof track

Exhibit a source-aware gradient, fractional/spurious minimum, vanishing rare-source signal,
target-dependent mirror, precision blowup, replay ambiguity, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy integral source objectives with a planted unique minimizer.
- Negative: fractional minima, equal objectives with different sources, empty fibres, rare
  singleton support, exceptional additions, and fresh blind targets.
- Baselines: Nesterov, Frank–Wolfe, P1553 R4, rho, and BSGS.
- Objective decrease is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact objective/integrality theorems, zero four-size/all-strata errors,
  full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing gradient, fractional false positive, cap violation, replay
  failure, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r09_objective_gradient_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r09_fractional_minima_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r09_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not mirror descent. Convergence or a valid relation remains toy,
heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Expand the proposed mirror subgradient on one restricted toy endpoint and preserve its first source-incidence query, fractional minimizer, or proof of exact subcap replay.
