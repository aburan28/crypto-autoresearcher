# ECDLP-IDEA-283 — Kolyvagin-derivative Euler-system scalar return

## Status and claim labels

- Class: `arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_euler_system_controls_selmer_modules_not_finite_field_scalar_orientation`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an Euler-system class, Kolyvagin derivative, Selmer bound, valid relation, localized class, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform globalization of a prime-field ECDLP instance admits an Euler system whose Kolyvagin derivative classes preserve the unknown scalar under localization and finite-field reduction.  Finite-singular comparison maps and reciprocity across auxiliary primes would orient those classes in a public basis and return exact factor points or the scalar for relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **globalize the finite subgroup and endpoints, form norm-compatible Euler-system classes, apply Kolyvagin derivative operators at auxiliary primes, and decode their localized finite-singular coordinates back to exact finite-field sources or scalar**.  This is an arithmetic-transfer operation rather than a same-field isogeny, solver substitution, or relation-only certificate.  Euler/Kolyvagin systems use supplied global Galois representations and norm-compatible classes to bound or control Selmer modules; their derivative relations do not create the coefficient of one point relative to another in a finite cyclic subgroup.  A scalar-compatible globalization and oriented local comparison map are the missing transfer, while enough localized coordinates to distinguish `N` scalars carry the original information/state.  The proposal merges with global-lift, cohomological-orientation, and source-return negatives after global construction, auxiliary primes, class data, and finite-field return are charged.

## Assumptions

1. Public `E/F_p,P,Q,N` and every relation endpoint admit a deterministic global Galois representation and scalar-compatible lifts without knowing the scalar or source tuple.
2. A nontrivial Euler system and all required Kolyvagin derivatives, local conditions, and comparison maps are constructible below rho.
3. Localized derivative classes have a canonical public orientation whose exact coordinate returns finite-field factor points or the unknown scalar with sub-rho ambiguity.
4. Globalization, conductors, auxiliary primes, cohomology classes, derivative operators, localizations, orientations, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | scalar_compatible_global_Galois_lift | Euler_system_norm_classes | Kolyvagin_derivative_localization | exact_finite_field_scalar_or_source_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator and exact return.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar-coordinate and orientation barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the lift, transfer, and specialization compatibility boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank transformed coordinates without source inversion.
5. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the factor-log completion and fresh-target descent requirement.

## Closest primary literature

- Howard, [The Heegner point Kolyvagin system](https://doi.org/10.1112/S0010437X04000569), constructs a Kolyvagin system from Heegner-point classes and proves Selmer-structure consequences in a global arithmetic setting.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field relation and factor-base equations whose sources the global classes would have to recover.

No checked source provides a target-uniform scalar-compatible globalization, an oriented Euler-system coordinate returning a finite-field discrete log, or complete sub-rho factor descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, global lifting rule, Galois representation, Euler-system family, auxiliary-prime set, derivative and finite-singular comparison conventions, factor base, masks, and verifier.
2. Globalize known-log relation endpoints and construct complete norm-compatible Euler-system classes and Kolyvagin derivatives without using their scalar labels or source tuples.
3. Localize every derivative class, apply the frozen comparison and orientation maps, and return all exact signed finite-field factor points or scalar residues.
4. Verify the resulting relations, collect independent rows, solve every factor log, and verify all recovered logs.
5. Apply the identical frozen globalization, Euler-system, derivative, and localization pipeline to fresh masked targets `Q+[t]P` without target-specific tuning or scalar advice.
6. Retain every localized branch, return a complete factor decomposition or scalar residue, remove the mask, and verify the reconstructed endpoint.
7. Accept only exact `[x]P=Q`, charging global model search, conductors, auxiliary primes, class construction and storage, derivatives, local comparisons, orientation ambiguity, rows, factor logs, fresh-target descent, verification, and live memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one globalize/Euler/derivative/return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, localized-class output be `N^o`, lift or orientation ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every global coefficient, conductor prime, Euler-system class, norm relation, Kolyvagin derivative term, localization, finite-singular comparison coordinate, orientation branch, failed return, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Kolyvagin derivatives convert norm-compatible global classes into cohomology classes satisfying local conditions; they control Selmer rank, index, or characteristic ideals rather than compute a discrete coordinate in a finite-field subgroup.  A generic finite-field point does not canonically lift to the global Heegner/Euler-system setting while preserving its unknown scalar.  Even granting a lift, finite-singular comparison identifies modules only after choices of generators and local orientations; choosing the coordinate corresponding to `Q=[x]P` is the reduced preimage problem.  Accumulating enough auxiliary local data to distinguish all `N` coordinates requires scalar-scale information or state unless a genuinely compact oriented decoder is supplied.

## Proof track

Construct a target-uniform scalar-compatible globalization and Euler system, prove a canonical oriented derivative-to-finite-field source/scalar decoder on every stratum, and certify both complete exponents at most `0.45`.

## Disproof track

Show generic endpoints admit no compatible global classes, prove derivative systems determine only ideals/ranks up to units, exhibit orientation collisions, prove auxiliary/localized state at least `N^0.50`, reduce coordinate return to ECDLP, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied global elliptic curve with a known Heegner/Euler-system class, fixed local generators, and independently computed Kolyvagin derivatives.
- Negative controls: arbitrary coordinate lifts of finite-field points, Euler systems reporting only Selmer bounds, unit-rescaled local bases, incompatible reduction primes, scalar-labelled global classes, relation-only cohomology certificates, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a scalar-compatible globalization and oriented Euler/Kolyvagin decoder of exponent at most `0.45`, exact all-strata finite-field factor or scalar return, full row rank and verified factor logs, blind fresh-target descent, and complete `lambda,mu<=0.45`.  Selmer-only output, noncanonical lift, unit/orientation ambiguity, auxiliary/class/output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-283/kolyvagin_scalar_return_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-283/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-283/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-283/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative arithmetic-transfer proposal.  Every finite globalization or cohomology computation would be toy and projections heuristic and model-bound.  A valid Euler-system relation, Kolyvagin derivative, Selmer bound, or recovered toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-283/kolyvagin_scalar_return_theorem.md` proving a scalar-compatible oriented derivative decoder or the global-lift/Selmer-only/orientation-state obstruction.
