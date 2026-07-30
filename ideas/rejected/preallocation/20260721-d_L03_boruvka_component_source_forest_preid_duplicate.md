# Pre-ID duplicate draft — Boruvka component source forest

## Status and claim labels

- Prospect: `20260721-d-L03`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: graph_algorithm / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_metric_edges_and_lossy_forest_skeleton.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a minimum forest or verified relation is not an ECDLP result.

## Falsifiable hypothesis

Construct a public weighted compatibility graph on endpoint-derived partial sources, apply Boruvka componentwise cheapest-edge merging to obtain a sparse exact source forest stable under restrictions, replay relation paths, and finish factor logs plus blind descent below rho and BSGS.

## Mechanism-new operation

The native operation lets every current component select its cheapest outgoing edge and contracts all selected edges in parallel. It counts only if the vertices, compatibility edges, weights, and relation path lift are endpoint-derived and the forest preserves every restricted witness; using a supplied source graph is an MST backend control.

## Assumptions

1. Public endpoint data provides exact weighted compatibility edges without enumerating source pairs.
2. Cheapest outgoing edges preserve at least one witness for every nonempty restriction.
3. Parallel contractions preserve signed occurrence identity and exceptional strata.
4. Forest paths replay complete signed decompositions with charged ambiguity.
5. One target-independent forest supports both relation collection and fresh masked targets.

## Semantic fingerprint

`public_endpoint_compatibility_graph | Boruvka_component_cheapest_edge_contraction | restriction_stable_source_forest | forest_path_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable existence and occurrence-return frontier.
2. `ideas/rejected/preallocation/20260721-a_I10_prim_minimum_source_skeleton_preid_duplicate.md` — an MST skeleton begins with supplied source edges and can discard witnesses.
3. `ideas/rejected/preallocation/20260721-c_K10_christofides_source_tour_preid_duplicate.md` — metric-tree construction does not create exact relation incidence.
4. `ideas/rejected/preallocation/20260720-b_F07_edmonds_arborescence_source_contraction_preid_duplicate.md` — directed contraction likewise processes a represented graph.
5. `ideas/rejected/ECDLP-IDEA-370_spectral_sparsification_source_router_hypothesis.md` — approximate/spectral edge preservation does not imply exact restricted witness preservation.

## Closest primary literature

- Boruvka's two 1926 papers, available in English translation with the originals in [Otakar Boruvka on minimum spanning tree problem](https://doi.org/10.1016/S0012-365X(00)00224-7), introduce componentwise cheapest-edge merging for a supplied weighted network.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than a sparse exact metric graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the endpoint compatibility graph, restriction-stable forest, or occurrence inverse; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, signed decks, restrictions, exceptional strata, weight rule, and independent point verifier.
2. Construct and certify endpoint-derived vertices, weighted edges, components, and occurrence backpointers without source-pair enumeration or scalar labels.
3. For each known-log target, answer at most `5 ceil(log_2 B)+O(1)` restrictions through the forest, replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, preserve failures/dependencies, collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge edge construction, weight evaluation, contractions, restriction updates, replay, density, rank, logs, blind descent, bit time, and memory.

## Full rho/BSGS cost model

Charge graph/forest setup in `a,a_m`, restricted lookup/replay in `q,q_m`, and output/ambiguity in `o,u`. For `B=N^beta`, `beta=1/5`, density `delta,delta_t`, rank credit `r`, and log costs `ell,ell_m`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS are `0.50`.

## Likely fatal obstruction

Boruvka reduces a supplied weighted graph to a spanning forest; it neither constructs elliptic compatibility edges nor preserves every source path. A cheapest edge has no known scalar-blind relation to future completability. Exact witness preservation across all restrictions can require retaining the discarded edges or a source-sized certificate, erasing the claimed compression.

## Proof track

Provide an endpoint-only metric and edge oracle with a theorem that Boruvka contractions preserve at least one occurrence in every nonempty restriction, plus an exact all-strata path lift and full below-rho cost.

## Disproof track

Construct two source fibres with the same endpoint/weights but different unique witnesses, or trace edge generation; falsify on explicit pair edges, lost restricted witnesses, ambiguous replay, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied weighted graphs with planted labelled relation paths preserved by the MST.
- Negative: equal-weight ties, unique witnesses on non-MST edges, disconnected restrictions, duplicate endpoints, and fresh targets.
- Baselines: explicit Boruvka, Prim, Edmonds, spectral sparsification, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only edge construction, four increasing sizes, zero false decisions, exact replay on all strata, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied edges, one lost witness, false restriction answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l03_edge_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l03_boruvka_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l03_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only Boruvka transplant, not minimum-spanning-forest algorithms. All finite forests remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
