# ECDLP-IDEA-304 — Jeffrey–Kirwan chamber-residue source extractor

## Status and claim labels

- Class: `geometric_representation`
- Risk band: `representation-changing`
- Top lane: `representation_changing`
- State: `merged_rejected_chamber_data_and_fixed_cones_encode_sources`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run `review_required` preflight draft
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct residue identity, fixed-point sum, valid relation, or toy extraction is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-computable torus arrangement and Jeffrey–Kirwan chamber residue isolates one exact factor-base source cone without enumerating source tuples, yielding reusable relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode the summation-polynomial fiber as a rational torus arrangement, choose a public endpoint chamber, apply the Jeffrey–Kirwan residue, and invert the surviving fixed-cone contribution to exact signed factor points**. This is not a dense resultant or generic coefficient extraction: the proposed routing primitive is chamber-dependent localization. The arrangement and cone weights, however, are defined by source incidences; an endpoint chamber that selects one source is post-hoc selector advice. It therefore merges with IDEAs 089, 094, 201, 239, and 248.

## Assumptions

1. A compact arrangement and rational form are computable from public curve and endpoint data without listing source tuples or source hyperplanes.
2. One public chamber selects a noncancelling source contribution uniformly across every signed and nonreduced stratum.
3. The residue contribution has a canonical biconditional inverse to exact factor points rather than only a multiplicity or aggregate weight.
4. Arrangement construction, chamber search, cone enumeration, residues, output, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`endpoint_torus_arrangement | Jeffrey_Kirwan_chamber_residue | fixed_cone_localization | exact_factor_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the source-complete coefficient-extraction obstruction.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate-norm control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit-incidence boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the compact one-transition primitive whose quadratic composition becomes dense.

## Closest primary literature

- Jeffrey and Kirwan, [Localization for nonabelian group actions](https://doi.org/10.1016/0040-9383(94)00028-J), derives chamber-dependent residue formulas from supplied group actions, weights, and fixed-point data.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives endpoint equations but no compact source arrangement or point-valued chamber inverse.

No checked source constructs a source-blind arrangement, a target-uniform source-selecting chamber, exact point unranking, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, arrangement construction, rational form, chamber rule, residue normalization, all-strata source inverse, and independent verifier.
2. Build the arrangement on known-log endpoints without enumerating hidden tuples or importing source-labelled weights.
3. Evaluate the chamber residue, invert every nonzero contribution to exact signed factor points, and verify each relation independently.
4. Collect independent rows, solve and verify all factor logs.
5. Reuse the identical construction and chamber rule on fresh masked targets `Q+[t]P`, without target-trained selectors.
6. Substitute factor logs, remove masks, retain ambiguity, and return candidates.
7. Accept only exact `[x]P=Q`, charging arrangement, cones, residues, output, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation/residue densities `N^delta,N^delta_t`, one arrangement/residue/inverse `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes construction, chamber evaluation, cone localization, source inversion, and verification; `o` includes every returned cone or tuple. Rho has time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Jeffrey–Kirwan residues localize a supplied weight arrangement and sum cone contributions; they do not discover the arrangement's hidden source incidences or label one factor tuple. Listing fixed cones materializes the source deck, while choosing a chamber after seeing the desired cone is exactly a forbidden post-hoc selector.

## Proof track

Prove a public compact endpoint-to-arrangement identity, a target-uniform chamber theorem, noncancelling exact all-strata point inverse, sufficient independent relation density, reusable factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Reduce arrangement or chamber construction to explicit source enumeration, exhibit equal public arrangements/residues with different point labellings, or prove cone/state/output exponent at least `0.50`.

## Positive and negative controls

- Positive: a frozen toric toy quotient with supplied weights and one predeclared chamber must reproduce its independently enumerated fixed-cone residue.
- Negative: permuted source labels and equal-residue arrangements with different exact cones must not be treated as point recovery.
- Baselines: dense resultants, ordinary multivariate residues, IDEAs 089/094/201/239/248, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata source inversion, 1,000 verified rows and 100 blind descents per large size, and both full exponents at most `0.45`.
- Falsify if source-labelled weights, cone enumeration, or a post-hoc chamber is required, or if construction/cones/output reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-304/chamber_residue_identity.md`
- `ideas/artifacts/ECDLP-IDEA-304/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-304/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-304/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of the stated chamber-residue router, not a universal impossibility theorem for equivariant localization. A correct toy localization identity or supplied-arrangement speedup is not scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-304/chamber_residue_identity.md` giving either a source-blind endpoint-to-arrangement-and-chamber formula or an explicit reduction showing that its weights and chamber encode the source list.
