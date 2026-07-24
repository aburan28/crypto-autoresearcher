# Pre-ID duplicate draft — Bradley IC3 source blocker

## Status and claim labels

- Provisional ID: `PREID-20260722-d-Q09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_transition_relation`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; an inductive invariant, counterexample, or SAT pass is not an ECDLP result.

## Falsifiable hypothesis

For a generic prime-order curve, encode partial signed-sum construction as a transition
system and use IC3/PDR frames to block all states that cannot reach a restricted target.
Convergence decides exact existence; a retained counterexample trace replays factor-base
occurrences for rank-complete relations and 100 fresh masked descents below exponent `0.45`.

## Mechanism-new operation

The native operation incrementally learns clauses inductive relative to reachability frames
without fully unrolling a supplied transition relation. It counts only if the transition
relation is compiled from public endpoints without source enumeration and if an unsafe trace
is exactly a signed occurrence. Applying IC3 to an explicit source-choice machine is a
control.

## Assumptions

1. A target-independent subcap transition relation represents all and only valid signed partial sums.
2. Frame SAT queries and clause generalization are source-blind and inside the online cap.
3. Convergence is exact for every restriction and exceptional addition stratum.
4. Counterexample traces retain factor-base indices, signs, and multiplicities.
5. The same transition relation and learned target-independent state serve 100 blind targets.

## Semantic fingerprint

`public_endpoint_transition_relation | ic3_relative_inductive_frames | exact_restricted_reachability | counterexample_signed_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260722-a_N04_grasp_conflict_clause_source_search_preid_duplicate.md` — learned clauses operate after source-bearing CNF construction.
2. `ideas/rejected/preallocation/20260722-a_N05_chaff_two_watch_source_propagator_preid_duplicate.md` — SAT propagation changes the solver, not the endpoint predicate.
3. `ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md` — refinement relies on a concrete source checker.
4. `ideas/rejected/preallocation/20260721-a_I11_savitch_recursive_source_reachability_preid_duplicate.md` — reachability algorithms must charge construction of the source state graph.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — current exact endpoint-existence and signed-replay owner.

## Closest primary literature

- Bradley, [SAT-Based Model Checking without Unrolling](https://doi.org/10.1007/978-3-642-18275-4_7), learns relatively inductive clauses over a supplied transition system and returns an invariant or counterexample.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not a compact transition relation with source replay.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

IC3 is a distinct native reachability procedure, but its ECDLP transplant is a SAT/
source-graph backend unless the transition compiler removes P1553 R4's obstruction.
Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, states, transition relation, frames, generalization, restrictions, trace replay, strata, and verifier.
2. Build endpoint-only transition state within `B^(9/4+o(1))`; forbid explicit source-choice edges, scalar labels, target fitting, and hidden decomposition calls.
3. For each known-log target, run exact frames to convergence or a trace, replay signed occurrences, and verify the elliptic sum before row admission.
4. Collect `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs while charging transition compilation, SAT calls, clauses/frames, traces, failures, and sparse linear algebra.
5. Reuse identical target-independent state for 100 fresh `R=Q+[t]P`, replay signed points, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge all states/edges/clauses, predecessor queries, obligation pushes, generalization, trace output, rank, logs, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, frame/query workspace `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and factor-log time/memory `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; every SAT query and learned clause is
charged. Promotion requires `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and
fresh work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent-`0.50` controls.

## Likely fatal obstruction

IC3 assumes an explicit transition relation. A relation that chooses factor-base points and
updates partial sums is the source graph/constraint system; compiling it materializes the
missing source choices. Clause learning may prove absence but does not create positive
occurrences, and target-specific frames are charged fresh work.

## Proof track

Prove an endpoint-only subcap transition compiler, bounded exact frame convergence under all
restrictions, signed trace replay, and the complete relation/log/descent path.

## Disproof track

Expose source-choice transitions, target-specific rebuild, exponential frames/SAT proofs, a
false/missed trace, lost replay, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy transition system with one labelled reachable target trace.
- Negative: remove one source edge; use unreachable targets, same abstract state/different occurrences, hard inductive-invariant families, and blind targets.
- Baselines: GRASP/CDCL, CEGAR, Savitch reachability, P1553 R4, rho, and BSGS.
- An invariant or counterexample is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with exact convergence/replay at four sizes/all strata, bounded frames/clauses, full rank/logs, 100 blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-bearing transition, reachability/replay error, cap violation, or any complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-d/q09_transition_compiler_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-d/q09_frame_generalization_cases.json`
- `ideas/rejected/preallocation/artifacts/20260722-d/q09_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not IC3/PDR. All evidence remains toy, heuristic, model-bound,
and novelty-unverified; an invariant, counterexample, or relation is not a breakthrough.

## Exactly one next executable action

1. Expand the proposed transition relation to primitive endpoint operations and preserve the first source-choice edge or exact predecessor query it contains.
