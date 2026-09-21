# ECDLP-IDEA-239 — Box-spline Todd source deconvolution

## Status and claim labels

- Class: `geometric_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_lattice_directions_and_samples_encode_source_enumerator`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a box-spline inversion identity or lattice multiplicity formula is not an ECDLP break.

## Falsifiable hypothesis

Generic signed elliptic addition fibers admit a scalar-blind, totally unimodular lattice lift whose
endpoint multiplicity function is a semidiscrete convolution with a compact box spline.  Applying a
Todd differential operator would deconvolve that function into lattice atoms that canonically lift
to exact factor points for relations and fresh masked-target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-to-unimodular lattice lifting, box-spline convolution modeling,
Todd-operator deconvolution, and lattice-atom-to-elliptic-source return**.  A supplied source lattice,
explicit large-prime table, dense resultant, generic interpolation, Barvinok counter, parameter
change, or post-hoc atom selector is a duplicate or control.

## Assumptions

1. `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, masks, lift lattice, and direction list are target-independent and scalar-blind.
2. The lift respects elliptic addition and finite-field wraparound on every stratum without source-labelled directions or one lattice cell per tuple.
3. Required box-spline samples, Todd order, precision, chamber decomposition, atoms, and return map all have exponent below `1/2`.
4. Source output, relation density, rank loss, factor logs, masked descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`elliptic_endpoint_scalar_blind_lattice_lift | unimodular_box_spline_convolution | todd_operator_deconvolution | canonical_lattice_atoms_to_exact_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the open endpoint source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the closed bounded-source coordinate reconstruction hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the symmetry-compression no-promotion boundary.
4. `inputs/ledger_inventory.json` — imported `P1477`, the compact-state payload question.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact local composition and dense-payload boundary.

## Closest primary literature

- De Concini, Procesi, and Vergne, [Box splines and the equivariant index theorem](https://arxiv.org/abs/1012.1049), relates Todd-class operations to deconvolution of semidiscrete box-spline convolution.
- Lenz, [Lattice points in polytopes, box splines, and Todd operators](https://arxiv.org/abs/1305.2784), gives lattice-point recovery formulas under supplied lattice and list-of-vectors hypotheses.

Neither source supplies a scalar-blind lattice lift of elliptic addition, endpoint box-spline samples,
or an inverse from recovered lattice multiplicities to exact factor points.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, lattice lift, direction vectors, chambers, box spline, Todd truncation, atom-to-point map, and verifier.
2. Lift each known-log endpoint and compute the required box-spline samples without enumerating signed point sources or source-labelled lattice directions.
3. Apply the Todd deconvolution, recover every lattice atom, map atoms to exact signed factor-base tuples, and verify elliptic sums.
4. Collect independent rows, solve all factor logs, and independently verify rank and logs.
5. Apply the identical lift, sampling, deconvolution, and atom inverse to fresh `Q+[t]P`, preserve all ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging chambers, samples, differential order, atoms, failed endpoints, rank loss, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let lattice/chamber setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one sampling/deconvolution/source inverse `N^q,N^q_m`,
independent-rank gain `N^r`, atom output and ambiguity `N^o,N^u`, and factor-log
completion `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Lift dimension, direction list, chambers, samples, coefficient bit lengths, Todd terms, lattice
atoms, point returns, relation rows, factor logs, target retries, verification, and peak state are
charged.  Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Box-spline inversion assumes a supplied lattice and direction multiset.  No scalar-blind,
totally unimodular linearization of generic elliptic addition is known; elliptic addition is rational
with exceptional strata and finite-field wraparound.  Choosing directions indexed by factor points,
or supplying multiplicity samples at the resolution needed to isolate atoms, encodes the source
enumerator.  Deconvolution returns multiplicities in the supplied lattice, not canonical elliptic
point labels, and the chamber/sample count can be as large as the original fiber.

## Proof track

Construct a target-independent sub-rho unimodular lift, prove exact all-strata box-spline
convolution and a canonical atom-to-point inverse, and establish complete `lambda,mu<=0.45`.

## Disproof track

Prove any faithful direction list or sample oracle factors through explicit sources, exhibit two
elliptic fibers with the same lifted multiplicity data but different point labels, or show dimension,
chambers, samples, atoms, ambiguity, or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: published unimodular vector lists with independently enumerated box-spline samples and lattice atoms.
- Negative controls: source-labelled directions, non-unimodular and wraparound lifts, IDEA-029/059/081, P1434, P1477/P1478, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an endpoint-only lift and sample oracle of exponent at most `0.45`, exact atom
and point recall with zero false sources, no source-labelled direction list, full factor-log rank, 100
blind descents at each of two largest future toy sizes, and complete `lambda,mu<=0.45`.  Failure of
unimodularity/all-strata correctness, source leakage, sample/output exponent at least `0.50`, or
complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-239/box_spline_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-239/lattice_deconvolution_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-239/independent_todd_deconvolution_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-239/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk hypothesis.  A correct lattice lift,
box-spline identity, Todd inversion, recovered toy atom, valid relation, or toy scalar is not a
complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-239/box_spline_source_lift_theorem.md` proving an endpoint-only unimodular lift and sample oracle or a direction/sample source-leakage no-go.
