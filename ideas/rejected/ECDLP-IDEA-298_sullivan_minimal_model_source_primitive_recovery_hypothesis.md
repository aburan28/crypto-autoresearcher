# ECDLP-IDEA-298 — Sullivan minimal-model source-primitive recovery

## Status and claim labels

- Class: `topological_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_rational_minimal_model_kills_prime_torsion_and_point_labels`
- Cohort: `20260718-l`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a minimal model, rational homotopy primitive, valid relation, or toy atom is not an ECDLP break.

## Falsifiable hypothesis

The endpoint source-fiber configuration space has a compact Sullivan minimal model whose indecomposable generators are canonically labelled by exact factor points, allowing source recovery, factor logs, and blind descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **construct a configuration space for the endpoint fiber, form its Sullivan minimal commutative differential graded algebra, extract primitive/indecomposable generators, and map them to exact factor points**. Sullivan models recover rational homotopy data of a supplied space. Rationalization kills finite prime torsion. A finite discrete m-point space still has H^0 isomorphic to Q^m and therefore retains its component count, but its primitive idempotents carry no canonical elliptic factor labels and are only identified up to permutation without external marking. An integral, etale, or point-faithful replacement that restores those labels carries the source deck. The operation merges with IDEAs 021, 069, 114, 176, 181, and 251 after space construction and exact point return are charged.

## Assumptions

1. A target-uniform endpoint-only configuration space is constructible without enumerating source tuples.
2. A sub-rho minimal model retains finite prime-order and point-label information despite rationalization.
3. Indecomposables lift canonically to every exact signed factor tuple and exceptional stratum.
4. Space/cell construction, DGA dimension, differential, minimization, primitives, output, rows, logs, descent, and memory are charged.

## Semantic fingerprint

`endpoint_source_configuration_space | Sullivan_minimal_CDGA | rational_homotopy_primitives | exact_factor_return | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source configuration generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the target-local exact-return obligation.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the generator and source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the exact materialized source complex control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate invariant without source labels.

## Closest primary literature

- Sullivan, [Infinitesimal computations in topology](https://doi.org/10.1007/BF02684341), constructs rational minimal-model methods for supplied spaces.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives x-coordinate relation equations; it does not supply signed or ordered factor labels.

No checked source canonically labels rational components by exact elliptic factors or constructs the required configuration space without the source deck; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, configuration-space functor, CDGA model, primitive decoder, masks, and verifier.
2. Construct spaces/models for known-log endpoints without enumerating or naming source tuples.
3. Minimize the DGA, extract every accepted primitive, and return exact signed factor points.
4. Verify rows, collect independent rank, solve and verify factor logs.
5. Apply the identical space/model pipeline to fresh masked targets `Q+[t]P`.
6. Preserve model-equivalence and primitive ambiguity, substitute logs, and remove masks.
7. Accept only exact `[x]P=Q`, charging cells, generators, differentials, reductions, primitives, outputs, rows, logs, descent, and memory.

## Full rho/BSGS cost model

Let setup be `N^a,N^a_m`, factor base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one model/primitive/inverse attempt `N^q,N^q_m`, rank gain `N^r`, output `N^o`, model ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `q` includes the named operation, exact inverse, and independent verification; `o` includes every enumerated relation branch; `u` is only residual scalar ambiguity in target descent.

Peak memory is included in `mu`; no table, representation, certificate, or output stream is free.

Pollard rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`. Every cell, generator, differential entry, homotopy operation, primitive, factor output, and live byte is charged.

## Likely fatal obstruction

A finite discrete m-point source fiber retains H^0=Q^m and its component count, while prime-order torsion vanishes under rationalization. The primitive component idempotents do not come with a canonical endpoint-derived bijection to signed elliptic factor tuples; relabelling the points permutes them. Building a connected configuration with point-labelled cells imports the source list. Replacing rational models by integral or etale data recovers fidelity only by carrying the same torsion and point deck the method sought to avoid.

## Proof track

Construct a compact endpoint-only model retaining prime torsion and labels, prove primitive-to-factor biconditionality, and certify complete exponents at most `0.45`.

## Disproof track

Prove rationalization kills the relevant information, exhibit point-permutation invariance, show faithful model/output state at least `N^0.50`, or derive either exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small nilpotent space with known Sullivan model and rational homotopy primitives.
- Negative controls: finite discrete sets with permuted unmarked H^0 idempotents, torsion-only spaces, source-labelled cell complexes, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires endpoint-only prime-torsion/label fidelity, exact all-source return, verified logs, blind descent, and `lambda,mu<=0.45`. Rational collapse, source-labelled cells, state/output at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-298/sullivan_source_primitive_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-298/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-298/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-298/cost_analysis.md`

All paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This novelty-unverified merged topological proposal is toy-only if instantiated; extrapolations remain heuristic and model-bound. Correct rational homotopy or a toy primitive is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-298/sullivan_source_primitive_theorem.md` proving a compact torsion-faithful primitive inverse or the rationalization/source-deck obstruction.
