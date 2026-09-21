# ECDLP-IDEA-295 — Bost–Connes KMS-state scalar orientation

## Status and claim labels

- Class: `arithmetic_operator`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_kms_extremal_state_requires_external_global_orientation`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a KMS state, phase transition, Artin label, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A canonical number-field or CM lift of the endpoint defines a Bost–Connes-type quantum statistical system whose extremal low-temperature KMS-state symmetry label gives the unknown finite-field scalar orientation and exact source factors below rho and BSGS.

## Mechanism-new operation

The screened operation is **map a globalized endpoint into an arithmetic Hecke C-star dynamical system, select its extremal KMS state after symmetry breaking, and decode the Artin/Galois symmetry label to the scalar or factor tuple**. The original Bost–Connes system is arithmetic data for the rationals, while the cited CM generalization starts from supplied imaginary-quadratic K-lattice data. Neither constructs a canonical system from a generic finite-field endpoint. Selecting one extremal state still requires an orientation; its Galois label is not a coordinate of a generic finite-field point. A source-separating observable or state family imports the global lift and source deck. This merges with IDEAs 018, 096, 127, 153, 221, and 283 after state preparation and readout are charged.

## Assumptions

1. Generic prime-field points admit a canonical scalar-compatible global/CM lift into one arithmetic dynamical system.
2. An extremal KMS state is publicly selected without source, scalar, or branch advice.
3. Its symmetry label has a canonical exact inverse to all signed factor tuples or `x mod N`.
4. Global construction, algebra/state dimension, temperature precision, state preparation, observables, output, logs, descent, and memory are charged.

## Semantic fingerprint

`number_field_or_CM_lift | Bost_Connes_Hecke_Cstar_system | extremal_KMS_state | Artin_symmetry_orientation | exact_scalar_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact target-local return requirement.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the public generator/orientation boundary.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-045`, the global representation-orientation negative.
5. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the full relation-to-blind-descent accounting gate.

## Closest primary literature

- Bost and Connes, [Hecke algebras, type III factors and phase transitions with spontaneous symmetry breaking in number theory](https://doi.org/10.1007/BF01589495), constructs the original rational arithmetic dynamical system and KMS symmetry.
- Connes, Marcolli, and Ramachandran, [KMS states and complex multiplication](https://doi.org/10.1007/s00029-005-0013-x), generalizes that framework to supplied imaginary-quadratic K-lattice data.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source canonically embeds a generic ECDLP endpoint or turns an extremal-state symmetry into an exact finite-field point coordinate; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, global lift, Hecke pair, C-star dynamics, temperature schedule, observables, masks, and verifier.
2. Build systems for known-log endpoints without source-labelled states or scalar advice.
3. Prepare/read every allowed extremal state and decode accepted symmetry labels to exact signed factors.
4. Verify rows, collect independent rank, solve and verify factor logs.
5. Apply the identical system and readout to fresh masked targets `Q+[t]P`.
6. Preserve phase, state, and Galois ambiguity; substitute logs and remove masks.
7. Accept only exact `[x]P=Q`, charging system construction, state dimension, precision, samples, outputs, rows, logs, descent, and verification.

## Full rho/BSGS cost model

Let setup be `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one state/readout/inverse attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, state ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. All algebra elements, representations, precision bits, states, samples, labels, outputs, and live bytes are charged.

## Likely fatal obstruction

Spontaneous symmetry breaking labels extremal states of a supplied arithmetic system. It does not select the state corresponding to an unrelated finite-field point. The required global lift and state orientation are precisely the missing scalar channel. Aggregate KMS data are common across symmetry orbits; point separation requires a source-sized state/observable dictionary.

## Proof track

Construct a canonical endpoint system and public extremal-state selector with exact scalar/source inversion and complete exponents at most `0.45`.

## Disproof track

Show state choice is symmetry-ambiguous, the global lift is noncanonical, source-separating state/observable dimension is at least `N^0.50`, or either exponent is at least `0.50`.

## Positive and negative controls

- Positive control: the supplied rational Bost–Connes system with independently labelled extremal states.
- Negative controls: symmetry-averaged KMS states, permuted extremal labels, source-labelled observables, unrelated finite-field endpoints, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires canonical endpoint embedding, public state selection, exact all-source inverse, verified logs, blind descent, and `lambda,mu<=0.45`. External orientation, symmetry averaging, state/output at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-295/kms_scalar_orientation_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-295/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-295/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-295/cost_analysis.md`

All paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged high-risk proposal is toy-only if instantiated; extrapolations remain heuristic and model-bound. A correct KMS-state calculation or arithmetic phase label is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-295/kms_scalar_orientation_theorem.md` proving a canonical endpoint-to-extremal-state scalar inverse or the symmetry/globalization obstruction.
