# ECDLP-IDEA-263 — Arithmetic differential-character scalar digits

## Status and claim labels

- Class: `arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `merged_rejected_additive_delta_character_kills_prime_to_p_torsion_or_lift_breaks_group_law`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: retired review-required zero-run preflight
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a nonzero differential value, a valid relation, a recovered source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A canonical arithmetic lift of the finite-field subgroup into a `p`-adic jet space admits a nonzero additive arithmetic differential character `psi` that is compatible with scalar multiplication.  Evaluating `psi` and its successive delta coordinates would reveal enough scalar digits, or source-linear coordinates, for complete factor-base descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **canonically lift finite-field points to arithmetic jet space, evaluate an additive delta-character, and decode scalar digits from its Frobenius/delta coordinates**.  For a group-compatible lift of a prime-to-`p` subgroup of order `N`, additivity gives `N psi(T)=psi([N]T)=0`; the characteristic-zero additive target is torsion-free and hence `psi(T)=0`.  Choosing non-torsion lifts can make values nonzero, but absent a group-homomorphic section it destroys `psi(tilde Q)=x psi(tilde P)`.  This is the same semantic boundary as IDEA-004 prime-to-`p` jet logarithms, IDEA-109 torsion sections, IDEA-140 de Rham-Witt coordinates, and IDEA-160 ramification features once lift compatibility is required.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. Public `E/F_p` and its prime-order subgroup have a deterministic target-uniform lift to a `p`-adically complete characteristic-zero ring with a fixed Frobenius lift and `p`-derivation.
2. A finite-order additive delta-character is evaluable at charged precision and is nonzero on the lifted subgroup.
3. The lift and character preserve the scalar equation and all factor-base sums strongly enough that character values decode exact residues, digits, or signed point sources.
4. Model construction, lift choices, precision, ramification, character evaluation, ambiguity, output, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`finite_field_prime_order_subgroup | canonical_p_adic_jet_lift | additive_delta_character | Frobenius_delta_scalar_digits | exact_group_compatible_decode | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar-coordinate and orientation barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the lift/transfer compatibility barrier.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear feature-rank boundary.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-044`, the transfer-output and cost-accounting negative.

## Closest primary literature

- Buium, Differential characters of abelian varieties over p-adic fields, [https://eudml.org/doc/144323](https://eudml.org/doc/144323), constructs arithmetic differential characters of supplied `p`-adic abelian schemes and proves kernel phenomena.
- Buium and Simanca, Arithmetic partial differential equations, [https://arxiv.org/abs/math/0605107](https://arxiv.org/abs/math/0605107), develops Fermat-quotient differential equations and canonical flows on supplied elliptic curves.
- Buium and Miller, Purely arithmetic PDEs over a p-adic field I: delta-characters and delta-modular forms, [https://arxiv.org/abs/2103.16627](https://arxiv.org/abs/2103.16627), constructs arithmetic-PDE Manin maps under additional arithmetic directions but not a nonzero finite-field torsion logarithm.

These primary records were checked for additive delta-characters and their supplied arithmetic input.  None provides a nonzero group-compatible character on a finite prime-to-`p` subgroup, a canonical scalar-preserving lift, factor-log calibration, and fresh masked descent.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, the characteristic-zero model, Frobenius lift, `p`-derivation, delta-character order, precision, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, lift `R` and every required public object without using `r`, evaluate the frozen delta-character coordinates, and derive a relation/source candidate without a discrete-log-labelled lift table.
3. Invert accepted coordinates to exact signed factor points, verify both the reduced elliptic sum and every claimed character compatibility, and preserve every zero value, precision failure, lift collision, ambiguity branch, repeated point, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and source output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen lift, character, and inverse to fresh masks `Q+[t]P`, with no known-log-only lift, target-selected Frobenius, or post-hoc scalar advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by character or lift ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every model coefficient, Frobenius/lift choice, ramified extension, precision bit, jet coordinate, failed target, zero character, branch, source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness or relation validity alone has no performance meaning.

## Likely fatal obstruction

An additive delta-character valued in a torsion-free characteristic-zero additive group kills finite prime-to-`p` torsion.  A group-compatible section of the finite subgroup therefore produces only zero character values.  A non-torsion pointwise lift can evade that zero, but then it is not a homomorphic section and its differential values do not preserve the unknown scalar or factor-base sums.  The proposal must choose between a zero invariant and a noncanonical value with no ECDLP equation.

## Proof track

Exhibit a canonical scalar-compatible lift on the whole subgroup, prove a nonzero additive delta-character and exact digit/source inverse on it, and derive complete time and memory exponents at most `0.45`.

## Disproof track

Prove the prime-to-`p` torsion-kernel statement for every admissible character, exhibit two scalar-related finite-field points whose chosen non-torsion lifts violate additivity, or show lift/precision/output or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied non-torsion `p`-adic point pair with a known exact scalar relation, where additivity and delta-character evaluation are independently verified.
- Negative controls: prime-to-`p` torsion lifts, arbitrary coordinate-wise lifts, two Frobenius lifts, a deliberately non-homomorphic section, IDEA-004, IDEA-109, IDEA-140, IDEA-160, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a target-uniform group-compatible lift and nonzero character of exponent at most `0.45`, exact scalar/source recovery with zero false outputs on all frozen strata, full factor-log rank, blind masked descent, and complete `lambda` and `mu` at most `0.45`.  Character values identically zero on the subgroup, dependence on a non-homomorphic/source-labelled lift, unresolved precision, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-263/delta_character_torsion_or_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-263/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-263/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-263/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A correct delta-character identity, nonzero value on unrelated lifts, valid relation, recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-263/delta_character_torsion_or_lift_theorem.md` proving a nonzero scalar-compatible subgroup character or the torsion-kernel/non-homomorphic-lift dichotomy.
