# Pre-ID duplicate draft — Suurballe disjoint source paths

## Status and claim labels

- Prospect: 20260720-b-F08; no canonical ECDLP idea ID was allocated
- Class / risk / lane: disjoint_shortest_path_routing / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_network_and_path_disjointness_not_source_compatibility
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; diversified paths in a supplied network are not scalar recovery.

## Falsifiable hypothesis

Route complementary elliptic partial sums through two vertex-disjoint paths whose common terminals encode a target. Suurballe reweighting and residual-path cancellation would recover compatible labelled routes, giving relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Suurballe finds minimum-total-length disjoint paths in a supplied nonnegatively weighted network through repeated shortest-path labeling, reweighting, residual reversal, and cancellation. It counts only if the network is endpoint-derived without source edges and disjointness plus shared terminals is biconditional with a five-source tuple. Routing on an explicit source network is a control.

## Assumptions

1. A compact target-independent network encodes all signed and exceptional source strata exactly.
2. Nodes/arcs/weights, shortest paths, reweighting, residual updates, cancellation, restrictions, replay, rank, logs, descent, time, and memory are charged.
3. Disjoint routes are jointly source-compatible rather than merely graph-disjoint.
4. Path cancellation retains point-labelled ancestry under arbitrary restrictions.
5. One frozen network serves known-log and fresh blind targets without target-specific arcs.

## Semantic fingerprint

public_partial_sum_network | Suurballe_reweight_residual_cancellation | exact_restricted_disjoint_terminal_paths | cancelled_routes_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 is the exact restricted-existence residual.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 requires a public source resolver.
3. ideas/rejected/ECDLP-IDEA-203_matrix_tree_arborescence_source_extractor_hypothesis.md — source paths require an explicit transition graph.
4. ideas/rejected/ECDLP-IDEA-352_implicit_dominator_tree_source_router_hypothesis.md — path structure assumes the missing predecessor graph.
5. ideas/rejected/ECDLP-IDEA-376_eppstein_sidetrack_source_path_router_hypothesis.md — path routing after graph construction is a backend.

## Closest primary literature

- Suurballe, [Disjoint paths in a network](https://doi.org/10.1002/net.3230040204), finds diversified routes in a supplied weighted network; it does not construct elliptic transition arcs or source labels.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a disjoint-path network.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the endpoint network, compatibility theorem, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, network/weights, terminals, residual/cancellation rules, restrictions, and verifier.
2. Build target-independent network/state within B^(9/4+o(1)) without materializing source paths.
3. For R=[kappa]P, find exact restricted routes and replay labelled A_i,epsilon_i in at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P, then record sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, preserve failures/dependencies, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, recover routes, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge network construction, every shortest-path iteration, reweighting/residual/cancellation step, restrictions, replay, rank, logs, descent, checks, bit time, and memory.

## Full rho/BSGS cost model

Let n,m be network sizes, freeze the named mechanism to K=2 routes, let C_arc be arc construction, T_SP(n,m) one charged shortest-path computation, Q_R restrictions, and C_inv route inversion. The stated two-route Suurballe path costs two shortest-path iterations plus residual transforms. Set a=log_N(T_network+m C_arc), a_m=log_N(n+m), q=log_N(Q_R(2 T_SP+O(m)+C_inv+T_rebuild)+T_replay), and q_m=log_N(n+m+M_SP+M_inv). Any K>2 generalization is a separate algorithmic claim and must be cited and charged separately. With beta=1/5 and delta,delta_t,r,o,u,ell,ell_m:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds. Rho and BSGS remain 0.50.

## Likely fatal obstruction

The network or arc oracle is source incidence. Vertex-disjointness does not enforce five-way elliptic compatibility, while gadgets that do so materialize tuples. Residual cancellation can erase occurrence ancestry, and restrictions rebuild the network. This merges with IDEAS 203/352/376.

## Proof track

Construct a compact endpoint-only network and exact disjoint-path/source theorem stable under restrictions, with point-faithful cancellation inversion and complete costs.

## Disproof track

Give two disjoint routes that splice incompatible source fragments or expose any source-bearing arc/terminal construction.

## Positive and negative controls

- Positive: a supplied network with two planted labelled disjoint routes.
- Negative: disjoint but source-incompatible paths, cancellation ancestry collisions, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEAS 203/352/376, explicit network routing, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only network, exact restriction-stable route/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source edge, incompatible route pair, ancestry loss, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f08_network_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f08_path_compatibility_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f08_cost_analysis.md

## Interpretation boundary

This rejects the elliptic network encoding, not Suurballe routing. Correct disjoint paths or one relation are not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f08_network_provenance.md; do not create it under this retired pre-ID screen.
