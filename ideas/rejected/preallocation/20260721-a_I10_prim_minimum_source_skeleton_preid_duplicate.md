# Pre-ID duplicate draft — Prim minimum source skeleton

## Status and claim labels

- Prospect: `20260721-a-I10`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: graph_optimization / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_metric_graph_and_nonpreserved_paths.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a minimum spanning tree, short path, or relation is not a breakthrough.

## Falsifiable hypothesis

Weight endpoint transition edges so a Prim minimum spanning tree preserves every exact restricted source connection and provides low-state occurrence paths for relation collection and blind descent below rho/BSGS.

## Mechanism-new operation

Prim greedily adds the minimum-weight edge crossing the current tree cut in a supplied weighted graph. It counts only if vertices, edges, and weights are endpoint-derived before source incidence and the tree preserves exact target-conditioned paths; an MST of a source graph is a representation control.

## Assumptions

1. A compact endpoint graph and exact weight rule are public and charged.
2. Every valid restricted source path survives in the MST or has an exact tree certificate.
3. Tree edges/backpointers preserve duplicates, signs, exceptional strata, and source occurrences.
4. Target restrictions do not require rebuilding the full graph/tree.
5. One state supports factor logs and blind descent.

## Semantic fingerprint

`public_endpoint_weighted_graph | Prim_cut_greedy_minimum_spanning_tree | exact_restricted_path_preservation | tree_path_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-b_F07_edmonds_arborescence_source_contraction_preid_duplicate.md` — a spanning structure requires supplied arcs.
2. `ideas/rejected/preallocation/20260720-c_G10_stoer_wagner_source_mincut_preid_duplicate.md` — cuts preserve connectivity summaries, not source tuples.
3. `ideas/rejected/preallocation/20260720-a_E05_parametric_maxflow_source_cut_preid_duplicate.md` — flow/cut backends assume the compatibility network.
4. `ideas/rejected/preallocation/20260719-d_D12_multilevel_coarsened_source_partition_preid_duplicate.md` — graph compression loses exact occurrence paths.
5. `ideas/rejected/ECDLP-IDEA-370_spectral_sparsification_source_router_hypothesis.md` — approximate connectivity is not exact source replay.

## Closest primary literature

- Prim, [Shortest connection networks and some generalizations](https://doi.org/10.1002/j.1538-7305.1957.tb01515.x), builds a minimum connection network from supplied terminals/links.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations without a weighted compatibility graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source proves an exact elliptic path-preserving MST representation; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, graph/weight grammar, tie-breaking, restrictions, signed strata, and verifier.
2. Build the weighted graph and MST from public endpoints without source enumeration or `Query2P1`.
3. For known-log targets, answer restricted path existence, replay labelled signed points along tree certificates, verify the point sum, and record valid rows.
4. Retain misses/dependencies; collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged tree for `Q+[t]P`, replay, compute `x`, and verify `[x]P=Q`.
6. Charge graph/weight construction, heap/cut work, tie cases, restrictions, path replay, density, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

Let `a,a_m` charge graph/MST construction and state; let `q,q_m` charge restricted tree queries, non-tree fallback, and replay. With `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Prim compresses a supplied weighted graph to connectivity, but an MST does not preserve all paths or target-conditioned compatible tuples. Constructing edges/weights already requires source incidence, and keeping non-tree occurrence certificates restores the original graph.

## Proof track

Derive endpoint-only graph/weights and prove an MST path biconditional for every restriction with exact all-occurrence lift and complete costs.

## Disproof track

Find a restriction whose only valid source path uses a deleted edge or trace any edge/weight to source enumeration; falsify if non-tree fallback restores full state.

## Positive and negative controls

- Positive: supplied tree metrics where all relevant paths lie in the unique MST and carry labels.
- Negative: equal-weight cycles, deleted-edge-only restricted paths, duplicate occurrences, shuffled backpointers, empty restrictions, and blind targets.
- Baselines: full graph, arborescence/mincut/sparsification owners, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require endpoint-only graph construction, a restriction path biconditional, exact lifts, four increasing sizes, rank `d_FB` from `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied graph state, one deleted necessary path, lost occurrence, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i10_tree_path_biconditional_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i10_mst_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i10_cost_analysis.md`

## Interpretation boundary

This rejects the elliptic MST skeleton, not Prim's algorithm. Toy path preservation remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not build the graph or tree.
