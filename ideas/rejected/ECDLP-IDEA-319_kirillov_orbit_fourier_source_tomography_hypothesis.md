# ECDLP-IDEA-319 — Kirillov-orbit Fourier source tomography

## Status and claim labels

- Class: `representation_theoretic_transform`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_orbit_character_is_aggregate_and_source_realization_is_supplied`
- Cohort: `20260718-n`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none; no contract was approved or dispatched
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an orbit-method character identity, relation, or toy spectral inversion is not an ECDLP break.

## Falsifiable hypothesis

A target-independent nilpotent-group realization of the relation fiber has Kirillov characters whose finite Fourier inversion separates exact signed factor points with sub-rho construction, state, output, relation collection, factor-log recovery, and blind target descent.

## Mechanism-new operation

The screened operation is **map endpoint data to a nilpotent representation, identify its coadjoint orbit, Fourier-invert the Kirillov character distribution, and lift isolated orbit atoms to exact factor points**. This is distinct at the operation level from ordinary heavy Fourier coefficients or Whittaker multiplicity-one. However the orbit method classifies representations from supplied Lie/coadjoint data; its character integrates over an orbit and does not name point vectors. A source-faithful orbit realization or polarization imports the source deck. It merges with IDEAs 048, 101, 153, 291, and 299.

## Assumptions

1. Public curve and endpoint data define a compact finite nilpotent group/Lie algebra and scalar-blind source realization.
2. Kirillov correspondence and a computable character formula hold in the relevant finite-field characteristic and size regime.
3. Fourier inversion yields point-labelled factor atoms rather than only an orbit measure, representation, or conjugacy class.
4. Realization, orbit enumeration, polarization, Fourier work, output, relation density, rank, factor logs, descent, verification, and memory are charged.
5. The same realization and inverse apply to fresh masked targets without a source dictionary.

## Semantic fingerprint

`elliptic_endpoint_nilpotent_realization | Kirillov_coadjoint_orbit | character_Fourier_inversion | exact_factor_atom_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact source-resolving feature boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the transposed target/source-return boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the tested full phase-rank boundary.
5. `inputs/ledger_inventory.json` — imported `P1479`, the failure of public low-dimensional feature spaces to orient factor logs.

## Closest primary literature

- Kirillov, [Unitary representations of nilpotent Lie groups](https://doi.org/10.1070/RM1962v017n04ABEH004118), treats supplied connected nilpotent Lie groups and coadjoint orbits; it does not establish the conjectured finite-field or finite-group realization.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), gives endpoint equations without a nilpotent realization, orbit polarization, or point inverse.

No checked source constructs the required finite-field source-blind orbit object, exact factor-point lift, or complete sub-rho descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor decks, signs, nilpotent group/Lie object, orbit convention, polarization, character evaluation, masks, and verifier.
2. For known-log endpoints, build the realization without sources, Fourier-invert characters, return exact signed factor points, and verify every relation.
3. Collect independent rows, solve all factor-base logs, and independently verify them.
4. Reuse the identical realization, character family, and point lift on fresh `Q+[t]P` targets without orbit-to-point advice.
5. Substitute factor logs, remove masks, retain orbit and polarization ambiguity, and return all scalar candidates.
6. Accept only `[x]P=Q`, charging realization, orbit/character work, Fourier state, output, rank, factor logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one orbit-character/source inverse `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Orbit size, polarization, all character samples, Fourier inversion, and exact point outputs are charged. Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Kirillov characters are orbit aggregates. Fourier inversion can reconstruct a supplied orbit measure or representation, but exact source vectors remain unidentified up to orbit, polarization, conjugacy, and basis choices. A realization in which orbit atoms are already factor points contains a source-labelled coadjoint dictionary, while a source-free realization loses the required exact point return.

## Proof track

Prove a public finite nilpotent realization, applicable orbit correspondence, compact character evaluation, canonical all-strata factor lift, sufficient independent rank, reusable factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Exhibit equal characters with different point-labelled sources, show that polarization or orbit construction imports the source deck, or prove state/output or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied finite nilpotent group with known orbit/representation pairs must reproduce its character table and externally labelled orbit atoms.
- Negative: conjugate/basis-permuted realizations with equal characters must not produce preferred elliptic points.
- Baselines: IDEAs 048/101/153/291/299, P1434, P1479, finite Fourier transform, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata exact point return, 1,000 verified rows and 100 blind descents per large future toy size, and both complete exponents at most `0.45`.
- Falsify if the realization or polarization names sources, if equal-character source collisions exist, or if state/output or either exponent reaches `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-319/kirillov_source_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-319/orbit_character_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-319/independent_kirillov_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-319/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of the stated orbit-character source lift, not a no-go theorem for the orbit method. Character correctness, a relation, or toy source recovery is not a generic ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-319/kirillov_source_theorem.md` proving a source-free point-faithful orbit inversion or an equal-character/different-factor-source collision.
