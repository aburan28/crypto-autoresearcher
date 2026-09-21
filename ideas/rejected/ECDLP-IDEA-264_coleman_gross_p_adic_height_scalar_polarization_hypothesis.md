# ECDLP-IDEA-264 — Coleman-Gross p-adic-height scalar polarization

## Status and claim labels

- Class: `arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_bilinear_p_adic_height_kills_torsion_or_lift_loses_scalar_relation`
- Cohort: `20260718-i`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a nonzero height, a valid relation, a recovered source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A canonical global or `p`-adic lift of the finite-field subgroup admits Coleman-Gross height pairings whose polarization preserves the unknown scalar: for frozen auxiliary divisor classes `Z_j`, the vector `(h_p(tilde Q,Z_j))_j` would equal `x(h_p(tilde P,Z_j))_j`.  Exact height ratios or source-linear height coordinates would then complete factor-base descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift finite-field points to divisor classes, evaluate frozen Coleman-Gross bilinear heights against auxiliary classes, and polarize the values into scalar or source coordinates**.  Bilinearity kills finite torsion in the torsion-free `p`-adic target.  Therefore a group-compatible lift of the prime-order subgroup gives zero heights, while non-torsion pointwise lifts can give nonzero values only by losing the finite-field scalar equation.  Coleman-Gross heights also require arithmetic input and auxiliary choices such as a global character and local de Rham/Hodge splitting.  The operation merges with IDEA-004 `p`-adic logarithms, IDEA-005 height transfer, IDEA-046 regulator pairings, IDEA-119 global Selmer lifts, and IDEA-211 bilinear-source forms once lift and choice dependence are charged.  A solver swap, parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector, dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. Public `E/F_p`, its factor points, and every masked target have deterministic target-uniform lifts to a global curve/Jacobian or a `p`-adic setting supporting the same frozen Coleman-Gross pairing.
2. The lift preserves `Q=[x]P` and all factor-base relations in the domain where height bilinearity applies.
3. Frozen auxiliary divisor classes and height choices produce a nonzero, well-conditioned vector that decodes exact scalar residues or signed factor sources.
4. Global model search, point lifting, bad-prime terms, local integration, splittings, precision, ambiguity, rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`finite_field_subgroup | canonical_global_or_p_adic_lift | Coleman_Gross_bilinear_height | auxiliary_divisor_polarization | exact_scalar_or_source_coordinates | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar-coordinate and orientation barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the lift/transfer compatibility barrier.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-044`, the transfer-output and cost-accounting negative.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-lift boundary.

## Closest primary literature

- Coleman and Gross, p-adic heights on curves, [https://doi.org/10.2969/aspm/01710073](https://doi.org/10.2969/aspm/01710073), constructs a bilinear `p`-adic height for divisor classes on supplied arithmetic curves with auxiliary choices.
- Coleman, The universal vectorial bi-extension and p-adic heights, [https://doi.org/10.1007/BF01239529](https://doi.org/10.1007/BF01239529), interprets `p`-adic heights through a supplied universal bi-extension.
- Besser, The p-adic height pairings of Coleman-Gross and of Nekovar, [https://arxiv.org/abs/math/0209006](https://arxiv.org/abs/math/0209006), compares two supplied arithmetic height constructions and does not define a scalar-preserving section of a finite-field subgroup.

These primary records were checked for bilinearity, arithmetic input, and auxiliary choices.  None gives a nonzero height on a group-compatible finite prime-to-`p` lift, an endpoint-only scalar/source inverse, factor-log calibration, and fresh masked descent.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, global/`p`-adic model, point-lift rule, global character, local splittings, auxiliary divisor classes, precision, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, lift `R` and the frozen auxiliary classes without using `r`, evaluate all local and global Coleman-Gross height terms, and derive scalar/source candidates without a discrete-log-labelled lift table.
3. Polarize or invert accepted height vectors to exact signed factor points, verify the reduced elliptic sum and every claimed lifted relation, and preserve every zero value, bad-reduction failure, lift collision, splitting dependence, ambiguity branch, repeated point, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and source output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen lifts, height choices, and inverse to fresh masks `Q+[t]P`, with no known-log-only lift, target-selected splitting, or post-hoc height advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by height/lift ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every arithmetic model, point lift, auxiliary divisor, global character, local splitting, prime contribution, integration step, precision bit, failed target, zero height, branch, source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation, and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness or relation validity alone has no performance meaning.

## Likely fatal obstruction

A bilinear height valued in a torsion-free `p`-adic additive group vanishes when either argument is finite torsion.  Hence a group-homomorphic lift of the finite prime-order subgroup produces no scalar signal.  Non-torsion lifts and alternative Hodge splittings may produce nonzero heights, but those values depend on arithmetic choices and no longer satisfy the finite-field equation `tilde Q=[x]tilde P`.  The proposal again chooses between a zero invariant and a noncanonical invariant unrelated to the hidden scalar.

## Proof track

Construct a target-uniform scalar-compatible lift with frozen height data, prove at least one nonzero height coordinate and exact scalar/source polarization on the whole subgroup, and derive both complete exponents at most `0.45`.

## Disproof track

Prove torsion annihilation for every admissible height pairing, exhibit scalar-related reductions whose non-torsion lifts violate the scalar equation or change under allowed splittings, or show lift/precision/output or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied non-torsion global divisor classes with a known Mordell-Weil relation and frozen Coleman-Gross choices, where bilinearity is independently verified.
- Negative controls: torsion divisor classes, arbitrary pointwise lifts with the same reductions, two valid Hodge splittings, auxiliary divisors of zero pairing, IDEA-004, IDEA-005, IDEA-046, IDEA-119, IDEA-211, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a target-uniform scalar-compatible lift and nonzero frozen height vector of exponent at most `0.45`, exact scalar/source recovery with zero false outputs, invariance under every permitted arithmetic choice, full factor-log rank, blind masked descent, and complete `lambda` and `mu` at most `0.45`.  Torsion-zero heights, dependence on non-homomorphic/source-labelled lifts or unfrozen splittings, unresolved precision, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-264/coleman_gross_torsion_or_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-264/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-264/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-264/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains heuristic and model-bound.  A correct height identity, nonzero value on unrelated lifts, valid relation, recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-264/coleman_gross_torsion_or_lift_theorem.md` proving a nonzero scalar-compatible height polarization or the torsion-zero/non-homomorphic-lift dichotomy.
