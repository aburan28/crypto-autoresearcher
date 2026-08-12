# Pre-ID duplicate draft — Floyd–Warshall semiring source closure

## Status and claim labels

- Prospect: `20260721-a-I12`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: dynamic_programming / conservative / conservative pre-ID screen.
- State: merged_rejected_dense_supplied_adjacency_and_aggregate_paths.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; transitive closure, shortest paths, or a relation is not a breakthrough.

## Falsifiable hypothesis

Evaluate Floyd–Warshall over a provenance semiring on endpoint-derived transition states so closure entries answer exact restricted relation existence and carry replayable signed sources below rho/BSGS.

## Mechanism-new operation

Floyd's dynamic program closes a supplied weighted adjacency matrix over intermediate vertices. A provenance-semiring variant counts only if the matrix is endpoint-derived without source enumeration and closure annotations remain compact, duplicate-preserving source witnesses; an explicit dense matrix is a control.

## Assumptions

1. A compact endpoint adjacency representation exists before source incidence.
2. Semiring addition/multiplication preserve exact zero semantics and signed occurrence provenance.
3. Intermediate-state closure stays within setup/state caps rather than densifying.
4. Restrictions reuse closure state and replay exact tuples.
5. The same state serves factor logs and blind targets.

## Semantic fingerprint

`public_endpoint_adjacency | Floyd_Warshall_semiring_intermediate_closure | exact_restricted_path_nonzero | closure_annotation_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-d_H04_johnson_potential_source_reweighting_preid_duplicate.md` — shortest-path backends assume a supplied graph.
2. `ideas/rejected/preallocation/20260720-d_H03_dinic_blocking_flow_source_router_preid_duplicate.md` — graph dynamic programs do not create compatibility arcs.
3. `ideas/rejected/preallocation/20260720-c_G11_pagerank_source_stationary_flow_preid_duplicate.md` — aggregate closure/flow loses occurrence provenance.
4. `ideas/rejected/ECDLP-IDEA-325_insideout_faq_source_join_hypothesis.md` — the exact provenance-semiring owner still requires supplied factors and source backtracking.
5. `ideas/rejected/ECDLP-IDEA-380_agm_linear_graph_sketch_source_router_hypothesis.md` — graph sketches preserve limited queries, not exact labelled paths.

## Closest primary literature

- Floyd, [Algorithm 97: Shortest path](https://doi.org/10.1145/367766.368168), computes all-pairs shortest paths from a supplied matrix.
- Green, Karvounarakis, and Tannen, [Provenance semirings](https://doi.org/10.1145/1265530.1265535), propagates annotations through supplied relational inputs; it does not construct elliptic adjacency or make provenance compact.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not adjacency closure.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source provides the endpoint matrix or compact exact provenance semiring; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, vertex/adjacency grammar, semiring, intermediate order, restrictions, signed strata, and verifier.
2. Build compact adjacency/closure state from public endpoints without source enumeration, explicit large-prime tables, or `Query2P1`.
3. For known-log targets, query restricted closure entries, replay labelled signed points, verify their sum, and record valid rows.
4. Preserve failures/dependencies; collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged state for `Q+[t]P`, replay, compute `x`, and verify `[x]P=Q`.
6. Charge adjacency construction, every semiring update, densification, annotations, restrictions, replay, density, rank, logs, descent, bit time, and peak memory.

## Full rho/BSGS cost model

For `V` represented vertices, native explicit closure charges `Theta(V^3)` semiring operations and `Theta(V^2)` state; any claimed compression must put full setup/query exponents in `a,a_m,q,q_m`. With `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Floyd–Warshall is a dense solver over supplied adjacency. Endpoint compatibility arcs are the missing source information; exact provenance annotations grow with the number of paths/occurrences, while ordinary min/Boolean closure discards them. Dense `V^2`/`V^3` state and work violate the relevant rectangles for source-sized `V`.

## Proof track

Derive endpoint-only low-state adjacency and a compact exact provenance semiring closed under every intermediate/restriction, with all-occurrence replay and complete costs.

## Disproof track

Track matrix density and annotation growth; falsify if adjacency is supplied, two source paths merge without invertible labels, or state/work exceeds caps.

## Positive and negative controls

- Positive: supplied small graphs over Boolean/min-plus/provenance semirings with unique labelled paths.
- Negative: exponentially many equal paths, duplicate occurrences, dense closure, shuffled annotations, empty restrictions, and blind targets.
- Baselines: Johnson/Dinitz/PageRank, explicit matrix closure, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require endpoint-only adjacency, compact exact provenance, zero false decisions, exact lifts, four increasing sizes, full rank from `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied/dense matrix state, provenance collision, false answer, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i12_closure_density_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i12_semiring_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i12_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint adjacency/provenance compiler, not Floyd–Warshall. Toy closure remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not materialize the closure matrix.
