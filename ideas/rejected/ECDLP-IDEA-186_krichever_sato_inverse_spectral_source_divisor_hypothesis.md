# ECDLP-IDEA-186 — Krichever–Sato inverse-spectral source divisor

## Status and claim labels

- Class: `representation`
- Risk band: `representation_changing`
- Top lane: `representation_changing`
- State: `merged_rejected_baker_akhiezer_divisor_preallocation_scoped_negative`
- Cohort: `20260718-d`
- Evidence scale: primary-literature and semantic preflight only; no experiment ran
- Contract posture: no contract warranted after the source-divisor reduction
- Scale labels: every prospective finite check is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an inverse-spectral identity, reconstructed supplied divisor, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A scalar-blind public elliptic endpoint determines compact Baker–Akhiezer or Sato-Grassmannian spectral data whose inverse-spectral transform canonically reconstructs every effective factor-base source divisor in the endpoint's Abel–Jacobi fiber. Those divisors yield complete relations, factor-base logarithms, and masked unknown-target descent with time and memory below rho and BSGS.

## Mechanism-new operation

The proposed operation is **endpoint-to-Baker–Akhiezer/Sato spectral compilation followed by inverse-spectral source-divisor reconstruction**. It is mechanism-new only if the endpoint alone determines the divisor-sensitive spectral point without a supplied effective divisor, line bundle trivialization, or source-labelled poles. Running Krichever reconstruction after supplying the divisor, changing theta/tau evaluation, increasing precision, or solving a dense resultant is a control.

Semantic review found that Krichever data explicitly contain a spectral curve, marked point/local parameter, line bundle, and effective divisor or equivalent pole data. In the ECDLP use, constructing those divisor-sensitive data from the degree-zero endpoint is already the missing source inversion. Finite theta/tau samples retain symmetric aggregates or a full-rank fiber, while sufficient samples to isolate every divisor preallocate the sources. This version is merged/rejected at that compiler, not at inverse-spectral correctness.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, divisor degree/arity, marked spectral data, masks, and verifier are frozen.
2. A finite-field, target-uniform, scalar-blind compiler maps any elliptic endpoint to Baker–Akhiezer or Sato data without source-divisor advice.
3. The data and inverse transform cover every signed point, repetition, infinity case, multiplicity, and special divisor stratum.
4. Inverse spectral reconstruction emits every exact effective factor-base divisor in the Abel fiber and no false divisor.
5. Field lifts, precision, theta/tau samples, Grassmannian coordinates, divisors, output, rank, descent, verification, time, and memory are charged.

## Semantic fingerprint

`finite_field_endpoint_to_Baker_Akhiezer_data | Sato_Grassmannian_inverse_spectral_transform | exact_effective_source_divisors | no_divisor_preallocation | blind_masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate preprocessing barrier relevant to a purported compact endpoint representation.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transposed-system boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear phase/source inverse gap.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the exact degree-two divisor-fiber and denominator-tree boundary.
5. `inputs/ledger_inventory.json` — imported `P1434`, the missing public algebraic source-fiber generator.

## Closest primary literature

- Krichever, [Methods of algebraic geometry in the theory of non-linear equations](https://doi.org/10.1070/RM1977v032n06ABEH003862), constructs algebro-geometric solutions from spectral curves and divisor data.
- Krichever, [Integration of nonlinear equations by the methods of algebraic geometry](https://doi.org/10.1007/BF01135528), develops the Baker–Akhiezer inverse-spectral framework with prescribed spectral and pole data.

The checked work reconstructs from supplied spectral/divisor inputs; it does not map one finite-field elliptic endpoint to every factor-base divisor or give complete sub-rho descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B=N^beta`, spectral curve, marked point, local parameter, divisor degree, field-lift and precision rules, masks, and an independent verifier.
2. Compile each known-log endpoint `R_j=[r_j]P` to identical-form Baker–Akhiezer/Sato data without using `r_j`, a source divisor, or endpoint-specific advice.
3. Apply the frozen inverse-spectral transform and emit every exact signed factor-base effective divisor in the endpoint fiber.
4. Verify point membership, divisor multiplicity, Abel–Jacobi/elliptic sum, repeated points, infinity, special strata, misses, false divisors, and all precision branches.
5. Collect at least `B+sigma` independently verified rows of rank `B`, solve factor-base logarithms, and verify every recovered logarithm by scalar multiplication.
6. Apply the identical compiler and inverse transform to fresh masked targets `Q+[t]P`.
7. Substitute verified factor logs, remove masks, retain all ambiguity candidates, and accept only `x` satisfying `[x]P=Q`.
8. Charge field lifting, spectral compilation, theta/tau evaluation, Grassmannian coordinates, inverse reconstruction, all output, failed trials, rank, linear algebra, descent, verification, time, and peak bit memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time; BSGS costs `N^(1/2+o(1))` time and memory. Let field lift, precision, spectral-curve, theta/tau, and Grassmannian setup together cost `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one complete inverse-spectral query cost `N^q,N^q_m`; divisor output and target ambiguity be `N^o,N^u`; and factor-log linear algebra cost `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Every precision bit, theta/tau sample, pole, divisor coordinate, Grassmannian cell, failed endpoint, source divisor, and descent branch is charged; the inverse-spectral map is not treated as an oracle.

