# ECDLP-IDEA-369 — Gomory–Hu cut-tree source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_cut_tree_requires_explicit_capacitated_source_graph`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cut value or cut tree on a supplied graph is not an ECDLP break.

## Falsifiable hypothesis

Partial elliptic source states form an endpoint-derived undirected capacitated graph whose Gomory–Hu tree preserves restricted source-to-target separation and routes one exact relation tuple within the P1553 gates.

## Mechanism-new operation

The screened operation is **compress all-pairs minimum-cut values of a source graph into a cut-equivalent tree, use the tree edge separating a target from admissible sources as an exact restricted-existence decision, and replay a witness path**. It is distinct only if the graph/capacities and max-flow oracle are source-free, the tree remains valid under arbitrary deck restrictions, and cut values return exact labelled paths rather than aggregate bottlenecks.

## Assumptions

1. A target-independent graph with subgate edges encodes relation completion as connectivity/cut structure.
2. Capacities are public endpoint functions and a zero/positive cut exactly separates empty/nonempty restricted fibres.
3. One cut tree or cheap updates handles dyadic source restrictions and fresh targets without rebuilding source-sized state.
4. A tree decision yields one exact signed tuple on every stratum through charged path/self-reduction.
5. Graph construction, max flows, updates, path output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_derived_capacitated_source_graph | Gomory_Hu_cut_equivalent_tree | restricted_min_cut_nonemptiness | exact_witness_path_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the source graph is the missing source-resolving structure.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public source generation and target batching remain unconstructed.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit capacitated edges already retain source incidence.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; constructing source paths from pair advice restores cubic work.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; max flow on a supplied source network is a control.

## Closest primary literature

- Gomory and Hu, [Multi-Terminal Network Flows](https://doi.org/10.1137/0109047), compresses all-pairs minimum-cut values of a supplied undirected capacitated graph.
- Ford and Fulkerson, [Maximal Flow Through a Network](https://doi.org/10.4153/CJM-1956-045-5), supplies the max-flow/min-cut machinery on explicit networks.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but not the graph, capacities, or path section.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, graph/capacity rule, cut-tree algorithm, restriction updates, masks, and verifier.
2. Construct the target-independent graph and tree without source-edge enumeration or scalar labels.
3. On known-log targets, use restricted cut decisions, recover a path/tuple, and replay it by direct group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply identical graph/tree updates to fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge edges, capacities, all max flows, updates, path output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Gomory–Hu trees preserve cut values only after the explicit capacitated graph exists. Constructing source edges is the missing incidence operation, and a cut value does not preserve a witness path or tuple. Arbitrary source restrictions change the graph and generally require rebuilding/max-flow work. The operation merges with network/Laplacian/cut lanes IDEAs 077, 203, 236, 348, and 352.

## Proof track

Construct the endpoint-only graph, prove restricted cut/existence and path/source biconditionals with subgate updates, and derive complete exponents at most `0.45`.

## Disproof track

Exhibit two graphs/fibres with identical available cut-tree data but different restricted witnesses, or prove graph construction/rebuild costs at least `B^3`.

## Positive and negative controls

- Positive: supplied capacitated graphs with known cut tree and labelled witness paths.
- Negative: source-permuted edges, equal cut values with different paths, arbitrary vertex restrictions, dense source graphs, and blind targets.
- Baselines: IDEAs 077/203/236/348/352, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph/tree construction, exact restricted path/source recovery, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on explicit source edges, witness-losing cut collisions, source-sized rebuilds, missed stratum, `B^3` flow traffic, or either exponent at least `0.50`.
- A correct cut tree for a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-369/source_graph_cut_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-369/cut_value_witness_cases.json`
- `ideas/artifacts/ECDLP-IDEA-369/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-369/cost_analysis.md`

## Interpretation boundary

This rejects the screened source-graph route, not Gomory–Hu trees. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A cut value is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-369/source_graph_cut_obligations.md` and prove whether a source-free graph has exact restriction-stable cut/source semantics.
