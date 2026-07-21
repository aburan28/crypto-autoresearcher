# ECDLP-IDEA-380 — AGM linear graph-sketch source router

## Status and claim labels

- Class: `streaming`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_sketch_update_stream_is_source_edges_and_cut_recovery_loses_exact_tuple_provenance`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct graph sketch or recovered cut is not an ECDLP break.

## Falsifiable hypothesis

Partial-sum compatibility edges can be streamed from endpoints into Ahn–Guha–McGregor linear sketches, from which exact restricted connectivity certificates and one occurrence-labelled relation source can be replayed below the P1553 gates.

## Mechanism-new operation

The screened operation is **linearly sketch a dynamic source-compatibility graph, recover sparse cut/connectivity certificates, and replay their labelled edges to an exact five-deck tuple under restrictions**. It differs from CountSketch and spectral sparsification only if the update stream itself is endpoint-generated without enumerating source edges and the sketch preserves rare exact provenance.

## Assumptions

1. Every sketch update is computed from public endpoints without listing a compatible pair or tuple edge.
2. Sketch dimension and update/query work fit the setup/state and fresh-target gates.
3. Recovery is exact for singleton relation paths, all signed strata, occurrence labels, and arbitrary dyadic restrictions.
4. Randomness is frozen before fresh targets, with all failure probabilities, repetitions, and rebuilds charged.
5. Edge generation, sketches, recovery, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`dynamic_partial_sum_edge_stream | AGM_linear_graph_sketch | exact_restricted_connectivity_certificate | labelled_edge_replay | occurrence_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; complete source and descent costs remain mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; endpoint-only target-uniform source generation is unconstructed.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit edge streams are the no-promotion boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; linear sketches did not remove full source rank.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless source transitions cannot be hidden as stream input.

## Closest primary literature

- Ahn, Guha, and McGregor, [Analyzing graph structure via linear measurements](https://doi.org/10.1137/1.9781611973099.40), recovers graph properties from linear sketches of a supplied edge stream.
- Ahn, Guha, and McGregor, [Graph sketches: sparsification, spanners, and subgraphs](https://doi.org/10.1145/2213556.2213560), produces probabilistic graph summaries, not rare labelled relation tuples.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint constraints but no subgate edge stream.

No checked source constructs or exactly replays the required source edges; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, compatibility graph semantics, update generator, sketch matrices/seeds, recovery, restrictions, masks, and verifier.
2. Stream target-independent updates and build sketches within `B^(9/4)` without enumerating the `B^3/B^4` compatibility edges.
3. On known-log targets, update target sketches, decide exact restricted existence, recover/replay one labelled path, obtain a tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charge sketch failures and dependent outputs, solve factor logs, and verify them.
5. Reuse frozen sketches/seeds for fresh scalar-blind `Q+[t]P`, charging negative restrictions, resampling, and rebuilds.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge edge generation, update volume, sketch state, recovery, replay, source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a fresh restricted query at most `B^(5/4+o(1))`, and promotion requires time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

AGM sketches consume an explicit stream of graph-edge updates. In this setting each update names a compatible partial-source transition, so generating the stream is the occupied source-incidence obstruction. Standard recovery is probabilistic and preserves cuts/connectivity or a sampled subgraph, not every rare labelled relation; exact correction or arbitrary restriction replay reconstructs the edge deck. This merges with IDEAs 203, 347, 348, 369, and 370 unless a new endpoint-only update generator and exact provenance theorem are supplied.

## Proof track

Construct endpoint-only updates, prove exact singleton-preserving restricted recovery and edge-to-tuple replay, and meet every setup/query/full-path gate.

## Disproof track

Show that any update names a hidden source edge, or construct equal sketches with different singleton witnesses under the frozen randomness and restriction policy.

## Positive and negative controls

- Positive: supplied sparse labelled graphs streamed independently must recover the promised properties and planted path.
- Negative: equal sketches with toggled singleton edges, dense random compatibility graphs, arbitrary restrictions, all strata, frozen seeds, and blind targets.
- Baselines: IDEAs 203/347/348/369/370, explicit edge streams, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with source-free updates, exact restricted provenance, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one explicit source update, one missed rare edge/stratum, target-fitted randomness, source-sized correction/rebuild, or either exponent at least `0.50`.
- Correct cut recovery from a supplied toy stream is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-380/update_stream_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-380/equal_sketch_singleton_cases.json`
- `ideas/artifacts/ECDLP-IDEA-380/edge_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-380/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic graph-sketch route, not AGM sketches. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; sketch correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-380/update_stream_obligations.md` and expand the constructor for one compatibility-edge update down to endpoint operations.

