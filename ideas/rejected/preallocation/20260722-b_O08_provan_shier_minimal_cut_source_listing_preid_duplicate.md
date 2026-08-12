# Pre-ID duplicate draft — Provan–Shier minimal-cut source listing

## Status and claim labels

- Provisional ID: `PREID-20260722-b-O08`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_source_graph_and_cut_certificate`.
- Class/risk: algorithm / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a minimal cut or relation certificate is not an ECDLP result.

## Falsifiable hypothesis

Public endpoint data define a compact terminal network whose minimal `(s,t)` cuts are in
bijection with signed five-source target decompositions. Provan–Shier listing under source
restrictions would replay occurrences and complete relations and blind descent below rho.

## Mechanism-new operation

The Provan–Shier paradigm lists a cut family of a supplied graph using pivoted restrictions.
It counts only if the network is endpoint-derived without compatibility/source edges, every
cut is exactly one target tuple, and cut output supports occurrence-labelled replay.

## Assumptions

1. Vertices, edges, capacities, and terminals are endpoint-only and fit the setup cap.
2. Minimality is biconditional with exact target equality, not merely separation.
3. Cuts retain signs, multiplicities, ordering, and exceptional strata.
4. Restriction updates do not rebuild source incidence and exact negatives fit the online cap.
5. One frozen network policy serves known-log and fresh masked targets.

## Semantic fingerprint

`public_endpoint_terminal_network | Provan_Shier_minimal_cut_listing | exact_restricted_cut_family | cut_to_signed_occurrence_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-369_gomory_hu_cut_tree_source_router_hypothesis.md` — cut summaries start from an explicit source graph.
2. `ideas/rejected/ECDLP-IDEA-365_submodular_flow_source_decomposition_hypothesis.md` — flow/cut certificates do not return rare source tuples.
3. `ideas/rejected/ECDLP-IDEA-343_avis_fukuda_reverse_search_source_enumerator_hypothesis.md` — listing presupposes represented feasible objects.
4. `ideas/rejected/preallocation/20260720-c_G10_stoer_wagner_source_mincut_preid_duplicate.md` — min-cut partitions are not source occurrences.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact source-return frontier.

## Closest primary literature

- Provan and Shier, [A Paradigm for Listing (s,t)-Cuts in Graphs](https://doi.org/10.1007/BF01961544), lists cut families in supplied graphs.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not construct a compact cut network.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

The title is distinct, but its information flow merges with supplied cut/network and
certificate-only lanes; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, network construction, terminals, capacities, pivot policy, restrictions, signs, strata, and verifier.
2. Build target-independent endpoint state within `B^(9/4+o(1))`; prohibit source edges, explicit relation graphs, target caches, and scalar labels.
3. For each known-log target, construct allowed target state, list a cut, invert it to signed occurrences, and verify the point sum.
4. Collect `max(d_FB+32,1000)` rows, reach rank `d_FB`, and solve all factor logs while charging rejected cuts.
5. Reuse identical state for 100 fresh `R=Q+[t]P` targets, invert a cut to occurrences, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge graph construction, pivots, cut outputs, negatives, restrictions, inversion, density, rank, logs, bits, and memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; relation and target reciprocal
densities be `N^delta,N^delta_t`; query/workspace be `N^q,N^q_m`; verified-rank
credit be `N^r`; output be `N^o`; ambiguity/amplification be `N^u`; and factor-log
time/memory be `N^ell,N^ell_m`.
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; graph construction, all cut outputs,
and inversion are charged. Promotion requires `lambda,mu<=0.45`, setup/state
`<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`. Pollard rho
expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

Network edges are the missing source-compatibility incidence. Cut minimality certifies
separation, not five-way elliptic equality, and many cuts can encode no source or aggregate
several sources. Listing is output-sensitive after the graph exists and arbitrary restrictions
can require rebuilding it.

## Proof track

Prove an endpoint-only compact network and an all-strata cut/source bijection with exact
restriction replay and complete descent costs.

## Disproof track

Find one source-derived edge, cut without tuple, tuple without cut, equal cuts/different
occurrences, exponential family, rebuild, or exponent `>=0.50`.

## Positive and negative controls

- Positive: a supplied toy graph whose unique minimal cut names five labelled edges.
- Negative: equal cut values/different witnesses, empty fibres, parallel edges, repeated points, and blind targets.
- Baselines: Gomory–Hu, Stoer–Wagner, Query2P1, rho, and BSGS.
- Controls are toy and model-bound.

## Quantitative promotion and falsification gates

- Promote only with an endpoint network theorem, exact cut/source replay over four sizes, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on source incidence, one cut/source mismatch, unpaid output/rebuild, cap failure, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-b/o08_network_constructor_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-b/o08_cut_source_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-b/o08_cost_analysis.md`

The artifact root is absent.

## Interpretation boundary

This rejects only the elliptic cut-listing route, not the graph algorithm. Evidence remains
toy, heuristic, model-bound, and novelty-unverified; no run or breakthrough is claimed.

## Exactly one next executable action

1. Specify the endpoint network and either prove minimal-cut/source biconditionality with signed replay or preserve the first cut that fails the mapping.
