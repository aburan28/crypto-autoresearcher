# ECDLP-IDEA-061 — Recillas saturated-Prym realization

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_merged`
- Evidence scale: `toy` geometry preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: semantic merge with ledger `TRANSFER-H008/PO96` and active idea `002`
- Breakthrough claim: **none**; realizing a Prym as a Jacobian is not an ECDLP break.

## Falsifiable hypothesis

After exact `Z[pi]`-Hom saturation of the ledger's hidden Prym block, a Recillas-style
trigonal/tetragonal construction yields an explicit principally polarized Jacobian
`J(Y)`, a complete divisor correspondence from the original `E` subgroup to native
Mumford coordinates on `J(Y)`, and an inverse source lift. Native smooth-divisor
relations and masked target descent on `J(Y)` then have complete time and memory
exponents below `1/2`.

## Mechanism-new operation

The proposed operation was the **explicit Recillas/Torelli realization plus two-way
divisor correspondence**. It would be more than another same-field isogeny only if the
saturated polarization lies in the construction's applicability locus and the inverse
returns factor-base atoms. Semantic review found that the ledger's `TRANSFER-H008`
already asks for exactly an indecomposable principal polarization `J(Y)` with native
divisor arithmetic after PO96 saturation. Naming Recillas does not remove a new obstruction.

## Assumptions

1. The PO96 saturation exists with exact divisibility certificates over the stated field.
2. The saturated principally polarized block lies in a Recillas or ramified-Recillas locus over `F_p`.
3. Both directions of the correspondence are explicit on complete rational divisor charts.
4. The image of `<P>` has a target-independent smoothness law better than its elliptic-factor control.
5. Construction, field extensions, divisor reduction, relation rank, descent, source inversion, and memory are charged.
6. No same-field isogeny, scalar pullback, or relation-only certificate receives mechanism credit.
7. All claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`Hom_saturated_hidden_Prym | Recillas_principal_Jacobian_realization | native_Mumford_divisors | two_way_source_correspondence | smoothness_and_descent`

Collision fingerprint: `TRANSFER_H008 | PO96_saturation | principal_polarized_JY | native_relation_structure`. The operation is already present in the ledger at the same semantic level.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H008`, the exact saturated hidden-`E^2` Prym/principal-polarization hypothesis.
2. `ledger/FINDING-PF-IC-001.md` — imported `PO96`, the explicit saturation problem this record restates.
3. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-054`, which rejects direct principal-polarization descent for the same block.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P063`, the closest verified connected Prym image and Rosati-form control.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H002`, the closest native-cover relation/factorization lane.

## Closest primary literature

- Lange and Ortega, [The trigonal construction in the ramified case](https://doi.org/10.1112/blms.12756), proves a Prym/Jacobian correspondence only on a specified cover locus.
- Carocca, Lange, and Rodriguez, [Etale double covers of cyclic p-gonal covers](https://doi.org/10.1016/j.jalgebra.2019.07.008), gives related Prym/Jacobian decompositions, not ECDLP smoothness or source inversion.
- Agostini, [On the Prym map for cyclic covers of genus two curves](https://arxiv.org/abs/2001.06264), studies the geometric Prym map rather than an algorithmic descent.

These sources bound applicability; none distinguishes the proposal from the ledger's
existing saturated-Prym successor or supplies a below-rho algorithm.

## Complete factor-base-to-target-descent path

1. Reproduce PO96's exact saturated lattice and polarization data.
2. Prove the cover lies in the chosen Recillas applicability locus over `F_p`.
3. Construct `Y`, the principal polarization, and both divisor correspondences.
4. Map target-independent factor atoms and verify every source inverse.
5. Collect native smooth-divisor relations and push them back to verified elliptic relations.
6. Solve and verify factor-base logarithms.
7. Map randomized `Q+[t]P`, perform native individual descent, and invert every divisor source.
8. Recover `x`, remove `t`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let saturation/Recillas setup exponent be `a`, genus
and extension representation exponent `g`, factor-base size `N^beta`, reciprocal native
smoothness and target-descent exponents `delta,delta_t`, divisor-reduction/source-inverse
exponent `kappa`, sparse linear algebra `2beta`, and memory `mu`. Then
`lambda=max(a,g,beta+delta+kappa,2beta,delta_t+kappa)`. The `beta` term charges the
`N^beta` accepted rows needed for factor-base calibration. Fixed-degree geometry can change only
constants; growing degree/genus/field data are charged in `a,g,kappa,mu`. A correct
correspondence with `lambda>=1/2` is a control, not a win.

## Likely fatal obstruction

The available type-`(1,39)` block may not admit the required principal polarization over
the base field or lie in the Recillas locus. Even if it does, the conorm image is an
elliptic isogeny factor whose native divisors have no enhanced smoothness; inverse divisor
lifting can be a full Jacobian decomposition problem. Most decisively for this record,
those are already the ledger's stated `TRANSFER-H008/PO96` questions.

## Proof track

Prove applicability, construct the explicit principal polarization and rational two-way
divisor maps, then establish a source-resolving smoothness and descent theorem with full
cost below rho and BSGS.

## Disproof track

Prove the saturated block is outside the construction locus, show the correspondence is
only a known scalar/isogeny map, show native smoothness matches the elliptic-factor control,
or establish `lambda>=1/2`; semantic identity with `TRANSFER-H008` already rejects this ID.

## Positive and negative controls

- Positive geometry control: a published tiny cover where Recillas reconstructs the expected Jacobian.
- Positive source control: exhaustive divisor maps and inverse points.
- Negative applicability control: matched Pryms outside the trigonal/ramified locus.
- Negative algorithm control: the original elliptic factor and same-field isogeny neighbors.
- Leakage control: no target-selected polarization, hidden scalar basis, or post-hoc smooth divisor.

## Quantitative promotion and falsification gates

No promotion gate is active because the candidate is merged/rejected. If a versioned
successor ever proves a mathematical operation absent from `TRANSFER-H008`, it must first
show zero map/source errors, a statistically distinct native smoothness law on at least
20 curves per size, 1,000 relations, 100 blind descents, and upper 95% complete
`lambda,mu<=0.45`. Applicability failure, scalar-map collapse, or lower 95%
`lambda>=0.50` falsifies the scoped successor; geometry correctness alone does not promote.

## Artifact plan

- Comparison: `ideas/artifacts/ECDLP-IDEA-061/ledger_collision.md`
- Applicability proof, if reopened: `ideas/artifacts/ECDLP-IDEA-061/recillas_applicability.md`
- Maps: `ideas/artifacts/ECDLP-IDEA-061/divisor_maps.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-061/verify_maps.sage`
- Retain saturation matrices, polarizations, cover equations, divisor maps, sources, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected record remains toy, heuristic, model-bound, and novelty-unverified. It
preserves a deduplication decision, not evidence against all Prym transfers. A principal
polarization or correct divisor map is not a breakthrough.

## Exactly one next executable action

1. If the coordinator reopens this lane, first produce `ideas/artifacts/ECDLP-IDEA-061/ledger_collision.md` proving a semantic operation not already required by `TRANSFER-H008/PO96`; otherwise execute nothing.
