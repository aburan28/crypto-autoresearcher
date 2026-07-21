# Pre-ID duplicate draft — Stoer–Wagner source min-cut

## Status and claim labels

- Prospect: 20260720-c-G10; no canonical ECDLP idea ID was allocated
- Class / risk / lane: deterministic_global_mincut / conservative / general pre-ID screen
- State: merged_rejected_supplied_source_graph_and_cut_not_witness
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; cut-gap extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; finding a minimum cut in a supplied graph is not an ECDLP break.

## Falsifiable hypothesis

Encode partial-source compatibility as a weighted undirected graph in which the global minimum cut separates exactly one accepting source branch. Stoer–Wagner phase contractions would recover the branch under restrictions, enabling relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Stoer–Wagner repeatedly runs maximum-adjacency phases, records a phase cut, and contracts the last two vertices to find a global min-cut without max-flow. It counts only if vertices/weights are endpoint-derived without source edges, a unique cut is biconditional with a signed source, and contraction retains occurrence replay. Running it on an explicit relation graph is a control.

## Assumptions

1. A compact public graph and nonnegative weights cover every signed and exceptional source stratum.
2. Vertex/edge/weight construction, phase searches, contractions, ties, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. The minimum cut has a proved gap and exact source biconditional, not merely a correlation.
4. Restrictions preserve the graph family without rebuilding source edges.
5. Fresh blind targets use the same construction without target-specialized weights.

## Semantic fingerprint

public_partial_source_weighted_graph | Stoer_Wagner_maximum_adjacency_contractions | exact_restricted_min_cut | cut_partition_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted source frontier.
2. ideas/rejected/ECDLP-IDEA-395_karger_stein_random_contraction_source_router_hypothesis.md — min-cut contraction assumes a supplied source graph.
3. ideas/rejected/ECDLP-IDEA-369_gomory_hu_cut_tree_source_router_hypothesis.md — cut trees summarize supplied capacities but do not return rare tuples.
4. ideas/rejected/preallocation/20260720-a_E05_parametric_maxflow_source_cut_preid_duplicate.md — source-dependent cut capacities restate Query2P1.
5. ideas/rejected/ECDLP-IDEA-380_agm_linear_graph_sketch_source_router_hypothesis.md — graph sketches lose edge/source provenance.

## Closest primary literature

- Stoer and Wagner, [A simple min-cut algorithm](https://doi.org/10.1145/263867.263872), finds a global min-cut of a supplied weighted graph in repeated maximum-adjacency phases.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint constraints but no cut graph or source-gap theorem.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the graph, cut/source biconditional, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, graph/weight construction, phase and tie rules, restriction updates, contraction provenance, and verifier.
2. Construct target-independent graph state within B^(9/4+o(1)) without explicit source compatibility edges.
3. For known-log R, run restricted min-cut phases, lift a cut to A_i,epsilon_i, verify point equality, and record a row.
4. Collect at least max(d_FB+32,1,000) verified rows, keep every cut/tie/failure/dependency, require rank d_FB, then solve factor logs.
5. Reuse unchanged state for Q+[t]P, recover a tuple from a cut, compute x, and verify [x]P=Q.
6. Charge graph construction, all edges/weights, phases/contractions, restrictions, provenance, verification, density, rank, logs, blind descent, bit time, and state.

## Full rho/BSGS cost model

Let V,E be represented graph sizes, C_edge edge/weight generation, Q_R restrictions, C_SW(V,E) the full min-cut phase work, and C_inv cut/source lift. The standard implementation is O(VE+V^2 log V) with appropriate priority queues on a supplied graph; dense matrix implementations are O(V^3). Set a=log_N(T_graph+E C_edge), a_m=log_N(M_graph), q=log_N(Q_R(C_SW+C_inv)+T_replay), and q_m=log_N(M_graph+V+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho/BSGS are 0.50.

## Likely fatal obstruction

Constructing exact graph edges/weights is the missing source predicate. A cut is a partition, not a five-source witness; coarse graphs admit cuts assembled from incompatible fragments, while faithful graphs materialize incidence. Deterministic contractions remove no information-flow obstruction. This merges with IDEAS 395/369/380 and E05.

## Proof track

Prove endpoint-only graph/weights, a restriction-stable cut-gap/source biconditional, exact contraction lift, rank, and blind descent under complete costs.

## Disproof track

Give two source instances with the same public weighted graph and different accepting tuples, or a minimum cut with no exact relation.

## Positive and negative controls

- Positive: supplied weighted graphs with planted unique labelled min-cuts.
- Negative: equal cuts, cut-without-witness graphs, shuffled edge ancestry, empty/singleton restrictions, exceptional and blind targets.
- Baselines: Karger-Stein/Gomory-Hu/parametric flow, full graph scan, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph, exact cut/source lift, proved gap, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing edge/weight, false cut, provenance loss, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g10_graph_weight_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g10_cut_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g10_cost_analysis.md

## Interpretation boundary

This rejects the elliptic min-cut graph, not Stoer–Wagner. A correct cut or planted source is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g10_graph_weight_provenance.md; do not create it under this retired pre-ID screen.
