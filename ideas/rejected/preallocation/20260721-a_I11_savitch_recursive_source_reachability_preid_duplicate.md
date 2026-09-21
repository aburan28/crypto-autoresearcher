# Pre-ID duplicate draft — Savitch recursive source reachability

## Status and claim labels

- Prospect: `20260721-a-I11`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: recursive_reachability / high_risk / high-risk pre-ID screen.
- State: merged_rejected_supplied_graph_and_quasipolynomial_time.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; low-space reachability, a path, or relation is not a breakthrough.

## Falsifiable hypothesis

Use Savitch midpoint recursion over an implicit endpoint transition graph to answer exact restricted reachability with logarithmic-depth state and reconstruct signed source paths below rho/BSGS memory and time.

## Mechanism-new operation

Savitch deterministically tests reachability by recursively guessing all midpoint vertices, trading squared logarithmic space for quasi-polynomial time. It counts only if the vertex/adjacency grammar is endpoint-derived and midpoint search avoids source enumeration while returning exact labelled paths.

## Assumptions

1. Graph vertices and adjacency are public-endpoint-derived and succinct.
2. Midpoints can be enumerated or selected below the source-domain exponent.
3. Recursive restrictions preserve signed, duplicate, exceptional, and empty cases.
4. Accepted recursion reconstructs an exact occurrence path with charged time/state.
5. One graph grammar serves relations and blind descent.

## Semantic fingerprint

`public_endpoint_implicit_graph | Savitch_midpoint_reachability_recursion | exact_restricted_path_decision | recursion_trace_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-364_reingold_universal_exploration_source_router_hypothesis.md` — low-space traversal still assumes the graph.
2. `ideas/rejected/ECDLP-IDEA-376_eppstein_sidetrack_source_path_router_hypothesis.md` — path enumeration starts from supplied arcs.
3. `ideas/rejected/ECDLP-IDEA-352_implicit_dominator_tree_source_router_hypothesis.md` — implicit graph structure does not create source incidence.
4. `ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md` — recursive refinement repeats the missing decision oracle.
5. `ideas/rejected/preallocation/20260720-d_H05_astar_heuristic_source_search_preid_duplicate.md` — an informative search oracle already encodes completion.

## Closest primary literature

- Savitch, [Relationships between nondeterministic and deterministic tape complexities](https://doi.org/10.1016/S0022-0000(70)80006-X), gives deterministic low-space reachability via recursive midpoint enumeration.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a succinct source graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required endpoint graph or sub-rho midpoint selector; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, implicit vertex/adjacency grammar, path-length bound, restrictions, signed strata, and verifier.
2. Construct the graph grammar from public endpoints without materializing source vertices/edges or invoking `Query2P1`.
3. For known-log targets, run restricted midpoint recursion, reconstruct labelled signed points, verify their sum, and record valid rows.
4. Preserve failures/dependencies; collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged grammar for `Q+[t]P`, reconstruct, compute `x`, and verify `[x]P=Q`.
6. Charge grammar construction, all midpoint loops, repeated adjacency calls, recursion traces, restrictions, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Let `V=N^v` be the admitted vertex domain and `L` the path bound. Native recursion may require `V^(O(log L))` adjacency calls; put that full exponent in `q` and recursion state in `q_m`. With setup `a,a_m`, `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Savitch reduces space, not time or graph-construction cost. It enumerates all midpoint vertices at every level; on a source-addressable domain this is at least source-sized and typically quasi-polynomial. A succinct graph with exact adjacency is the missing completion oracle, and path replay preserves the same source state.

## Proof track

Derive an endpoint-only succinct graph plus a restricted midpoint family of sub-rho size, prove exact path/source lift, and bound the entire recursion within the complete exponents.

## Disproof track

Count midpoint candidates and adjacency calls at each level; falsify if the domain is source-addressable, if any adjacency call is `Query2P1`, or if total time reaches `N^0.5`.

## Positive and negative controls

- Positive: supplied sparse graphs with short paths and exact labelled midpoint recursion.
- Negative: layered graphs with broad midpoint sets, no-path targets, duplicate paths, shuffled labels, empty restrictions, and blind targets.
- Baselines: DFS/BFS, Reingold, A-star, explicit path tables, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require endpoint-only adjacency, sub-rho midpoint families, exact lifts, four increasing sizes, full rank from `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied graph state, source-sized midpoint loops, false reachability, lost path, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i11_midpoint_domain_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i11_reachability_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i11_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint graph/midpoint compiler, not Savitch's theorem. Toy low-space runs remain heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run recursive reachability.
