# ECDLP-IDEA-232 — Exit-path sheaf-stalk source inversion

## Status and claim labels

- Class: `algebraic_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_exit_category_and_stalks_require_source_stratification`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exit-path equivalence or reconstructed constructible sheaf is not an ECDLP break.

## Falsifiable hypothesis

The universal marked elliptic addition correspondence has a finite target-independent stratification
whose exit-path category and endpoint constructible pushforward admit an exact Möbius-style inversion
to the point-source stalks.  Querying the endpoint functor would then recover every signed factor-base
tuple and enable full relation collection and blind descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **compile an endpoint-relative exit-path category, represent the marked
addition pushforward as a constructible functor, and invert specialization maps to exact source
stalks**.  A generic sheaf package, stratification after source recovery, source-labelled quiver,
cohomology-only invariant, or categorical equivalence without a point inverse is a duplicate/control.

## Assumptions

1. A finite algebraic or topological stratification and its exit category are defined uniformly from public curve, factor-base, sign, and endpoint data.
2. Category size, functor representation, specialization maps, inversion, and peak state have exponents below `1/2` and do not list all source branches.
3. Recovered stalk atoms biject with exact signed finite-field points, including nonreduced and boundary fibers, rather than only ranks or isomorphism classes.
4. Construction, output, relation density, rank, factor logs, fresh masked descent, verification, and memory are fully charged.

## Semantic fingerprint

`universal_marked_addition_stratification | endpoint_exit_path_category | constructible_pushforward_functor | specialization_mobius_inverse | exact_point_stalk_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the endpoint source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the failed public source-resolving coordinate-predicate lane.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic source-fiber generator lane.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless source-ancestry edge boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.

## Closest primary literature

- Treumann, [Exit paths and constructible stacks](https://arxiv.org/abs/0708.0659), reconstructs constructible stacks from the exit-path 2-category of a supplied stratified space.
- Lejay, [Constructible hypersheaves via exit paths](https://arxiv.org/abs/2102.12325), proves exit-path representation results for constructible hypersheaves under stated stratification hypotheses.

Neither source supplies a finite source-blind stratification of elliptic addition fibers or an inverse
from a pushforward isomorphism class to exact finite-field point labels.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, stratification, exit-path presentation, functor coefficients, inversion order, and verifier.
2. Construct the universal stratification and compact exit category once without enumerating point-source incidences.
3. For each known-log endpoint, evaluate the constructible pushforward, invert its specialization maps, recover every exact signed source tuple, and verify sums.
4. Collect independent rows and solve and independently verify all factor logs.
5. Apply the identical category/functor/inverse to fresh `Q+[t]P`, preserve all ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging category construction, stalk output, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let category setup time/memory be `N^a,N^a_m`, reciprocal base and target densities
`N^delta,N^delta_t`, one functor evaluation plus exact stalk/source inverse
`N^q,N^q_m`, independent-rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log
completion `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every stratum, exit morphism, stalk, specialization map, inversion branch, source tuple, rejected
endpoint, rank loss, factor log, descent replay, and verifier call is charged.  Promotion requires
`lambda,mu<=0.45`.

## Likely fatal obstruction

Exit-path theorems classify constructible objects on a stratified space that has already been
supplied.  A stratification fine enough for pointwise elliptic sources has strata, exit morphisms, or
stalk bases carrying the same source labels and ancestry edges sought by P1434.  Coarsening removes
those labels and retains only aggregate ranks, monodromy, or isomorphism classes, so distinct source
tuples share the same functor data.  Categorical reconstruction recovers the supplied sheaf, not a
canonical basis of hidden finite-field preimages.

## Proof track

Construct a finite target-uniform stratification with sub-rho exit category, prove point-source
faithfulness and a canonical all-strata stalk inverse, and bound full relation and target paths by
`lambda,mu<=0.45`.

## Disproof track

Exhibit two source fibers with identical coarse exit-functor data, or prove any point-faithful
stratification must contain one labelled object/morphism per incidence; alternatively show category,
output, ambiguity, or complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: published finite stratified examples with independently reconstructed constructible functors and known stalk bases.
- Negative controls: source-label permutations, coarsened strata, constant sheaves, IDEA-073/080/087/103/174, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a finite source-blind category of size exponent at most `0.45`, exact point-source
recall on all strata, zero false sources, no source-labelled incidence quiver, full factor-log rank,
100 blind descents at each large future toy size, and complete `lambda,mu<=0.45`.  A coarse collision,
explicit source morphism, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-232/exit_path_source_inverse_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-232/constructible_functor_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-232/independent_exit_path_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-232/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation hypothesis.  An exit-path
equivalence, correct stalk rank, reconstructed toy functor, valid relation, or toy scalar is not a
point-source compiler, crypto-scale ECDLP evidence, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-232/exit_path_source_inverse_theorem.md` proving a finite endpoint-only point-faithful exit category and canonical stalk inverse or an incidence-size/collision obstruction.
