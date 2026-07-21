# Pre-ID duplicate draft — Fibonacci-heap source frontier

## Status and claim labels

- Prospect: 20260720-c-G07; no canonical ECDLP idea ID was allocated
- Class / risk / lane: amortized_priority_frontier / conservative / general pre-ID screen
- State: merged_rejected_priority_queue_backend_after_source_graph_construction
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; heuristic frontier claims are model-bound and novelty-unverified
- Breakthrough claim: none; faster decrease-key on a supplied graph is not an ECDLP result.

## Falsifiable hypothesis

Expose partial source states through a best-first frontier whose public key predicts exact completions. A Fibonacci heap would make repeated decrease-key operations amortized constant time and exact minimum extraction logarithmic, allowing source replay, relation collection, and blind descent below rho and BSGS.

## Mechanism-new operation

A Fibonacci heap lazily consolidates heap-ordered trees, using cuts and cascading cuts to achieve amortized O(1) insert/decrease-key and O(log n) delete-min on supplied items. It counts only if states, edges, and priorities are endpoint-derived without enumerating source continuations, and popped items give exact sources. Swapping it into an explicit search is a solver/backend control.

## Assumptions

1. A target-independent partial-state graph and admissible public priority exist.
2. State/edge generation, comparisons, cuts, marks, consolidation, failed pops, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. A minimum frontier item is biconditional with an exact source or all false pops are charged.
4. Heap records preserve signed occurrence genealogy under decrease-key and restrictions.
5. Fresh blind targets reuse the same graph/priority without target-trained scores.

## Semantic fingerprint

public_partial_source_frontier | Fibonacci_heap_cascading_cut_priority_queue | exact_restricted_best_first_search | heap_record_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted source-search frontier.
2. ideas/rejected/preallocation/20260719-d_D01_soft_heap_source_priority_router_preid_duplicate.md — a priority queue acts on supplied source items.
3. ideas/rejected/preallocation/20260720-b_F06_hungarian_primal_dual_source_assignment_preid_duplicate.md — faster augmenting selection still needs a source-bearing cost graph.
4. ideas/rejected/ECDLP-IDEA-352_implicit_dominator_tree_source_router_hypothesis.md — graph navigation does not construct predecessor/source edges.
5. ideas/rejected/ECDLP-IDEA-365_submodular_flow_source_decomposition_hypothesis.md — flow optimization consumes an explicit source-side network.

## Closest primary literature

- Fredman and Tarjan, [Fibonacci heaps and their uses in improved network optimization algorithms](https://doi.org/10.1145/28869.28874), improves priority-queue costs after graph items and updates are supplied.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations but no compact frontier graph or admissible key.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic frontier, exact priority/source theorem, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, partial states/edges, priority and tie rules, heap operations, restrictions, genealogy, and verifier.
2. Construct the target-independent frontier generator within B^(9/4+o(1)) without materializing the source graph.
3. For known-log R, pop/expand until an exact tuple is replayed under bounded restrictions; verify point equality before recording the unknown-log row.
4. Collect at least max(d_FB+32,1,000) verified rows, keep all pops/misses/dependencies, require rank d_FB, and solve factor logs.
5. Reuse unchanged state for Q+[t]P, recover a tuple, compute x, and verify the scalar.
6. Charge state/edge generation, every heap operation and false pop, restrictions, genealogy, replay, density, rank, logs, blind descent, bit time, and state.

## Full rho/BSGS cost model

Let I,D,X be inserts, decrease-keys, and delete-mins, C_gen item/edge generation work, n_h maximum heap size, Q_R restrictions, and C_inv replay. Native amortized heap work is O(I+D+X log n_h) on supplied items. Set a=log_N(T_frontier_build), a_m=log_N(M_frontier), q=log_N(Q_R((I+D)C_gen+X(log n_h+C_gen)+C_inv)+T_replay), and q_m=log_N(M_frontier+n_h+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho/BSGS are 0.50.

## Likely fatal obstruction

Priority-queue complexity is secondary to generating exact states, edges, and keys. If those objects are source-faithful, they materialize the missing search graph; if coarse, the heap pops false states and loses genealogy. Cascading cuts remove no P1553 obstruction. This is a backend merge with D01/F06/IDEAS 352/365.

## Proof track

Prove endpoint-only frontier generation, admissible exact priority, restriction-stable genealogy, sub-gate pop count, rank, and blind descent.

## Disproof track

Identify one source-bearing edge/key or a family requiring source-sized false pops despite constant-time decrease-key.

## Positive and negative controls

- Positive: a supplied labelled graph with admissible priorities and planted accepting paths.
- Negative: uninformative priorities, shuffled genealogy, many false low keys, empty/singleton restrictions, and blind targets.
- Baselines: binary heap, D01/F06/IDEAS 352/365, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only state/edge/key construction, exact replay, bounded total pop/edge costs, rank d_FB, 100 blind descents, and lambda,mu<=0.45.
- Falsify on one source-bearing frontier object, genealogy collision, source-sized pop count, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g07_frontier_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g07_priority_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g07_cost_analysis.md

## Interpretation boundary

This rejects the priority-queue substitution, not Fibonacci heaps. Fewer heap operations or a valid path is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g07_frontier_provenance.md; do not create it under this retired pre-ID screen.
