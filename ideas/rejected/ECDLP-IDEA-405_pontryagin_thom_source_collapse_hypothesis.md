# ECDLP-IDEA-405 — Pontryagin–Thom source collapse

## Status and claim labels

- Class: `framed_cobordism_source_collapse`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_embedding_and_framing_require_source_fiber_while_stable_class_forgets_occurrence_labels`
- Cohort: `20260718-u`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Thom collapse or framed-cobordism class is not an ECDLP break.

## Falsifiable hypothesis

Each endpoint relation fiber has a public compact framed embedding whose Pontryagin–Thom collapse has a subgate stable representative, and transverse inverse images of a fixed regular value canonically recover exact factor occurrences under every restriction.

## Mechanism-new operation

The screened operation is **embed and frame the source fiber, collapse the complement to a Thom space, manipulate the resulting stable homotopy class, and recover a framed preimage as occurrence-labelled factors**. The proposed primitive is collapse/preimage duality rather than homology, persistence, or a relation-only certificate.

## Assumptions

1. The source fiber, ambient embedding, tubular neighborhood, and framing are endpoint-constructible without source enumeration.
2. Stable representatives remain compact and exact over a finite-field-compatible lift.
3. A fixed regular-value preimage returns occurrence labels, not only a bordism class or signed count.
4. Restrictions update the collapse map without rebuilding a source-sized embedding.
5. Lift, embedding, framing, collapse, transversality, inverse image, output, rank, logs, descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`endpoint_relation_fiber_embedding | framed_normal_bundle | Pontryagin_Thom_collapse_to_Thom_space | regular_preimage_to_factor_occurrences | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; exact existence must return a labelled source.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; aggregate topological classes need a typed inverse.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; occurrence labels and restrictions remain charged.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; lossless ancestry cannot be hidden in collapse state.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-labelled embedding data cross the explicit-source boundary.

## Closest primary literature

- Thom, [Quelques propriétés globales des variétés différentiables](https://doi.org/10.1007/BF02566923), relates cobordism to homotopy of Thom spaces through supplied smooth embeddings and normal data.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies algebraic finite fibers without a public framed embedding or point inverse.

No checked source supplies the proposed finite-field-compatible collapse and occurrence inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, compactification, ambient space, embedding, framing, collapse convention, restrictions, and verifier.
2. Build the target-independent framed collapse state within `B^(9/4+o(1))` without listing source points or normal fibers.
3. For known-log targets, apply restricted collapse data, choose the frozen regular value, recover every preimage branch to one labelled tuple, and verify its sum.
4. Collect at least `B` independent verified rows, charging empty preimages, perturbations, ambiguity, output, and dependent rows; solve factor logs.
5. Reuse the unchanged collapse construction on fresh scalar-blind `Q+[t]P` targets.
6. Substitute factor logs, remove `t`, retain all framing/transversality branches, and verify `[x]P=Q`.
7. Charge lift, embedding, framing, collapse, inverse image, output, rank, logs, descent, verification, bit time, and peak memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

With `0<=r<=o`, setup/state must be at most `B^(9/4+o(1))`, a complete fresh restricted query at most `B^(5/4+o(1))`, and promotion needs `lambda<=0.45` and `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Pontryagin–Thom begins with a supplied embedded framed source manifold. For a finite relation fiber, constructing the zero-dimensional embedding already identifies its points. Stable homotopy retains a framed bordism class or signed aggregate, not canonical occurrence labels; point-faithful framing data rematerialize the source. This meets IDEAs 080, 126, 181, 220, 234, 249, 298, and 300 at the class-versus-point boundary.

## Proof track

Construct a compact endpoint-only framed embedding, prove exact restriction-stable collapse/preimage biconditionality, and certify `lambda,mu<=0.45`.

## Disproof track

Exhibit framed-bordant fibers with different labelled points, show embedding/framing construction enumerates the fiber, or prove state/inverse cost above the caps.

## Positive and negative controls

- Positive: supplied framed zero-manifolds and embeddings with planted preimages must replay collapse and inverse image.
- Negative: relabelled framed point sets with the same stable class, cancelling signed points, altered framings, all signed strata, restrictions, and blind targets.
- Baselines: IDEAs 080/126/181/220/234/249/298/300, explicit point embeddings, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only embedding/framing, exact occurrence preimage, `1,000` independent rows, `100` blind descents, caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing embedding datum, equal-class/different-source pair, cancellation, cap violation, or either exponent at least `0.50`.
- A correct toy Thom collapse is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-405/thom_collapse_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-405/framed_bordism_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-405/restricted_preimage_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-405/cost_analysis.md`

## Interpretation boundary

This rejects the screened elliptic collapse route, not Pontryagin–Thom theory. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; a stable-class calculation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-405/thom_collapse_source_obligations.md` and classify each embedding, framing, collapse, regular-value, and inverse-preimage datum by endpoint versus source dependence.
