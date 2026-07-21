# ECDLP-IDEA-364 — Reingold universal-exploration source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_rotation_map_is_missing_source_neighbor_oracle`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; log-space connectivity in a supplied graph is not an ECDLP break.

## Falsifiable hypothesis

Partial elliptic sums form a public bounded-degree undirected graph with an endpoint-computable rotation map, so a Reingold universal exploration sequence decides restricted target reachability and recovers one exact source path within the P1553 gates.

## Mechanism-new operation

The screened operation is **regularize an implicit partial-sum graph, follow a universal exploration sequence through its rotation map, decide whether a restricted target state lies in the start component, and replay the discovered path as a source tuple**. It is distinct only if the rotation map is derived from endpoints without a source-neighbor oracle, exploration time is subgate rather than merely logarithmic space, and arbitrary deck restrictions preserve exact reachability.

## Assumptions

1. A bounded-degree undirected partial-sum graph encodes exact five-source relations as source-to-target paths.
2. Its rotation map is evaluable from public endpoints without listing factor choices or relation edges.
3. Universal exploration length and path reconstruction fit `B^(5/4+o(1))` fresh-target work and `B^(9/4+o(1))` setup/state.
4. Dyadic source restrictions, repeated/signed/singular/infinity/coloured strata, and target updates preserve the reachability biconditional.
5. Regularization, rotation queries, repeated path recovery, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`implicit_partial_sum_graph | endpoint_rotation_map | Reingold_universal_exploration_sequence | restricted_connectivity_decision | exact_path_to_source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; the rotation map must construct the missing source-resolving operation.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public source-fibre generation and target batching remain unconstructed.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit graph neighbors are source-bearing evidence.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; enumerating partial-sum neighbors from pair advice restores cubic traffic.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; traversal of a supplied exact graph is only a control.

## Closest primary literature

- Reingold, [Undirected connectivity in log-space](https://doi.org/10.1145/1391289.1391291), gives deterministic log-space connectivity using rotation-map access to a supplied bounded-degree graph.
- Aleliunas et al., [Random walks, universal traversal sequences, and the complexity of maze problems](https://doi.org/10.1109/SFCS.1979.34), studies traversal of explicit graphs with neighbor access.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than a rotation map or path/source section.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, graph states, rotation map, regularization, exploration sequence, restrictions, masks, and verifier.
2. Construct the target-independent graph interface without source-edge enumeration or scalar labels.
3. On known-log targets, decide restricted connectivity, self-reduce/replay one path, and verify its endpoint by group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Reuse the identical graph/rotation rule for fresh scalar-blind `Q+[t]P` targets.
6. Recover a path/tuple, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge graph/rotation construction, every exploration and replay, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Reingold's theorem saves space after a rotation map for every vertex/edge is available; it does not construct neighbors or give sublinear time. For partial sums, enumerating the next factor/source is the missing incidence oracle, and universal exploration may visit the entire source graph. Exact path recovery repeats that work. This merges with graph-state/automaton/reverse-search lanes IDEAs 077, 083, 120, 343, and 352.

## Proof track

Construct a source-free bounded-degree rotation map, prove restricted connectivity equals exact relation existence and path replay, and derive complete exponents at most `0.45`.

## Disproof track

Show one rotation query requires source enumeration, prove the reachable graph is source-sized, or exhibit identical accessible graph state with different restricted relation paths.

## Positive and negative controls

- Positive: supplied bounded-degree mazes with known rotation maps and labelled paths.
- Negative: source-permuted rotation tables, implicit graphs without neighbor access, source-sized components, dyadic restrictions, and blind targets.
- Baselines: IDEAs 077/083/120/343/352, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only rotation access, exact restricted path/source recovery, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on a source-neighbor oracle, one false reachability decision, source-sized exploration, missed stratum, `B^3` traffic, or either exponent at least `0.50`.
- Log-space traversal of a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-364/rotation_map_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-364/restriction_and_path_cases.json`
- `ideas/artifacts/ECDLP-IDEA-364/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-364/cost_analysis.md`

## Interpretation boundary

This rejects the screened implicit-graph router, not Reingold's connectivity theorem. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Log space is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-364/rotation_map_obligations.md` and prove whether one rotation query avoids source-neighbor enumeration.
