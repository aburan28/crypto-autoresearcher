# Pre-ID duplicate draft — Makino–Uno biclique source enumerator

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O12`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_bipartite_graph_and_maximality_only`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a maximal biclique or valid relation is not an ECDLP result.

## Falsifiable hypothesis

Endpoint-derived compatibility between factor-half occurrences forms a compact bipartite
graph whose maximal bicliques are exactly signed five-source target decompositions. Makino–Uno
enumeration and restriction replay would complete relation collection and blind descent below rho.

## Mechanism-new operation

Makino–Uno enumerates maximal cliques and maximal bipartite cliques of a supplied graph with
polynomial-delay variants. It counts only if adjacency is endpoint-derived without source
incidence, maximality enforces target equality, and biclique output replays signed occurrences.

## Assumptions

1. The bipartite graph is endpoint-derived and fits setup/state caps.
2. Biclique completeness/maximality is biconditional with the five-way target sum.
3. Output retains all signs, occurrence labels, multiplicities, and exceptional strata.
4. Restrictions and empty fibres have exact sub-rho behavior without graph rebuild.
5. The same graph policy works for known-log and fresh masked targets.

## Semantic fingerprint

`public_endpoint_bipartite_compatibility | Makino_Uno_maximal_biclique_enumeration | exact_target_source_block | signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-b_F05_bron_kerbosch_source_clique_preid_duplicate.md` — clique enumeration consumes a supplied graph.
2. `ideas/rejected/ECDLP-IDEA-353_fully_sparse_boolean_product_witness_router_hypothesis.md` — Boolean-product witnesses require represented adjacency and source inverse.
3. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — joins charge source-bearing compatibility and output provenance.
4. `ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md` — bipartite matching structure begins from source edges.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence/replay frontier.

## Closest primary literature

- Makino and Uno, [New Algorithms for Enumerating All Maximal Cliques](https://doi.org/10.1007/978-3-540-27810-8_23), includes maximal bipartite-clique enumeration for supplied graphs.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not construct sparse compatibility edges or a biclique/source bijection.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the baseline.

This directly merges with clique, Boolean-product witness, and join lanes; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, bipartition, adjacency predicate, enumeration order, restrictions, signs, strata, and verifier.
2. Build endpoint-only graph state within `B^(9/4+o(1))`; forbid source edges, pair tables, target caches, and scalar labels.
3. For each known-log target, enumerate bicliques, map one to signed occurrences, and verify the elliptic sum before retaining a row.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs while charging false/maximal outputs.
5. Reuse identical state for 100 fresh `R=Q+[t]P` targets, recover tuples, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph construction, matrix-multiplication or degree-dependent delay, all bicliques, replay, density, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; all edges, preprocessing, outputs,
and inversion are charged. Promotion requires `lambda,mu<=0.45`, setup/state
`<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Pollard rho
expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Compatibility edges are the missing source-incidence table. A maximal biclique captures
complete bipartite adjacency, not the five-way elliptic sum, and maximal bicliques can be
exponentially numerous. Polynomial delay begins only after the full graph is supplied and
does not certify an empty target fibre cheaply.

## Proof track

Prove an endpoint-only sparse graph whose maximal bicliques are exactly all-strata target
tuples, with charged output, signed replay, and complete descent inside the caps.

## Disproof track

Find one source-derived edge, false/missed tuple, exponential output family, wrong-size
biclique, restriction rebuild, lost sign, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy bipartite graph with one labelled maximal biclique.
- Negative: maximal wrong-size bicliques, same graph/different source interpretation, empty fibres, repeated signs, and blind targets.
- Baselines: Bron–Kerbosch, Boolean-product witnesses, explicit joins, Query2P1, rho, and BSGS.
- Controls remain toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only with exact graph/source biconditionality, bounded outputs over four sizes, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on source incidence, one biclique/source mismatch, output/cap failure, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o12_bipartite_graph_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o12_biclique_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o12_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects only the transplant, not Makino–Uno enumeration. Evidence is toy, heuristic,
model-bound, and novelty-unverified; no experiment or breakthrough is claimed.

## Exactly one next executable action

1. Specify the endpoint adjacency predicate and either prove maximal-biclique/source biconditionality with bounded output or preserve the smallest false biclique.
