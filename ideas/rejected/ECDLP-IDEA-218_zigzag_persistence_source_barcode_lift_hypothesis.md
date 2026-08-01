# ECDLP-IDEA-218 — Zigzag-persistence source-barcode lift

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_barcode_forgets_generators_and_source_correspondence`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired zero-run `review_required` theorem preflight
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a barcode, persistent class, or correct source on a fixture is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-indexed zigzag of sparse relation complexes has a barcode whose bounded interval summands are canonically labelled by exact signed factor-base sources. A target-uniform lift from interval generators to point tuples would yield independent relation rows and blind target descent with time and memory below rho and BSGS.

## Mechanism-new operation

The claimed operation is **zigzag-module interval decomposition followed by a canonical generator-to-point lift**, not a different homology solver. It merges/rejects because a barcode classifies the supplied type-A representation only up to isomorphism: interval endpoints do not retain a preferred cycle representative, chain basis, or exact elliptic source tuple. Building the source-faithful complexes or storing the change-of-basis maps restores the missing relation deck.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, and target-independent filtration rules are frozen.
2. Each boundary map is constructible from the endpoint without enumerating signed source tuples or a dense Semaev fiber.
3. Barcode intervals have canonical, all-strata lifts to exact point identities, signs, repeats, and multiplicities.
4. Complex construction, reductions, basis changes, output, rank, factor logs, masked descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_relation_zigzag | interval_module_barcode | canonical_persistent_generator | exact_signed_point_lift | factor_logs | blind_target_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact-source predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the source-generation and transposed-join boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry floor.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit terminal-source edge boundary.

## Closest primary literature

- Carlsson and de Silva, [Zigzag persistence](https://arxiv.org/abs/0812.0197), decomposes a supplied zigzag module into interval summands; it does not canonically recover input generators.
- Zomorodian and Carlsson, [Computing persistent homology](https://doi.org/10.1007/s00454-004-1146-y), gives the graded-module/barcode algorithmic foundation for supplied filtered complexes.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the elliptic endpoint-relation baseline but no barcode-to-source lift.

No checked source supplies an endpoint-only complex and exact point-labelled interval inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the factor base, relation-complex grammar, zigzag order, masks, lift, and verifier.
2. Construct sparse endpoint complexes without listing source tuples; compute the interval decomposition and every retained basis map.
3. Lift accepted intervals to all exact signed factor points and verify every resulting elliptic relation.
4. Collect at least `B+sigma` independent rows, solve the factor-base logarithms, and independently verify them.
5. Apply the identical construction to fresh `Q+[t]P`, lift every target interval, substitute factor logs, and subtract `t`.
6. Preserve ambiguity and accept only candidates satisfying `[x]P=Q`, charging construction, output, rank, descent, verification, and peak memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let complex setup cost `N^a,N^a_m`, reciprocal base/target densities `N^delta,N^delta_t`, barcode plus exact lift cost `N^q,N^q_m`, independent rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every boundary nonzero, basis map, interval generator, and point lift contributes to setup, query, output, or memory. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Interval decomposition forgets the basis that created a homology class. Distinct source-labelled complexes and cycles can have the same barcode, and representative cycles differ by boundaries. Retaining a canonical source-bearing basis requires the reduction matrix or a point-labelled chain cell for each occupied source, recreating the `B^2/B^3/B^5` relation traffic that persistence was supposed to compress.

## Proof track

Construct a target-independent sparse complex and prove that every interval has a unique, functorial, all-strata lift to exact signed factor points with complete `lambda,mu<=0.45`.

## Disproof track

Exhibit two exact-source fibers with isomorphic zigzag modules but different point tuples, prove basis-state growth at least square-root scale, or show that complex construction already enumerates source edges.

## Positive and negative controls

- Positive control: a planted labelled zigzag in which interval generators and point labels are supplied and independently replayed.
- Negative controls: basis-scrambled isomorphic zigzags, source-label deletion, ordinary homology ranks, IDEA-073 discrete Morse, IDEA-174 HN filtrations, explicit source complexes, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires two generic factor-base families, 100% interval-to-source recall, zero false sources on every sign/repeat stratum, no source-labelled boundary matrix, and `lambda,mu<=0.45`. One barcode collision, retained source deck, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-218/zigzag_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-218/barcode_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-218/independent_barcode_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-218/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected representation analysis. Finite checks would be toy and projections heuristic and model-bound. A barcode, homology class, exact fixture lift, or valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-218/zigzag_source_lift_theorem.md` proving a functorial interval-generator-to-point lift for the generic signed five-source fiber or recording an explicit equal-barcode/different-source collision.
