# ECDLP-IDEA-365 — Submodular-flow source decomposition

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_submodular_oracle_is_missing_source_feasibility_oracle`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; integral flow feasibility on a supplied network is not an ECDLP break.

## Falsifiable hypothesis

The five-source completion constraints define an endpoint-derived integral submodular-flow polyhedron whose augmenting paths return one exact signed source tuple and support blind target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode partial source choices as arcs, impose a submodular boundary function on vertex subsets, and use primal-dual augmenting paths to reach an integral feasible flow whose arc support is the relation tuple**. It is distinct only if the network and value oracle are public endpoint constructions, the elliptic fibre satisfies exchange/submodularity, and an integral flow maps back to exact points without a source-labelled arc table.

## Assumptions

1. Partial elliptic sums admit a target-uniform network representation with subgate arcs and no scalar/source advice.
2. The boundary function is submodular and evaluable below the query gate without solving restricted completion.
3. Integrality and augmenting-path corrections cover every source stratum and return exact signed labelled points.
4. Target updates change capacities/oracles without rebuilding source-sized state.
5. Network/oracle construction, minimization, augmentation, output, rank, logs, descent, verification, and memory are charged.

## Semantic fingerprint

`partial_elliptic_source_network | endpoint_submodular_boundary_oracle | primal_dual_integral_flow | exact_arc_to_point_section | restricted_feasibility | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the required boundary oracle must itself resolve source feasibility.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public source generation and target batching remain unconstructed.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-labelled arcs reproduce the forbidden edge surface.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; partial-sum arcs expanded through targets restore cubic work.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; exact represented source networks are controls.

## Closest primary literature

- Cunningham and Frank, [A Primal-Dual Algorithm for Submodular Flows](https://doi.org/10.1287/moor.10.2.251), is polynomial modulo a supplied submodular minimization oracle and explicit network.
- Edmonds and Giles, [A min-max relation for submodular functions on graphs](https://doi.org/10.1016/0022-247X(77)90092-0), establishes integral submodular-flow structure for represented submodular systems.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not give the submodular value oracle or integral source section.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, network, boundary function, oracle, capacity/update rules, restrictions, masks, and verifier.
2. Construct target-independent network/oracle from endpoints without source-labelled arcs.
3. For known-log targets, solve restricted feasible flows, return one tuple, and replay it by group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply identical augmentation/oracle rules to fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge oracle evaluation, minimization, arcs, augmentations, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

The submodular-flow theorem assumes the exact network and a value/minimization oracle. For arbitrary elliptic fibres, no exchange/submodular law is proved; evaluating whether a boundary set can complete is Query2P1. If arcs encode partial point choices, the network is source-sized. Thus the operation merges with matroid/transport/delta-matroid lanes (IDEAs 104, 137, 143, 212, 257) and does not remove the missing source operation.

## Proof track

Prove a public submodular boundary identity, oracle/query bounds, integral all-strata source section, and complete exponents at most `0.45`.

## Disproof track

Exhibit a violated submodular inequality/exchange, identical oracle state with different restricted nonemptiness, or source-sized network/oracle cost.

## Positive and negative controls

- Positive: supplied integral submodular-flow networks with known feasible arc supports.
- Negative: random elliptic fibres, source-permuted arcs, non-submodular completion functions, oracle-free endpoints, and blind targets.
- Baselines: IDEAs 104/137/143/212/257, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only network/oracle, exact restricted flow/source recovery, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on a source-labelled arc, completion oracle, violated submodularity, missed stratum, `B^3` network work, or either exponent at least `0.50`.
- A correct integral flow on a supplied toy network is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-365/submodular_boundary_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-365/exchange_and_oracle_cases.json`
- `ideas/artifacts/ECDLP-IDEA-365/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-365/cost_analysis.md`

## Interpretation boundary

This rejects this submodular-flow encoding, not submodular flow generally. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Flow feasibility is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-365/submodular_boundary_obligations.md` and test the completion function against submodularity without using a source oracle.
