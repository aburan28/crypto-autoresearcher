# ECDLP-IDEA-269 — Mordell-Weil sieve target return

## Status and claim labels

- Class: `global_arithmetic_transfer`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_scalar_compatible_global_lift_and_sieve_state_unsupplied`
- Cohort: `20260718-j`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a local sieve exclusion, a global point, a valid relation, a recovered tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A canonical target-uniform lift of the finite-field ECDLP instance to a curve and Mordell-Weil subgroup over a global field preserves the unknown scalar.  Intersecting its reductions at many auxiliary primes via a Mordell-Weil sieve would isolate the scalar or exact source divisor with total time and memory below rho and BSGS.

## Mechanism-new operation

The screened operation is **lift the finite subgroup and target to a global Mordell-Weil lattice, intersect scalar/source residue classes across auxiliary reductions, and return the unique finite-field scalar or factor tuple**.  Mordell-Weil sieves assume a global curve, a known finite-index Mordell-Weil subgroup, and computable local images.  P1543-R1 proves that the canonical finite-etale/Teichmuller scalar-compatible lift exists, but it is torsion and height-zero; arbitrary non-torsion coordinate lifts carry a nonlinear formal-kernel defect, while encoding a useful positive-height/free-Mordell-Weil lift, its joint defect decoder, or enough residue classes can contain the original discrete log.  This merges with IDEA-005 global height compression, IDEA-026 Kummer cocycles, IDEA-037 generalized-Jacobian dithering, IDEA-045 shifted leakage, and IDEA-264 p-adic height polarization after global-lift compatibility and sieve state are charged.

## Assumptions

1. Public `E/F_p,P,Q,N` has a deterministic global model and points `tilde P,tilde Q` satisfying `tilde Q=[x]tilde P` without knowing `x`.
2. A finite-index Mordell-Weil subgroup, saturation data, reduction maps, and local images are computable below rho.
3. The intersection of local conditions isolates exact scalar/source classes with sub-rho modulus, state, and ambiguity.
4. Global model search, heights, generators, saturation, all primes, residue classes, output, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | scalar_compatible_global_lift | Mordell_Weil_subgroup | auxiliary_prime_sieve_intersection | exact_scalar_or_source_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the scalar-coordinate and orientation barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the lift/transfer compatibility boundary.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-044`, the ordinary transfer-output and cost negative.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-lift boundary.

## Closest primary literature

- Bruin and Stoll, [The Mordell-Weil sieve: proving non-existence of rational points on curves](https://doi.org/10.1112/S1461157009000187), uses a known global Mordell-Weil subgroup and local images to constrain rational points.
- Kim, [The unipotent Albanese map and Selmer varieties for curves](https://arxiv.org/abs/math/0510441), supplies a different global-to-local point constraint but no scalar-compatible lift of a generic finite-field ECDLP.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations.

No checked source provides the lift or complete sub-rho return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, global lifting rule, Mordell-Weil basis rule, auxiliary primes, local images, masks, and verifier.
2. Construct the global curve, scalar-compatible lifts, finite-index subgroup, saturation certificate, and height bounds without target advice.
3. For known-log endpoints, intersect local reduction images and map every surviving global class to exact signed finite-field factor points.
4. Verify relations, collect full-rank rows, solve factor logs, and verify each log.
5. Lift fresh masked targets `Q+[t]P` with the identical rule and run the same frozen sieve.
6. Retain every surviving residue/global branch, return finite-field factor points or scalar residues, and charge the full modulus/state.
7. Remove masks and accept only `[x]P=Q`, preserving complete cost receipts.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one lift/sieve/exact inverse cost `N^q,N^q_m`, independent-rank gain be `N^r`, output and ambiguity be `N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every global coefficient, generator, saturation step, height bit, auxiliary prime, local image, CRT residue, failed lift, source branch, factor log, verification, and live byte is charged.

## Likely fatal obstruction

Reduction from a global Mordell-Weil relation to the finite field is easy.  The canonical reverse section preserving the unknown prime-order scalar is the torsion/Teichmuller section, which has height zero and reproduces the original order-`N` relation problem.  Every non-torsion section adds a formal-kernel defect; computing its coordinates in a fully oriented Mordell-Weil basis is already the reduced multigenerator preimage problem.  Even granting such a section, enough local intersections to isolate one of `N` classes require cumulative information/state commensurate with the hidden scalar unless a compact joint finite-and-defect decoder is supplied.

## Proof track

Construct a target-uniform useful non-torsion global section, a sub-rho Mordell-Weil basis/saturation procedure, and a compact joint finite-and-defect intersection returning exact sources with both complete exponents at most `0.45`.

## Disproof track

Show the only scalar-compatible canonical section is the height-zero torsion lift, show every non-torsion section has an uncontrolled formal defect or requires the original reduced preimage, prove sieve state/output at least `N^0.50`, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied global curve, Mordell-Weil basis, and known compatible reduction/lift pair.
- Negative controls: coefficient-wise lifts, incompatible global points, incomplete subgroup saturation, random local residues, IDEA-005, IDEA-264, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a useful positive-height/free-Mordell-Weil global lift with a compact joint finite-and-defect decoder, certified subgroup and sieve of exponent at most `0.45`, exact all-strata return, full factor-log rank, blind descent, and complete `lambda,mu<=0.45`.  A height-zero torsion-only lift, uncontrolled formal defect, scalar-labelled global data, residue state/output at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-269/mordell_weil_sieve_return_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-269/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-269/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-269/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative global-transfer proposal.  Every finite check would be toy and projections heuristic and model-bound.  A successful local sieve or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-269/mordell_weil_sieve_return_theorem.md` proving a useful non-torsion global lift with a compact joint defect decoder and compressed sieve, or the torsion/defect/state obstruction.
