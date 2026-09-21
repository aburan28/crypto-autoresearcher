# ECDLP-IDEA-389 — Plünnecke magnification source graph

## Status and claim labels

- Class: `additive-combinatorial`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_magnification_bounds_are_aggregate_and_do_not_construct_exact_endpoint_sources`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; measured small doubling or a correct toy path is not an ECDLP break.

## Falsifiable hypothesis

A prospectively defined signed factor-deck subset has a commutative layered addition graph with subpolynomial Plünnecke magnification, and an endpoint-only minimal-magnification witness supports exact enumeration of enough independent five-factor relations and blind target decompositions below the frozen gates.

## Mechanism-new operation

The screened operation is **construct a layered sum graph, select a minimal-magnification source set by the Plünnecke/Petridis method, propagate disjoint or controlled paths through five layers, and invert a target endpoint to one occurrence-labelled path**. It is mechanism-new only if the low-magnification set and inverse paths are public and prospective rather than a post-hoc selector on known relations.

## Assumptions

1. A coefficient-only rule selects a nonnegligible factor-deck subset with uniformly small magnification through all signed five-factor layers and blind target shifts.
2. The layered graph is implicit: neighbors, path intersections, and source predecessors are computable without materializing pair-, triple-, or five-fold sumsets.
3. Plünnecke paths are exact elliptic group-law paths and retain occurrence labels, signs, multiplicity, and every Semaev stratum.
4. The same frozen selection/query procedure yields full-rank relations and blind descent, not only aggregate set-size inequalities.
5. Selection, graph construction, path output, density loss, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`prospective_small_doubling_deck | Plunnecke_layered_magnification_graph | minimal_magnification_subset | endpoint_path_inversion | occurrence_labelled_blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H673`; additive-energy enrichment is the nearest prospective structure hypothesis.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION`; training energy failed to transfer to held-out relation and rank gates.
3. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-043`; natural Abel–Jacobi completion labels matched random or relabelled controls.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact exact source-resolving circuit remains missing.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; aggregate phase structure did not construct exact nonlinear sources.

## Closest primary literature

- Petridis, [New proofs of Plünnecke-type estimates for product sets in groups](https://doi.org/10.1017/S096354831100037X), gives a minimal-growth argument for magnification estimates.
- Petridis, [New proofs of Plünnecke-type estimates for product sets in groups](https://arxiv.org/abs/1101.2532), provides the preprint form of the same combinatorial bounds.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relation equations but no prospective small-magnification source set or inverse path oracle.

No checked primary source turns Plünnecke magnification into exact occurrence-labelled inversion for elliptic factor decks; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, `B=N^(1/5)` signed factor decks, prospective subset rule, five-layer graph, magnification functional, path conventions, restrictions, masks, and verifier.
2. Construct the target-independent low-magnification subset and implicit path oracle within `B^(9/4+o(1))`, before observing relation or target outcomes and without materializing large sumsets.
3. For known-log targets, query the endpoint layer, recover one complete occurrence-labelled five-edge path, and verify its signed group sum and all stratum conditions.
4. Collect at least `B` independent verified rows, charging subset density loss, empty endpoints, path multiplicity, duplicate/dependent rows, and output; solve factor logs and verify them.
5. Reuse the unchanged subset and path oracle on fresh scalar-blind `Q+[t]P`, with every restriction frozen before outcomes and all target-specific work charged.
6. Recover a path, substitute verified factor logs, remove `t`, retain path ambiguity, and verify `[x]P=Q`.
7. Charge subset discovery, magnification certificates, graph/path queries, source recovery, output, relation density, rank, factor logs, blind descent, verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Plünnecke theory bounds cardinalities from a supplied small-product premise; it neither supplies that premise for sparse elliptic factor decks nor inverts an endpoint to labelled summands. Generic sparse decks behave like low-collision sets, while any subset selected after seeing relations is a forbidden post-hoc selector. Materializing graph edges restores the sumset/source boundary, and aggregate magnification can coexist with concentrated, dependent, or target-useless paths. This merges with IDEAs 027, 118, 340, 351, and 360 unless a prospective exact path-inversion theorem is proved.

## Proof track

Prove prospective low magnification on matched held-out curves, construct an implicit source-labelled path oracle, establish target-uniform endpoint inversion and full rank, and derive complete exponents at most `0.45`.

## Disproof track

Show random-like magnification on held-out decks, selection instability, path/source ambiguity, rank collapse, target nontransfer, or graph materialization above the setup/query caps.

## Positive and negative controls

- Positive: supplied arithmetic progressions and synthetic commutative graphs with known minimal-magnification subsets and labelled paths must recover endpoints exactly.
- Negative: matched random-scalar and random-x decks, shuffled labels, post-hoc selectors, equal-cardinality/different-path graphs, target shifts, arbitrary restrictions, all signed strata, and blind targets.
- Baselines: IDEAs 027/118/340/351/360, explicit sumset tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with prospectively frozen magnification `B^(o(1))`, exact implicit predecessor queries, `1,000` independent rows, `100` blind descents, state/query caps, held-out improvement over matched controls, and `lambda,mu<=0.45`.
- Falsify on one post-hoc selection dependency, held-out magnification matching random controls, one endpoint/source collision, rank below `0.9B`, a materialized supergate sumset, or either exponent at least `0.50`.
- Small doubling or correct toy paths alone are only controls.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-389/magnification_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-389/heldout_magnification_controls.json`
- `ideas/artifacts/ECDLP-IDEA-389/path_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-389/cost_analysis.md`

## Interpretation boundary

This rejects the screened source-graph use, not Plünnecke inequalities. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; additive-structure evidence is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-389/magnification_source_obligations.md` and specify the first endpoint-only predecessor query that avoids materializing a pair sumset.
