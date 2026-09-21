# ECDLP-IDEA-376 — Eppstein sidetrack source-path router

## Status and claim labels

- Class: `algorithmic`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_sidetrack_graph_and_shortest_path_tree_are_source_incidence`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; enumerating paths in a supplied graph is not an ECDLP break.

## Falsifiable hypothesis

The five-deck relation fibre has an endpoint-implicit weighted digraph with a compact shortest-path tree and sidetrack heaps, allowing exact target paths and occurrence-labelled source tuples to be enumerated with subgate preprocessing and delay.

## Mechanism-new operation

The screened operation is **build a shortest-path tree, encode every alternative relation as an ordered heap of sidetrack edges, and pop the first target-compatible path under dyadic restrictions**. It differs from universal exploration or reverse search only if adjacency, edge weights, and sidetrack deltas are computed from endpoints without materializing the source graph.

## Assumptions

1. Partial elliptic sums define a compact, random-access, source-faithful digraph with nonnegative public weights.
2. A shortest-path tree and sidetrack heaps fit the preprocessing/state gate without explicit source edges.
3. Path order is target-uniform and exact; the first accepted path returns signed occurrence labels on all strata.
4. Arbitrary dyadic restrictions and fresh targets reuse the same state without source-sized rebuilding.
5. Graph construction, shortest paths, heaps, rejected paths, output, rank, factor logs, blind descent, and memory are fully charged.

## Semantic fingerprint

`partial_sum_digraph | shortest_path_tree | Eppstein_sidetrack_heaps | exact_target_path | occurrence_source | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the complete source and descent accounting is mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; compact source-resolving transitions are unconstructed.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; a fresh-target path generator is the missing operation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; a lossless partial-sum graph cannot be free input.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit edge construction is a no-promotion control.

## Closest primary literature

- Eppstein, [Finding the k shortest paths](https://doi.org/10.1137/S0097539795290477), obtains constant amortized output delay after preprocessing a supplied digraph.
- Eppstein, [the original technical report](https://ics.uci.edu/~eppstein/pubs/Epp-TR-94-26.pdf), makes the shortest-path-tree and sidetrack representation explicit.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides endpoint equations but not the required graph or weights.

No checked source constructs an endpoint-only sidetrack graph; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, partial-state vertices, adjacency/weight oracle, shortest-path policy, sidetrack heaps, restrictions, masks, and verifier.
2. Build target-independent tree/heaps within `B^(9/4)` without enumerating all source transitions.
3. On known-log targets, pop paths in frozen order, charge rejected paths, apply exact restricted-existence bisection, return one occurrence-labelled tuple, and verify it.
4. Collect `B` independent verified rows, solve and independently verify factor logs, charging duplicate and dependent paths.
5. Apply the identical graph and sidetrack policy to fresh scalar-blind `Q+[t]P`, charging target updates and mask rebuilds.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge adjacency, shortest-path preprocessing, heaps, enumeration delay, restrictions, source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state is at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion requires time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Eppstein's delay bound begins after the full weighted digraph and shortest-path tree are available. For partial elliptic sums, a random-access outgoing edge exposes the next factor occurrence, so a faithful graph is exactly the missing source incidence. Endpoint-only quotient vertices merge different source histories; restoring labels or rebuilding under restrictions recreates `B^3` or larger work. This merges with IDEAs 083, 203, 230, 343, and 364 unless a new compact adjacency theorem is supplied.

## Proof track

Construct the graph/weights from endpoints alone, prove a source-biconditional path map and restriction-stable heaps, and meet every state/query/full-path exponent gate.

## Disproof track

Show that adjacency or weights require explicit source edges, that equal quotient states have different valid continuations, or that rejected-path density makes online delay supergate.

## Positive and negative controls

- Positive: supplied sparse weighted DAGs with labelled planted paths must reproduce Eppstein order and sources.
- Negative: equal endpoint states with different continuations, high sidetrack density, arbitrary source restrictions, all strata, and blind targets.
- Baselines: IDEAs 083/203/230/343/364, explicit pair graphs, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a subgate endpoint adjacency oracle, exact path/source biconditional, restriction stability, `1,000` independent rows, `100` blind descents, and `lambda,mu<=0.45`.
- Falsify on one source-labelled edge, one quotient collision, supergate rejected-path delay/rebuild, a missed stratum, or either exponent at least `0.50`.
- Fast enumeration in a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-376/implicit_graph_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-376/quotient_state_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-376/source_path_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-376/cost_analysis.md`

## Interpretation boundary

This rejects the screened source-graph construction, not Eppstein's algorithm. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a valid path is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-376/implicit_graph_obligations.md` and formalize one random-access sidetrack edge including its endpoint-only construction cost.

