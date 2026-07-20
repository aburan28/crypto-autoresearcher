# ECDLP-IDEA-261 — Finite-field separating-invariant source orbit

## Status and claim labels

- Class: `finite_field_invariant_theory`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_orbit_separator_requires_source_representative`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; orbit separation, invariant equality, relation validity, a recovered orbit, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A small finite-field separating set for the `S_5` action on five signed factor-point coordinates has values computable directly from the endpoint sum.  Inverting that signature would recover the unordered source orbit and enable complete relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **evaluate finite-field separating invariants for the `S_5` source-slot action and invert the resulting signature to the exact unordered source orbit**.  Credit applies only to an invariant whose value is computable from the endpoint without enumerating or lifting the source fiber.  It merges with IDEA-151 because fixed-slot orbit compression forgets coordinate payload, with IDEA-246 because quotient invariants do not restore labelled sheets, and with IDEA-149 because an orbit decoder needs a source-calibrated message map; live `P1539` is the exact endpoint-predicate-without-orbit-locator control and live `P1536` is the derivative-localization control.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. Five signed factor points admit a fixed finite-field coordinate representation with a well-defined `S_5` action through every sign, multiplicity, infinity, and exceptional stratum.
2. A bounded separating family descends to values computable from one endpoint sum without a tuple representative, source-indexed elimination, or orbit table.
3. The invariant signature has a target-uniform exact inverse to every factor-base source orbit, including point identities and multiplicities needed for factor logs.
4. Invariant construction, evaluation, orbit inversion, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`five_source_coordinate_tuple | finite_field_S5_separating_invariants | endpoint_signature_to_source_orbit | exact_factor_point_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the proposed exact source-resolving feature representation.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the proposed public source-fiber generator and transposed join.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear invariant/feature-to-source boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact aggregate transition primitive whose composition becomes dense.

## Closest primary literature

- Kemper, Lopatin, and Reimers, Separating invariants over finite fields, [https://doi.org/10.1016/j.jpaa.2021.106904](https://doi.org/10.1016/j.jpaa.2021.106904), constructs separating sets for supplied finite-field matrix-group representations but does not derive hidden tuple invariants from a coarser endpoint quotient.
- Reimers, Separating Invariants of Finite Groups, [https://doi.org/10.1016/j.jalgebra.2018.03.022](https://doi.org/10.1016/j.jalgebra.2018.03.022), studies orbit separation for supplied group actions on affine varieties rather than inversion of an elliptic addition fiber.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies neighboring symmetric endpoint equations but no endpoint-to-source-orbit separator.

These primary records were checked for the named finite-field separation operation.  None supplies endpoint-computable separating values, an exact factor-point orbit inverse, factor-log calibration, and fresh masked descent.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity five, tuple coordinates, the `S_5` action, separating family, inverse, masks, tie rules, exceptional strata, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, compute the claimed separating signature from compact endpoint and factor-base data without a source representative, `B^5` tuple enumeration, dense elimination, or a signature-to-orbit dictionary.
3. Invert the signature to all exact unordered signed factor-point orbits, verify sums, and preserve every invariant collision, repeated point, stabilizer, multiplicity, infinity chart, ambiguity branch, false orbit, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen invariant evaluator and orbit inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected separator, or post-hoc orbit advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by invariant ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one invariant evaluation plus exact orbit inverse cost `N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every coordinate, invariant coefficient and degree, field operation, orbit representative, stabilizer branch, elimination or table entry, preprocessing query, failed target, source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; orbit separation or relation validity alone has no performance meaning.

## Likely fatal obstruction

Separating invariants distinguish `S_5` orbits only when evaluated on a tuple representative.  The endpoint sum is a much coarser quotient containing many distinct `S_5` source orbits.  Any invariant descending through the sum is constant across that whole fiber, while a non-descending separator requires the hidden tuple or dense elimination/table state to evaluate.  Orbit separation therefore does not provide endpoint-to-orbit inversion.

## Proof track

Construct a bounded separating signature directly from the endpoint, prove its exact all-strata inverse to signed factor-point orbits without source advice, and derive complete exponents at most 0.45.

## Disproof track

Exhibit two distinct `S_5` source orbits in one endpoint fiber with every endpoint-derived invariant equal, show a non-descending separator requires a tuple representative or dense source state, or prove degree, output, or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: a supplied finite-field group representation with known orbit representatives and a published separating set checked against exhaustive small-orbit enumeration.
- Negative controls: distinct source orbits sharing one endpoint, same-orbit slot permutations, nontrivial stabilizers, source-label permutations, dense orbit tables, IDEA-149, IDEA-151, IDEA-246, live `P1536`, live `P1539`, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires endpoint-computable separating values and orbit inversion of exponent at most 0.45, exact all-source and multiplicity recall with zero false orbits, no supplied tuple or signature table, full factor-log rank, blind descent, and complete lambda and mu at most 0.45.  One same-endpoint orbit collision, source-representative input, dense elimination/orbit state, or either exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-261/separating_invariant_source_no_go.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-261/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-261/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-261/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A correct separating set, invariant equality, valid relation, recovered source orbit, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-261/separating_invariant_source_no_go.md` proving either an endpoint-computable exact orbit signature or that every nonconstant source separator requires a tuple representative or dense fiber state.