## Likely fatal obstruction

Baker–Akhiezer data are source-divisor data in another representation. A degree-`m` Abel–Jacobi fiber over one elliptic endpoint contains many effective divisors, so the endpoint does not determine a unique pole divisor. Supplying a divisor makes inverse spectral reconstruction circular; retaining only endpoint-derived theta/tau samples aggregates the fiber or leaves a full-rank system. Sampling enough coordinates to separate every divisor recreates the source deck and its output cost.

## Proof track

Construct a finite-field endpoint compiler independent of a source divisor, prove its inverse-spectral output is biconditional with all exact factor-base divisors on every stratum, prove compactness and precision bounds, and derive complete `lambda,mu<=0.45` rank and blind descent.

## Disproof track

Exhibit two effective source divisors with one endpoint and identical compiled spectral data, show the compiler must include divisor-labelled poles, derive a full-rank or `B^m` separation cost, lose one special divisor stratum, or prove either complete exponent at least `0.5`.

## Positive and negative controls

- Positive: classical Baker–Akhiezer reconstruction with the spectral curve, marked point, local parameter, and effective divisor deliberately supplied.
- Positive: degree-one toy Jacobi inversion where one endpoint can determine one point under frozen conventions.
- Negative: degree-`m>1` same-sum effective divisors, which must not become distinguishable from endpoint-only data by assumption.
- Negative: finite theta/tau moment sets, explicit divisor tables, characteristic-zero lifts, dense resultants, rho, BSGS, known-log leakage, and blind-target checks.

## Quantitative promotion and falsification gates

This version is merged/rejected at the endpoint-to-divisor-sensitive spectral compiler. A successor under a new ID requires 100% divisor/multiplicity recall, zero false divisors, no supplied or preallocated source poles, frozen finite-field precision, verified rank `B`, successful blind masked descent, and formal `lambda,mu<=0.45`. Values in `(0.45,0.50)` are inconclusive; one same-endpoint collision, hidden divisor input, full-rank/source-deck cost, or either exponent at least `0.50` falsifies the scoped successor. A correct reconstruction from supplied data cannot promote it.

## Artifact plan

- Endpoint compiler and source-divisor theorem: `ideas/artifacts/ECDLP-IDEA-186/baker_akhiezer_endpoint_inverse_theorem.md`
- Frozen inverse-spectral specification: `ideas/artifacts/ECDLP-IDEA-186/inverse_spectral_spec.md`
- Prospective fixtures and independent verifier: `ideas/artifacts/ECDLP-IDEA-186/fixtures.json` and `ideas/artifacts/ECDLP-IDEA-186/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-186/cost_analysis.md`

All research-artifact paths are prospective. No artifact directory, contract, or run exists.

## Interpretation boundary

This is a novelty-unverified representation-changing scoped negative. Every finite observation would be toy, and all cost projections are heuristic and model-bound. The conclusion rejects the circular endpoint compiler, not Krichever reconstruction, and it makes no breakthrough claim.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-186/baker_akhiezer_endpoint_inverse_theorem.md` specifying the endpoint-only spectral data and proving or refuting exact recovery of every degree-`m` factor-base divisor without divisor-labelled pole input.
