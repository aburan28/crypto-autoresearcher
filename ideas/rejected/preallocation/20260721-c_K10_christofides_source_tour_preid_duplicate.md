# Pre-ID duplicate draft — Christofides source tour

## Status and claim labels

- Prospect: `20260721-c-K10`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: metric_tour_approximation / representation-changing / pre-ID screen.
- State: merged_rejected_supplied_metric_graph_and_approximate_tour.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a short tour or relation is not an ECDLP result.

## Falsifiable hypothesis

Construct a metric on endpoint-compatible partial sources, use Christofides minimum-spanning-tree plus odd-vertex matching and Eulerian shortcutting to traverse every required source class, and extract exact restricted occurrences below rho and BSGS.

## Mechanism-new operation

The native operation combines an MST, minimum matching on odd vertices, Euler tour, and metric shortcutting to approximate a tour of a supplied metric graph. It counts only if metric vertices/edges are endpoint-derived and the tour gives exact source-existence/replay, not merely coverage of a supplied catalogue.

## Assumptions

1. A compact public metric graph represents all exact source occurrences.
2. Triangle inequality and shortcutting preserve source ancestry and restriction semantics.
3. The tour can answer negative and singleton restrictions without scanning its full length.
4. Every visited source class lifts to signed factor-base occurrences.
5. One target-independent tour serves fresh masked targets.

## Semantic fingerprint

`public_endpoint_metric_graph | Christofides_MST_odd_matching_Euler_shortcut | exact_restricted_tour_lookup | tour_vertex_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restriction/replay frontier.
2. `ideas/rejected/ECDLP-IDEA-376_eppstein_sidetrack_source_path_router_hypothesis.md` — path routing begins with the explicit source graph.
3. `ideas/rejected/ECDLP-IDEA-389_plunnecke_magnification_source_graph_hypothesis.md` — a layered graph does not invert endpoints to sources.
4. `ideas/rejected/preallocation/20260721-a_I10_prim_minimum_source_skeleton_preid_duplicate.md` — an MST consumes the source graph and can delete witnesses.
5. `ideas/rejected/preallocation/20260720-b_F06_hungarian_primal_dual_source_assignment_preid_duplicate.md` — matching consumes a supplied cost matrix.

## Closest primary literature

- Christofides, [Worst-case analysis of a new heuristic for the travelling salesman problem](https://doi.org/10.1007/s43069-021-00101-z), combines a spanning tree and matching for a supplied metric TSP instance.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply the metric source graph.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the ECDLP metric catalogue or exact occurrence lookup; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, metric/graph, restrictions, tie policy, charts, and verifier.
2. Construct the metric and graph from endpoints only; certify triangle inequality and source provenance.
3. For known-log targets, build/reuse the tour, answer exact restrictions, replay a tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged tour for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph/metric construction, MST, matching, Euler tour, shortcutting, lookup, replay, density, rank, logs, bit time, and memory.

## Full rho/BSGS cost model

Charge graph/tour setup in `a,a_m`, restricted lookup/replay in `q,q_m`, and tour/output ambiguity in `o,u`. With `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, and charge all metric/catalogue construction. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Christofides starts from all metric vertices and edges and returns an approximate tour, not an exact query index. Constructing vertices for exact elliptic source occurrences is the missing catalogue; an MST/shortcut can erase edges carrying unique provenance. Even a short tour may be source-sized and requires linear negative-query scans unless another index is supplied.

## Proof track

Construct the metric publicly, prove tour coverage plus occurrence-preserving shortcuts and sublinear exact restriction lookup, and charge every graph operation.

## Disproof track

Trace metric points/edges, plant witnesses on shortcut/deleted edges, test negative queries, and falsify on supplied catalogue, source-sized tour, missing replay, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied labelled metric graphs with tour-indexed witnesses.
- Negative: witnesses on non-tour edges, duplicate vertices, long negative scans, empty restrictions, and fresh targets.
- Baselines: Prim MST, Hungarian matching, explicit scan, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only metric construction, exact coverage/lookup theorem, four sizes, zero false answers, exact lifts, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied graph, approximate-only coverage, lost witness, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k10_metric_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k10_tour_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k10_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-source tour transplant, not Christofides' metric-TSP approximation. Any finite tour remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
