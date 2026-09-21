# Pre-ID duplicate draft — PageRank source stationary flow

## Status and claim labels

- Prospect: 20260720-c-G11; no canonical ECDLP idea ID was allocated
- Class / risk / lane: damped_stationary_flow / high-risk / general pre-ID screen
- State: merged_rejected_supplied_transition_graph_and_aggregate_scores
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; a high stationary score is not an exact relation or scalar.

## Falsifiable hypothesis

Build a target-independent directed graph of partial relation states and use a damped random-surfer stationary distribution to concentrate mass on states with many accepting continuations. Ranked states would yield exact signed sources under restrictions, full-rank relations, and fresh blind descent below rho and BSGS.

## Mechanism-new operation

PageRank computes the stationary vector of a supplied damped link graph by repeated sparse matrix-vector multiplication. It counts only if the graph is endpoint-derived without source edges, high score has a proved exact-source density, occurrence genealogy survives aggregation, and exact negatives exist. Ranking an explicit state graph is a control.

## Assumptions

1. A compact public directed transition graph covers all signed and exceptional source strata.
2. Edge generation, dangling-node rule, damping, iterations/precision, sorting, restrictions, sampling, verification, replay, rank, logs, descent, bit time, and memory are charged.
3. Stationary mass yields a quantified verified-source hit rate, not post-hoc correlation.
4. Aggregated state mass retains occurrence genealogy and exact restriction semantics.
5. The same graph and damping serve fresh blind targets without retraining.

## Semantic fingerprint

public_partial_source_link_graph | PageRank_damped_stationary_power_iteration | ranked_restricted_source_search | stationary_state_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 requires exact restricted existence, not a score.
2. ideas/rejected/ECDLP-IDEA-316_doob_h_transform_endpoint_source_bridge_hypothesis.md — tilted transitions require a source-bearing harmonic function.
3. ideas/rejected/ECDLP-IDEA-370_spectral_sparsification_source_router_hypothesis.md — spectral graph summaries consume explicit edges and lose sources.
4. ideas/rejected/ECDLP-IDEA-394_weisfeiler_leman_tuple_refinement_source_quotient_hypothesis.md — graph aggregation merges source genealogies.
5. ideas/rejected/ECDLP-IDEA-387_balanced_truncation_hankel_mode_source_reduction_hypothesis.md — dominant aggregate modes do not isolate rare source occurrences.

## Closest primary literature

- Page, Brin, Motwani, and Winograd, [The PageRank citation ranking: bringing order to the Web](https://ilpubs.stanford.edu/422/), computes importance on a supplied link graph using a random-surfer model.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint constraints but no compact transition graph or mass/source theorem.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic graph, source-density theorem, exact absence, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, state graph, damping/dangling rule, iteration/precision, selection/restriction rule, genealogy, and verifier.
2. Construct target-independent graph/state within B^(9/4+o(1)) without enumerating source transitions.
3. For known-log R, rank/select states, exactly verify and replay A_i,epsilon_i under bounded restrictions, verify point equality, and record a row.
4. Collect at least max(d_FB+32,1,000) verified rows, retain all samples/misses/dependencies, require rank d_FB, and solve factor logs.
5. Reuse unchanged graph/vector for Q+[t]P, recover a tuple, compute x, and verify [x]P=Q.
6. Charge graph construction, every sparse multiply/iteration and precision bit, sorting/sampling, restrictions, verification, genealogy, replay, rank, logs, descent, and memory.

## Full rho/BSGS cost model

Let V,E be graph sizes, I iterations, b_prec precision bits, K states tested, Q_R restrictions, C_edge edge generation, C_exact verification, and C_inv replay. Approximate PageRank costs O(I E) arithmetic on a supplied graph plus sorting/selection; exact rational stationarity requires separately charged linear algebra and coefficient growth. Set a=log_N(T_graph+I E C_prec+T_sort), a_m=log_N(M_graph+V b_prec), q=log_N(Q_R(K C_exact+C_inv)+T_replay), and q_m=log_N(M_graph+M_vector+K+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds on verified hit rate and cost. Rho/BSGS are 0.50.

## Likely fatal obstruction

The link graph contains the missing source transitions. Stationary mass is aggregate and may favour high-degree dead ends rather than rare exact tuples; finite precision cannot certify absence. Preserving genealogy removes aggregation. This merges with IDEAS 316/370/394/387.

## Proof track

Prove endpoint-only graph construction, a stationary-mass-to-exact-source density theorem stable under restrictions, point-faithful genealogy, rank, and blind descent.

## Disproof track

Construct a graph with identical PageRank scores but different accepting source support, or a high-rank dead-end component dominating valid states.

## Positive and negative controls

- Positive: a supplied graph with a planted high-mass labelled accepting component.
- Negative: degree traps, shuffled genealogy, rare low-mass valid states, empty/singleton restrictions, precision changes, and blind targets.
- Baselines: uniform sampling, IDEAS 316/370/394/387, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph, proved verified-source mass, exact negative semantics, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing edge, aggregate genealogy loss, precision-dependent false negative, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g11_graph_genealogy_audit.md
- ideas/rejected/preallocation/artifacts/20260720-c/g11_stationary_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g11_cost_analysis.md

## Interpretation boundary

This rejects the elliptic PageRank transplant, not stationary link analysis. A high score, converged vector, or one relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g11_graph_genealogy_audit.md; do not create it under this retired pre-ID screen.
