# Pre-ID duplicate draft — Régin all-different source filter

## Status and claim labels

- Prospect: `20260722-a-N06`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: algorithm / conservative / secondary screen.
- State: `merged_rejected_supplied_variable_value_graph_and_distinctness_only`.
- Evidence: exhaustive ledger/corpus and primary-literature review only; no experiment ran.
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; domain consistency or a matching is not an ECDLP result.

## Falsifiable hypothesis

Signed factor-base relation positions form an endpoint-derived variable-value graph in which a Régin all-different filter, combined with the elliptic target constraint, removes all values lacking a global matching and returns exact occurrence-labelled tuples with sufficient density for full factor logs and 100 blind descents below rho/BSGS.

## Mechanism-new operation

The screened operation computes a maximum matching in the variable-value graph and uses alternating paths/components to delete values not belonging to any complete distinct assignment. It counts only if graph edges are endpoint-derived, matching support is also sufficient for the elliptic sum constraint, and a surviving matching replays the signed target tuple.

## Assumptions

1. Variable domains/edges are public-endpoint-derived without explicit tuple or compatibility tables.
2. Distinctness is a valid frozen stratum and repeated/tangent cases are handled separately and exactly.
3. Matching support plus local elliptic factors is globally complete for target existence.
4. Alternating-graph state and restrictions fit both gates and preserve occurrence labels.
5. One target-independent filter supports relation collection and blind masks.

## Semantic fingerprint

`public_endpoint_variable_value_graph | Regin_all_different_matching_filter | exact_target_supported_domains | signed_matching_replay | complete_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — matching support cannot replace exact target-labelled existence/replay.
2. `ideas/rejected/ECDLP-IDEA-137_matroid_representative_completion_kernel_hypothesis.md` — represented independence/extension data are supplied state.
3. `ideas/rejected/ECDLP-IDEA-345_linear_matroid_parity_source_packing_hypothesis.md` — packing/matching begins after source elements and compatibility exist.
4. `ideas/rejected/preallocation/20260721-e_M06_micali_vazirani_blossom_source_matching_preid_duplicate.md` — general matching on a supplied graph can recombine invalid five-way sources.
5. `ideas/rejected/ECDLP-IDEA-147_moser_tardos_relation_resampling_hypothesis.md` — locally supported assignments do not create the rare exact target fibre.

## Closest primary literature

- Régin, [A Filtering Algorithm for Constraints of Difference in CSPs](https://aaai.org/Papers/AAAI/1994/AAAI94-055.pdf), enforces generalized arc consistency for a supplied all-different constraint using matching; it does not construct elliptic compatibility or target sums.
- Micali and Vazirani, [An O(sqrt(V)E) Algorithm for Finding Maximum Matching](https://doi.org/10.1109/SFCS.1980.12), is a supplied-graph matching control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the nonlocal endpoint equation.

The transplant's exact endpoint graph and global sufficiency are absent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, `B=N^(1/5)`, factor base/decks, distinct/repeated strata, variable-value graph rule, matching/filter policy, restrictions, masks, and verifier.
2. Build target-independent graph/state within `B^(9/4+o(1))`; forbid explicit tuple/edge catalogues beyond caps, log labels, target-fitted advice, dense resultants, and Query2P1.
3. For known-log `R`, combine exact endpoint factors with filtering, use at most `5 ceil(log_2 B)+O(1)` restrictions, recover actual signed occurrences, and verify their point sum.
4. Collect at least `max(d_FB+32,1000)` verified rows, retain failures/dependencies, require rank `d_FB`, and solve all factor logs.
5. Reuse eligible state for fresh `Q+[t]P`, recover/verify a tuple, compute the scalar, and verify `[x]P=Q` for 100 blind targets.
6. Charge graph construction, matching, alternating reachability, restrictions, repeated-stratum routing, output, verification, density, rank, factor solve, masks, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use setup/state `N^a,N^a_m`, densities `N^delta,N^delta_t`, query/workspace `N^q,N^q_m`, rank credit `N^r`, output `N^o`, amplification `N^u`, and factor-log costs `N^ell,N^ell_m`. Charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

Require `lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`. Rho and BSGS remain exponent `0.50`; every edge and matching update is charged.

## Likely fatal obstruction

All-different filtering answers whether values can participate in some distinct assignment in an explicit variable-value graph. It does not enforce the five-way elliptic sum. Pairwise/value support can recombine into matchings that miss the target, and exact target-aware edges are precisely the missing source incidence. Repeated-source strata further violate the all-different premise. Thus it merges with matching and local-consistency controls.

## Proof track

Prove a public endpoint graph whose matching support is biconditional with the all-strata target relation and whose alternating inverse returns signed occurrences within the complete gates.

## Disproof track

Exhibit a perfect matching with no target relation, a valid repeated-source relation removed by all-different, a source-derived edge, equal filtered graphs with different target sources, or exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied toy all-different CSPs with unique labelled matchings.
- Negative: matching-but-no-target instances, repeated/tangent relations, equal domains with different sums, singleton fibres, and blind targets.
- Baselines: Micali–Vazirani/Hopcroft–Karp, explicit compatibility, P1553 R4, rho, and BSGS.
- Controls are toy/model-bound; filtering correctness is not promotion evidence.

## Quantitative promotion and falsification gates

- Promote only on four-size exactness, all-strata completeness, charged source replay, full rank/logs, 100 blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one spurious/lost relation, supplied graph edge, cap breach, or complete exponent at least `0.50`.
- A matching or verified relation is never itself a breakthrough.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260722-a/n06_graph_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260722-a/n06_matching_target_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260722-a/n06_cost_analysis.md`

The prospective artifact root is not created.

## Interpretation boundary

This rejects the screened ECDLP transplant, not Régin filtering. Evidence remains toy, heuristic, model-bound, and novelty-unverified. No experiment or breakthrough is claimed.

## Exactly one next executable action

1. Write the graph-origin audit and preserve the smallest perfect-matching instance whose assignments all miss the elliptic target.
