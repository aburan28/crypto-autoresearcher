# Pre-ID duplicate draft — DBToaster higher-order-delta source view

## Status and claim labels

- Provisional ID: `PREID-20260722-c-P11`; no canonical ID allocated.
- Disposition: `merged_rejected_materialized_source_views_and_solver_update`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a fast view refresh, relation, or correct delta is not an ECDLP result.

## Falsifiable hypothesis

Treating masked targets and factor-base updates as deltas to a five-source relation query permits
recursive finite differencing. A bounded family of higher-order materialized views answers exact
target existence and signed replay, completing factor logs and blind descent below exponent `0.45`.

## Mechanism-new operation

DBToaster's viewlet transform recursively materializes a query and its higher-order deltas so
updates can be processed cheaply. It counts only if base/delta views are endpoint-derived without
source enumeration, their total state is sub-rho, and a target update returns signed occurrences.
Maintaining explicit pair/source joins or target histories is a control.

## Assumptions

1. Base and delta views are target-independent, scalar-blind, and fit the setup cap.
2. View construction does not enumerate source tuples or hide dense quotient state.
3. Update order, refreshes, higher-order view count, output, and failures are charged.
4. Each update has exact empty-fibre semantics on all strata and restrictions.
5. Returned provenance gives signs, multiplicities, and actual points for 100 fresh masks.

## Semantic fingerprint

`public_endpoint_relation_query | recursive_higher_order_delta_views | exact_target_update_answer | charged_signed_delta_provenance | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — maintained factorized joins retain source/input width.
2. `ideas/artifacts/ECDLP-IDEA-117/p1511_factorized_semijoin_derivation.md` — explicit semijoin input-floor owner.
3. `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` — dynamic evaluation over supplied source state is occupied.
4. `ideas/ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md` — shared transition state needs an endpoint source lift.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact update/existence/replay frontier.

## Closest primary literature

- Koch et al., [DBToaster: Higher-Order Delta Processing for Dynamic, Frequently Fresh Views](https://doi.org/10.1007/s00778-013-0348-4), maintains supplied SQL views via recursive finite differencing.
- Olteanu and Závodný, [Factorised Representations](https://doi.org/10.1145/2274576.2274607), is the nearby compact-view control.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not construct the base/delta views; Shoup's [generic bound](https://www.shoup.net/papers/dlbounds1.pdf) controls ECDLP cost.

Higher-order deltas are title-new here but are a solver/update strategy over the occupied
factorized provenance and dynamic-evaluation lanes. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, base query, delta variables/order, viewlet depth, materialized views,
   restrictions, provenance, strata, and verifier.
2. Build endpoint-only base/delta state within `B^(9/4+o(1))`; forbid explicit source/pair
   tables, target histories, scalar residues, dense resultants, and uncharged views.
3. For each known-log target update, refresh views, obtain exact signed occurrences, and verify
   the elliptic relation.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, solve every factor log, and
   charge construction, refreshes, deltas, output, failures, and sparse linear algebra.
5. Reuse identical state and frozen update order for 100 fresh `R=Q+[t]P`, compute
   `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge all base/view state, update work, bit cost, rank, factor logs, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, setup/state are `N^a,N^a_m`; relation/target reciprocal densities
`N^delta,N^delta_t`; update/workspace `N^q,N^q_m`; rank credit `N^r`; output/view
multiplicity `N^o`; update ambiguity `N^u`; factor-log time/memory `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Promotion requires `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, with every
higher-order view charged. Rho and BSGS controls have exponent `0.50`.

## Likely fatal obstruction

The materialized base and delta views encode the missing source joins. Recursive finite
differencing makes updates cheap only after paying this target-independent state, while treating
each fresh target as an update does not create a public source inverse.

## Proof track

Construct endpoint-only bounded views, prove exact update semantics and signed provenance,
and bound total initialization, updates, descent, and memory below both controls.

## Disproof track

Expand the viewlet transform until source enumeration appears; find super-cap view state,
target-history dependence, false update, lost provenance, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy join with exact first/second-order delta views and labelled update.
- Negative: initialization-dominant instances, empty updates, repeated targets, equal deltas/
  different sources, shuffled update order, repeated signed points, and blind targets.
- Baselines: IDEA-117/P1511, dynamic evaluation trees, P1553 R4, rho, and BSGS.
- Fast updates after supplied initialization are toy/model-bound evidence only.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only bounded views, zero semantic errors at four sizes, full
  rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45` including initialization.
- Falsify on source-bearing/super-cap views, target history, one replay error, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-c/p11_viewlet_expansion_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-c/p11_update_order_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-c/p11_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not DBToaster. All evidence remains toy, heuristic,
model-bound, and novelty-unverified; update throughput is not scalar recovery.

## Exactly one next executable action

1. Symbolically expand the viewlet transform through the first nonzero higher-order delta and preserve the first source-join or super-cap materialized-view dependency.
