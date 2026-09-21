# ECDLP-IDEA-225 — Jones planar-algebra source factorization

## Status and claim labels

- Class: `composition`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_planar_contraction_consumes_boundary_source_labels`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a planar identity, finite-depth evaluation, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

Elliptic addition admits a finite-depth planar algebra whose boundary colours are public factor atoms and whose annular/jellyfish normal form contracts an endpoint tangle to a bounded source-separating expansion. Conditioning the expansion would return exact signed factors for relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **finite-depth planar contraction followed by conditioned boundary-source factorization**. It merges/rejects with IDEA-050 matchgates, IDEA-102 Yang–Baxter transfer, IDEA-108 skein traces, and IDEA-213 dimers unless a new elliptic planar identity changes the support law. A planar algebra acts on supplied labelled boundary boxes; erasing them yields aggregate traces, while retaining them stores the source tensor.

## Assumptions

1. Public `E/F_p`, prime-order subgroup, factor base `F` of size `B=N^beta`, planar generators, relations, and endpoint tangle are frozen.
2. The planar algebra has bounded depth/dimension independent of source enumeration and no source-labelled tensor of size `B^m`.
3. Normal-form coefficients invert canonically to every exact signed point and multiplicity.
4. Algebra construction, contractions, boundary state, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_addition_planar_algebra | endpoint_annular_tangle | finite_depth_jellyfish_reduction | conditioned_boundary_exact_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the endpoint-to-source compiler gap.
2. `inputs/ledger_inventory.json` — imported `P1477`, the dense backward serial-state control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry floor.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge floor.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact one-transition/dense-composition boundary.

## Closest primary literature

- Jones, [Planar algebras, I](https://arxiv.org/abs/math/9909027), defines planar contraction systems from supplied boundary-labelled tensor spaces.
- Jones, [Quadratic tangles in planar algebras](https://arxiv.org/abs/1007.1158), derives finite-dimensional tangle relations but no elliptic source compiler.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the endpoint relation but not a finite-depth planar factorization.

No checked source gives the required elliptic functor and exact boundary inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the planar generators, relations, boundary colours, endpoint tangle, normal form, masks, and verifier.
2. Build and reduce known-endpoint tangles without materializing source-labelled tensors or paths.
3. Condition every accepted coefficient to exact signed factor points and independently verify each relation.
4. Collect full rank, solve and verify all factor-base logarithms.
5. Apply the unchanged contraction to fresh `Q+[t]P`, return target sources, substitute logs, and subtract `t`.
6. Preserve gauge/boundary ambiguity and accept only `[x]P=Q`, charging contraction and output state.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. For setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, contraction plus exact inverse `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`, the complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every box-space dimension, boundary colour, contraction term, and source output is charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Planar evaluation is a backend for an already defined tensor/functor. A finite-depth unlabelled algebra contracts to traces and aggregate invariants; exact factor identities live in boundary colours or conditioned tensor indices. Making those indices faithful across arbitrary factor bases expands the object to the occupied source tensor/serial-S3 state, while bounded universal relations cannot select rare endpoint fibers.

## Proof track

Derive a target-independent elliptic planar identity with bounded box spaces, exact all-source conditioning, and complete `lambda,mu<=0.45`.

## Disproof track

Show the functor needs source-labelled boundary boxes, prove unlabelled tangles collide on different source tuples, or reduce contraction to matchgate/skein/dimer/serial-S3 controls.

## Positive and negative controls

- Positive control: a supplied finite-depth planar algebra with planted boundary labels and independently replayed tangle reductions.
- Negative controls: label-erased closures, random tensor networks, IDEA-050/102/108/213, P1477/P1478, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires a new support-changing identity, 100% source recall, zero false outputs, box/boundary state exponent at most `0.45`, and `lambda,mu<=0.45`. Backend reduction, source tensor materialization, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-225/elliptic_planar_identity.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-225/planar_source_collisions.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-225/independent_planar_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-225/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected composition analysis. Finite checks would be toy and projections heuristic and model-bound. A planar identity, correct contraction, valid relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-225/elliptic_planar_identity.md` deriving a source-free support-changing planar identity or proving that exact conditioning necessarily retains the boundary source tensor.
