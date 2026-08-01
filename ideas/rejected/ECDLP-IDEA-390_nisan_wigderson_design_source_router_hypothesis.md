# ECDLP-IDEA-390 — Nisan–Wigderson design source router

## Status and claim labels

- Class: `combinatorial`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_low_overlap_routes_do_not_correlate_with_exact_relations_and_complete_coverage_restores_incidence_cost`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct design or isolated planted toy source is not an ECDLP break.

## Falsifiable hypothesis

An explicit Nisan–Wigderson low-intersection set design can route public endpoint features of five factor occurrences through a subquadratic family of buckets so that every exact relation has an isolating route, false candidates remain bounded, and blind targets admit exact source recovery below the frozen gates.

## Mechanism-new operation

The screened operation is **assign factor-feature coordinates to low-overlap design blocks, compute block-local endpoint sketches, intersect the resulting candidate routes, and decode the unique surviving route to five signed factor occurrences**. It is mechanism-new only if the design uses public algebraic features and deterministically isolates true sources without enumerating all candidates or using post-hoc relation labels.

## Assumptions

1. A target-independent explicit design of at most `B^(9/4+o(1))` total state covers every admissible source tuple while keeping block intersections `B^(o(1))`.
2. Public endpoint sketches are exact and sufficiently source-sensitive that a true five-factor tuple has an isolating route on every prospective curve/restriction.
3. False route intersections and decoder ambiguity fit the complete `B^(5/4+o(1))` query cap, including all signs and repeated factors.
4. The same frozen design yields full-rank relation rows and scalar-blind descent rather than only planted-source recovery.
5. Design construction, sketches, routes, decoder output, density, rank, factor logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`explicit_low_intersection_set_design | public_endpoint_feature_blocks | exact_source_isolating_route | bounded_candidate_intersection | blind_factor_decoder`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H680`; a recursive compact source locator is the closest unresolved circuit proposal.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless routing retains one distinguishable ancestry path per source.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE2-TRANSLATED-CIRCUIT-TRADEOFF`; compact predicates and exact source unranking retain the ordinary tradeoff.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; explicit compatibility routes recover the no-promotion source-edge surface.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1431-CANONICAL-ROOT-PRODUCT-NO-PROMOTION`; a canonical aggregate does not by itself isolate factor sources.

## Closest primary literature

- Nisan and Wigderson, [Hardness vs randomness](https://doi.org/10.1016/S0022-0000(05)80043-1), uses low-intersection combinatorial designs in pseudorandom-generator constructions from hardness assumptions.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), provides the exact endpoint predicate but no design-indexed source isolator.

No checked primary source proves that an NW design isolates elliptic factor-deck sources from public endpoint features; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, `B=N^(1/5)` signed factor occurrences, feature map, design universe and blocks, sketch and decoder rules, restrictions, masks, and independent verifier.
2. Build target-independent design sketches and routing state within `B^(9/4+o(1))`, before relation outcomes and without one stored route per candidate source tuple.
3. For known-log targets, evaluate target sketches, intersect compatible blocks, decode one occurrence-labelled five-factor tuple, and verify its signed group sum and stratum.
4. Collect at least `B` independent verified rows, charging uncovered sources, false intersections, ambiguity, duplicate/dependent rows, and output; solve factor logs and verify them.
5. Apply the unchanged design, sketches, and decoder to fresh scalar-blind `Q+[t]P`, with restrictions fixed before outcomes and all target-specific computations charged.
6. Decode a factor tuple, substitute verified factor logs, remove `t`, retain every ambiguity branch, and verify `[x]P=Q`.
7. Charge design construction, feature evaluation, sketch state, route intersections, decoding, output, relation density, rank, logs, descent, verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

NW designs guarantee small intersections among chosen coordinate sets; they do not make public coordinate sketches correlate with the rare nonlinear elliptic relation predicate. To guarantee isolation of an unknown true source under arbitrary endpoint collisions, the route family must distinguish essentially all source tuples or the decoder must solve the original membership problem inside a block. Increasing the number or resolution of routes recreates the explicit incidence surface, while sampled routes only change success probability and density. This merges with IDEAs 064, 148, 168, 337, and 361 unless an exact algebraic isolating lemma is supplied.

## Proof track

Prove an endpoint-feature isolating lemma for every valid source, construct and decode the design subgate, establish bounded false intersections and full rank on held-out curves, and derive complete exponents at most `0.45`.

## Disproof track

Construct equal-sketch source tuples with different validity, show that complete coverage needs source-sized routes, or measure false-route and density exponents at or above the explicit boundary.

## Positive and negative controls

- Positive: standard NW block systems and synthetic sparse predicates with planted feature-isolatable sources must satisfy coverage, overlap, and exact decoding.
- Negative: matched random blocks, shuffled feature labels, equal-sketch/different-source tuples, planted versus blind targets, arbitrary restrictions, repeated factors, all signed strata, and target shifts.
- Baselines: IDEAs 064/148/168/337/361, disjunct matrices, explicit source tables, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with deterministic coverage and exact decoding, route state at most `B^(9/4+o(1))`, complete query at most `B^(5/4+o(1))`, `1,000` independent rows, `100` blind descents, and `lambda,mu<=0.45`.
- Falsify on one equal-sketch validity collision, uncovered valid source, source-sized route table, restriction-specific redesign, blind success matching random routing, or either exponent at least `0.50`.
- A correct design, low pairwise overlap, or planted-source isolation alone is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-390/design_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-390/route_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-390/decoder_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-390/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic source router, not NW designs or pseudorandomness theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; routing correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-390/design_source_obligations.md` and construct the smallest equal-sketch pair that any exact isolating route must distinguish.
