# ECDLP-IDEA-296 — Ronkin-amoeba spine source section

## Status and claim labels

- Class: `representation_changing`
- Risk band: `representation_changing`
- Top lane: `representation_changing`
- State: `merged_rejected_amoeba_spine_lacks_canonical_root_labels_and_finite_field_section`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct amoeba, Ronkin potential, spine cell, valid relation, or toy branch is not an ECDLP break.

## Falsifiable hypothesis

A canonical characteristic-zero Laurent lift of each endpoint source polynomial has a Ronkin potential whose amoeba-spine chamber and order-map data select one exact signed factor tuple, yielding source rows and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift endpoint equations to Laurent polynomials, compute the Ronkin convex potential and amoeba spine, choose an order-map chamber, and reduce its lifted branch to exact finite-field factors**. Ronkin/amoeba data organize a supplied complex polynomial through its Log image, coefficients, and Newton-polytope cells. The Log image and spine do not by themselves provide pointwise root arguments, residue labels, signs, permutations, tuple pairing, or a canonical labelling of roots. Adding coamoeba/phase or branch data until all sources separate restores a source dictionary, while no canonical archimedean lift exists. The operation merges with IDEAs 029, 059, 076, 103, 248, and 289 after lift height and branch output are charged.

## Assumptions

1. A target-uniform bounded-height Laurent lift preserves every finite-field source branch and no spurious branch.
2. A bounded Ronkin/spine/coamoeba state separates all signed, repeated, singular, and infinity strata.
3. Chamber data have a canonical exact reduction to factor points without post-hoc branch selection.
4. Lift height, precision, amoeba sampling, spine construction, phase data, branches, rows, factor logs, descent, and memory are charged.

## Semantic fingerprint

`finite_field_endpoint_polynomial | characteristic_zero_Laurent_lift | Ronkin_convex_potential | amoeba_spine_order_chamber | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full transformed-state/no-inverse boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the exact product that materializes sources.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate norm without source return.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the exact lifted-pencil control.

## Closest primary literature

- Passare and Rullgård, [Amoebas, Monge–Ampère measures, and triangulations of the Newton polytope](https://doi.org/10.1215/S0012-7094-04-12134-7), derives convex/spine information for a supplied complex Laurent polynomial.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source gives a canonical source-faithful lift, a pointwise root labelling compatible with finite-field reduction, or an exact factor inverse from an amoeba chamber; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, integral lift, Laurent chart, Ronkin/spine convention, chamber inverse, masks, and verifier.
2. Lift known-log endpoint equations without source tuples, target-selected heights, or branch advice.
3. Compute Ronkin/spine and any preregistered phase data, then return every accepted chamber as exact signed finite-field factors.
4. Verify rows, collect independent rank, solve and verify factor logs.
5. Apply the identical lift and chamber rule to fresh masked targets `Q+[t]P`.
6. Preserve all lift, chamber, phase, and reduction ambiguity; substitute logs and remove masks.
7. Accept only exact `[x]P=Q`, charging coefficients, heights, precision, cells, phases, branches, outputs, rows, logs, descent, and memory.

## Full rho/BSGS cost model

Let setup be `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one lift/Ronkin/chamber attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, lift/phase ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. All lifted coefficients, precision bits, sampled cells, coamoeba phases, branches, reductions, outputs, and bytes are charged.

## Likely fatal obstruction

The Ronkin function and amoeba spine are coefficient-dependent convex data of a chosen complex lift. Their Log/spine summary lacks a canonical pointwise root argument and label needed for finite-field factor return. Restoring a point-faithful reduction map requires additional phase/branch data or a source-labelled lift. Different integral lifts can have different amoebas while reducing to the same endpoint, so no canonical finite-field section is supplied.

## Proof track

Construct a bounded canonical lift, prove all-source chamber injectivity and exact reduction, and certify complete exponents at most `0.45`.

## Disproof track

Exhibit lift dependence or source collisions, prove phase/chamber state or output at least `N^0.50`, show reduction needs branch advice, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small Laurent polynomial with known amoeba, spine, and independently labelled roots.
- Negative controls: root relabellings or phase configurations with the same Log/spine summary, alternate integral lifts of one reduction, source-labelled coamoebas, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires canonical bounded lift, all-strata exact chamber-to-factor return, verified logs, blind descent, and `lambda,mu<=0.45`. Lift dependence, phase collisions, state/output at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-296/ronkin_source_section_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-296/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-296/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-296/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged/scoped-negative representation-changing proposal is toy-only if instantiated; extrapolations are heuristic and model-bound. A correct amoeba or recovered toy chamber is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-296/ronkin_source_section_theorem.md` proving a canonical finite-field-faithful lift and exact chamber inverse or the phase/lift/source-state obstruction.
