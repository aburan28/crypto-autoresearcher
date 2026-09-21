# ECDLP-IDEA-359 — Kakeya-Nikodym directional source focusing

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_direction_family_requires_source_incidence_materialization`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Kakeya bound or recovered incidence is not an ECDLP break.

## Falsifiable hypothesis

Pair wedges derived from factor-base points define a finite-field direction family whose target-conditioned Kakeya-Nikodym multiplicity polynomial decides exact restricted Abel-Jacobi incidence nonemptiness for source bisection.

## Mechanism-new operation

The screened operation is **map pair wedges to projective directions and use a multiplicity-polynomial Kakeya transform as an exact incidence-existence oracle under dyadic source restrictions**. It is new only if the line family and restricted decision are endpoint-derived rather than supplied by enumerated pairs.

Minimum-interface correction: a canonical point-pair inverse and all incidences are unnecessary. A target-labelled, subset-stable exact incidence-existence bit under arbitrary dyadic deck restrictions, with `O(log B)` charged line queries, suffices to recover one signed tuple.

## Assumptions

1. Pair directions and target-bearing line predicates are computable without listing all factor-base pairs.
2. Multiplicity constraints focus genuine relations rather than only bound the size of their union.
3. Restricted direction-line state preserves exact incidence nonemptiness, so bisection recovers one exact point pair.
4. All exceptional directions, tangencies, signs, and target strata are covered.
5. Direction construction, polynomial interpolation, line tests, inverses, outputs, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`abel_jacobi_pair_wedges | finite_field_direction_line_family | kakeya_nikodym_multiplicity_polynomial | subset_stable_exact_incidence_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1429-EXPLICIT-ROOT-ROW-NO-PROMOTION`; exact root-row hyperplanes remain cubic when explicitly materialized.
2. `inputs/ledger_inventory.json` — imported `ECFG-P1429-EXACT-FACTOR-ROOT-HYPERPLANE-CONTROL`; exact supplied incidences are only a correctness control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION`; directional aggregate structure did not transfer to exact held-out relation reporting.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; algebraic focusing still lacks an endpoint-derived exact source section.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; labelled source edges dominate output-sensitive routes.

## Closest primary literature

- Dvir, [On the size of Kakeya sets in finite fields](https://doi.org/10.1090/S0894-0347-08-00607-3), proves a polynomial-method size bound; it does not construct labelled incidences from an implicit direction family.
- Ellenberg, Oberlin, and Tao, [The Kakeya set and maximal conjectures for algebraic varieties over finite fields](https://doi.org/10.1112/S0025579309000400), studies finite-field Kakeya-Nikodym estimates rather than source inversion for Abel-Jacobi relations.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the relation predicate but no implicit directional oracle.

No checked source supplies the endpoint-only direction family plus source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, pair-wedge chart, direction/line conventions, multiplicities, inverse, masks, and verifier.
2. Construct target-independent direction state or a bounded target update without enumerating point pairs.
3. Query restricted exact line incidence for known-log targets, bisect to one signed source tuple, and replay its group relation.
4. Collect `B` independent rows, solve factor logs, and verify them.
5. Repeat the unchanged direction-line procedure on fresh masked targets.
6. Substitute factor logs, remove masks, retain all ambiguity, and verify `[x]P=Q`.
7. Charge pair/direction construction, line-polynomial state, incidence reporting, source inverses, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(beta)`, `beta=1/5`, and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `a` includes the direction-line family and multiplicity polynomial, `q` includes line queries plus target/restriction updates, `o` is exact point-pair output, and `u` is residual ambiguity. Require `0<=r<=o`, setup/state `<=B^(9/4)`, fresh query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time are exponent `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

Kakeya-Nikodym estimates consume or quantify a line family; they do not generate an endpoint-derived family or decide exact incidence existence under arbitrary source restrictions. Explicit factor-pair directions cost `Theta(B^2)` state, and the audited restricted pair-of-pair/target compatibility tests restore `B^3` to `B^4` work. Direction collisions alone are not fatal because bounded correction is allowed, but no subset-stable correction below the gates is constructed; point-label inversion is only a stronger control.

## Proof track

Construct an endpoint-only implicit direction oracle, prove subset-stable exact incidence decisions plus bisection, and derive all-strata costs below the gates.

## Disproof track

Prove pair enumeration is necessary, exhibit a restricted direction family with differing exact incidence answers and no sub-gate correction, or show exact restricted decisions cost at least the explicit source-incidence boundary.

## Positive and negative controls

- Positive: a supplied low-degree Kakeya line family with labelled point generators.
- Negative: independently relabelled pair decks with identical direction multisets and different valid source tuples.
- Baselines: IDEAs 112/160/234/326/348, P1429, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an endpoint-only line-family constructor, zero source errors, 1,000 rows, 100 blind descents, and complete time/memory exponents at most `0.45`.
- Falsify on required pair materialization, a same-direction/different-source family whose every public correction or point section exceeds the gates, incomplete strata, or complete exponent at least `0.50`.
- A Kakeya cardinality bound, polynomial vanishing certificate, or supplied-line toy is insufficient.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-359/direction_line_biconditional.md`
- `ideas/artifacts/ECDLP-IDEA-359/kakeya_source_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-359/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-359/cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only source-focusing adaptation, not finite-field Kakeya theory. All prospective checks are toy, heuristic, model-bound, and novelty-unverified. An incidence bound is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-359/direction_line_biconditional.md` as a subset-stable exact restricted-incidence specification, with source recovery only through charged dyadic bisection.
