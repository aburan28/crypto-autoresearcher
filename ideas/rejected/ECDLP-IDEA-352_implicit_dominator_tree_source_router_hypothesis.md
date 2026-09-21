# ECDLP-IDEA-352 — Implicit dominator-tree source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_dominator_backend_requires_explicit_source_DAG_and_does_not_select_paths`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a dominator tree or recovered toy path is not an ECDLP break.

## Falsifiable hypothesis

The coloured partial-sum relation DAG has a target-uniform implicit predecessor primitive and a narrow dominator structure whose restricted reachability decisions support bisection to exact signed source paths without materializing `B^3` transition traffic.

## Mechanism-new operation

The screened operation is **compute endpoint-rooted dominators in an implicit addition DAG, update restricted branches, and decide exact target reachability for path bisection**. It is new only if predecessor generation is cheaper than source completion and dominators preserve restricted reachability rather than merely vertices shared by all paths.

Minimum-interface correction: dominators need not name a path directly. A target-labelled, subset-stable exact reachability bit under arbitrary dyadic deck restrictions, with `O(log B)` bisection and all predecessor/restriction costs charged, suffices to recover one path.

## Assumptions

1. The partial-sum DAG and its DFS/predecessor access are public and source-free.
2. Predecessors are enumerated inside the setup/query gates without a transition table.
3. Dominator recursion yields exact restricted reachability, or one exact path directly, rather than only unrestricted aggregate reachability.
4. The representation handles multiple paths, repeated points, signs, singularities, and infinity.
5. DFS, link-eval, predecessor work, branches, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`implicit_coloured_partial_sum_DAG | endpoint_rooted_dominators | link_eval_without_edge_materialization | subset_stable_exact_reachability_decision | dyadic_path_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless source ancestry did not compress below the canonical edge set.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact exact source-resolving graph or circuit is the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; implicit arithmetic source-fibre generation remains the open operation.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; exact recursive transcripts retain at least one terminal record per witness.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1434-GENERATIVE-RULE-POSITIVE-CONTROL`; source generation is a control only when the scalar inputs are already supplied.

## Closest primary literature

- Lengauer and Tarjan, [A fast algorithm for finding dominators in a flowgraph](https://doi.org/10.1145/357062.357071), is near-linear after a graph and predecessor relation are supplied; it does not build an implicit elliptic relation graph or select one feasible source path.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint constraints rather than the predecessor oracle.

No checked source supplies the missing source-free graph interface; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, DAG grammar, predecessor routine, dominator algorithm, masks, and verifier.
2. Build only target-independent graph state without enumerating source edges.
3. For known-log targets, compute restricted dominator reachability, bisect to one complete source path, and replay the tuple.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Run the identical implicit graph and dominator procedure on fresh masked targets.
6. Substitute logs, remove masks, retain alternative paths, and verify `[x]P=Q`.
7. Charge graph construction, DFS, predecessor generation, link-eval, branches, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(1/5)` and terms `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m` as setup, density, query, rank, output, ambiguity, and factor-log exponents, use

`lambda=max(a,1/5+delta+q-r+o,ell,delta_t+q+o+u,1/5)`

`mu=max(a_m,q_m,1/5+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4)`, fresh query at most `B^(5/4)`, and `lambda,mu<=0.45`. Rho and BSGS time exponents are `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

At the first useful two-to-three-list layer, exact predecessor generation already represents about `B^3` source traffic. An oracle avoiding it is the desired source-completion oracle. Dominators identify vertices common to every path, not which path is feasible: generic relation DAGs can have only root and target as dominators, while unique-path instances leave discovering the path unchanged.

## Proof track

Construct a target-uniform sub-gate predecessor primitive, prove subset-stable exact reachability and bisection on every stratum, and derive full rank/log/descent costs.

## Disproof track

Give two relation DAGs with identical dominator trees and different source tuples, or prove predecessor generation/materialization costs at least `B^3`.

## Positive and negative controls

- Positive: planted layered DAGs with supplied narrow articulation chains.
- Negative: equal-dominator graphs with disjoint source paths, full-branching relation DAGs, and source-label permutations.
- Baselines: IDEAs 077/120/233/343, the explicit `B^3` join, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a public predecessor primitive, subset-stable exact reachability plus charged bisection or a direct path, zero source errors, 1,000 rows, 100 blind descents, and complete gates at most `0.45`.
- Falsify on an identical-dominator/different-source family with no public bounded path correction or section, a trivial tree plus `B^3` predecessor traffic, target-trained state, or exponent at least `0.50`.
- A correct dominator tree or one toy path cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-352/dominator_source_biconditional.md`
- `ideas/artifacts/ECDLP-IDEA-352/equal_tree_source_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-352/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-352/cost_analysis.md`

## Interpretation boundary

This rejects the implicit-source adaptation, not dominator algorithms. All checks would be toy, heuristic, model-bound, and novelty-unverified. Graph correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-352/equal_tree_source_counterexamples.json` with two smallest coloured relation DAGs having the same dominator tree and disjoint valid source tuples.
