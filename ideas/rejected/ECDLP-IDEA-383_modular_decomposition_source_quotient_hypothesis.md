# ECDLP-IDEA-383 — Modular-decomposition source quotient

## Status and claim labels

- Class: `combinatorial`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_generic_endpoint_graph_is_prime_and_module_tree_requires_source_edges`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct module tree or quotient is not an ECDLP break.

## Falsifiable hypothesis

The endpoint compatibility graph has large public strong modules whose canonical modular-decomposition tree gives a compact quotient and an exact restriction-stable leaf replay to one occurrence-labelled relation source below the P1553 gates.

## Mechanism-new operation

The screened operation is **identify vertices with identical external neighborhoods, recurse through the canonical strong-module tree, and lift a positive quotient leaf to an exact source tuple**. It is distinct from generic graph decompositions only if neighborhoods and leaf provenance are endpoint-constructible without explicit source incidence.

## Assumptions

1. A source-biconditional compatibility graph is compactly constructible from public endpoints.
2. Generic instances have nontrivial strong modules that reduce state below the frozen cap.
3. The quotient/tree preserves target labels, signed occurrences, all strata, and arbitrary dyadic restrictions exactly.
4. Leaf replay is canonical and does not enumerate each member of a large module.
5. Graph construction, neighborhood tests, tree/quotient state, restrictions, output, rank, logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`source_compatibility_graph | strong_module_neighborhood_equivalence | canonical_modular_decomposition_tree | exact_leaf_source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; complete source/descent accounting is mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact source-resolving quotient is missing.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation remains unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; exact neighborhoods cannot be hidden as free transitions.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit compatibility edges are the no-promotion boundary.

## Closest primary literature

- McConnell and Spinrad, [Modular decomposition and transitive orientation](https://doi.org/10.1016/S0012-365X(98)00319-7), computes canonical modules of a supplied graph.
- McConnell and Spinrad, [Linear-time modular decomposition and efficient transitive orientation](https://doi.org/10.46298/dmtcs.274), obtains linear time after graph incidence is available.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide nontrivial modules or a compatibility graph.

No checked source proves modular structure for generic elliptic fibres; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, compatibility graph, edge/neighborhood constructor, module algorithm, restrictions, masks, and verifier.
2. Build a target-independent module tree/quotient within `B^(9/4)` without enumerating source edges.
3. For known-log targets, update quotient labels, decide restricted existence, descend strong modules, replay one occurrence-labelled tuple, and verify it.
4. Collect at least `B` independent verified rows, charge duplicate/dependent leaves, solve factor logs, and verify them independently.
5. Reuse the unchanged graph/module operation for fresh scalar-blind `Q+[t]P`, charging restriction-induced splits and rebuilds.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge graph/neighborhood construction, module tree, target updates, restrictions, source replay, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state is at most `B^(9/4+o(1))`, a fresh restricted query at most `B^(5/4+o(1))`, and promotion requires time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Modular decomposition starts with explicit adjacency. Generic target-labelled compatibility graphs can be prime, giving only singleton and whole-graph modules. Dropping labels may create false twins but destroys point provenance; retaining labels restores full incidence. Arbitrary deck restrictions split modules and require rebuilding. This merges with IDEAs 120, 338, 348, 352, and 369 unless a new endpoint-only nontrivial-module theorem is supplied.

## Proof track

Construct exact endpoint neighborhoods, prove target-uniform nontrivial strong modules and restriction-stable leaf replay, and meet complete exponents at most `0.45`.

## Disproof track

Exhibit generic prime compatibility graphs, equal module trees with different singleton witnesses, or restriction families that split every nontrivial module.

## Positive and negative controls

- Positive: supplied cographs/graphs with known strong modules and labelled leaves must decompose and replay exactly.
- Negative: prime random graphs, false-twin label mutations, arbitrary restrictions, all strata, and blind targets.
- Baselines: IDEAs 120/338/348/352/369, explicit adjacency, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint neighborhood and nontrivial-module theorems, exact leaf replay, `1,000` independent rows, `100` blind descents, frozen caps, and `lambda,mu<=0.45`.
- Falsify on a prime instance, explicit source adjacency, one label collision, source-sized restriction rebuild, or either exponent at least `0.50`.
- Correct modular decomposition of a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-383/module_structure_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-383/prime_graph_and_label_cases.json`
- `ideas/artifacts/ECDLP-IDEA-383/leaf_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-383/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic quotient route, not modular decomposition. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a module tree is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-383/module_structure_obligations.md` and test whether source-label preservation forces every module in the minimal compatibility graph to be trivial.
