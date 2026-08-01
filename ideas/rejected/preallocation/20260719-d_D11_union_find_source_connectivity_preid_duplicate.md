# Pre-ID duplicate draft — Union–find source connectivity

## Status and claim labels

- Prospect: `20260719-d-D11`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `dynamic_connectivity_quotient` / `conservative` / pre-ID screen
- State: `merged_rejected_supplied_edges_and_component_without_witness_path`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Create public vertices for partial elliptic endpoints and union two components whenever a source-compatible extension connects them. Near-constant amortized find/union would decide whether a target label joins the accepting component under restrictions, while a union forest would replay one signed tuple for relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

Union by rank with path compression maintains connected components of a supplied incremental edge stream. It counts only if compatible edges are generated endpoint-only, deletions/restrictions remain exact, and the forest returns an occurrence-valid path; connectivity after explicit edge insertion is a control.

## Assumptions

1. A sub-gate graph has connectivity biconditional with every complete signed relation and no spurious path recombination.
2. Vertex/edge construction, unions, finds, rollback/deletions, restrictions, witness forest, replay, rank, logs, descent, bit time, and memory are charged.
3. Arbitrary dyadic restrictions are supported without rebuilding all source edges.
4. One frozen graph serves known-log and fresh scalar-blind targets.
5. No explicit compatibility edge list, scalar-labelled vertex, post-hoc path selector, or solver-only rename is admitted.

## Semantic fingerprint

`endpoint_compatibility_graph | union_by_rank_path_compression | exact_restricted_component_membership | union_forest_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted support is the residual.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: the public source-resolving circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: source compatibility cannot be supplied as edges.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`: witness-faithful forest edges retain source incidence.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: explicit compatibility edges cross the source boundary.

## Closest primary literature

- Tarjan, [Efficiency of a good but not linear set union algorithm](https://doi.org/10.1145/321879.321884), analyzes find/union after elements and unions are supplied; it does not construct graph edges.
- Holm, de Lichtenberg, and Thorup, [Poly-logarithmic deterministic fully-dynamic algorithms for connectivity](https://doi.org/10.1145/502090.502095), makes deletion/restriction maintenance explicit but still consumes edge updates.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, vertices, edge rule, restriction/rollback policy, and verifier.
2. Build target-independent connectivity state within `B^(9/4+o(1))` without source-edge materialization.
3. On known-log targets, answer exact restricted component membership and replay five verified occurrences.
4. Collect at least `B` independent rows, preserve failed finds/dependencies, and solve factor-base logarithms.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover/verify a forest path, remove `t`, and verify `[x]P=Q`.
6. Charge vertex/edge generation, all updates/finds/rollbacks, negative queries, replay, rank, logs, descent, verification, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge every vertex/compatibility edge, union operation, rank/parent field, witness forest, and rollback/dynamic-connectivity state; let `q,q_m` charge target attachment, every restricted delete/rollback/find, exact negative certification, path validation, bisection, and replay. Let `delta,delta_t` be reciprocal verified relation/target success, `o` output, `r` verified independent-rank credit, `u` component/path ambiguity plus restriction rebuild overhead, and `ell,ell_m` factor-log time/state.

For `B=N^beta`, `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Setup/state must be `<=B^(9/4+o(1))`, fresh edge/update/restriction/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho time and BSGS time/memory are exponent-`0.50` controls. Compatibility-edge construction, deletions, witness validation, and rebuilds are charged.

## Likely fatal obstruction

Union–find makes queries cheap only after every relevant union edge has been generated. Those compatibility edges are the missing source incidence, ordinary union–find is insertion-only while restrictions delete sources, and component membership does not ensure a source-consistent five-step path. This merges with IDEAs `352/365/369/383/395` and pre-ID `A05/B09/C04`.

## Proof track

Construct edges endpoint-only, prove path/source biconditional and sub-gate fully dynamic restriction maintenance, then close replay and complete descent.

## Disproof track

Expose one source-bearing edge, a connectivity/source-recombination mismatch, restriction rebuild cost, or complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied incremental graph with planted labelled connection and auditable union forest.
- Negative: connected gadgets whose paths recombine invalid source labels, deletions that split components, absent targets, exceptional charts, and blind targets.
- Baselines: IDEAs `352/365/369/383/395`, pre-ID `A05/B09/C04`, explicit dynamic connectivity, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only edges, exact source-consistent restricted connectivity/replay, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied edge, one spurious component path, restriction rebuild, target dependence, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d11_edge_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d11_recombination_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d11_cost_analysis.md`

## Interpretation boundary

This rejects the elliptic graph construction, not union–find. Near-constant find time or correct toy connectivity is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d11_edge_provenance.md` and expand each proposed union edge into the exact endpoint/source predicate needed to insert it.
