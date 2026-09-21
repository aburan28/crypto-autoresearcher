# ECDLP-IDEA-300 — Elliptic-spectrum theorem-of-cube source factorization

## Status and claim labels

- Class: `cohomological_representation`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `merged_rejected_cubical_elliptic_orientation_records_curve_data_not_source_decomposition`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cubical orientation, power-operation identity, valid relation, or toy factor is not an ECDLP break.

## Falsifiable hypothesis

A cubically oriented elliptic spectrum turns endpoint addition relations into power-operation or Hecke-operation values whose primitive factors canonically return the exact signed elliptic source tuple below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile endpoint relations into an elliptic cohomology theory with theorem-of-cube orientation, apply separately cited power/Hecke operations, factor the output into primitives, and invert them to exact source points**. Ando–Hopkins–Strickland construct coherent cubical line-bundle/formal-group orientations for supplied elliptic spectra; they are not cited as the source of the power/Hecke operations. Ando treats power operations through isogenies, and Baker constructs Hecke operations in a specified elliptic-cohomology theory. These data and operations act on supplied curve/cohomology objects, not a labelled decomposition of one point. Faithful `N`-level structure, a point-indexed spectrum, or inverse operation stores the missing orientation/source deck. This merges with IDEAs 015, 031, 112, 161, 251, 270, and 271 after level and state costs are charged.

## Assumptions

1. A generic prime-field endpoint canonically maps into one finite, computable elliptic spectrum without source advice.
2. Cubical power/Hecke operations separate all signed factor tuples and exceptional strata.
3. Primitive factors have a canonical exact point inverse with sub-rho ambiguity and output.
4. Spectrum construction, level structure, coefficients, power operations, factorization, output, rows, logs, descent, and memory are charged.

## Semantic fingerprint

`elliptic_spectrum_cubical_orientation | theorem_of_cube | power_and_Hecke_operations | primitive_source_factorization | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the target-local exact-return requirement.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the scalar orientation/source-return boundary.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the hidden representation-orientation negative.
5. `inputs/ledger_inventory.json` — imported `P1479`, the complete cost and descent frontier.

## Closest primary literature

- Ando, Hopkins, and Strickland, [Elliptic spectra, the Witten genus and the theorem of the cube](https://doi.org/10.1007/s002220100175), constructs the cubical elliptic orientation for supplied spectra.
- Ando, [Power operations in elliptic cohomology and representations of loop groups](https://doi.org/10.1090/S0002-9947-00-02412-0), describes power operations in terms of isogenies of the supplied elliptic curve.
- Baker, [Hecke operators as operations in elliptic cohomology](https://doi.org/10.1016/0022-4049(90)90052-J), constructs stable Hecke operations in a specified elliptic-cohomology theory.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source compiles a generic endpoint into a point-faithful spectrum or inverts cubical/power-operation data to exact factors; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, elliptic spectrum, cubical orientation, operation family, primitive inverse, masks, and verifier.
2. Compile known-log endpoints into spectrum classes without source labels or target-dependent level choices.
3. Evaluate power/Hecke operations, factor every accepted output, and return exact signed factor points.
4. Verify rows, collect independent rank, solve and verify factor logs.
5. Apply the identical spectrum and operation pipeline to fresh masked targets `Q+[t]P`.
6. Preserve level, basis, operation, and factor ambiguity; substitute logs and remove masks.
7. Accept only exact `[x]P=Q`, charging spectrum/level state, coefficients, operations, factors, outputs, rows, logs, descent, and memory.

## Full rho/BSGS cost model

Let setup be `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one spectrum/operation/inverse attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, orientation ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. Every coefficient, level point, spectrum class, operation term, primitive factor, output branch, and live byte is charged.

## Likely fatal obstruction

The theorem of the cube supplies coherent functorial line-bundle data common to the elliptic curve; it does not distinguish decompositions in one Abel fiber. Power operations act on supplied cohomology classes. Point separation requires marked `N`-level structure or a source-indexed class family, which reintroduces the original orientation and source-scale state.

## Proof track

Construct a finite endpoint-only point-faithful spectrum, prove operation-to-factor biconditionality on all strata, and certify complete exponents at most `0.45`.

## Disproof track

Show cubical data are common across source tuples, prove faithful level/spectrum/output state at least `N^0.50`, expose noncanonical inverse factors, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small elliptic spectrum with independently known cubical orientation and power operations.
- Negative controls: source tuples with the same Abel endpoint, unmarked cubical structures, explicit `N`-level dictionaries, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires endpoint-only point-faithful construction, exact all-source return, verified logs, blind descent, and `lambda,mu<=0.45`. Common curve-only data, source-sized level/state, one missing stratum, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-300/cubical_power_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-300/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-300/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-300/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged/scoped-negative high-risk proposal is toy-only if instantiated; extrapolations remain heuristic and model-bound. A correct cubical orientation or toy power-operation factor is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-300/cubical_power_source_theorem.md` proving a finite point-faithful operation inverse or the curve-only/orientation/source-state obstruction.
