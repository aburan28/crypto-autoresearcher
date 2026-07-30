# Pre-ID duplicate draft — Havel-Hakimi degree source realization

## Status and claim labels

- Prospect: `20260721-d-L05`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: combinatorial_algorithm / conservative / conservative pre-ID screen.
- State: merged_rejected_degree_aggregate_loses_source_incidence.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a graphical degree sequence or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Compress an endpoint-derived relation hypergraph to degree data, apply Havel-Hakimi greedy degree reduction to construct an exact compatible source graph under restrictions, replay signed relations, and complete factor logs plus blind descent below rho and BSGS.

## Mechanism-new operation

The native operation removes a maximum-degree vertex and decrements the largest remaining degrees, recursively realizing a simple graph when the sequence is graphical. It counts only if endpoint degree data determines the relation incidences needed for exact restricted source replay; realizing an arbitrary supplied graph with the same degrees is a control.

## Assumptions

1. Public endpoint observables determine a compact degree sequence without enumerating relation incidences.
2. Degree realizations are source-faithful or admit a public canonical section preserving signed occurrences.
3. Coordinate restrictions update degree data without reconstructing the full hypergraph.
4. Greedy reductions preserve a witness whenever the restricted source fibre is nonempty.
5. One target-independent realization supports relation collection and fresh blind descent.

## Semantic fingerprint

`public_endpoint_relation_degrees | Havel_Hakimi_greedy_degree_reduction | canonical_restricted_incidence_realization | realized_edges_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact target-labelled existence and occurrence replay frontier.
2. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — aggregate degree/density summaries do not preserve individual restricted edges.
3. `ideas/rejected/ECDLP-IDEA-368_pippenger_spencer_nibble_source_packing_hypothesis.md` — degree conditions support approximate packing only after a hypergraph oracle exists.
4. `ideas/rejected/preallocation/20260721-c_K11_fiduccia_mattheyses_source_partition_refinement_preid_duplicate.md` — hypergraph nets are supplied source incidence and heuristic moves can strand witnesses.
5. `ideas/rejected/ECDLP-IDEA-361_robust_sunflower_core_source_router_hypothesis.md` — set-family aggregates and cores do not give exact source occurrence inversion.

## Closest primary literature

- Havel, [A remark on the existence of finite graphs](https://eudml.org/doc/19050), gives the original 1955 degree-reduction result for supplied finite degree data.
- Hakimi, [On realizability of a set of integers as degrees of the vertices of a linear graph I](https://doi.org/10.1137/0110037), characterizes and recursively realizes supplied graph degree sequences.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies algebraic endpoint equations rather than source-faithful degree data.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source makes degree data a canonical exact relation-source section; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, degree semantics, and the independent point verifier.
2. Construct endpoint-derived degree data and a canonical realization rule without enumerating source incidences, DLP labels, or target advice.
3. For each known-log target, make at most `5 ceil(log_2 B)+O(1)` restrictions, realize/replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, preserve failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge degree construction, sorting, reductions, ambiguity across realizations, restrictions, replay, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge degree setup/state in `a,a_m`, restricted realization/replay in `q,q_m`, and outputs/realization ambiguity in `o,u`. For `B=N^beta`, `beta=1/5`, density `delta,delta_t`, rank credit `r`, and log costs `ell,ell_m`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS are `0.50`.

## Likely fatal obstruction

Degree sequences forget which vertices are adjacent. Many nonisomorphic source graphs share the same degrees, and Havel-Hakimi selects one arbitrary realization that need not contain the actual relation or survive a restriction. Adding enough data to choose the source-faithful realization is essentially the missing incidence catalogue.

## Proof track

Prove endpoint degree data uniquely determines a canonical relation-incidence realization on all strata and restrictions, with charged reconstruction and a complete below-rho factor-base/descent path.

## Disproof track

Produce two source fibres with identical degree data but different restricted witnesses, or trace the canonicalization state; falsify on nonuniqueness, source incidence advice, false replay, or exponent at least `0.50`.

## Positive and negative controls

- Positive: uniquely realizable supplied degree sequences with labelled edges.
- Negative: degree-equivalent nonisomorphic graphs, unique witnesses absent from the greedy realization, empty restrictions, duplicate occurrences, and fresh targets.
- Baselines: explicit Havel-Hakimi, hypergraph containers, nibble packing, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only degree construction, four increasing sizes, zero false decisions across adversarial degree-equivalent fibres, exact all-strata replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on one ambiguous fibre, supplied incidence, lost witness, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l05_degree_sufficiency_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l05_havel_hakimi_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l05_cost_analysis.md`

## Interpretation boundary

This rejects degree-sequence compression as an exact endpoint source interface, not Havel-Hakimi graph realization. All finite controls remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
