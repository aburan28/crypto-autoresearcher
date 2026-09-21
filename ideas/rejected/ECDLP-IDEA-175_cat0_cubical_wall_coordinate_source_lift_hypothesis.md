# ECDLP-IDEA-175 — CAT(0)-cubical wall-coordinate source lift

## Status and claim labels

- Class: `geometric_representation`
- Risk band: `representation_changing`
- Top lane: `none`
- State: `rejected_scoped_no_public_wall_orientation_operation_supplied`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and scoped structural rejection only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: any finite check would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a cubulation, median path, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The public endpoint/source-decision system admits an equivariant lift to a finite-dimensional CAT(0) cube complex whose separating hyperplanes give canonical wall coordinates. Reading the oriented walls from an endpoint would recover every exact signed factor-base source leaf and enable complete sub-rho relation collection and masked target descent.

## Mechanism-new operation

The operation is **endpoint cubulation followed by canonical oriented-wall inversion to source leaves**. The proposed removal is global: median/wall coordinates would replace source-path enumeration by a unique public lift. This differs from a lossless source DAG or labels attached after decomposition. It qualifies only if equivariance supplies orientation from endpoint data; a non-equivariant choice of halfspaces simply restates the missing source orientation.

Independent review narrowed the boundary: the cited cubulation papers do not prove a
universal no-go for finite cyclic wall coordinates. What fails here is the concrete
record's absence of a public endpoint-derived orientation and source inverse. Any stronger
fixed-point claim requires a separate precisely scoped theorem and primary citation.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, wallspace, cubulation, action, masks, and verifier are frozen.
2. The cyclic elliptic action and endpoint map extend equivariantly without scalar-index labels.
3. Finitely many oriented separating walls determine exact point identities, signs, multiplicities, and order conventions.
4. Wall construction, dimension, stabilizers, inversion, and ambiguity remain sub-rho on all strata.
5. Cubulation, coordinates, source output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_endpoint_wallspace | equivariant_CAT0_cubulation | canonical_oriented_hyperplanes | wall_to_source_leaf_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-path barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the direct source-label control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1411-SEGMENTED-DIRECTORY-NO-PROMOTION`, the segmented source-directory control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1418-DIFFERENTIAL-STATE-NO-PROMOTION`, the differential-state orientation boundary.

## Closest primary literature

- Sageev, [Ends of group pairs and non-positively curved cube complexes](https://doi.org/10.1112/plms/s3-71.3.585), constructs cubical actions from wall/codimension-one data; it does not construct elliptic source walls.
- Niblo and Reeves, [Groups acting on CAT(0) cube complexes](https://arxiv.org/abs/math/9702231), studies group actions and boundedness phenomena; it does not give a source-orienting coordinate for finite cyclic DLP actions.

Both primary URLs were checked. Neither supplies the asserted equivariant source lift or inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the endpoint wallspace, halfspace conventions, cubulation, factor base, masks, decoder, and verifier.
2. Build the cube-complex point for each known `R_j=[r_j]P` equivariantly and without a source path.
3. Read all separating hyperplanes, orient them canonically, and invert their coordinates to every signed factor-base tuple.
4. Verify tuples; preserve fixed cubes, bounded orbits, wall collisions, stabilizers, misses, infinity, ambiguity, and output.
5. Collect rank `B`, solve the relation matrix, and independently verify every factor-base logarithm.
6. Apply the identical wall lift and inverse to fresh masked targets `Q+[t]P`.
7. Substitute verified logs, remove masks, retain all candidates, and verify `[x]P=Q`.
8. Charge wall construction, cube dimension, orientation, inversion, output, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup be `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, cubulation/wall inversion `N^q,N^q_m`, output and ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are complete time and peak-memory exponents; every wall, cube, orientation branch, stabilizer case, and source output is charged.

## Likely fatal obstruction

The record supplies no theorem or operation deriving canonical oriented halfspaces from a public endpoint. A non-equivariant lift may choose them, but that choice is exactly the missing orientation; encoding it through walls or a fundamental domain materializes the source directory rather than removing source search. This is a scoped missing-operation result, not a universal fixed-point theorem for all finite cyclic cubulations.

## Proof track

An outside-scope successor must give an endpoint-only equivariant wallspace with canonical orientations, prove exact wall/source biconditional inversion, and derive complete `lambda,mu<=0.45`.

## Disproof track

Prove the cyclic action has only bounded/fixed wall coordinates, show orientation requires a base-to-endpoint source path, construct indistinguishable tuples, expose a source directory, or derive an exponent at least `0.5`.

## Positive and negative controls

- Trees and cube complexes with supplied oriented source paths.
- The same wallspace with reversed or randomized halfspace orientations.
- Lossless DAG, direct-label, segmented-directory, rho, and BSGS controls.
- Exhaustive toy fibers and blind-target verification.

## Quantitative promotion and falsification gates

This scoped formulation is rejected. Reopening requires a new equivariant orientation theorem, exact all-strata source inverse, and symbolic `lambda,mu<=0.45`. Bounded/fixed coordinates, any non-equivariant advice, one source collision, a materialized directory, or either exponent at least `0.5` falsifies it.

## Artifact plan

- Prospective scoped no-go: `ideas/artifacts/ECDLP-IDEA-175/cubical_orientation_no_go.md`
- Prospective wallspace specification: `ideas/artifacts/ECDLP-IDEA-175/wallspace_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-175/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-175/cost_analysis.md`

All paths are ID-owned and prospective; no experiment or artifact exists.

## Interpretation boundary

This is rejected, scoped, novelty-unverified evidence. Finite checks would be toy and projections heuristic and model-bound. Valid cubulation or relation recovery after supplied orientations is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-175/cubical_orientation_no_go.md` proving the finite-cyclic bounded/fixed-wall dichotomy and locating every non-equivariant orientation input.
