# ECDLP-IDEA-382 — Gallai–Edmonds source-matching decomposition

## Status and claim labels

- Class: `combinatorial`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_five_ary_relation_is_not_matching_and_compatibility_graph_is_source_incidence`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct matching decomposition or valid row is not an ECDLP break.

## Falsifiable hypothesis

Endpoint compatibility admits a compact ordinary graph whose Gallai–Edmonds `D/A/C` decomposition isolates factor-critical components and lifts a target-perfect matching to one exact five-deck relation source below the frozen gates.

## Mechanism-new operation

The screened operation is **construct the endpoint compatibility graph, compute a maximum matching and its Gallai–Edmonds partition, then replay factor-critical components to an occurrence-labelled relation tuple**. It is distinct only if the five-ary equality is represented without tuple gadgets or explicit compatible edges.

## Assumptions

1. Exact five-deck endpoint equality has a source-biconditional ordinary-graph matching representation of subgate size.
2. Graph vertices/edges are endpoint-constructible without enumerating compatible tuples.
3. The `D/A/C` partition and factor-critical replay preserve target labels, signed occurrences, all strata, and arbitrary restrictions.
4. A recovered maximum matching yields an independent relation row rather than post-generation packing.
5. Graph construction, matching, decomposition, replay, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_compatibility_graph | maximum_matching | Gallai_Edmonds_DAC_partition | factor_critical_occurrence_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; complete source and descent accounting remains mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; compact exact source resolution is missing.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation remains unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit compatibility edges are the no-promotion boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; tuple gadgets/materialized products remain controls.

## Closest primary literature

- Lovász, [On the structure of factor-critical graphs](https://doi.org/10.1007/BF01889914), develops the decomposition for a supplied graph.
- Cheriyan, [Randomized `O(M(|V|))` algorithms for problems in matching theory](https://doi.org/10.1137/S0097539793256223), computes matching structure after the graph is represented.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives a five-ary endpoint relation, not an ordinary matching graph.

No checked source supplies the required compact matching representation or point lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, graph/gadget semantics, edge constructor, matching/decomposition algorithm, restrictions, masks, and verifier.
2. Build target-independent graph state within `B^(9/4)` without explicit source edges or tuple gadgets.
3. For known-log targets, update target constraints, compute matching and `D/A/C`, decide restricted existence, replay one occurrence-labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charge duplicate/dependent matchings, solve factor logs, and verify them independently.
5. Reuse the unchanged graph construction and decomposition for fresh scalar-blind `Q+[t]P`, charging restrictions and rebuilds.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge graph construction, all matching/decomposition work, source replay, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion requires time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Gallai–Edmonds applies to ordinary matchings in an explicit graph. A five-ary elliptic sum is a hyperedge constraint; translating it into matching requires compatibility edges or tuple gadgets that materialize the source incidence. The `D/A/C` partition describes maximum-matchability, not the target-labelled relation or an exact point lift, and arbitrary restrictions can force rebuilding. This merges with IDEAs 137, 212, 257, 345, and 368 unless a new compact biconditional reduction is proved.

## Proof track

Construct a subgate ordinary graph from endpoints, prove matching-to-relation biconditional and labelled replay under every restriction, and meet complete exponents at most `0.45`.

## Disproof track

Show any biconditional reduction needs one edge/gadget per compatible source combination, or produce maximum matchings with identical `D/A/C` data but different target relation sources.

## Positive and negative controls

- Positive: supplied factor-critical graphs with planted labelled matchings must reproduce `D/A/C` and replay.
- Negative: genuine five-uniform constraints, equal decompositions with different target hyperedges, arbitrary restrictions, all strata, and blind targets.
- Baselines: IDEAs 137/212/257/345/368, explicit tuple gadgets, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a compact graph-reduction theorem, exact source replay, `1,000` independent rows, `100` blind descents, frozen setup/query caps, and `lambda,mu<=0.45`.
- Falsify on one explicit compatibility edge deck, one false matching/relation correspondence, one missed stratum, supergate rebuild, or either exponent at least `0.50`.
- Correct matching on a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-382/matching_reduction_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-382/dac_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-382/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-382/cost_analysis.md`

## Interpretation boundary

This rejects the screened matching representation, not Gallai–Edmonds theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a matching is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-382/matching_reduction_obligations.md` and count every edge/gadget needed for a source-biconditional five-ary-to-matching reduction.

