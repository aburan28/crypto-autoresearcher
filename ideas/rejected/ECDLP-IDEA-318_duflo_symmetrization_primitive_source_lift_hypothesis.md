# ECDLP-IDEA-318 — Duflo-symmetrized primitive-source lift

## Status and claim labels

- Class: `representation_theoretic_transform`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_central_invariants_do_not_select_orbit_points`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Duflo isomorphism, central character, relation, or toy inverse is not an ECDLP break.

## Falsifiable hypothesis

Elliptic source tuples admit a public compact Lie-algebra realization in which the Duflo map converts endpoint invariant polynomials into central operators whose primitive joint spectrum canonically returns exact signed factor points with complete exponents at most `0.45`.

## Mechanism-new operation

The screened operation is **apply the Duflo-corrected symmetrization from invariant polynomials to the enveloping-algebra center, diagonalize the resulting central action, and lift primitive spectral labels to factor points**. The correction factor is a concrete new operation, not a generic eigenvalue solver. Yet central operators are constant on representation/orbit data and do not select vectors or source points; a point-faithful module and weight dictionary already encode the hidden sources. The proposal merges with IDEAs 025, 177, 188, 246, and 273.

## Assumptions

1. A target-independent finite-field Lie algebra, module, and endpoint invariant are constructed without source enumeration.
2. A characteristic-compatible Duflo analogue is defined and computable below rho for the relevant prime fields.
3. Primitive central spectral data distinguish every signed factor point rather than only an orbit or isomorphism class.
4. Module construction, central operators, diagonalization, output, relation density, rank, factor logs, descent, verification, and memory are charged.
5. The identical representation and inverse work for fresh masked targets.

## Semantic fingerprint

`elliptic_source_Lie_realization | Duflo_corrected_symmetrization | enveloping_center_joint_spectrum | primitive_exact_factor_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving feature boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batch source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the aggregate phase/rank versus exact-source gap.
5. `inputs/ledger_inventory.json` — imported `P1479`, whose tested public feature spaces do not contain the factor-log orientation.

## Closest primary literature

- Duflo, [Opérateurs différentiels bi-invariants sur un groupe de Lie](https://www.numdam.org/articles/10.24033/asens.1327/), concerns supplied characteristic-zero Lie structures and bi-invariant/central operators; it does not provide the conjectured characteristic-`p` elliptic source module.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), does not furnish a compact Lie module or central-spectrum-to-point inverse.

No checked source supplies the finite-field realization, point-faithful primitive inverse, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor decks, signs, Lie algebra/module realization, invariant polynomials, Duflo correction, spectral normalization, masks, and verifier.
2. On known-log endpoints, construct central operators without source labels, recover primitive spectral atoms, lift them to exact signed points, and verify relations.
3. Collect independent rows, solve every factor-base logarithm, and independently verify the solution.
4. Reuse the identical module, central action, and lift for fresh `Q+[t]P` targets without a weight-to-point table.
5. Substitute factor logs, remove masks, retain spectral multiplicities and ambiguities, and return scalar candidates.
6. Accept only `[x]P=Q`, charging representation construction, operators, spectra, output, rank, factor logs, descent, verification, and peak memory.

## Full rho/BSGS cost model

For setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one central-spectrum/source inverse `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Module dimension, correction evaluation, central matrices, multiplicities, and point output are included. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

The Duflo map preserves invariant/central information. Central characters identify irreducible representations or coadjoint-orbit data, not a preferred vector or labelled factor tuple. A module whose primitive eigenspaces are one-to-one with factor points contains a point dictionary of factor-base scale or larger; omitting it leaves multiplicity and orbit ambiguity.

## Proof track

Prove a public compact finite-field Lie realization, a valid Duflo analogue, a simple point-faithful central spectrum, canonical all-strata point lift, sufficient rank, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Exhibit different source points with the same central character, show that a point-faithful module materializes the source dictionary, or prove representation/state/output or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied small Lie module with known central characters and externally labelled weights must reproduce those labels.
- Negative: isomorphic modules with basis-permuted source dictionaries must not acquire canonical elliptic point labels.
- Baselines: IDEAs 025/177/188/246/273, P1434, P1479, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an all-strata point-faithful theorem, 1,000 verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if central-character collisions remain, a weight-to-point dictionary is required, or state/output or either exponent reaches `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-318/duflo_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-318/central_character_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-318/independent_duflo_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-318/cost_analysis.md`

## Interpretation boundary

This rejects the specified central-spectrum source lift only. A correct Duflo map, representation, central character, relation, or toy scalar is not generic-prime ECDLP recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-318/duflo_source_theorem.md` proving a compact point-faithful central spectrum or an explicit equal-central-character/different-source collision.
