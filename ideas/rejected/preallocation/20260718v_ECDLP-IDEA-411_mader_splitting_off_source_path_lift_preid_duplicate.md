# Pre-ID duplicate draft — Mader splitting-off source-path lift

## Status and claim labels

- Class: `mader_splitting_off_source_path_lift`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_endpoint_graph_compiler_is_source_incidence_and_terminal_connectivity_is_not_exact_restricted_relation_existence`
- Cohort: `20260718-v`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid splitting-off sequence is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructed compatibility multigraph admits restriction-stable admissible splitting-off that compresses internal partial-sum vertices while preserving exact terminal relation existence; charged `O(log B)` dyadic bisection and singleton verification then recover one labelled five-factor source below rho and BSGS.

## Mechanism-new operation

The screened operation is **repeatedly replace two incident edges at a nonterminal by one shortcut edge while preserving terminal connectivity, then unsplit a surviving terminal path to a factor tuple**. The required new law is an exact five-sum, occurrence-preserving analogue of Mader admissibility, not a different graph solver.

## Assumptions

1. The compatibility multigraph and terminals are built from public endpoints without materializing pair/triple source incidence.
2. Terminal connectivity is biconditional with restricted five-term relation existence, not merely a relaxation.
3. An admissible split can be selected and updated within the state/query caps under every restriction.
4. Terminal connectivity decides exact restricted existence; reverse history is optional because charged bisection and singleton verification can recover occurrences.
5. Graph construction, admissibility tests, splits, history, path output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_compatibility_multigraph | mader_admissible_splitting_off | exact_terminal_existence | dyadic_bisection_singleton_verification | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the open frontier asks for exact restricted existence with charged self-reduction, not connectivity alone.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; structured-coordinate compression must include preprocessing and source construction.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; materialized source joins already hit the cubic boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; source-recoverable products fail cost and rank.
5. `inputs/ledger_inventory.json` — imported `P1478`; compact transition tests still lack five-term source composition.

## Closest primary literature

- Lau and Yung, [Efficient edge splitting-off algorithms maintaining all-pairs edge-connectivities](https://doi.org/10.1137/100790239), gives splitting operations for a supplied undirected multigraph under its admissibility and degree hypotheses; it does not establish an elliptic five-sum/connectivity biconditional.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not construct a sparse graph whose connectivity is exact labelled relation existence.

No checked source gives the required endpoint compiler, five-ary biconditional, or provenance-free unsplitting; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, restrictions, graph compiler, terminals, admissibility rule, history format, and verifier.
2. Build the target-independent graph and split state within `B^(9/4+o(1))` without enumerating compatibility edges.
3. For known-log targets, apply restriction updates, decide exact relation existence by terminal connectivity, and use charged `O(log B)` dyadic bisection plus singleton verification to recover and verify five occurrences; unsplitting is an optional stronger route.
4. Collect at least `B` independent verified rows, charging edge output, failed splits, history, cancellations, and dependent rows; solve factor logs.
5. Reuse the unchanged compiler and split policy on fresh scalar-blind `Q+[t]P` targets.
6. Substitute logs, remove `t`, preserve every unsplitting branch, and verify `[x]P=Q`.
7. Charge graph construction, edge access, admissibility, splitting, history, path replay, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`; the total fresh online restriction/bisection sequence plus singleton verification must be at most `B^(5/4+o(1))`; and promotion needs `lambda<=0.45` and `mu<=0.45`. Here `q` charges every `O(log B)` positive-parent/negative-child query and singleton verification, while `o` charges final tuple or direct output. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Mader splitting starts from an explicit undirected multigraph satisfying admissibility hypotheses. Any graph whose edges are biconditional with elliptic factor compatibility is the missing source-incidence object, and the theorem does not make all-pairs connectivity equivalent to exact five-way zero-sum existence under restrictions. A split history can be retained at charged `O(E)` cost, so lack of provenance is not the theorem-level fatal boundary. This meets IDEAs 223, 352, 364, 369, and 388 at the supplied-graph and exact-predicate boundary.

## Proof track

Derive a public sparse graph compiler and five-sum/exact-connectivity biconditional under restrictions, recover labels by charged bisection and singleton verification, then certify the complete descent exponents.

## Disproof track

Show one edge/admissibility query is Query2P1, construct two restrictions with the same retained connectivity state but different relation existence, or prove graph/update scale above the caps.

## Positive and negative controls

- Positive: supplied multigraphs with known admissible splits and unique path ancestry must replay exactly.
- Negative: equal terminal connectivity with different source paths, parallel-edge multiplicity, signed cancellations, singleton relations, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 223/352/364/369/388, explicit compatibility graphs, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph construction, exact restricted relation/connectivity biconditional, charged `O(log B)` bisection and singleton verification, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one explicit source-edge table, one connectivity/existence mismatch, one inexact restriction update, cap violation, or either exponent at least `0.50`.
- Correct splitting on a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-411/splitting_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-411/connectivity_relation_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-411/restricted_existence_bisection_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-411/cost_analysis.md`

## Interpretation boundary

This rejects the screened relation-graph splitting route, not Mader's theorem. Every prospective check is toy, heuristic, model-bound, and novelty-unverified; connectivity preservation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-411/splitting_source_obligations.md` and classify every vertex, edge, admissibility test, shortcut, and history token by endpoint versus source dependence while auditing the exact restricted-existence predicate, positive-parent/negative-child bisection, and singleton verification.
