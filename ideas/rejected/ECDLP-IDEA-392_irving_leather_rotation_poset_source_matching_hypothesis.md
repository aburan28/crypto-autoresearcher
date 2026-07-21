# ECDLP-IDEA-392 — Irving–Leather rotation-poset source matching

## Status and claim labels

- Class: `combinatorial_matching`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_rotation_poset_requires_explicit_preference_incidence_and_does_not_create_elliptic_sources`
- Cohort: `20260718-t`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct toy stable matching or rotation enumeration is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-constructible stable-marriage instance has a compact Irving–Leather rotation poset whose closed subsets are in source-preserving bijection with the five signed factor-deck tuples of a target, so one exact tuple can be recovered under restrictions and used in a complete blind descent below the frozen P1553 gates.

## Mechanism-new operation

The screened operation is **compile endpoint equations into preference lists, expose rotations of stable matchings, order them by precedence, select a closed rotation set, and decode the resulting matching to occurrence-labelled factor points**. This is more than a generic matching or path backend only if preferences and rotations are constructed without first enumerating the source compatibility relation.

## Assumptions

1. Every signed P1553 stratum admits endpoint-only, target-uniform preference lists of subgate size.
2. Stable matchings correspond biconditionally to exact five-deck relations, with no spurious or missing tuples.
3. The rotation poset and one closed set can be constructed without materializing source-labelled preference edges.
4. Restrictions commute with the matching/rotation construction and preserve a canonical occurrence-labelled inverse.
5. Preference construction, rotation discovery, closure selection, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_preference_compiler | stable_matching_instance | Irving_Leather_rotation_poset | closed_rotation_set | exact_occurrence_source_decode | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`; complete five-source query, rank, and descent accounting remains mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; supplied preference edges are source incidence in another form.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; a lossless precedence DAG cannot hide source-labelled ancestry.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact exact source-resolving combinatorial object remains missing.
5. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source generation and batching remain unconstructed.

## Closest primary literature

- Irving and Leather, [The Complexity of Counting Stable Marriages](https://doi.org/10.1137/0215048), develops the rotation-poset representation for a supplied stable-marriage instance; it does not construct preference lists from elliptic endpoints.
- Gusfield, [Three Fast Algorithms for Four Problems in Stable Marriage](https://doi.org/10.1137/0216013), computes stable-marriage structure after preferences are explicit.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relation equations but no preference compiler or stable-matching inverse.

No checked source supplies the proposed endpoint-only preferences or exact matching-to-point lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, preference compiler, tie policy, rotation conventions, restrictions, masks, and independent tuple verifier.
2. Build target-independent preference/rotation state within `B^(9/4+o(1))`, without one edge, rank entry, or rotation record per source tuple.
3. For known-log targets, construct the restricted instance, find a stable matching through a closed rotation set, decode one occurrence-labelled five-point tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charging empty or spurious instances and dependent rows; solve factor logs and verify them.
5. Apply the unchanged compiler and rotation decoder to fresh scalar-blind `Q+[t]P`, charging restrictions, ambiguity, output, and rebuilds.
6. Substitute factor logs, remove `t`, retain every ambiguity branch, and verify `[x]P=Q`.
7. Charge preference construction, rotation-poset state, closure selection, source decoding, output, rank, factor logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Rotation posets compress the family of stable matchings only after complete preference lists are supplied. Encoding whether two partial elliptic states are compatible creates the exact source edges already charged by the ledger, while rotation construction scans those lists. Stable matchings also optimize mutual preference consistency rather than enforce a five-ary elliptic sum, so a faithful reduction needs tuple gadgets or post-hoc verification. This merges with IDEAs 157, 171, 257, 343, and 382 unless endpoint data alone yields a compact source-biconditional preference oracle.

## Proof track

Construct subgate endpoint-only preferences for every stratum, prove stable matching iff exact relation, prove a restriction-stable matching-to-occurrence inverse, and derive complete `lambda,mu<=0.45` bounds.

## Disproof track

Exhibit one required preference comparison that evaluates source incidence, two source fibres with identical compact rotation data but different tuples, or a family whose explicit lists/rotations exceed the frozen caps.

## Positive and negative controls

- Positive: supplied stable-marriage instances with known rotations and planted labelled matchings must reproduce the independently computed rotation poset and labels.
- Negative: permuted labels, equal rotation posets with different preferences, empty/spurious stable matches, arbitrary restrictions, all signed strata, and blind targets.
- Baselines: IDEAs 157/171/257/343/382, explicit compatibility graphs, post-hoc selectors, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only preference construction, an exact source biconditional, `1,000` independent rows, `100` blind descents, frozen state/query caps, and `lambda,mu<=0.45`.
- Falsify on one supplied source edge, one same-rotation/different-source collision, one missing/spurious tuple, a restriction rebuild above cap, or either exponent at least `0.50`.
- A correct toy rotation poset or matching is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-392/preference_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-392/rotation_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-392/matching_to_source_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-392/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic rotation-poset construction, not stable-matching theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; combinatorial correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-392/preference_source_obligations.md` and classify every preference comparison in the smallest proposed instance as endpoint-derived or source-incidence advice.
