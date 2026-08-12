# Pre-ID duplicate draft — Tarjan SCC source quotient

## Status and claim labels

- Prospect: `20260721-a-I09`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: graph_decomposition / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_transition_graph_and_component_provenance.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an SCC decomposition, path, or valid relation is not a breakthrough.

## Falsifiable hypothesis

Build an endpoint-derived directed transition graph and use Tarjan lowlink SCC decomposition to quotient mutually reachable partial sources while preserving exact restriction and occurrence lift, enabling sub-rho relation collection and blind descent.

## Mechanism-new operation

Tarjan's DFS lowlink invariant reports SCCs of a supplied directed graph in linear time. It counts only if vertices/arcs arise from public endpoints before source incidence and a component quotient preserves exact labelled paths; decomposing a supplied source graph is a backend control.

## Assumptions

1. A compact implicit transition graph is endpoint-derived with charged adjacency queries.
2. SCC equivalence coincides with interchangeable source completions under every restriction.
3. Component formation preserves signs, duplicates, exceptional strata, and exact occurrence paths.
4. Path replay from a quotient node is charged and source-complete.
5. One quotient serves known-log relations and fresh blind targets.

## Semantic fingerprint

`public_endpoint_transition_graph | Tarjan_DFS_lowlink_SCC | restriction_stable_component_nonemptiness | component_path_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-d_D11_union_find_source_connectivity_preid_duplicate.md` — connectivity consumes supplied edges and is weaker than equality.
2. `ideas/rejected/preallocation/20260720-c_G01_hopcroft_dfa_source_partition_preid_duplicate.md` — automaton minimization needs supplied transitions.
3. `ideas/rejected/ECDLP-IDEA-352_implicit_dominator_tree_source_router_hypothesis.md` — graph routers do not construct source arcs.
4. `ideas/rejected/ECDLP-IDEA-364_reingold_universal_exploration_source_router_hypothesis.md` — reachability still starts after graph construction.
5. `ideas/rejected/ECDLP-IDEA-369_gomory_hu_cut_tree_source_router_hypothesis.md` — graph quotients preserve aggregate connectivity, not source occurrences.

## Closest primary literature

- Tarjan, [Depth-first search and linear graph algorithms](https://doi.org/10.1137/0201010), computes SCCs and biconnected components of a supplied graph.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a sparse transition graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required endpoint graph or exact quotient lift; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, vertex/arc grammar, adjacency oracle, restrictions, signed strata, and verifier.
2. Build or expose the graph and SCC quotient from public endpoints without source enumeration or `Query2P1`.
3. For each known-log target, answer restricted reachability, replay a labelled signed path/tuple, verify the point sum, and record valid rows.
4. Preserve misses/dependencies; collect at least `max(d_FB+32,1000)` verified rows for actual `d_FB`, require rank `d_FB`, and solve logs.
5. Reuse unchanged graph/quotient for `Q+[t]P`, replay, compute `x`, and verify `[x]P=Q`.
6. Charge graph construction, every adjacency query, DFS stacks, lowlinks, quotient arcs, restrictions, path replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Let `a,a_m` charge graph/SCC construction and represented vertices/arcs; let `q,q_m` charge restricted reachability and path replay. With `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

SCC algorithms classify a supplied graph. Constructing exact elliptic compatibility arcs is the missing source-incidence problem, and mutually reachable partial states need not have the same restricted completions. Collapsing a component loses which labelled occurrence realizes a target unless path/source state is retained.

## Proof track

Derive a compact endpoint-only adjacency oracle and prove SCC equivalence is restriction-stable with exact all-occurrence path lift and complete costs.

## Disproof track

Trace every arc and quotient backpointer; falsify if any requires source enumeration, if two SCC-equivalent states differ under a restriction, or if replay materializes the component subgraph.

## Positive and negative controls

- Positive: supplied directed graphs with labelled paths and known SCC quotient.
- Negative: SCC-equivalent vertices with different labelled completions, shuffled arcs, duplicate paths, empty restrictions, and blind targets.
- Baselines: union-find, DFA minimization, explicit DFS, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require endpoint-only arcs, a proved restriction biconditional, exact lifts, four increasing sizes, full rank from `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied graph state, quotient collision, lost path, false answer, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i09_arc_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i09_scc_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i09_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint graph/quotient compiler, not Tarjan SCC. Toy graph results remain heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct a source graph.
