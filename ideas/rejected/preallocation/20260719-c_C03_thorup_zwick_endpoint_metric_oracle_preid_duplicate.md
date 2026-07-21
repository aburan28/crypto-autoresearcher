# Pre-ID duplicate draft — Thorup–Zwick endpoint-metric oracle

## Status and claim labels

- Prospect: `20260719-c-C03`; no canonical ID allocated
- Class / risk / lane: `metric_oracle` / `representation-changing` / pre-ID screen
- State: `merged_rejected_supplied_graph_and_approximate_distance`
- Evidence: complete-corpus and primary-literature review only; no run
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Construct a public weighted endpoint graph in which exact five-source compatibility is separated by a distance gap, preprocess Thorup–Zwick landmark bunches, and use constant-query approximate distances plus self-reduction to replay exact signed relations and blind targets below rho/BSGS.

## Mechanism-new operation

The native operation samples nested landmark sets and stores bunches giving stretch-`2k-1` distance estimates in a supplied weighted graph. It counts only if the graph is endpoint-derived without source edges and the approximation preserves an exact zero/nonzero relation gap under every restriction.

## Assumptions

1. A compact target-independent metric graph is exactly biconditional with all signed/chart-complete relations.
2. Zero distance is preserved by the stretch guarantee; any positive relation/nonrelation threshold has a uniform gap wider than the allowed stretch, including under restrictions.
3. Graph construction, landmarks, bunches, queries, self-reduction, source replay, rank, logs, descent, and memory are charged.
4. The same oracle supports known-log and fresh scalar-blind targets without rebuild.
5. No explicit compatibility graph, post-hoc embedding, approximate-only acceptance, or source-labelled path is admitted.

## Semantic fingerprint

`public_endpoint_metric_graph | Thorup_Zwick_landmark_bunch_oracle | exact_gap_preserving_restricted_decision | path_to_source_replay | blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact subset-stable existence is required.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H673`: graph structure must change exact relation supply.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION`: graph concentration did not transfer source return.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: the open object is a public exact source-resolving circuit.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: explicit source-fibre joins restore materialization.

## Closest primary literature

- Thorup and Zwick, [Approximate Distance Oracles](https://doi.org/10.1145/1044731.1044732), preprocess a supplied weighted graph and return stretch-bounded distances.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations, not a low-stretch source graph.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), is the matched baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, exceptional charts, graph grammar, distance gap, restrictions, and verifier.
2. Build graph/oracle state within `B^(9/4+o(1))` without materializing source incidence.
3. On known-log targets, answer exact restrictions and replay five occurrences by charged self-reduction and path verification.
4. Collect at least `B` independent rows and solve factor logs.
5. Reuse state on fresh scalar-blind `Q+[t]P`, verify the recovered tuple, remove `t`, and verify `[x]P=Q`.
6. Charge graph generation, preprocessing, negative queries, path output, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

With `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, fresh work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Pollard rho time and BSGS time/memory are `0.50` baselines.

## Likely fatal obstruction

Thorup–Zwick assumes the weighted graph; source-compatible edges are the missing relation catalogue. The usual stretch guarantee does preserve graph distance zero, but no endpoint-only graph or pseudometric is supplied whose zero-distance classes are exactly the relation fibers. Any positive threshold additionally needs a uniform gap wider than the stretch, and a returned path can omit point provenance. This merges with IDEAs `326/341/344/350/370/393` and WSPD pre-ID `B08`.

## Proof track

Give an endpoint-only sparse graph, a uniform exact gap theorem under restrictions, a path-to-points inverse, and complete cost bounds.

## Disproof track

Find one source-bearing edge, show that zero-distance equivalence is not relation-biconditional or a proposed positive gap is crossed by stretch, or derive graph/oracle costs beyond the caps.

## Positive and negative controls

- Positive: supplied weighted graphs with a planted robust distance gap.
- Negative: graph pairs differing by one source edge, zero-gap collisions, exceptional charts, restrictions, blind targets.
- Baselines: IDEAs `326/341/344/350/393`, B08, exact shortest paths, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact zero-error decision/replay, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on a supplied edge list, one stretch ambiguity, target-dependent rebuild, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-c/c03_graph_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-c/c03_gap_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260719-c/c03_cost_analysis.md`

## Interpretation boundary

This rejects this transplant, not distance oracles. Approximate distance correctness or a toy relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-c/c03_graph_provenance.md` and classify every vertex, edge, landmark, and returned path label by source provenance.
