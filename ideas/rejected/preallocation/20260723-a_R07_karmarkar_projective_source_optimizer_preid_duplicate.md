# Pre-ID duplicate draft — Karmarkar projective source optimizer

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R07`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_linear_program_solver`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; LP convergence, a valid relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, public endpoint constraints define a compact linear program whose
unique optimal vertex is an exact signed factor-base occurrence. Karmarkar projective steps find
that vertex for relations and 100 blind targets with complete time and memory exponents at most
`0.45`.

## Mechanism-new operation

Karmarkar's method applies projective transformations and interior descent to a supplied linear
program. It counts only if every variable and constraint is compiled from public endpoints
without source incidence and the optimum has a charged exact inverse to signed occurrences.
Solving an LP whose columns are source tuples is a backend control.

## Assumptions

1. Endpoint equations have an exact polynomial-size LP formulation without relaxation gap.
2. Variables and constraints contain no enumerated source, scalar residue, or decomposition advice.
3. Conditioning, bit precision, and iterations meet both caps.
4. The optimum is integral, unique under arbitrary restrictions, and replays signs and occurrences.
5. Target-independent formulation state is reused unchanged on fresh masked targets.

## Semantic fingerprint

`public_endpoint_linear_program | projective_interior_transform_descent | exact_integral_source_vertex | charged_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-d_D09_frank_wolfe_source_convex_hull_preid_duplicate.md` — convex optimization starts from a supplied source polytope.
2. `ideas/rejected/preallocation/20260721-d_L11_nesterov_accelerated_source_relaxation_preid_duplicate.md` — acceleration does not create an exact source formulation.
3. `ideas/rejected/preallocation/20260719-b_B03_sinkhorn_knopp_source_coupling_preid_duplicate.md` — continuous relaxation can merge integral source fibres.
4. `ideas/rejected/preallocation/20260719-d_D08_dantzig_wolfe_source_column_generation_preid_duplicate.md` — source columns and pricing oracles encode the missing answer.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — owns exact restricted existence and signed replay.

## Closest primary literature

- Karmarkar, [A New Polynomial-Time Algorithm for Linear Programming](https://doi.org/10.1007/BF02579150), optimizes a supplied LP by projective transformations.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not give an exact compact source LP.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source proves the required integral formulation or inverse; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, LP formulation, projective map, start point, precision, tie rule, restrictions, strata, and verifier.
2. Compile target-independent variables and constraints inside `B^(9/4+o(1))`; reject source columns, scalar labels, and hidden pricing/decomposition oracles.
3. For each known-log target, solve the LP exactly, replay the integral signed occurrence, and verify the elliptic sum.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve every factor log.
5. Reuse identical formulation state on 100 fresh masked targets, recover sources, subtract masks, and verify scalars.
6. Charge formulation, projective steps, linear solves, precision, rounding/ties, failures, replay, rank, logs, bits, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let `a,a_m` be setup/state; `delta,delta_t` reciprocal densities;
`q,q_m` solve work/workspace; `r` verified-rank credit; `o` output; `u` ambiguity;
and `ell,ell_m` factor-log costs. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain `0.50`.

## Likely fatal obstruction

A compact exact LP would already encode the source-incidence polytope. Natural relaxations have
fractional optima or indistinguishable empty and nonempty integer fibres. Adding source columns,
separation, or integrality cuts restores the missing predicate and its full cost.

## Proof track

Prove an endpoint-only polynomial-size integral formulation, uniform bit complexity, exact
restriction stability, and signed vertex inversion through full relation rank and blind descent.

## Disproof track

Exhibit a fractional optimum, source-labelled column, exponential facet/separation cost,
target-dependent formulation, replay ambiguity, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied totally unimodular toy source LP with one planted signed vertex.
- Negative: fractional relaxations, equal objective distinct sources, empty integer fibres with
  feasible fractional points, exceptional strata, and blind targets.
- Baselines: Frank–Wolfe, Dantzig–Wolfe, P1553 R4, rho, and BSGS.
- Polynomial LP convergence is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with an exact compactness/integrality theorem, zero four-size/all-strata errors,
  full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one fractional false positive, source column/oracle, cap violation, replay failure,
  or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r07_lp_formulation_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r07_fractional_gap_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r07_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not Karmarkar's algorithm. LP feasibility, convergence, and
valid relations remain toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Write the smallest claimed endpoint-only LP completely and preserve its first source-indexed variable, fractional false positive, or proof of exact integral replay within both caps.
