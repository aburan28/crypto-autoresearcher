# ECDLP-IDEA-080 — Microlocal characteristic-cycle atomization

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `rejected_characteristic_cycle_collapse`
- Evidence scale: `toy` sheaf/cycle identity only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a characteristic cycle or vanishing-cycle count is not an ECDLP break.

## Falsifiable hypothesis

Let `K_F` be a source-labelled constructible sheaf encoding a factor-base subset and let `K_F^{*m}` be its addition convolution on `E`. For a target `R`, a target-local microlocal specialization of the singular support/characteristic cycle decomposes into components in bijection with the exact factor-base atoms of every valid relation. If the cycle has subquadratic degree and admits an inverse source map, it can emit auditable rows and blind descents below rho.

## Mechanism-new operation

The operation is **microlocal deconvolution: recover source atoms from conormal components of the target-specialized addition convolution**. Trace values, Fourier transforms, stationary-phase counts, support detection, and relation-only characteristic classes are controls. Survival requires a biconditional component-to-source theorem and a constructive inverse.

## Assumptions

1. The factor-base sheaf has a finite public description smaller than an explicit point dictionary of forbidden size.
2. Addition convolution preserves annotations needed to distinguish exact point sources.
3. Characteristic-cycle components at `R` correspond one-to-one with valid source tuples, including multiplicity and sign.
4. Components and inverse source maps can be computed without materializing the full incidence surface.
5. `B=N^beta` independent rows, rank, factor-log solving, target descent, output, and memory are charged.
6. Blind targets use a frozen target-independent sheaf.

## Semantic fingerprint

`factor_base_constructible_sheaf | elliptic_addition_convolution | microlocal_characteristic_cycle | conormal_component_to_exact_atom_inverse | full_relation_and_target_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the closest open algebraic source-fiber generator/target join.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, where exact source-fiber joining remains cubic.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H629`, the closest pre-certificate source-split signal.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H667`, the nearest exact algebraic source/complement construction.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`, the exact pair-advice/triple-source baseline.

## Closest primary literature

- Beilinson, [Constructible sheaves are holonomic](https://arxiv.org/abs/1505.06768), establishes singular support but not source atomization.
- Saito, [The characteristic cycle and the singular support of a constructible sheaf](https://arxiv.org/abs/1510.03018), develops characteristic cycles and index formulas without an elliptic decomposition inverse.
- Katz, [Exponential sums over finite fields and differential equations over the complex numbers: Some interactions](https://doi.org/10.1090/S0273-0979-1990-15922-1), is the nearby trace/sheaf boundary; trace functions alone do not retain source labels.

No checked source gives the claimed component/source biconditional. Novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, coefficient field, sheaf presentation, convolution, annotations, and microlocal specialization.
2. Build `K_F` and compare `K_F^{*m}` against exhaustive source tuples on tiny curves.
3. Compute the target-local characteristic cycle and prove every component maps to exactly one source tuple and vice versa.
4. Emit and verify source-labelled randomized relation rows until full factor-base rank.
5. Solve and verify every factor log.
6. Apply the same specialization to masked blind targets, combine factor logs, unmask, and verify the recovered scalar.

## Full rho/BSGS cost model

Pollard rho time exponent is `1/2`; BSGS time and memory exponents are `1/2`. Let sheaf/convolution setup exponent be `s`, factor-base exponent `beta`, characteristic-cycle degree exponent `c`, per-specialization/inverse exponent `k`, reciprocal relation/target densities `delta,delta_t`, output exponent `o`, linear algebra `ell`, and memory `mu`. Then `lambda=max(s,c,beta+delta+k+o,ell,delta_t+k+o,beta)`. Any cycle/component list equal to all source incidences is charged at its full output exponent.

## Likely fatal obstruction

For the natural factor-base sheaf `K_F=sum_{a in F} delta_a` on smooth `E`, the `m`-fold addition convolution is the sum of skyscrapers `delta_{a_1+...+a_m}`. At a target `R`, its characteristic cycle has the single conormal `T^*_R E` with aggregate witness multiplicity; it cannot split into one conormal component per source tuple. Retaining tuple annotations makes the sheaf rank/cycle data the full incidence table. This is a direct no-go for ordinary characteristic cycles and a collision with the sheaf, stationary-phase, and reporter records `022/044/051/072`.

## Proof track

Construct the annotated sheaf, prove the component/source biconditional and inverse, and bound convolution rank, cycle degree, output, relation density, rank, descent, and memory below rho.

## Disproof track

Exhibit distinct source tuples with the same microlocal component, prove the cycle forgets annotations, or show sheaf rank/cycle degree/output exponent at least `1/2`.

## Positive and negative controls

- Published characteristic-cycle/index identities on low-dimensional sheaves.
- Planted finite maps with source-labelled conormal branches.
- Constant and skyscraper sheaves under addition convolution.
- Trace-function-only and stationary-phase controls.
- Complete exhaustive source tuples on tiny ordinary curves.
- Blind masked targets with no target-chosen sheaf.

## Quantitative promotion and falsification gates

The theorem gate requires zero component/source mismatches on complete charts and a cycle-degree bound strictly below explicit incidence output. A later promotion gate requires at least 1,000 independent rows, 100 blind descents, and upper 95% `c,lambda,mu<=0.45`. Falsify the scoped mechanism if any component has unresolved source multiplicity `>=N^(1/2)` or lower 95% complete exponent is at least `0.50`.

## Artifact plan

- Theorem: `ideas/artifacts/ECDLP-IDEA-080/microlocal_atomization.md`
- Sheaf specification: `ideas/artifacts/ECDLP-IDEA-080/factor_base_sheaf.yaml`
- Prototype: `ideas/artifacts/ECDLP-IDEA-080/characteristic_cycle.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-080/verify_atoms.py`
- Runs: `ideas/artifacts/ECDLP-IDEA-080/runs/<run-id>/`

## Interpretation boundary

This deferred mechanism is toy, heuristic, model-bound, and novelty-unverified. A correct singular support, characteristic cycle, or witness count is not a relation source, target descent, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-080/characteristic_cycle_no_go.md` computing the convolution of factor-base skyscraper sheaves and proving that its target conormal records only aggregate multiplicity unless the full tuple table is retained.
