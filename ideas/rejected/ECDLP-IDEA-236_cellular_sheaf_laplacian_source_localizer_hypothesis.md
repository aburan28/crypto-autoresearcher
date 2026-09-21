# ECDLP-IDEA-236 — Cellular-sheaf Laplacian source localizer

## Status and claim labels

- Class: `representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_sheaf_restrictions_encode_source_incidence_and_spectrum_aggregates`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a sheaf Laplacian spectrum, harmonic section, or sparsifier is not an ECDLP break.

## Falsifiable hypothesis

The endpoint relation fiber admits a compact cellular sheaf whose restriction maps encode elliptic
addition locally and whose low sheaf-Laplacian modes have canonical localized representatives at the
exact signed factor-base sources.  Spectral localization would then recover relation rows and fresh
masked-target sources below rho and BSGS.

## Mechanism-new operation

The claimed operation is **compile an endpoint cellular sheaf, form its Hodge Laplacian, isolate
source-localized eigensections, and invert their stalk support to exact elliptic points**.  A graph
Laplacian, generic eigensolver, supplied source sheaf, spectral score, rank certificate, or post-hoc
localized basis is a duplicate/control.

## Assumptions

1. Cell complex, stalks, restriction maps, inner products, masks, spectral window, localization rule, and point inverse are public and target-independent.
2. Sheaf representation, matvecs, eigenspaces, and peak state have exponents below `1/2` and do not contain one cell or coordinate per source incidence.
3. Localized sections canonically return all exact signed point sources on every stratum rather than a harmonic span or aggregate cohomology class.
4. Setup, precision, output, relation density, rank, factor logs, blind descent, verification, and memory are fully charged.

## Semantic fingerprint

`endpoint_cellular_sheaf | local_elliptic_restriction_maps | sheaf_hodge_laplacian | canonical_localized_eigensection_point_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the source-fiber generator and transposed join gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the compact structured-coordinate barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the measured public spectral/tensor rank boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the nonlinear phase-feature rank boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.

## Closest primary literature

- Hansen and Ghrist, [Toward a spectral theory of cellular sheaves](https://arxiv.org/abs/1808.01513), develops Hodge Laplacians, spectra, sparsification, and cohomology for a supplied cellular sheaf.
- Curry, [Sheaves, cosheaves and applications](https://arxiv.org/abs/1303.3255), develops cellular sheaf and cosheaf constructions on supplied cell complexes.

Neither source constructs a source-blind elliptic sheaf or proves that a Laplacian eigenspace has a
canonical finite-field point-source basis.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, cell compiler, stalks, restrictions, inner products, spectral rule, point inverse, and verifier.
2. Construct the endpoint sheaf and implicit Laplacian without enumerating source cells or restriction edges.
3. Compute the admitted spectral subspace, canonically localize its sections to every signed point-source tuple, and verify elliptic sums.
4. Collect independent relation rows and solve and independently verify all factor logs.
5. Apply the identical sheaf/Laplacian/source inverse to fresh `Q+[t]P`, retain ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging sheaf state, precision, output, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let sheaf setup time/memory be `N^a,N^a_m`, reciprocal relation and target densities
`N^delta,N^delta_t`, one spectral query plus exact source inverse `N^q,N^q_m`,
independent-rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion
`N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Cells, stalk dimensions, restriction nonzeros, matvecs, precision, eigenvectors, source output, rank
loss, factor logs, masked descent, and verification are charged.  Promotion requires
`lambda,mu<=0.45`.

## Likely fatal obstruction

A cellular sheaf is specified by its cell incidence, stalks, and restriction maps.  Encoding the
elliptic source constraints in those maps supplies the missing point-labelled transition deck.
Removing labels leaves a Laplacian spectrum or harmonic subspace invariant under basis/source
permutations; eigenvectors in a repeated eigenspace are not canonical point atoms.  Localizing them
requires the stalk coordinates or source annotations the method is meant to recover, while a faithful
complex may have one cell per relation incidence.

## Proof track

Construct a sub-rho source-blind cellular sheaf, prove a simple and canonically localized source
spectrum on every stratum, and establish complete `lambda,mu<=0.45`.

## Disproof track

Exhibit source-permuted sheaves with the same spectral data, prove any faithful restriction system
contains explicit source incidences, or show cell, eigenspace, output, ambiguity, or complete exponent
at least `0.50`.

## Positive and negative controls

- Positive control: supplied small cellular sheaves with independently known harmonic sections and localized stalk support.
- Negative controls: basis-conjugated restrictions, isospectral source permutations, constant sheaves, IDEA-001/048/073/132/155/174/218/224, P1421/P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires sheaf state and matvec exponents at most `0.45`, exact all-source recall, zero
false sources, no explicit source-edge deck, full factor-log rank, 100 blind descents at each large
future toy size, and complete `lambda,mu<=0.45`.  Isospectral source collisions, basis dependence,
missed sources, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-236/sheaf_laplacian_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-236/sheaf_spectral_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-236/independent_sheaf_laplacian_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-236/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation hypothesis.  A valid sheaf,
Laplacian, spectrum, cohomology group, sparsifier, toy localization, relation, or toy scalar is not a
generic ECDLP improvement, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-236/sheaf_laplacian_source_theorem.md` proving a source-blind compact sheaf with canonical point-localized modes or an isospectral/source-incidence obstruction.
