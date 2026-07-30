# Pre-ID duplicate draft — Tsukiyama independent-source enumerator

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O09`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_conflict_graph_and_pairwise_maximality`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a maximal independent set or valid tuple is not an ECDLP result.

## Falsifiable hypothesis

An endpoint-derived conflict graph on factor occurrences has maximal independent sets
exactly equal to signed five-source target decompositions, so Tsukiyama enumeration under
restrictions supplies relations and fresh descent within the complete sub-rho gates.

## Mechanism-new operation

Tsukiyama et al. enumerate all maximal independent sets of a supplied graph with
output-sensitive total time. It counts only if edges arise from public endpoints without
source incidence and maximality is biconditional with exact target equality and replay.

## Assumptions

1. The conflict graph is endpoint-derived and sub-rho in size.
2. Pairwise independence is complete for the five-way target equation.
3. Every maximal independent set has exactly the required signed occurrence structure.
4. Empty fibres and restrictions are exact without rebuilding graph edges.
5. The same graph policy serves known-log relations and blind masked targets.

## Semantic fingerprint

`public_endpoint_conflict_graph | Tsukiyama_maximal_independent_set_enumeration | exact_target_compatible_set | signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-b_F05_bron_kerbosch_source_clique_preid_duplicate.md` — clique enumeration uses a supplied compatibility graph.
2. `ideas/rejected/preallocation/20260721-c_K05_luby_mis_source_peeling_preid_duplicate.md` — MIS maximality does not encode target equality.
3. `ideas/rejected/ECDLP-IDEA-200_hypergraph_container_relation_router_hypothesis.md` — graph/hypergraph edges expose source incidence.
4. `ideas/rejected/ECDLP-IDEA-137_matroid_representative_completion_kernel_hypothesis.md` — pairwise independence does not preserve every completion.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact existence/replay frontier.

## Closest primary literature

- Tsukiyama et al., [A New Algorithm for Generating All the Maximal Independent Sets](https://doi.org/10.1137/0206036), enumerates maximal independent sets of a supplied graph.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not provide a compact pairwise conflict graph.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the baseline.

This is a direct graph-enumerator merge with the Bron–Kerbosch and Luby-MIS pre-ID
controls; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, vertices, conflict predicate, enumeration order, restrictions, signs, strata, and verifier.
2. Build endpoint-only graph state within `B^(9/4+o(1))`; forbid source edges, pair tables, target fitting, and scalar labels.
3. For each known-log target, enumerate candidate MISs, map one to signed occurrences, and verify the elliptic sum.
4. Collect `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs while charging false/maximal outputs.
5. Reuse identical state for 100 fresh `R=Q+[t]P` targets, recover tuples, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph construction, adjacency tests, enumeration delay, all outputs, replay, density, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; all graph edges and MIS outputs are
charged. Promotion requires `lambda,mu<=0.45`, `B^(9/4)` setup/state, and
`B^(5/4)` fresh caps. Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Conflict edges are source incidence, and pairwise compatibility cannot express the rare
five-way elliptic sum without higher-order constraints. Maximal independent sets need not
have size five or satisfy the target, can be exponentially numerous, and do not certify an
empty target fibre.

## Proof track

Prove an endpoint-only graph where maximal independent sets are exactly occurrence-labelled
target tuples across restrictions, with output bounds and complete descent.

## Disproof track

Find one source-derived edge, false/missed tuple, wrong-size MIS, exponential output family,
lost sign, rebuild, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy graph with one labelled maximal independent set of size five.
- Negative: maximal wrong-size sets, pairwise-compatible false tuples, empty fibres, repeated points, and blind targets.
- Baselines: Bron–Kerbosch, Luby MIS, Query2P1, rho, and BSGS.
- Controls remain toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only with exact graph/source biconditionality, bounded outputs over four sizes, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on source incidence, one false/missed tuple, output/cap failure, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o09_conflict_graph_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o09_mis_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o09_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects the transplant, not maximal-independent-set enumeration. Evidence is toy,
heuristic, model-bound, and novelty-unverified; no run or breakthrough is claimed.

## Exactly one next executable action

1. Specify the endpoint conflict predicate and either prove pairwise maximality is target biconditional or preserve the smallest pairwise-compatible false tuple.
