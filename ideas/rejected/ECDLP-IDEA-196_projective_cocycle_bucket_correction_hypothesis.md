# ECDLP-IDEA-196 — Projective-cocycle bucket correction

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_cocycle_is_coboundary_or_n_torsion_orientation`
- Cohort: `20260718-d`
- Evidence scale: literature and theorem audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective finite evidence is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a nonzero cocycle or corrected merge is not an ECDLP break.

## Falsifiable hypothesis

An efficiently evaluable finite-algebra two-cocycle attached to Kummer pair labels makes generalized-birthday merges compose projectively rather than through a forbidden proper quotient. Its phase correction preserves exact source replay and changes support density enough to complete relation collection and masked descent below rho and BSGS.

## Mechanism-new operation

The operation is **projective label composition with a public two-cocycle and exact coboundary-aware source replay**. It attempts to escape P1523's ordinary congruence theorem. However, for coefficients of order coprime to the prime subgroup order, the extension splits and the cocycle is a relabeling; useful `N`-torsion coefficients require the same costly orientation/torsion data as theta, pairing, and nilpotent-central-extension lanes. List restriction restores an explicit pair table.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of order `N`, `F` of size `B=N^beta`, and target are fixed.
2. A finite coefficient algebra and normalized cocycle are constructed without scalar logs or an `N`-torsion field of super-rho size.
3. Corrected labels change admissible support rather than only rephase identical merges.
4. Every corrected path returns all exact signed sources and exceptional strata.
5. Setup, list growth, coefficients, output, rank, descent, verification, and memory are charged.

## Semantic fingerprint

`Kummer_pair_labels | public_projective_two_cocycle | support_changing_corrected_merge | exact_coboundary_source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1475`, the residual-character bucket control.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, where stable-deck transitions do not compress.
3. `inputs/ledger_inventory.json` — imported `ISO-SP-001`, the self-pairing torsion-information lane.
4. `inputs/ledger_inventory.json` — imported `TRANSFER-H004`, a transfer-orientation hypothesis.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1401`, the scalar-orientation negative boundary.

## Closest primary literature

- Eilenberg and Mac Lane, [Cohomology theory in abstract groups I](https://doi.org/10.2307/1969215), classifies extension/cocycle data but gives no elliptic support router.
- Boneh and Silverberg, [Applications of multilinear forms to cryptography](https://eprint.iacr.org/2002/080), supplies the multilinear/self-pairing control rather than a generic return map.
- Shoup, [Lower bounds for discrete logarithms](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison boundary.

No checked source provides the proposed correction; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze coefficient algebra, cocycle normalization, labels, merge tree, charts, masks, and verifier.
2. Prove nontriviality, public evaluability, support change, and exact replay without scalar orientation.
3. Route known-log endpoints through corrected buckets and verify all emitted sources.
4. Preserve failed merges, list sizes, cocycle branches, signs, repeats, infinity, and multiplicity.
5. Collect full-rank rows, solve and verify factor-base logs.
6. Route fresh `Q+[r]P` masks with the same correction.
7. Substitute logs, subtract masks, retain ambiguities, and verify `[x]P=Q`.
8. Charge all setup, attempts, rank, factor-log, descent, output, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup be `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, corrected query `N^q,N^q_m`, ranked rows/query `N^r`, output/ambiguity `o,u`, and linear algebra `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; cocycle nontriviality alone has no cost significance.

## Likely fatal obstruction

For a cyclic prime-order group and coefficient module with invertible `N`, averaging kills higher cohomology, so the two-cocycle is a coboundary and only relabels merges. Coefficients retaining `N`-torsion require order-`N` representation/torsion data or a multiplicative-group DLP. Restricting the cocycle to the factor-base list makes evaluation a `B^2` source table.

## Proof track

Construct a non-split public coefficient module, prove the cocycle changes support and is not scalar-oriented, prove exact source replay, and derive `lambda,mu<=0.45`.

## Disproof track

Exhibit an explicit coboundary, prove cohomology vanishes for the admitted coefficients, lower-bound the torsion representation or field by `N^(1/2)`, or show list evaluation needs `Omega(B^2)` advice and complete cost at least rho.

## Positive and negative controls

- Positive control: manufactured projective representations with supplied nontrivial cocycles.
- Negative control: explicit coboundaries, ordinary quotient labels, theta/Heisenberg representations, and Hilbert-symbol values requiring exponent extraction.
- Negative control: source-indexed pair tables, rho, BSGS, known-log endpoints, and blind masks.

## Quantitative promotion and falsification gates

This version is merged/rejected. A successor requires a public non-split cocycle, measurable support-law change, exact all-strata replay, no order-`N` hidden orientation, no `B^2` table, and `lambda,mu<=0.45`. A coboundary, relocated field DLP, one missed source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective cohomology gate: `ideas/artifacts/ECDLP-IDEA-196/cocycle_nontriviality_gate.md`
- Prospective source-replay specification: `ideas/artifacts/ECDLP-IDEA-196/projective_source_replay_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-196/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified mechanism analysis. Any finite test is toy and any scaling inference heuristic and model-bound. A cocycle, projective identity, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-196/cocycle_nontriviality_gate.md` classifying the admitted coefficient modules and proving either a non-split public support-changing cocycle with exact replay or that every admissible cocycle is a coboundary/orientation relocation.
