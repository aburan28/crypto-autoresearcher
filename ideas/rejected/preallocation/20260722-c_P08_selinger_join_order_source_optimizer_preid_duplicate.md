# Pre-ID duplicate draft — Selinger join-order source optimizer

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P08`; no canonical ID allocated.
- Disposition: `merged_rejected_plan_selection_without_new_relation_operation`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a low estimated plan cost or valid relation is not an ECDLP result.

## Falsifiable hypothesis

A target-independent Selinger dynamic program over endpoint-relation access paths selects a
join order whose intermediate widths stay below the P1553 caps on every fresh target. The chosen
plan returns signed occurrences and completes factor logs plus descent below exponent `0.45`.

## Mechanism-new operation

The Selinger optimizer enumerates supplied access paths and left-deep join orders using cost and
cardinality estimates. It counts only if an access path is a new endpoint-derived mathematical
operation, selection is frozen before outcomes, and actual—not estimated—full costs pass. Merely
choosing among existing solvers or post-hoc plans is a control.

## Assumptions

1. Candidate access paths are endpoint-only, scalar-blind, and source-faithful.
2. Statistics and plan choice are target-independent and prospective.
3. Optimization, misestimation, rejected paths, intermediates, and output are charged.
4. The selected plan has exact empty-fibre semantics and signed replay on all strata.
5. One plan/state serves relations and 100 fresh masked targets.

## Semantic fingerprint

`public_endpoint_access_paths | Selinger_dynamic_program_plan_selection | prospective_low_width_plan | charged_signed_execution | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — variable/order optimization is an occupied join backend.
2. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — actual widths and provenance dominate estimates.
3. `ideas/rejected/preallocation/20260721-d_L11_nesterov_accelerated_source_relaxation_preid_duplicate.md` — optimizer substitution does not create the source object.
4. `ideas/rejected/ECDLP-IDEA-381_megiddo_cole_parametric_source_search_hypothesis.md` — search/selection is downstream without a new predicate.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current operation-level frontier.

## Closest primary literature

- Selinger et al., [Access Path Selection in a Relational Database Management System](https://doi.org/10.1145/582095.582099), optimizes supplied database access paths.
- Graefe, [Volcano](https://doi.org/10.1109/69.273032), is the physical-plan execution control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), supplies equations rather than a sub-rho access path; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) is the baseline.

The optimizer is title-new here but is a solver/plan substitution unless an access path itself
removes the recorded obstruction. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, access paths, statistics, cost equations, plan search space,
   restrictions, signed schema, strata, and verifier.
2. Construct endpoint-only statistics/state within `B^(9/4+o(1))`; forbid secret-labelled
   calibration, source tables, target fitting, and uncharged alternative-plan search.
3. Select one plan prospectively; for each known-log target execute it, replay signed points,
   and verify the elliptic relation.
4. Collect `max(d_FB+32,1000)` rows, require rank `d_FB`, solve all factor logs, and charge
   optimization, estimation errors, actual intermediates, failures, output, and linear algebra.
5. Reuse the frozen plan for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge all access-path construction, plan search, execution, bit cost, rank, logs, and memory.

## Full rho/BSGS cost model

Let `beta=1/5`; setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; actual query/workspace `N^q,N^q_m`; rank credit `N^r`; output
`N^o`; misestimation/retry `N^u`; and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Estimated cost never substitutes for actual
cost. Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, fresh
work/workspace `<=B^(5/4+o(1))`. Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

All candidate access paths begin from the same absent source relations or restricted predicate.
Join-order optimization may improve constants but cannot lower the construction/information
floor; selecting after measured successes becomes a forbidden post-hoc selector.

## Proof track

Exhibit one endpoint-only access path with a new operation, prove prospective plan selection,
exact replay, and complete sub-rho costs on fresh targets.

## Disproof track

Show every path is a solver/order variant, find target-dependent statistics, estimate/actual
width failure, lost replay, cap violation, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy relations with two plans and correctly predicted costs.
- Negative: adversarial cardinality correlation, plan misestimation, empty fibres, identical
  costs/different sources, post-hoc selection, and blind targets.
- Baselines: InsideOut, Megiddo-Cole, P1553 R4, rho, and BSGS.
- Accurate planning on supplied relations is toy/model-bound evidence only.

## Quantitative promotion and falsification gates

- Promote only if a path is mathematically new, plan is prospectively frozen, errors are zero
  at four sizes, rank/logs/descent complete, caps pass, and `lambda,mu<=0.45`.
- Falsify on solver-only paths, post-hoc choice, one semantic error, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p08_access_path_novelty_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p08_estimate_actual_matrix.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p08_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects plan optimization as a new ECDLP mechanism, not the Selinger optimizer. All
evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Classify every proposed access path by mathematical operation and preserve the first proof that all paths are solver/order variants of an occupied source relation.
