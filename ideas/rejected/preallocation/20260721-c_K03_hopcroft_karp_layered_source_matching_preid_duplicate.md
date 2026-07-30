# Pre-ID duplicate draft — Hopcroft–Karp layered source matching

## Status and claim labels

- Prospect: `20260721-c-K03`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: bipartite_matching / conservative / pre-ID screen.
- State: merged_rejected_supplied_compatibility_graph.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a matching or verified tuple is not an ECDLP result.

## Falsifiable hypothesis

Derive a sparse bipartite compatibility graph between partial signed sources, use Hopcroft–Karp BFS layers plus vertex-disjoint shortest augmenting paths to find exact restricted matches, and replay full tuples below rho and BSGS.

## Mechanism-new operation

The native operation batches many shortest augmenting paths in a supplied bipartite graph. It counts only if vertices, edges, bipartition, and source backpointers are derived from public endpoints without enumerating compatible pairs; running layered matching on an explicit source graph is a solver control.

## Assumptions

1. Exact five-source compatibility factors through a sparse endpoint-derived bipartite graph.
2. Restrictions update layers and matching state without scanning all source edges.
3. A matched edge/path retains signed occurrence identity across exceptional strata.
4. Maximum matching nonemptiness is biconditional with source existence, not merely a relaxation.
5. One graph serves known-log relations and fresh masked targets.

## Semantic fingerprint

`public_endpoint_bipartite_graph | Hopcroft_Karp_layered_augmenting_paths | exact_restricted_matching | matched_edges_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restriction and replay requirement.
2. `ideas/rejected/ECDLP-IDEA-345_linear_matroid_parity_source_packing_hypothesis.md` — packing begins with represented candidates.
3. `ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md` — matching decomposition consumes explicit compatibility edges.
4. `ideas/rejected/preallocation/20260719-b_B04_edmonds_blossom_source_matching_preid_duplicate.md` — blossom shrinking is an occupied solver-stage merge.
5. `ideas/rejected/preallocation/20260720-d_H06_tutte_randomized_source_matching_preid_duplicate.md` — determinant matching also requires the source graph.

## Closest primary literature

- Hopcroft and Karp, [An n^(5/2) algorithm for maximum matchings in bipartite graphs](https://doi.org/10.1137/0202019), batches shortest augmenting paths in a supplied graph.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a sparse compatibility graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the graph or exact source lift from public endpoints; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, graph semantics, charts, and verifier.
2. Construct the bipartite graph and certify every edge from endpoints only, without source enumeration or `Query2P1`.
3. For each known-log target, run exact restricted layering, replay a labelled tuple from a matching, and verify point equality before retaining a row.
4. Collect at least `max(d_FB+32,1000)` rows, require actual rank `d_FB`, and solve every factor log.
5. Reuse unchanged state for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph construction, edge scans, layers, augmentations, restrictions, replay, density, rank, logs, blind descent, bit time, and memory.

## Full rho/BSGS cost model

Charge graph construction/state in `a,a_m`, BFS/DFS restrictions and replay in `q,q_m`, and candidate output in `o,u`. With `beta=1/5`, use the complete `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Hopcroft–Karp improves matching only after the compatibility graph exists. Exact elliptic pair and middle-source edges are the missing source-incidence object and can require `B^2` or `B^3` traffic. A pairwise graph may also admit matchings that do not satisfy the five-way endpoint equation, while gadgets restoring equivalence encode source tuples.

## Proof track

Give a sparse endpoint-only graph reduction with a biconditional matching theorem, restriction stability, exact lifts, and complete edge plus matching costs.

## Disproof track

Trace every edge and gadget to source data, construct false pairwise matchings, and falsify on source enumeration, dense layers, lost labels, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied sparse bipartite graphs with planted labelled matchings.
- Negative: dense compatibility graphs, pairwise-consistent but globally-false tuples, duplicate endpoints, and empty restrictions.
- Baselines: explicit matching, blossom/Tutte controls, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only graph construction, a biconditional proof, four sizes, zero false decisions, full rank, 100 fresh blind descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied edges, a relaxation gap, lift failure, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k03_edge_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k03_matching_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k03_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint graph compiler, not Hopcroft–Karp. Any matching remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
