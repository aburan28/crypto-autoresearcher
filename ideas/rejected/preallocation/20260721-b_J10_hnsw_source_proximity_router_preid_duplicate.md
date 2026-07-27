# Pre-ID duplicate draft — HNSW source proximity router

## Status and claim labels

- Prospect: `20260721-b-J10`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: approximate_proximity_graph / high-risk / high-risk pre-ID screen.
- State: merged_rejected_supplied_catalogue_graph_and_approximate_recall.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; high recall, a navigable graph, or a verified relation is not an ECDLP result.

## Falsifiable hypothesis

Build a target-independent hierarchical navigable small-world graph on endpoint features of partial source sums, then route fresh targets with high enough exact recall to recover signed sources and complete relation/descent costs below rho and BSGS.

## Mechanism-new operation

The native operation incrementally constructs layered approximate-nearest-neighbor proximity graphs and greedily descends them. It counts only if vertices/features/edges are endpoint-derived without source enumeration and zero-error exact source semantics replace empirical recall; indexing a supplied vector catalogue is a control.

## Assumptions

1. Source-compatible partial sums admit public features with an exact compatibility margin.
2. Catalogue and graph construction fit the setup/state cap.
3. Greedy layered search has target-uniform miss probability at most `2^-80` after charged retries.
4. Returned nodes retain exact signed occurrence labels across duplicates and exceptional strata.
5. The graph remains unchanged for fresh masked targets and supplies independent relations.

## Semantic fingerprint

`public_endpoint_feature_catalogue | HNSW_layered_proximity_graph | greedy_restricted_ANN_route | neighbor_node_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact negative answers and source replay are required.
2. `ideas/rejected/ECDLP-IDEA-344_locality_sensitive_exact_complement_filter_hypothesis.md` — approximate feature neighborhoods lack exact completeness.
3. `ideas/rejected/preallocation/20260720-d_H05_astar_heuristic_source_search_preid_duplicate.md` — heuristic graph search assumes represented transitions.
4. `ideas/rejected/preallocation/20260721-a_I09_tarjan_scc_source_quotient_preid_duplicate.md` — graph algorithms begin with supplied compatibility arcs.
5. `ideas/rejected/preallocation/20260720-c_G11_pagerank_source_stationary_flow_preid_duplicate.md` — navigation scores do not reconstruct source incidence.

## Closest primary literature

- Malkov and Yashunin, [Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs](https://arxiv.org/abs/1603.09320), builds a layered graph over a supplied data set and reports approximate recall.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply source vectors, proximity edges, or an exact metric gap.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source provides exact target-uniform recall or an endpoint-to-HNSW source compiler; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, feature map, distance, HNSW seeds/parameters, restrictions, exceptional charts, labels, and verifier.
2. Construct features, vertices, and every graph edge from public endpoints without source tuples; retain insertion and search receipts.
3. For known-log targets, issue exact restricted searches, self-reduce at most `5 ceil(log_2 B)+O(1)` times, replay a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, include misses/dependencies, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged graph on `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge feature/catalogue construction, all proximity edges, build `efConstruction`, search `efSearch`, retries, all-negative scans, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Put catalogue/graph build and peak state in `a,a_m`; put every layer visit, distance calculation, retry, exact fallback, and replay in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require total failure `<=2^-80`, setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

HNSW is an approximate index for a supplied data set. Constructing vertices and edges exposes the source catalogue and compatibility traffic, while empirical high recall cannot certify an empty restriction or a rare singleton. Exact fallback can scan the catalogue, and returned vectors do not contain hidden factor-base ancestry unless backpointers were supplied.

## Proof track

Derive endpoint-only exact features and graph edges, prove worst-case navigation and zero-error source lift, and bound every retry and negative query.

## Disproof track

Use rare isolated witnesses, adversarial insertion orders, duplicate features, disconnected greedy basins, and fresh targets; charge exact fallback and trace all vertex origins.

## Positive and negative controls

- Positive: supplied clustered vectors with labelled nearest neighbors and measured recall.
- Negative: isolated singleton neighbors, hub traps, duplicate features, shuffled insertion, empty restrictions, and fresh targets.
- Baselines: exact scan, A-star, LSH, cover tree, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only vertices/edges, a proved exact gap and target-uniform miss bound, four sizes, zero false decisions, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied catalogue, empirical-only recall, any missed singleton, exact-scan fallback, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j10_graph_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j10_hnsw_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j10_cost_analysis.md`

## Interpretation boundary

This rejects the exact endpoint-source transplant, not HNSW for approximate nearest neighbors. Finite results remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
