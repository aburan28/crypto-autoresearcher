# Pre-ID duplicate draft — Gabay–Mercier dual source splitting

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R10`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_split_objective_and_prox_oracles`.
- Class/risk: composition / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; primal-dual convergence, a valid relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, elliptic addition, factor-base membership, sign, and restriction
constraints admit endpoint-only separable objectives coupled by public equalities. Alternating
dual/proximal updates converge to an exact signed occurrence, enabling full factor logs and 100
fresh blind descents with complete exponents at most `0.45`.

## Mechanism-new operation

The native operation splits a supplied constrained variational problem into proximal subproblems
and alternates primal and dual updates. It counts only if each prox operator and coupling is
endpoint-derived without source state, and the limit has an exact charged inverse to signed
occurrences. Splitting already source-aware objectives is a composition control.

## Assumptions

1. Each component objective/prox is complete and source-blind inside the online cap.
2. Coupling equalities encode only public endpoints, not tuple or scalar labels.
3. Exact convergence and precision bounds hold under arbitrary restrictions and all strata.
4. The limit is integral and replays signs, repetitions, and occurrences uniquely.
5. Target-independent component state is reused byte-identically for blind targets.

## Semantic fingerprint

`public_endpoint_separable_constraints | alternating_primal_dual_prox_updates | exact_integral_source_fixed_point | charged_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260722-d_Q01_nelson_oppen_theory_cooperation_preid_duplicate.md` — combining supplied complete components leaves the source component missing.
2. `ideas/rejected/preallocation/20260719-d_D08_dantzig_wolfe_source_column_generation_preid_duplicate.md` — decomposition assumes source columns and a pricing oracle.
3. `ideas/rejected/preallocation/20260719-d_D07_benders_source_cut_generation_preid_duplicate.md` — split master/subproblem interfaces preserve supplied source state.
4. `ideas/rejected/preallocation/20260721-d_L11_nesterov_accelerated_source_relaxation_preid_duplicate.md` — convergence acceleration is downstream of the missing objective.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted source return remains the owner.

## Closest primary literature

- Gabay and Mercier, [A Dual Algorithm for the Solution of Nonlinear Variational Problems via Finite Element Approximation](https://doi.org/10.1016/0898-1221(76)90003-1), alternates dual updates for a supplied split problem.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not provide complete source-blind proximal components.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls generic costs.

The source compiler and exact integral inverse are not supplied; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, split formulation, prox maps, penalties, initialization, precision, restrictions, strata, and verifier.
2. Build every target-independent component within `B^(9/4+o(1))`, excluding source tuples, scalar labels, and hidden decomposition oracles.
3. For known-log targets, alternate exact updates, replay a signed occurrence from the fixed point, and verify the elliptic sum.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs.
5. Reuse identical component state on 100 fresh masked targets, recover points, subtract masks, and verify scalars.
6. Charge component construction, every prox call, dual updates, penalties, precision, failures, replay, rank, logs, bits, and peak live memory.

## Full rho/BSGS cost model

For `beta=1/5`, define setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, split-query work/workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS retain exponent `0.50`.

## Likely fatal obstruction

At least one prox operator must decide factor-base/source compatibility, so the split only
relocates Query2P1. Relaxed primal-dual consensus can converge to fractional aggregates, and
exact source replay or arbitrary restriction support restores the full source representation.

## Proof track

Prove endpoint-only complete prox maps, exact integral convergence on every restriction,
subcap iteration and precision, and signed inversion through full logs and blind descent.

## Disproof track

Expose one source-aware prox, fractional fixed point, divergent/adversarial penalty schedule,
restriction rebuild, occurrence ambiguity, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied separable toy source problems with a unique integral saddle point.
- Negative: fractional consensus, equal component objectives with different sources, empty
  fibres, exceptional strata, penalty sensitivity, and fresh blind targets.
- Baselines: Nelson–Oppen, Benders, Dantzig–Wolfe, P1553 R4, rho, and BSGS.
- Fixed-point convergence is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact component/integrality theorems, zero four-size/all-strata errors,
  full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-aware prox, fractional false positive, cap violation, replay failure,
  or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r10_prox_interface_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r10_fractional_fixed_points.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r10_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not dual splitting. Convergence, feasibility, and valid relations
remain toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Expand every prox call in one toy split endpoint instance and preserve the first source-aware oracle or prove exact integral signed replay within both caps.
