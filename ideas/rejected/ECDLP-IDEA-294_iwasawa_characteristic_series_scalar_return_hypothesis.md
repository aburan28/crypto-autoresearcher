# ECDLP-IDEA-294 — Iwasawa characteristic-series scalar return

## Status and claim labels

- Class: `arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_iwasawa_characteristic_ideal_aggregates_global_module_without_scalar_orientation`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a characteristic series, main-conjecture identity, valid relation, or toy factor is not an ECDLP break.

## Falsifiable hypothesis

A scalar-compatible global lift places the marked subgroup in a cyclotomic `Z_p` tower whose Iwasawa module has distinguished characteristic-series factors encoding the unknown scalar orientation and exact source decomposition below rho and BSGS.

## Mechanism-new operation

The screened operation is **globalize the endpoint, construct a Lambda-module over a `Z_p` tower, factor its characteristic series by Weierstrass preparation, and decode distinguished factors to the scalar or exact source points**. Iwasawa characteristic ideals aggregate a supplied global module; they do not orient a generic finite-field order-`N` line. The canonical prime-to-characteristic lift is torsion and height-zero, while non-torsion sections carry the P1543 defect. A series refined to distinguish every source tuple stores their global classes. The operation merges with IDEAs 005, 018, 211, 264, 269, and 283 after globalization and orientation are charged.

## Assumptions

1. A canonical target-uniform globalization preserves `Q=[x]P` in one explicit `Z_p` tower.
2. The resulting finite module and characteristic series are computable below rho without knowing source tuples or `x`.
3. Distinguished factors admit a canonical scalar/source inverse on all strata.
4. Tower levels, local conditions, module presentation, series precision, factorization, output, rows, logs, descent, and memory are charged.

## Semantic fingerprint

`scalar_compatible_global_lift | Iwasawa_Lambda_module | characteristic_series_Weierstrass_factors | exact_scalar_or_source_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the target-local exact-return requirement.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the generator/transposed-return boundary.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the hidden global representation/orientation negative.
5. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the complete known-log-to-blind-descent obligation.

## Closest primary literature

- Iwasawa, [On Gamma-extensions of algebraic number fields](https://doi.org/10.1090/S0002-9904-1959-10317-7), establishes the Gamma-extension setting.
- Iwasawa, [On some modules in the theory of cyclotomic fields](https://doi.org/10.2969/jmsj/01610042), develops the supplied cyclotomic-module setting; neither paper supplies the hypothesized finite-field endpoint compiler or oriented factor inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source supplies a canonical scalar-compatible globalization or an oriented characteristic-factor inverse for a generic prime-field subgroup; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, global lift, `Z_p` tower, Lambda-module presentation, factorization rule, masks, and verifier.
2. Globalize known-log endpoints without target-dependent choices or source advice.
3. Construct and factor the characteristic series, then return every accepted factor as an exact scalar residue or signed factor tuple.
4. Verify relations, collect independent rows, solve and verify factor logs.
5. Repeat the identical tower/module pipeline on fresh masked targets `Q+[t]P`.
6. Preserve all unit, pseudo-isomorphism, and factor ambiguities; substitute logs and remove masks.
7. Accept only exact `[x]P=Q`, charging tower construction, precision, module state, factors, outputs, rows, logs, descent, and verification.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one tower/module/factor attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, orientation ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. All primes, levels, local classes, coefficients, precision bits, factors, outputs, and live bytes are charged.

## Likely fatal obstruction

Characteristic ideals summarize a module up to pseudo-isomorphism and units; they do not identify a marked point or basis coordinate. The generic subgroup order is unrelated to the tower's `p`-primary direction. Constructing an oriented global lift is already the missing scalar channel, and retaining source-separating classes makes the module or series source-sized.

## Proof track

Construct a canonical scalar-compatible globalization, prove oriented factor injectivity and exact return, and certify complete exponents at most `0.45`.

## Disproof track

Show the canonical lift is torsion/height-zero, exhibit identical series for different source orientations, prove series/module state at least `N^0.50`, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small Iwasawa module with independently known characteristic series and factorization.
- Negative controls: unit-equivalent series, unmarked module bases, torsion lifts, source-labelled global classes, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires canonical globalization, oriented all-source inversion, verified rank/logs, blind descent, and `lambda,mu<=0.45`. Unoriented ideals, source-sized module state, one missing stratum, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-294/iwasawa_scalar_return_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-294/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-294/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-294/cost_analysis.md`

All paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged arithmetic-transfer proposal is toy-only if instantiated; extrapolations remain heuristic and model-bound. A correct series or main-conjecture identity is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-294/iwasawa_scalar_return_theorem.md` proving a canonical oriented characteristic-factor inverse or the globalization/aggregate-invariant obstruction.
