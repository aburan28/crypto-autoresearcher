# ECDLP-IDEA-177 — Jucys-Murphy branching-spectrum source chain

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `none`
- State: `merged_rejected_branching_spectrum_without_point_inverse`
- Cohort: `20260718-c`
- Evidence scale: checked primary literature and scoped structural rejection only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: any finite check would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a branching spectrum, tableau, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Endpoint source circuits admit a target-independent multiplicity-free centralizer tower whose commuting Jucys-Murphy operators have a simple joint spectrum. Unranking the resulting Bratteli path from an endpoint would recover every exact signed factor-base source chain and enable complete sub-rho relation collection and masked target descent.

## Mechanism-new operation

The operation is **endpoint-to-centralizer-tower compilation followed by Jucys-Murphy joint-spectrum/Bratteli-path unranking to source points**. The proposed removal is spectral: a multiplicity-free path would replace enumeration of source orderings. This is not an additive-character transform or a tableau backend after sources are colored. It qualifies only if public spectral contents identify actual factor-base points without a `B^m` source dictionary.

Independent review found that uncolored contents are another branching/spectral
representation of the occupied source-label lanes IDEA-123/127/153/169. No new
endpoint-to-point inverse is supplied, so this version is a merge as well as a scoped
content-collision rejection.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, tower, commuting operators, branching conventions, masks, and verifier are frozen.
2. The endpoint module is constructed without a source chain, scalar index, or precolored tuple dictionary.
3. The tower is multiplicity-free and its joint spectrum canonically determines exact point identities, signs, and multiplicities.
4. Spectrum computation, Bratteli unranking, branching output, and ambiguity remain sub-rho.
5. Module construction, operators, source output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_endpoint_centralizer_tower | commuting_Jucys_Murphy_spectrum | multiplicity_free_Bratteli_path | path_to_factor_point_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1410-DIRECT-LABEL-NO-PROMOTION`, the direct source-label control.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank spectral representation control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the additive-character spectral no-promotion result.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`, the full-phase nonlinear source gap.

## Closest primary literature

- Okounkov and Vershik, [A New Approach to the Representation Theory of the Symmetric Groups. 2](https://arxiv.org/abs/math/0503040), develops branching and Gelfand-Tsetlin/Jucys-Murphy structure; it does not construct an elliptic source tower.
- Murphy, [A new construction of Young's seminormal representation of the symmetric groups](https://doi.org/10.1016/0021-8693(81)90205-2), supplies the seminormal/Jucys-Murphy framework; it does not make tableau contents factor-base identities.

Both primary URLs were checked. Neither supplies the endpoint compiler or exact point inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the centralizer tower, modules, Jucys-Murphy operators, branching order, factor base, masks, and verifier.
2. Compile each known endpoint `R_j=[r_j]P` into the tower module without source colors or tuple advice.
3. Compute the joint spectrum, unrank every Bratteli path, and invert path labels to signed factor-base tuples.
4. Verify tuples; preserve multiplicities, content collisions, tableau permutations, misses, infinity, ambiguity, and output.
5. Collect rank `B`, solve the relation matrix, and independently verify every factor-base logarithm.
6. Apply the identical tower/spectrum/inverse pipeline to fresh masked targets `Q+[t]P`.
7. Substitute verified logs, remove masks, retain every candidate, and verify `[x]P=Q`.
8. Charge module construction, spectra, branching paths, point-color inversion, output, rank, descent, time, and peak memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup be `N^a,N^a_m`, reciprocal relation and target densities `N^delta,N^delta_t`, spectrum/path inversion `N^q,N^q_m`, output and ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are complete time and peak-memory exponents; every module block, spectral collision, tableau path, source color, and output tuple is charged.

## Likely fatal obstruction

Jucys-Murphy eigenvalues record tableau/permutation contents, not elliptic point identities. Coloring branching edges by factor-base points requires the missing source dictionary; for `m` leaves that dictionary or its refinement has `B^m` scale. Multiplicity-free combinatorics therefore does not imply source invertibility.

## Proof track

An outside-scope successor must construct the endpoint tower without source colors, prove simple spectrum and an exact path/point biconditional, and derive complete `lambda,mu<=0.45`.

## Disproof track

Produce distinct point tuples with the same contents, show edge coloring consumes the source tuple/dictionary, count `B^m` branching states, expose hidden scalar orientation, or derive an exponent at least `0.5`.

## Positive and negative controls

- Symmetric-group towers with supplied tableaux and known seminormal spectra.
- Uncolored versus factor-base-colored branching graphs.
- Direct-label, additive-character, full-phase, rho, and BSGS controls.
- Exhaustive toy fibers and blind-target verification.

## Quantitative promotion and falsification gates

This scoped formulation is rejected. Reopening requires an endpoint-only tower, exact all-strata path/point inverse, and symbolic `lambda,mu<=0.45`. Any content collision, supplied source coloring, `B^m` dictionary, one lost tuple, or either exponent at least `0.5` falsifies it.

## Artifact plan

- Prospective scoped no-go: `ideas/artifacts/ECDLP-IDEA-177/jm_content_no_go.md`
- Prospective tower specification: `ideas/artifacts/ECDLP-IDEA-177/centralizer_tower_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-177/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-177/cost_analysis.md`

All paths are ID-owned and prospective; no experiment or artifact exists.

## Interpretation boundary

This is rejected, scoped, novelty-unverified evidence. Finite checks would be toy and projections heuristic and model-bound. A simple spectrum or correct relation after supplied colors is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-177/jm_content_no_go.md` proving that uncolored branching contents cannot identify factor-base points without a `B^m` source dictionary.
