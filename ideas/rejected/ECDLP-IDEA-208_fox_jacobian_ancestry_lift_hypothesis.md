# ECDLP-IDEA-208 — Fox-Jacobian ancestry lift

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_fox_derivative_requires_source_relator_and_abelianizes`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Fox identity, sparse derivative, or valid relator is not an ECDLP break.

## Falsifiable hypothesis

Elliptic addition admits a public bounded nonabelian lift in which each endpoint has a compact relator and Fox derivatives of that relator give sparse signed leaf coefficients. An exact inverse maps derivative terms to factor points, enabling full relation collection and masked target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **nonabelian endpoint relator lifting followed by Fox free differentiation and leaf inversion**. The current version is merged/rejected: constructing a short endpoint relator is already the source witness, while abelian or cyclic specialization collapses Fox derivatives to augmentation/geometric sums that retain aggregate coefficients but not labelled ancestry.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>`, factor base `F` of size `B=N^beta`, and target are frozen.
2. A target-independent bounded presentation and endpoint relator compiler exist without source words.
3. Fox derivatives are sparse and biconditional with all exact signed factor leaves.
4. Relator normalization, word length, coefficient growth, inverse labels, output, rank, factor logs, descent, and memory are charged.
5. A supplied source word, lossless ancestry DAG, or post-hoc relator selection is forbidden.

## Semantic fingerprint

`elliptic_addition_nonabelian_lift | endpoint_compact_relator | Fox_free_derivative | sparse_leaf_coefficients | exact_factor_word_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the exact ancestry edge floor.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the implicit coordinate/source representation hypothesis.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the missing arithmetic source-fiber generator.
4. `inputs/ledger_inventory.json` — imported `P1434`, the open public source-fiber generator question.
5. `inputs/ledger_inventory.json` — imported `P1477`, where source-faithful serial state polynomials become dense.

## Closest primary literature

- Fox, [Free differential calculus I: Derivation in the free group ring](https://doi.org/10.2307/1969736), supplies the derivative identity for a supplied group word.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relations but not a nonabelian relator compiler.

No checked source gives the proposed public lift, compact relator, and exact point inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the presentation, generator-to-point map, relator normal form, Fox decoder, masks, and verifier.
2. Prove that every accepted endpoint has a compact relator and that its derivatives are source-biconditional.
3. Compile relators for known endpoints without source words or a provenance DAG.
4. Differentiate, recover every signed factor leaf and multiplicity, and independently verify each elliptic row.
5. Collect at least `B+sigma` independent rows while charging word and derivative output.
6. Solve and verify factor-base logarithms.
7. Compile and differentiate fresh masked targets `Q+[r]P` under the identical grammar.
8. Substitute logs, subtract `r`, preserve ambiguity, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, relator compilation plus exact derivative inverse `N^q,N^q_m`, independent row gain `N^r`, word/output and ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both time and memory exponents must be at most `0.45`; treating the relator or source word as input invalidates the model.

## Likely fatal obstruction

Fox calculus differentiates a supplied word; it does not construct that word from an abelian endpoint. Any lift faithful enough to retain factor identities must encode the source path. Projecting to the prime cyclic group makes all generators commute and reduces the derivatives to aggregate exponent sums, erasing ancestry.

## Proof track

Construct a bounded nonabelian lift and source-free relator compiler, prove exact all-strata derivative inversion, and derive complete sub-rho time and memory through blind descent.

## Disproof track

Show any endpoint relator compiler outputs a source witness, prove abelianization identifies distinct source words with identical Fox data, lower-bound word/derivative traffic by `B^3`, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied free-group relators with planted leaf words and independently checked Fox derivatives.
- Negative control: distinct relators with the same abelianized derivative vector.
- Negative control: explicit provenance DAGs, augmentation ideals, generic word solvers, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires a relator compiler and inverse of state at most `B^2.25`, query at most `B^1.25`, 100% leaf recall, zero false leaves, post-aggregation rank `B`, and `lambda,mu<=0.45`. A supplied source word, abelian collision, one missing leaf, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-208/fox_relator_compiler_theorem.md`
- Prospective collision family: `ideas/artifacts/ECDLP-IDEA-208/abelianized_derivative_collisions.json`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-208/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/rejected mechanism analysis. Finite checks would be toy and scaling heuristic and model-bound. A derivative identity, sparse word, or valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-208/fox_relator_compiler_theorem.md` proving a source-free bounded relator compiler or an abelianized Fox-data collision for the generic signed two-plus-three elliptic relation.
