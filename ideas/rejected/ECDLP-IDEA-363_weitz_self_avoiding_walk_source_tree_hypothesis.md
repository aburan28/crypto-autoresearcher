# ECDLP-IDEA-363 — Weitz self-avoiding-walk source tree

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_saw_tree_requires_supplied_source_constraint_graph`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correlation decay or a correct marginal is not an ECDLP break.

## Falsifiable hypothesis

The elliptic relation fibre admits a bounded-degree public constraint graph whose Weitz self-avoiding-walk tree gives a target-uniform exact restricted-nonemptiness decision, or a zero-safe approximation convertible to one, below the P1553 setup and query gates.

## Mechanism-new operation

The screened operation is **unroll a loopy source-constraint graph into a self-avoiding-walk tree with boundary conditions, then recurse on tree messages to decide whether a restricted target fibre is empty**. It differs from a generic belief-propagation backend only if the constraint graph is derived from endpoints without enumerating source tuples and the recursion is exact or zero-safe on rare fibres. Charged dyadic restrictions must recover one labelled tuple.

## Assumptions

1. A bounded-degree source-constraint graph and its boundary rules are constructible from public endpoints without source-edge enumeration.
2. The hard-core/independent-set partition function or an exact analogue has zero iff the elliptic restricted fibre is empty.
3. Correlation decay is uniform for campaign and fresh-target graphs and remains zero-safe under arbitrary dyadic restrictions.
4. The truncated tree has at most `B^(5/4+o(1))` target-query work and does not hide exponential boundary state.
5. Graph construction, tree expansion, precision, failure probability, output, rank, logs, descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_derived_source_constraint_graph | self_avoiding_walk_tree_unrolling | boundary_condition_message_recursion | zero_safe_restricted_nonemptiness | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a source-resolving circuit must be constructed, not assumed as the constraint graph.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; arithmetic source-fibre generation and target batching remain the dominant missing operations.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; an explicit constraint edge is already source-bearing evidence.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; source generation from pair advice restores cubic traffic.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; exact represented joins are only controls.

## Closest primary literature

- Weitz, [Counting independent sets up to the tree threshold](https://doi.org/10.1145/1132516.1132538), constructs a self-avoiding-walk tree for a supplied bounded-degree graph and proves approximate counting below a uniqueness threshold.
- Guo and Lu, [Uniqueness, spatial mixing, and approximation for the hard-core model](https://arxiv.org/abs/1511.04250), analyzes correlation-decay approximations on represented graphs, not exact hidden elliptic fibres.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than a bounded-degree source graph or zero-safe tree recursion.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, constraint-graph rule, boundary order, activity, restriction policy, precision, masks, and verifier.
2. Construct the target-independent graph/tree interface from endpoints without listing relations.
3. On known-log targets, decide restricted nonemptiness, bisect to one tuple, and replay it by direct addition.
4. Collect and rank at least `B` verified rows, solve factor logs, and independently verify them.
5. Use the identical graph rule and recursion for fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge graph and boundary construction, tree size, precision, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

The Weitz theorem begins with an explicit graph and returns approximate marginals under uniqueness. Constructing the elliptic source-conflict graph exposes the missing source incidences, while a rare relation can have exponentially small mass so multiplicative approximation is not a zero-safe emptiness test. Outside uniqueness, the SAW tree or its boundary state expands exponentially. This merges with the supplied-model/aggregate boundary of IDEAs 079, 240, 316, and 342.

## Proof track

Construct a source-free bounded-degree graph, prove an exact zero biconditional and uniform correlation decay under restrictions, and derive complete exponents at most `0.45`.

## Disproof track

Exhibit identical public local neighborhoods with different restricted fibre nonemptiness, a uniqueness violation, or source-edge/tree growth of at least `B^3`.

## Positive and negative controls

- Positive: supplied bounded-degree hard-core graphs below the uniqueness threshold with exact small-instance enumeration.
- Negative: source-permuted graphs, rare singleton fibres, long loops, nonuniqueness activities, and endpoint-only instances without adjacency.
- Baselines: IDEAs 079/240/316/342, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph construction, zero-error restricted decisions plus bisection, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on a supplied source edge, one false zero, one missed stratum, nonuniform correlation decay, `B^3` tree/graph work, or either exponent at least `0.50`.
- Approximate marginals on a supplied toy graph are controls and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-363/source_graph_construction_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-363/saw_tree_zero_safety_cases.json`
- `ideas/artifacts/ECDLP-IDEA-363/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-363/cost_analysis.md`

## Interpretation boundary

This rejects the screened SAW-tree route, not correlation decay or all exact recursion. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A correct marginal is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-363/source_graph_construction_obligations.md` and test whether the required bounded-degree adjacency can be defined from endpoints without source enumeration.
