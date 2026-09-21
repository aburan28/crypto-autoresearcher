# Pre-ID duplicate draft — Edmonds arborescence source contraction

## Status and claim labels

- Prospect: 20260720-b-F07; no canonical ECDLP idea ID was allocated
- Class / risk / lane: directed_branching_contraction / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_supplied_transition_digraph_and_nonfaithful_contraction
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; an optimum branching in a supplied digraph is not scalar recovery.

## Falsifiable hypothesis

Build a directed partial-sum graph rooted at a target label and assign public edge weights so an optimum arborescence contains a valid five-source root path. Chu–Liu/Edmonds cycle contraction and expansion would return exact factor occurrences for relations and blind descent below rho and BSGS.

## Mechanism-new operation

The directed branching algorithm selects minimum incoming edges, contracts directed cycles, adjusts weights, solves the quotient, and expands an optimum branching of a supplied weighted digraph. It counts only if vertices, arcs, and weights are endpoint-derived without source paths and expansion returns point-faithful occurrences. Solver substitution on an explicit transition graph is a control.

## Assumptions

1. A compact target-independent weighted digraph represents every signed and exceptional source stratum exactly.
2. Vertex/arc construction, weights, cycle detection/contraction/expansion, restrictions, replay, rank, logs, descent, time, and memory are charged.
3. An optimum root path is biconditional with exact source existence, not merely low aggregate weight.
4. Cycle contraction preserves occurrence ancestry and arbitrary source restrictions.
5. One frozen graph serves known-log and fresh blind targets without target-specific arcs or post-hoc weights.

## Semantic fingerprint

public_directed_partial_sum_graph | Chu_Liu_Edmonds_cycle_contraction | exact_restricted_optimum_root_path | expanded_arcs_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted existence and source replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source resolver.
3. ideas/rejected/ECDLP-IDEA-203_matrix_tree_arborescence_source_extractor_hypothesis.md — arborescence aggregation starts from the source-transition graph.
4. ideas/rejected/preallocation/20260719-d_D05_wilson_cycle_popping_source_tree_preid_duplicate.md — random tree paths consume a supplied transition graph.
5. ideas/rejected/ECDLP-IDEA-369_gomory_hu_cut_tree_source_router_hypothesis.md — tree summaries of supplied graphs lose source paths.

## Closest primary literature

- Edmonds, [Optimum branchings](https://doi.org/10.6028/jres.071B.032), optimizes a supplied weighted directed graph; it does not construct elliptic transition arcs or a source inverse.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations, not a compact branching graph.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the endpoint graph, path/source theorem, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, digraph/weight constructor, root, contraction/tie rule, restrictions, and verifier.
2. Construct target-independent graph/state within B^(9/4+o(1)) without enumerating source transitions.
3. For R=[kappa]P, solve exact restricted branchings and replay labelled A_i,epsilon_i in at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P, then record sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB for actual factor-log unknowns, preserve cycles/ties/failures, and only then solve.
5. Reuse unchanged graph/state for R=Q+[t]P, recover a path, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge all vertices/arcs/weights, contractions/expansions, restrictions, path extraction, replay, rank, logs, descent, scalar checks, bit complexity, and memory.

## Full rho/BSGS cost model

Let n,m be graph sizes, C_arc exact arc/weight work, Q_R restrictions, T_ARB the charged branching implementation, and C_inv expansion-to-source work. A direct contraction implementation may cost O(nm) time and O(n+m) state after reading all arcs. Set a=log_N(T_graph+m C_arc), a_m=log_N(n+m), q=log_N(Q_R(T_rebuild+T_ARB+C_inv)+T_replay), and q_m=log_N(n+m+M_contract+M_inv). With beta=1/5 and delta,delta_t,r,o,u,ell,ell_m:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

The directed transition graph is the missing source catalogue. Aggregate vertices let an optimum branching splice arcs from incompatible occurrences; faithful vertices/arcs materialize partial tuples. Public weights do not make a relation path uniquely optimal without post-hoc source knowledge, and restrictions rebuild cycles. This merges with IDEA-203/369 and pre-ID D05.

## Proof track

Construct an endpoint-only sub-gate digraph and weight theorem with exact branching-path/source biconditional and restriction-stable expansion, then close costs.

## Disproof track

Show one source-bearing arc/weight, one expanded path with incompatible ancestry, or a restriction causing source-sized graph reconstruction.

## Positive and negative controls

- Positive: a supplied weighted digraph with one planted labelled optimum arborescence path.
- Negative: equal quotient cycles with different ancestry, incompatible arc splicing, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEA-203/369, pre-ID D05, explicit arborescence solvers, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph/weights, exact restricted branching/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source arc, false optimum path, contraction ancestry loss, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f07_graph_weight_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f07_contraction_ancestry_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f07_cost_analysis.md

## Interpretation boundary

This rejects the elliptic branching encoding, not Edmonds' algorithm. A correct branching or one relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f07_graph_weight_provenance.md; do not create it under this retired pre-ID screen.
