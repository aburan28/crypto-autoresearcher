# Pre-ID duplicate draft — Bron–Kerbosch source clique

## Status and claim labels

- Prospect: 20260720-b-F05; no canonical ECDLP idea ID was allocated
- Class / risk / lane: pivoted_clique_enumeration / high-risk / high-risk pre-ID screen
- State: merged_rejected_explicit_compatibility_graph_and_exponential_output
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; enumerating cliques in a supplied graph is not scalar recovery.

## Falsifiable hypothesis

Represent signed factor choices as a multipartite compatibility graph whose five-cliques are exact decompositions. Bron–Kerbosch pivoting would prune nonextendible vertices, enumerate a relation clique with provenance, and support blind descent below rho and BSGS.

## Mechanism-new operation

Bron–Kerbosch recursively maintains a growing clique R, candidate set P, excluded set X, and pivots to reduce branches while enumerating maximal cliques of a supplied graph. It counts only if the compatibility graph is endpoint-derived below the gate and clique adjacency is cheaper than Query2P1. Running it on explicit source edges is a control.

## Assumptions

1. A compact public graph has a five-clique/source biconditional for every signed and exceptional stratum.
2. Vertices, edges, adjacency, pivot selection, recursion, output, restrictions, replay, rank, logs, descent, time, and memory are charged.
3. Maximal-clique output contains exact five-source witnesses without enumerating irrelevant larger structures.
4. Arbitrary deck restrictions update P/X without rebuilding source adjacency.
5. One graph serves known-log and fresh blind targets without target-specific edges.

## Semantic fingerprint

public_multipartite_compatibility_graph | Bron_Kerbosch_pivot_recursion | exact_restricted_five_clique | clique_vertices_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 is the exact restricted-existence residual.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 requires a public source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md — supplied relation hypergraphs do not generate rare edges.
4. ideas/rejected/ECDLP-IDEA-343_avis_fukuda_reverse_search_source_enumerator_hypothesis.md — local adjacency/parent operations already encode sources.
5. ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md — graph compatibility gadgets materialize source incidence.

## Closest primary literature

- Bron and Kerbosch, [Algorithm 457: finding all cliques of an undirected graph](https://doi.org/10.1145/362342.362367), enumerates cliques of a supplied graph; it does not construct elliptic compatibility edges.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but no sparse clique graph.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the graph, cheap adjacency, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, graph constructor, adjacency/pivot/order, restrictions, clique filter, and verifier.
2. Construct target-independent vertices/edges within B^(9/4+o(1)) without source-tuple materialization.
3. For R=[kappa]P, find an exact restricted clique, replay labelled A_i,epsilon_i using at most 5 ceil(log_2 B)+O(1) queries plus failed siblings, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, preserve failed branches/dependencies, and solve only after the rank gate.
5. Reuse unchanged graph/state for R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge graph construction, all adjacency/pivot operations, recursive calls, maximal-clique output, restrictions, replay, rank, logs, descent, checks, bit time, and memory.

## Full rho/BSGS cost model

Let n,m be graph vertices/edges, R_BK recursive calls, C_adj adjacency work, C_out clique-output work, Q_R restrictions, and C_inv inversion. Set a=log_N(T_graph+n+m), a_m=log_N(n+m), q=log_N(Q_R(R_BK C_adj+C_out+C_inv)+T_replay), and q_m=log_N(n+m+M_stack+M_inv). R_BK can be exponential and the maximal-clique output itself can be 3^(n/3). With beta=1/5 and the common delta,delta_t,r,o,u,ell,ell_m:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

Exact adjacency is source compatibility, so building the graph or testing an edge invokes the missing predicate. Pairwise compatibility is not sufficient for a five-way elliptic sum without tuple gadgets, while faithful gadgets materialize sources. Pivoting changes enumeration order, not information or worst-case output. This merges with IDEAS 200/343/382.

## Proof track

Construct a sub-gate endpoint graph with a clique/source biconditional and bounded pivot tree under all restrictions, then close replay and descent.

## Disproof track

Show one false clique from pairwise-compatible fragments, one source-bearing adjacency test, or a family with exponential recursive/output cost.

## Positive and negative controls

- Positive: a supplied multipartite graph with one planted labelled five-clique.
- Negative: pairwise-compatible but globally invalid colors, Moon–Moser output families, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEAS 200/343/382, explicit clique search, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph/adjacency, exact restriction-stable clique/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source edge, false clique, exponential output beyond cap, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f05_graph_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f05_pairwise_global_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f05_cost_analysis.md

## Interpretation boundary

This rejects the elliptic graph encoding, not Bron–Kerbosch. Correct clique enumeration or one relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f05_graph_provenance.md; do not create it under this retired pre-ID screen.
