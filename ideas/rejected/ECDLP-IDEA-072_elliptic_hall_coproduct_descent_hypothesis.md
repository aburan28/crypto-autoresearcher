# ECDLP-IDEA-072 — Elliptic-Hall coproduct descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `rejected_merged`
- Evidence scale: `toy` algebraic-identity derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: categorical collapse into ideas `022/038` and ordinary divisor-splitting enumeration
- Breakthrough claim: **none**; a Hall-algebra identity or decomposition count is not an ECDLP break.

## Falsifiable hypothesis

Factor-base points embedded as length-one torsion sheaves on `E` admit a sparse,
source-labelled elliptic-Hall product. A target Picard/determinant coefficient can be
extracted without enumerating all extensions or all `E(F_p)` classes, and iterated Green
coproducts condition that coefficient to exact factor-base atoms. Relation collection,
factor-log calibration, and masked target descent then have full exponents below `1/2`.

## Mechanism-new operation

The proposed operation was a **sparse source-retaining Hall coefficient oracle with
coproduct self-reduction**. Hall multiplication represents extensions rather than merely
rewriting coordinates; the coproduct would retain extension provenance while determinant
projects a completed atom tuple to its elliptic class.

A formal Hall identity, canonical-basis conversion, determinant-only relation, explicit
extension enumeration, Fourier–Mukai relabeling, or generic shuffle backend is a duplicate/control.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N` and factor base `F` of size `N^beta`.
2. Point sheaves and all Hall structure constants are represented over the finite field without scalar labels.
3. The target determinant/Picard coefficient is extractable without an `N`-entry class dictionary.
4. Coproduct conditioning returns exact atom sources and multiplicities with bounded branching.
5. Basis conversion, extension counting, shuffle support, output, rank, descent, verification, and memory are charged.
6. No target-selected basis, post-hoc support filter, or relation-only determinant receives credit.
7. Claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`point_torsion_sheaves | elliptic_Hall_product | sparse_target_determinant_coefficient | Green_coproduct_source_conditioning | factor_atoms_to_target_descent`

For point torsion sheaves at distinct supports, the relevant extension group vanishes;
the Hall product is the direct sum. Same-support extensions add local partition data,
while determinant forgets it. Coproduct conditioning therefore enumerates the original
atom splittings and merges with ideas `022/038`.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H004`, the closest non-homomorphic cover label that still must preserve source data.
2. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-001`, which closes a representation move without a new relation/decomposition profile.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-002`, which requires target-coupled sparse divisor relations after rank and descent.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H006`, the closest hidden elliptic-factor representation lane.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H629`, the closest source-labelled atom-composition/relation-generation lane.

## Closest primary literature

- Burban and Schiffmann, [On the Hall algebra of an elliptic curve, I](https://arxiv.org/abs/math/0505148), presents the elliptic Hall algebra but no sparse factor-base coefficient algorithm.
- Schiffmann, [On the Hall algebra of an elliptic curve, II](https://arxiv.org/abs/math/0508553), develops its geometric/canonical basis without ECDLP source descent.
- Negut, [The shuffle algebra revisited](https://doi.org/10.1093/imrn/rnt156), supplies shuffle presentations, not bounded support or target coefficient extraction.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the comparison relation family.

No checked source provides the claimed sparse coefficient oracle or atom self-reduction;
novelty and feasibility remain unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, factor base, Hall basis, determinant grading, and coefficient normalization.
2. Map every factor atom to a length-one torsion sheaf with a verified point/source label.
3. Multiply the factor-base generating element and extract coefficients for known random targets.
4. Apply iterated coproduct conditioning until every accepted coefficient yields exact atom sources.
5. Collect verified elliptic relations and solve/verify factor-base logs.
6. Form the same coefficient query for randomized `Q+[t]P`.
7. Coproduct to a source-labelled individual descent and substitute logs.
8. Remove `t` and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let basis/setup exponent be `a`, factor-base size
`N^beta`, coefficient-query exponent `kappa`, reciprocal relation/target densities
`N^delta,N^delta_t`, coproduct branching/output exponent `omega`, basis-conversion
exponent `c`, sparse linear algebra `2beta`, and memory `mu`. Then
`lambda=max(a,c,beta+delta+kappa+omega,2beta,delta_t+kappa+omega,mu)` when one
accepted coefficient emits one usable row; the `N^beta` calibration rows are mandatory.
An `N`-component Picard grading or enumeration of Hall extensions is charged at exponent `1`.

## Likely fatal obstruction

At distinct point supports there are no nontrivial extensions, so Hall multiplication
adds no cross-support relation structure. Hall coefficients otherwise count the same extension objects as divisor decompositions, so their
support can be as large as the original candidate space. Determinant projection forgets
internal sheaf data, while retaining it through coproduct can expand exponentially.
Selecting the coefficient of `Q` may require an `N`-indexed Picard basis whose orientation
is the original DLP.

## Proof track

Construct a finite sparse basis and coefficient oracle, prove coproduct source recovery,
and bound basis conversion, extension support, relation density, rank, target descent,
verification, and memory below rho.

## Disproof track

Prove target coefficient extraction needs `Omega(N^(1/2))` basis/output, determinant loses
source data, coproduct enumerates extensions, or complete `lambda>=1/2`.

## Positive and negative controls

- Positive Hall control: tiny elliptic curves with exhaustively computed Hall products and coproducts.
- Positive source control: planted sparse extension products with known sheaf atoms.
- Negative categorical control: determinant-only and Fourier–Mukai representations.
- Negative support control: matched random extension algebras with the same grading.
- Leakage control: no scalar-indexed Picard table, target-chosen basis, or discarded coproduct branches.

## Quantitative promotion and falsification gates

No promotion gate remains for this categorical formulation. Its historical gate would
have required an exact coefficient oracle and coproduct source theorem whose time,
output, and memory exponents were each below `0.25` on a stated family. A future
preflight requires zero coefficient/source errors, 1,000 relations, 100 blind descents,
and upper 95% `lambda,mu<=0.45`. Falsify if basis, support, or branch lower 95% exponent
is at least `0.50`, or target coefficients require scalar indexing.

## Artifact plan

- Missing theorem: `ideas/artifacts/ECDLP-IDEA-072/sparse_coefficient_oracle.md`
- Hall arithmetic: `ideas/artifacts/ECDLP-IDEA-072/hall_coproduct.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-072/verify_sources.sage`
- Future runs: `ideas/artifacts/ECDLP-IDEA-072/runs/<run-id>/`
- Retain bases, structure constants, products, coproduct branches, determinants, sources, relations, targets, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected hypothesis is toy, heuristic, model-bound, and novelty-unverified. A Hall
identity, sparse count, or correct determinant relation is not a breakthrough.

## Exactly one next executable action

1. Preserve `ideas/artifacts/ECDLP-IDEA-072/sparse_coefficient_oracle.md` as the categorical no-go boundary; do not reopen this lane without a new operation that creates cross-support information before determinant projection.
