# Pre-ID duplicate draft — Multilevel-coarsened source partition

## Status and claim labels

- Prospect: `20260719-d-D12`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `multilevel_graph_coarsening` / `representation-changing` / pre-ID screen
- State: `merged_rejected_supplied_graph_and_heuristic_coarsening_loss`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Construct a public weighted compatibility graph of partial elliptic sums, repeatedly contract heavy edges, partition the coarse graph, then uncoarsen/refine so every target's accepting source fibre lies in a small boundary region. Exact restricted search inside that region would replay relations and fresh blind descents below rho and BSGS.

## Mechanism-new operation

Multilevel partitioning alternates heavy-edge contraction, coarse partitioning, and uncoarsening refinement on a supplied graph. It counts only if graph construction is endpoint-only and coarsening provably preserves every rare accepting occurrence and its ancestry; heuristic graph preprocessing is a control.

## Assumptions

1. A sub-gate weighted graph is biconditional with all signed source relations and has a target-uniform small-boundary partition hierarchy.
2. Graph construction, edge weights, contractions, partition/refinement, restrictions, boundary search, replay, rank, logs, descent, bit time, and memory are charged.
3. Contracted vertices retain exact point ancestry without restoring all original edges.
4. One frozen hierarchy serves known-log and fresh scalar-blind targets.
5. No explicit compatibility graph, source-labelled contraction table, post-hoc selector, same-field isogeny variant, or heuristic-only promotion is admitted.

## Semantic fingerprint

`endpoint_weighted_compatibility_graph | heavy_edge_multilevel_coarsening | exact_rare_fibre_boundary_preservation | uncoarsened_path_to_signed_sources | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact restricted target support is the residual.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a public source-resolving circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: source fibres cannot be supplied as a weighted graph.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`: lossless ancestry retains the graph's source edges.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: constructing the weighted graph crosses the source boundary.

## Closest primary literature

- Karypis and Kumar, [A fast and high quality multilevel scheme for partitioning irregular graphs](https://doi.org/10.1137/S1064827595287997), contracts and refines a supplied graph heuristically; it does not preserve an unknown exact singleton.
- Hendrickson and Leland, [A multilevel algorithm for partitioning graphs](https://www.osti.gov/biblio/10137304), is the neighboring coarsen/uncoarsen framework on represented graphs.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, graph/weights, contraction/refinement rules, restrictions, and verifier.
2. Build target-independent hierarchy within `B^(9/4+o(1))` without explicit source-edge materialization.
3. On known-log targets, localize exact restricted support to a small boundary and replay five verified occurrences.
4. Collect at least `B` independent rows, preserve failed partitions/dependencies, and solve factor-base logarithms.
5. Reuse unchanged hierarchy on fresh scalar-blind `Q+[t]P`, recover/verify a source path, remove `t`, and verify `[x]P=Q`.
6. Charge graph construction, every contraction/refinement, boundary searches, restrictions, replay, rank, logs, descent, verification, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge every graph vertex/edge/weight, heavy-edge contraction, coarse partition, refinement level, and exact ancestry record; let `q,q_m` charge target localization, every restricted hierarchy update/rebuild, boundary scan, negative certification, uncoarsening, bisection, and replay. Let `delta,delta_t` be reciprocal verified relation/target success after boundary localization, `o` output, `r` verified independent-rank credit, `u` coarse-cell/source ambiguity plus heuristic restarts/rebuilds, and `ell,ell_m` factor-log time/state.

With `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`, `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, total fresh graph/hierarchy/boundary/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Rho and BSGS remain exponent-`0.50` controls. Source-graph construction, retained ancestry, every restriction rebuild, and all scanned boundary items are charged.

## Likely fatal obstruction

The weighted compatibility graph is already the missing source incidence. Heavy-edge coarsening is heuristic and can merge a singleton accepting vertex with nonaccepting mass; keeping exact ancestry and every cut edge restores the original graph, while arbitrary restrictions can invalidate the hierarchy. This merges with IDEAs `326/348/369/370/386/393` and pre-ID `A05/A08/B08/C10`.

## Proof track

Construct the graph endpoint-only and prove target-uniform exact singleton preservation, small boundary, source replay, and restriction stability through every contraction, then close full costs.

## Disproof track

Expose source-bearing edges/weights, a coarsening that merges opposite support bits, restriction rebuild cost, or any complete exponent outside the gates.

## Positive and negative controls

- Positive: a supplied planted clustered graph with a labelled rare boundary vertex and exact ancestry.
- Negative: equal coarse graphs with different singleton support, adversarial heavy-edge contractions, restrictions, exceptional charts, and blind targets.
- Baselines: IDEAs `326/348/369/370/386/393`, pre-ID `A05/A08/B08/C10`, uncoarsened graph search, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only graph/weights, exact all-restriction singleton preservation/replay, sub-gate boundary size, `1,000` independent rows, `100` blind descents, and `lambda,mu<=0.45`.
- Falsify on one source edge, one lost/merged witness, target-trained hierarchy, restriction rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d12_graph_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d12_coarsening_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d12_cost_analysis.md`

## Interpretation boundary

This rejects the elliptic graph transplant, not multilevel partitioning. A small cut or good toy partition is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d12_graph_provenance.md` and classify every vertex, edge, weight, contraction, and retained ancestry field by endpoint/source dependence.
