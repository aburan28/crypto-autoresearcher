# ECDLP-IDEA-278 — Gelfand-Levitan-Marchenko source-potential decoder

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `representation_changing`
- State: `merged_rejected_scattering_data_requires_source_deck_and_lacks_finite_field_inverse`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a solved Marchenko equation, recovered potential, valid relation, decoded site, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A public ECDLP relation endpoint determines compact reflection data together with bound-state poles and norming constants for an auxiliary scattering problem.  Solving the Gelfand-Levitan-Marchenko inverse-scattering equation would recover a finite-support potential whose labelled sites encode the exact signed factor points, yielding rows and blind fresh-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile an endpoint into reflection, bound-state, and norming data, solve the Gelfand-Levitan-Marchenko inverse equation, and decode the reconstructed finite-support potential sites to exact source factors**.  This changes an algebraic source fiber into inverse-scattering data and is distinct from IDEA-279's scalar moment/Jacobi quadrature atomization, a dense resultant, or a solver swap.  Classical continuous and discrete inverse-scattering theorems reconstruct a potential after complete admissible scattering data are supplied; they do not derive source-faithful data from an elliptic-curve endpoint.  If each potential site identifies a factor point, the reflection coefficient and norming data must preserve the source deck or an equivalent labelled generating function.  A compressed spectrum has isoscattering or phase ambiguities, and the analytic positivity, reality, decay, and normalization used by Marchenko theory have no canonical finite-field analogue.  Semantic collisions are IDEA-186's supplied inverse-spectral divisor, IDEA-267's supplied transfer samples, IDEA-247's supplied spectral cover/eigenline, IDEA-273's source-sized spectral module, and IDEA-224's noninjective scattering representation.  The proposal therefore merges with those endpoint-to-source, dense state-composition, and supplied-spectral-data negatives after all scattering data and return costs are charged.

## Assumptions

1. Public source equations and each endpoint canonically compile to finite-field or exactly reducible reflection data, bound states, and norming constants without source-tuple advice.
2. An all-strata algebraic Gelfand-Levitan-Marchenko equation exists and has a unique finite-support solution computable below rho.
3. The recovered potential sites and amplitudes canonically decode to exact signed elliptic-curve factor tuples with sub-rho output and ambiguity.
4. Scattering compilation, spectral samples, poles, norming data, kernel construction, equation solving, potential output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`endpoint_relation | compact_scattering_data | GLM_integral_equation | discrete_poles_norming_constants | exact_factor_return | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, the materialized source-state compression negative.
3. `inputs/ledger_inventory.json` — imported `P1478`, the sparse one-step representation whose composed source state becomes dense.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the exact full-rank transformed data without a compact source inverse.
5. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the public source-fiber generator and transposed-return boundary.

## Closest primary literature

- Deift and Trubowitz, [Inverse scattering on the line](https://doi.org/10.1002/cpa.3160320202), proves inverse-scattering reconstruction for one-dimensional Schrödinger operators from suitably complete scattering data.
- Case and Kac, [A discrete version of the inverse scattering problem](https://doi.org/10.1063/1.1666364), develops the discrete inverse-scattering analogue closest to a finite-support source potential.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations whose factor tuples the reconstructed potential would have to encode.

No checked source derives admissible source-faithful scattering data from a generic ECDLP endpoint, supplies a canonical finite-field Marchenko inverse, or completes sub-rho factor return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, source equations, auxiliary scattering model, reflection and norming normalization, Marchenko kernel convention, potential-to-factor decoder, factor base, masks, and verifier.
2. Derive complete reflection coefficients, bound-state data, and norming constants for known-log relation endpoints without enumerating or labelling their source tuples.
3. Build and solve every required Gelfand-Levitan-Marchenko equation, recover all finite-support potentials, and map every accepted labelled site to exact signed factor points.
4. Verify the resulting relations, collect independent rows, solve every factor log, and verify all recovered logs.
5. Apply the identical frozen scattering compiler, inverse equation, and decoder to fresh masked targets `Q+[t]P` without target-specific tuning or source advice.
6. Retain every admissible potential branch, return a complete factor decomposition or scalar residue, remove the mask, and verify the reconstructed endpoint.
7. Accept only exact `[x]P=Q`, charging scattering-data generation and storage, poles and norming constants, kernel state, inverse solves, potential branches, rows, factor logs, fresh-target descent, verification, and live memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one scatter/GLM/potential-return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, scattering/potential output be `N^o`, isoscattering or inverse ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every reflection sample or coefficient, bound-state pole, norming constant, field extension, Marchenko-kernel entry, linear/integral-equation operation, potential site and amplitude, inverse branch, failed decode, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Inverse scattering is injective only after a complete, correctly normalized scattering data set is supplied.  A public elliptic-curve endpoint does not determine the factor-labelled reflection coefficient, bound states, and norming constants; constructing data rich enough to recover every source site is an encoding of the missing source fiber and can require deck-scale samples or coefficients.  Omitting norming or phase data creates isoscattering potentials, while retaining them restores the source-sized state.  Moreover the positivity, conjugation, decay, ordering, and analytic boundary values that support continuous or discrete Marchenko uniqueness have no canonical finite-field specialization.  Correctly solving an inverse equation therefore reconstructs supplied source-sensitive data but does not create the missing endpoint-to-source map.

## Proof track

Construct endpoint-only source-faithful scattering data and a canonical finite-field GLM/Marchenko inverse, prove exact potential-site-to-factor decoding on every stratum, and certify both complete exponents at most `0.45`.

## Disproof track

Exhibit distinct source fibers or finite potentials with identical frozen scattering data, prove reflection/norming/potential state at least `N^0.50`, show the compiler enumerates sources, prove no characteristic-safe canonical inverse, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small real or discrete finite-support potential with complete reflection, bound-state, and norming data and an independently known inverse.
- Negative controls: reflection data with omitted norming constants, phase-scrambled or isoscattering inputs, nondecaying and nonpositive finite-field analogues, random endpoint spectra, source-labelled reflection tables, scalar moment/Jacobi atomization, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires endpoint-only admissible scattering data and a finite-field inverse of exponent at most `0.45`, exact all-strata potential-site and factor return, full row rank and verified factor logs, blind fresh-target descent, and complete `lambda,mu<=0.45`.  Isoscattering collisions, source-labelled norming data, scattering/potential/output/state at least `N^0.50`, absent finite-field uniqueness, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-278/marchenko_source_potential_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-278/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-278/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-278/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite inverse-scattering computation would be toy and projections heuristic and model-bound.  A correct Marchenko solve, reconstructed supplied potential, valid relation, or recovered toy site does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-278/marchenko_source_potential_theorem.md` proving compact endpoint-only scattering compilation and finite-field factor return or the source-data/isoscattering/finite-field-uniqueness obstruction.
