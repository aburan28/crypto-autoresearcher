# Pre-ID duplicate draft — Hierholzer cycle-splice source tour

## Status and claim labels

- Prospect: `20260721-d-L04`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: graph_algorithm / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_eulerian_edges_and_tour_not_relation_index.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an Euler tour, verified cycle, or relation is not an ECDLP result.

## Falsifiable hypothesis

Compile all signed source transitions into a public Eulerian multigraph, use Hierholzer cycle splicing to store every occurrence once in a compact tour, answer restricted relation queries by tour intervals, replay tuples, and finish factor logs plus blind descent below rho and BSGS.

## Mechanism-new operation

The native operation follows unused edges until returning to a start vertex and recursively splices tours at vertices with remaining unused edges. It counts only if the Eulerian multigraph is built from endpoint data below source scale and tour intervals support exact subset restrictions and tuple replay; touring a supplied edge catalogue is a control.

## Assumptions

1. Endpoint data yields a balanced connected multigraph whose edge occurrences correspond exactly to signed source transitions.
2. The graph can be constructed without enumerating all source occurrences.
3. A single tour supports subset-stable exact existence rather than only sequential enumeration.
4. Edge positions replay complete occurrence-distinct relation tuples including exceptional strata.
5. The same tour serves known-log relations and fresh scalar-blind target descent.

## Semantic fingerprint

`public_endpoint_eulerian_source_multigraph | Hierholzer_unused_edge_cycle_splicing | exact_restricted_tour_interval | tour_edges_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted predicate and source-return frontier.
2. `ideas/rejected/preallocation/20260721-c_K10_christofides_source_tour_preid_duplicate.md` — Euler touring a supplied metric skeleton is not an exact source index.
3. `ideas/rejected/preallocation/20260721-b_J05_prufer_tree_source_code_preid_duplicate.md` — a compact traversal code starts after a labelled source tree exists.
4. `ideas/rejected/preallocation/20260719-d_D05_wilson_cycle_popping_source_tree_preid_duplicate.md` — cycle processing assumes the source graph and does not certify restricted occurrences.
5. `ideas/rejected/ECDLP-IDEA-203_matrix_tree_arborescence_source_extractor_hypothesis.md` — aggregate tree counts/determinants do not supply an exact occurrence lift.

## Closest primary literature

- Hierholzer, [Ueber die Moeglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren](https://eudml.org/doc/156599), proves the Eulerian tour construction for a supplied multigraph.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not an occurrence-complete Eulerian graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the endpoint multigraph, restriction index, or factor-base descent interface; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, signed decks, restrictions, exceptional strata, edge semantics, and independent point verifier.
2. Construct and certify the endpoint-derived Eulerian multigraph, edge multiplicities, and tuple backpointers without source enumeration or scalar labels.
3. For each known-log target, impose at most `5 ceil(log_2 B)+O(1)` restrictions on the tour index, replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, keep failures and dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph and tour construction, edge traffic, interval restrictions, replay, density, rank, logs, target descent, bit complexity, and peak memory.

## Full rho/BSGS cost model

Charge multigraph/tour setup in `a,a_m`, restricted lookup/replay in `q,q_m`, and outputs/ambiguity in `o,u`. With `B=N^beta`, `beta=1/5`, `delta,delta_t,r,ell,ell_m` as usual, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50`.

## Likely fatal obstruction

An Euler tour is a lossless ordering only after every edge occurrence is materialized, so its construction already pays source traffic. Sequential adjacency in the tour has no reason to align with arbitrary five-coordinate restrictions. Adding a multidimensional exact restriction index and tuple backpointers restores source-scale state; omitting them cannot certify empty queries or replay a relation.

## Proof track

Construct an endpoint-only Eulerian multigraph with sub-source edge representation and a theorem that one compact tour supports exact arbitrary restrictions and complete signed tuple replay inside the full caps.

## Disproof track

Audit every edge occurrence and tour index; falsify on enumerated source edges, source-scale satellites, a false empty query, lost multiplicity, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied Eulerian multigraphs with labelled edge occurrences and interval-aligned restrictions.
- Negative: non-Eulerian source graphs, duplicate edges, restrictions cutting across tour intervals, empty fibres, and fresh targets.
- Baselines: explicit Hierholzer, Christofides, Wilson, matrix-tree, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only graph construction, four increasing sizes, zero false decisions, exact multiplicity replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied edges, source-sized index state, any false answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l04_edge_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l04_hierholzer_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l04_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only Hierholzer transplant, not Euler-tour construction. Every finite tour remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
