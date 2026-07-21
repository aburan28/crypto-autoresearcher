# Pre-ID duplicate draft — Baker-layered source graph

## Status and claim labels

- Prospect: 20260720-a-E04; no canonical ECDLP idea ID was allocated
- Class / risk / lane: planar_layer_decomposition / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_supplied_planar_source_graph_and_deleted_witnesses
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; a planar approximation scheme or bounded-width solve is not scalar recovery.

## Falsifiable hypothesis

Embed signed partial-sum compatibility as a planar layered graph, delete one residue class of breadth-first layers, and solve exact bounded-outerplanarity subinstances. Cycling the deleted class would preserve at least one complete relation path, permitting exact source replay, factor logs, and fresh blind descent below rho and BSGS.

## Mechanism-new operation

Baker's method partitions a supplied planar graph by BFS layers, removes one congruence class, and solves the resulting bounded-outerplanarity pieces. It counts only if the planar graph is constructed endpoint-only below the gate, a complete accepting path survives in a charged layer choice, and piece solutions invert to elliptic sources. Layering an explicit source-incidence graph is a control.

## Assumptions

1. A target-independent planar compatibility graph represents all signed and exceptional addition strata exactly.
2. Graph construction, embedding, BFS layers, deleted classes, piece decompositions, dynamic programs, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. At least one charged deletion class preserves every vertex and edge of an accepting source path without recombination.
4. Piece states retain point-faithful source ancestry and exact absence semantics.
5. One frozen graph serves known-log and fresh scalar-blind targets without target-specific remeshing or explicit tuple edges.

## Semantic fingerprint

public_planar_compatibility_graph | Baker_BFS_layer_deletion | exact_bounded_outerplanar_source_path | piece_state_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact subset-stable target-label existence.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing exact source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-338_chordal_network_source_elimination_hypothesis.md — a supplied compatibility graph and its bags retain source incidence.
4. ideas/rejected/ECDLP-IDEA-363_weitz_self_avoiding_walk_source_tree_hypothesis.md — tree unfolding begins from a supplied graph and can lose source-consistent cycles.
5. ideas/rejected/ECDLP-IDEA-386_twin_width_red_edge_contraction_source_quotient_hypothesis.md — graph contraction/quotients merge rare source ancestry.

## Closest primary literature

- Baker, [Approximation algorithms for NP-complete problems on planar graphs](https://doi.org/10.1145/174644.174650), decomposes a supplied planar graph by layers and obtains approximation schemes; it does not construct an elliptic compatibility graph.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) supplies endpoint equations, not a planar source graph.
- Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) supplies the matched baseline.

No checked source proves planarity, exact witness preservation, or complete ECDLP descent for this representation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, graph constructor, planar embedding, layer modulus, deletion schedule, piece solver, restrictions, and verifier.
2. Construct target-independent graph/decomposition state within B^(9/4+o(1)) without enumerating source tuples or edges.
3. For known-log R=[kappa]P, solve every charged layer choice and restriction until one exact source path is replayed; for labelled points A_i with signs epsilon_i verify sum_i epsilon_i A_i=[kappa]P and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; preserve failures/dependencies, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged graph/decomposition for fresh R=Q+[t]P, recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge graph generation, embeddings, all deletion classes, dynamic programs, negative pieces, at most 5 ceil(log_2 B)+O(1) replay restrictions plus siblings, rank, logs, descent, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge vertices, edges, embedding, layers, decompositions, and piece tables; q,q_m charge target labels, every deleted-class solve, restrictions, negative pieces, bisection, and replay. Let delta,delta_t be reciprocal verified relation/target densities after layer survival, r independent-rank credit, o output, u deleted-class ambiguity/recombination/repairs, and ell,ell_m factor-log time/state.

Let n,m be graph vertices/arcs, k the layer modulus, h the number of layer residues touched by a witness, and f(k) the exact bounded-width dynamic-program state factor. Building costs at least Theta(n+m); trying all residues costs at least Theta(k f(k)n) after embedding, with piece-table memory Theta(f(k)n) unless streamed and recomputed. Set a=log_N(T_graph+n+m), a_m=log_N(M_graph), q=log_N(k f(k)n+T_restriction+T_replay), and q_m=log_N(M_piece). A witness is guaranteed to avoid some deleted residue only when h<k; Baker's approximation theorem by itself does not guarantee exact path survival. Map n,m,k,f(k),h to B before assigning numerical exponents.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), total fresh piece solving/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are exponent 0.50. All source edges and all O(k) deletion classes are charged; approximation ratios do not count as exact existence.
Every fresh masked-target all-residue solve and replay must independently fit <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion requires h<k on every accepted witness, exact rather than approximate piece semantics, and one-sided 95% upper bounds below build/state/fresh/complete gates at four increasing B values.

## Likely fatal obstruction

Baker layering acts after a planar graph is supplied. Constructing exact source-compatibility edges is the missing incidence catalogue, while endpoint-only quotient vertices permit invalid path recombination. Deleting layers may remove the unique witness; trying every class restores graph-wide work, and approximation of an objective does not certify exact target existence. This merges with IDEAS 338/363/377/386.
Within this cohort it collides with E05 because both begin from a supplied exact source graph and merely change the downstream graph primitive.

## Proof track

Give an endpoint-only sub-gate planarization theorem, exact accepting-path biconditional on all charts, a survival/inverse theorem for a charged deletion class, and close rank and blind descent.

## Disproof track

Exhibit one source-bearing edge, a nonplanar forced minor, two quotient paths that recombine invalid sources, or a unique accepting path cut by every admissible cheap deletion schedule.

## Positive and negative controls

- Positive: a supplied planar layered graph with redundant planted source-labelled accepting paths.
- Negative: a unique path crossing every deletion residue, equal quotient paths with incompatible source colors, nonplanar incidence minors, absent targets, exceptional charts, restrictions, and blind targets.
- Baselines: IDEAS 338/363/377/386, exact dynamic programming on explicit graphs, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only planar graph construction, exact all-strata path/source biconditional, charged deletion survival, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source edge, one invalid recombination or lost singleton, target-specific remeshing, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e04_graph_edge_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e04_layer_deletion_path_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e04_cost_analysis.md

## Interpretation boundary

This rejects the transplant, not Baker's technique. Toy planar solving or an approximation guarantee is not an ECDLP breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e04_graph_edge_provenance.md and derive every vertex and edge of one complete signed-addition chart before any solver run.
