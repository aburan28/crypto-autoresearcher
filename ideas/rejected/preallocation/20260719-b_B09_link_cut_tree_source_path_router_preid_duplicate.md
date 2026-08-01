# Pre-ID duplicate draft — Link-cut-tree source path router

## Status and claim labels

- Prospect: `20260719-b-B09`; no canonical ID allocated
- Class / risk / lane: `dynamic_tree` / `conservative` / conservative pre-ID screen
- State: `merged_rejected_supplied_forest_and_missing_hyperedge_incidence`
- Evidence: complete corpus/ledger and primary-literature review only; no run; no contract
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; no breakthrough claim

## Falsifiable hypothesis

Maintain a forest of compatible partial sums under source restrictions; use link, cut, and exposed-path aggregates to locate a root-to-leaf path whose labels form an exact five-source relation. Dynamic updates and blind-target queries meet the P1553 rectangle.

## Mechanism-new operation

The native operation represents a supplied dynamic forest with preferred paths, supporting logarithmic link/cut/path queries. It counts only if the forest edges are endpoint-derived and exact five-way compatibility reduces to a tree-path predicate.

## Assumptions

1. A target-independent forest captures every signed/chart-complete occurrence without cyclic/hypergraph loss.
2. Edge generation and updates do not invoke source search or materialize a dense compatibility graph.
3. Path aggregates preserve exact labels and restrictions, not only endpoint totals.
4. Graph construction, link/cut rotations, misses, output, rank, logs, blind descent, and memory are charged.
5. No supplied source forest, post-hoc spanning tree, or uncharged edge oracle is admitted.

## Semantic fingerprint

`public_endpoint_forest | link_cut_preferred_path_updates | exact_path_existence | labelled_path_source_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ECFG-H673` — structure must alter exact relation supply.
2. `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION` — aggregate structure did not transfer sources.
3. `ECFG-H675` — exact public source resolution remains missing.
4. `ECFG-H676` — explicit source-fibre edges restore materialization.
5. `P1476` — complete membership/output/rank/descent/memory costs are required.

## Closest primary literature

- Sleator and Tarjan, [A Data Structure for Dynamic Trees](https://doi.org/10.1016/0022-0000(83)90006-5), maintains a supplied forest; it does not construct compatibility edges or solve a hypergraph source problem.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but not a forest reduction.
- Shoup, [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, forest grammar, restriction/update policy, and verifier.
2. Construct target-independent forest/state within `B^(9/4+o(1))` without source-product materialization.
3. On known-log targets, answer exact restricted existence and expose/replay a verified five-occurrence path.
4. Collect `B` independent rows and solve factor logs, retaining failed queries and dependencies.
5. Reuse state on `Q+[t]P`, recover a path/tuple, remove `t`, and verify `[x]P=Q`.
6. Charge edge construction, link/cut/path operations, restrictions, misses, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, use
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require setup/state `<=B^(9/4)`, fresh online `<=B^(5/4)`, and `lambda,mu<=0.45`; rho and BSGS remain `0.50` baselines.

## Likely fatal obstruction

Link-cut trees accelerate operations after a forest is supplied. Five-source incidence is naturally cyclic and hypergraphic; choosing a spanning forest discards accepting hyperedges, while supplying all compatible edges is the missing source table. This merges with IDEAs `217/223/352/369/376` and pre-ID SPQR `A05`.

## Proof track

Construct an endpoint-only forest with relation/path biconditional, prove restriction-stable labelled replay, and close complete descent costs.

## Disproof track

Show one required non-tree hyperedge, one source-bearing edge, identical path aggregates with different relation bits, or construction/update cost beyond a gate.

## Positive and negative controls

- Positive: a supplied dynamic forest with a planted labelled path.
- Negative: cyclic/hypergraph cases, relabelled equal path aggregates, no-hit restrictions, charts, and blind targets.
- Baselines: IDEAs `217/223/352/369/376`, pre-ID `A05`, explicit incidence, Query2P1, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only forest theorem, exact replay, `1,000` independent rows, `100` blind descents, and all caps/exponents.
- Falsify on one supplied edge, one lost relation, target-specific forest rebuild, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-b/b09_source_obligations.md`
- `ideas/rejected/preallocation/artifacts/20260719-b/b09_hypergraph_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260719-b/b09_cost_analysis.md`

## Interpretation boundary

Dynamic-tree correctness on a supplied forest is a control, not an ECDLP result or breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-b/b09_source_obligations.md` and prove or refute an exact forest reduction before implementing link/cut operations.
