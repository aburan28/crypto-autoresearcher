# Pre-ID duplicate draft — push–relabel source-flow router

## Status and claim labels

- Prospect: `20260719-c-C04`; no canonical ID allocated
- Class / risk / lane: `flow_algorithm` / `conservative` / pre-ID screen
- State: `merged_rejected_solver_on_supplied_source_network`
- Evidence: ledger/corpus and primary-literature review only; no experiment
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Compile endpoint compatibility into a capacitated network whose integral unit flows correspond exactly to signed five-source relations, then use push–relabel excess propagation and min-cut self-reduction to recover independent rows and fresh blind descents below rho and BSGS.

## Mechanism-new operation

The operation maintains a preflow, vertex excesses, residual capacities, and admissible height-labelled pushes on a supplied network. It counts only if public endpoints construct a compact relation-exact network without source edges; changing the max-flow solver is a duplicate.

## Assumptions

1. Integral source-to-sink flows are biconditional with all signed/chart-complete relations and decompose to actual point occurrences.
2. Network construction, residual updates, pushes, relabels, restrictions, output, rank, logs, descent, and memory are charged.
3. Integral-capacity optima remain integral, and capacity aggregation introduces no integral path recombination that fails to correspond to one source tuple.
4. Frozen target-independent structure supports arbitrary restrictions and fresh `Q+[t]P` without rebuild.
5. No explicit incidence network, source-labelled edge catalogue, post-hoc flow decomposition, or uncharged oracle is admitted.

## Semantic fingerprint

`public_endpoint_capacity_network | Goldberg_Tarjan_push_relabel_preflow | exact_unit_flow_existence | integral_path_source_decomposition | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted existence and replay are required.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H673`: graph structure must improve exact relation supply.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a public source-resolving circuit is missing.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: explicit source fibres restore the forbidden join.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: explicit source-edge networks are materialized evidence.

## Closest primary literature

- Goldberg and Tarjan, [A New Approach to the Maximum-Flow Problem](https://doi.org/10.1145/48014.61051), solves maximum flow in a supplied capacitated graph.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but not a compact integral-flow compiler.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), supplies the matched baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, network grammar, capacities, restrictions, and verifier.
2. Construct target-independent network/state within `B^(9/4+o(1))` without source incidence materialization.
3. For known-log targets, decide exact restricted unit flow and decompose it to five verified occurrences.
4. Retain failures/dependencies, collect at least `B` independent rows, and solve factor logs.
5. Reuse state on fresh scalar-blind `Q+[t]P`, replay/verify a flow witness, remove `t`, and verify `[x]P=Q`.
6. Charge graph construction, all residual operations, negative restrictions, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; Pollard rho time and BSGS time/memory remain `0.50` baselines.

## Likely fatal obstruction

Push–relabel only changes the solver after the network exists. A faithful layered network has an edge or gadget for source compatibility; omitting those edges admits spurious recombinations, while retaining them costs the missing incidence table. This is a solver substitution merging with IDEAs `345/365/369/370/382`.

## Proof track

Construct an endpoint-only compact network, prove an integral-flow/source bijection under restrictions, and close full descent costs.

## Disproof track

Show one source-bearing capacity, an integral recombined flow with no valid source tuple, a lost witness, or complete cost beyond the gates.

## Positive and negative controls

- Positive: supplied layered integral networks with planted source paths.
- Negative: same cuts with different path provenance, integrality-preserving recombination gadgets, missing edges, exceptional charts, restrictions, blind targets.
- Baselines: IDEAs `345/365/369/370/382`, generic max-flow, explicit joins, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only network construction, exact path replay, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one supplied source edge, one false flow/source mismatch, target rebuild, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-c/c04_network_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-c/c04_flow_mutations.json`
- `ideas/rejected/preallocation/artifacts/20260719-c/c04_cost_analysis.md`

## Interpretation boundary

This rejects the transplant, not push–relabel. A valid max flow, relation, or toy speedup is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-c/c04_network_provenance.md` and charge every vertex, capacity, and residual edge needed for source fidelity.
