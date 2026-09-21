# ECDLP-IDEA-276 — Riemann-Kempf theta tangent-cone source split

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `representation_changing`
- State: `merged_rejected_theta_tangent_data_requires_supplied_divisor_and_special_stratum`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a tangent cone, recovered ruling, valid relation, divisor split, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform Jacobian or auxiliary-curve representation maps ECDLP relation fibers to singular points of a theta divisor whose Riemann-Kempf tangent cone canonically decomposes into rulings indexed by source divisor summands.  Recovering those rulings would return exact factor points and complete descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **encode a relation endpoint as a singular theta point, compute its tangent cone or osculating data, and invert the cone's rulings to the effective divisor/source factors**.  This is a geometry-changing split, not a dense resultant or post-hoc selector.  Riemann-Kempf geometry starts from a supplied line bundle or divisor class on a Jacobian; multiplicity and tangent-cone data describe special theta strata.  A generic endpoint does not canonically supply the effective divisor whose summands are sought, and constructing source-sensitive cone data can require that divisor.  Even on the special stratum, a tangent cone may recover a curve or linear spans rather than select a rational factor tuple.  It merges with Jacobian transfer and incidence/reconstruction negatives once divisor input and cone output are charged.

## Assumptions

1. Public `E/F_p,P,Q,N` and a relation endpoint canonically determine an auxiliary curve/Jacobian and singular theta point without a source divisor.
2. The tangent cone or finite osculating data separate all relevant effective divisor decompositions over `F_p`.
3. Cone rulings admit an exact, target-uniform inverse to signed factor points on `E` with sub-rho ambiguity.
4. Auxiliary-curve construction, theta equations, derivatives, cone/ruling enumeration, return, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | Jacobian_theta_singular_encoding | Riemann_Kempf_tangent_cone | divisor_ruling_split | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the auxiliary-geometry and local-algebra representation hypothesis.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, the incidence/reconstruction state negative.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the shared geometric invariant without source promotion control.
4. `inputs/ledger_inventory.json` — imported `P1478`, the dense source-state and output frontier.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the exact secant/incidence control.

## Closest primary literature

- Kempf, [On the geometry of a theorem of Riemann](https://annals.math.princeton.edu/1973/98-1/p06), describes theta-divisor singularities and the tangent-cone geometry underlying the proposed split.
- Kempf and Schreyer, [A Torelli theorem for osculating cones to the theta divisor](https://www.numdam.org/item/CM_1988__67_3_343_0/), shows how richer osculating-cone data can reconstruct curve geometry in a special setting.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field relation and factor-base baseline.

No checked source constructs the target-uniform singular-theta encoding or an exact sub-rho ruling-to-factor inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the ECDLP instance, auxiliary curve/Jacobian construction, theta equations, tangent/osculating order, factor base, masks, and verifier.
2. Map known-log relation endpoints to singular theta points without supplying their source divisors and compute exact cone data.
3. Enumerate every rational ruling/component, invert each to an effective divisor, and return exact signed factor points on `E`.
4. Verify relations, collect independent rows, solve and verify every factor log.
5. Apply the identical frozen theta encoding and cone computation to fresh masked targets `Q+[t]P`.
6. Retain all cone components and divisor branches, return a complete factorization or scalar residue, remove the mask, and verify equality.
7. Accept only exact `[x]P=Q`, charging auxiliary construction, theta coefficients, derivatives, cone output, ruling/divisor ambiguity, factor logs, descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one theta/cone/ruling/inverse attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, cone/divisor output be `N^o`, ruling ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every auxiliary-curve coefficient, theta term, derivative, tangent/osculating coefficient, cone component, ruling, divisor branch, failed return, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

The tangent cone is attached to a singular theta point determined by a line bundle/effective divisor class.  The ECDLP endpoint does not canonically provide the source divisor decomposition, and generic classes need not lie on the singular theta stratum required by Riemann-Kempf.  Supplying or constructing a source-sensitive singular point imports the factorization; using only its class leaves many effective divisors/rulings.  Cone reconstruction can recover ambient curve geometry while still failing to select the exact rational source tuple.

## Proof track

Construct a target-uniform singular-theta encoding for all source strata, prove compact cone data and an exact ruling-to-factor inverse, and certify complete exponents at most `0.45`.

## Disproof track

Show generic endpoints miss the singular stratum, prove cone construction requires the source divisor, exhibit multiple divisor branches with identical cone data, prove cone/ruling state at least `N^0.50`, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied special divisor on a small Jacobian whose Riemann-Kempf tangent cone and labelled summands are known.
- Negative controls: generic nonsingular theta points, linearly equivalent divisors with ambiguous rational representatives, permuted source summands, secant/incidence pencils, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an all-strata target-uniform singular-theta encoding, cone/ruling computation and return of exponent at most `0.45`, blind descent, and complete `lambda,mu<=0.45`.  Missing strata, source-divisor input, ambiguous rulings, cone/output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-276/riemann_kempf_source_split_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-276/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-276/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-276/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite theta computation would be toy and projections heuristic and model-bound.  A correct cone, recovered curve, divisor split, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-276/riemann_kempf_source_split_theorem.md` proving all-strata cone-to-factor return or the divisor-input/stratum/ambiguity obstruction.
