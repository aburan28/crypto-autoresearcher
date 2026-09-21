# ECDLP-IDEA-234 — Khovanov-cube source resolution

## Status and claim labels

- Class: `topological_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_resolution_cube_consumes_source_diagram_and_homology_loses_states`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a categorified invariant, cube differential, or homology generator is not an ECDLP break.

## Falsifiable hypothesis

The signed elliptic addition correspondence admits a target-independent diagram whose cube of local
resolutions has surviving Khovanov-type generators in canonical bijection with exact factor-base
source tuples.  Computing only the relevant homology class and lifting its resolution states would
then yield relation rows and masked target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **compile an endpoint addition diagram, form its categorified resolution
cube, cancel the differential, and lift surviving generators to exact signed elliptic sources**.  A
skein identity, Jones-type polynomial, supplied tangle, source-labelled cube, generic homology
solver, or post-hoc state selector is a duplicate/control.

## Assumptions

1. Public curve, factor base, endpoint, signs, masks, diagram grammar, Frobenius algebra, grading, and lift are scalar-blind and target-independent.
2. The diagram and implicit cube have sub-rho construction and state and do not contain one resolution vertex per source tuple.
3. Surviving generators have a canonical all-strata inverse to every exact signed finite-field source, not only an invariant rank or Euler characteristic.
4. Cube construction, cancellation, output, relation density, rank, factor logs, blind descent, verification, and memory are fully charged.

## Semantic fingerprint

`elliptic_addition_diagram | implicit_cube_of_resolutions | khovanov_type_differential | canonical_generator_to_point_source_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the public source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic pair/four-source generator lane.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-edge boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.
5. `inputs/ledger_inventory.json` — imported `P1478`, the exact local composition whose dense source payload remains.

## Closest primary literature

- Khovanov, [A categorification of the Jones polynomial](https://doi.org/10.1215/S0012-7094-00-10131-7), constructs a bigraded theory from a supplied link diagram and its resolution cube.
- Bar-Natan, [On Khovanov's categorification of the Jones polynomial](https://doi.org/10.2140/agt.2002.2.337), develops and computes the diagrammatic complex while retaining diagram input.

Neither source constructs an elliptic addition diagram or recovers hidden finite-field source states
from homology without the resolution deck.  Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, diagram compiler, local resolutions, differential, grading, cancellation order, source lift, and verifier.
2. Compile each known-log endpoint into a compact diagram and implicit resolution complex without enumerating source tuples.
3. Compute the required homology generators, lift every surviving resolution state to exact signed factor-base points, and verify elliptic sums.
4. Collect independent rows and solve and independently verify all factor logs.
5. Apply the identical diagram/cube/lift to fresh `Q+[t]P`, retain all ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging cube state, generator output, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let diagram/cube setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one implicit homology/source inverse `N^q,N^q_m`,
independent-rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log completion
`N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every crossing, resolution, chain group, differential entry, cancellation, generator, source output,
rank loss, factor log, masked descent, and verifier call is charged.  Promotion requires
`lambda,mu<=0.45`.

## Likely fatal obstruction

Khovanov theory starts from a diagram, and its resolution cube records the local choices of that
diagram.  A diagram fine enough for elliptic source branches must encode the same point-labelled
ancestry transitions sought by P1434; its cube can have one state per branch.  Passing to homology
then forgets preferred chain generators and retains only classes up to boundaries and basis change.
Restoring a canonical source-labelled representative reinstates the cube state or source deck.

## Proof track

Construct an endpoint-only compact diagram and implicit complex, prove a canonical bijection from
surviving generators to every exact source on every stratum, and establish complete
`lambda,mu<=0.45`.

## Disproof track

Show the diagram compiler requires source transitions, exhibit chain-homotopy-equivalent complexes
with identical homology but different source labels, or prove cube, representative, output, or
complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: small supplied link diagrams with independently computed resolution complexes and homology generators.
- Negative controls: basis-scrambled complexes, source-label permutations, Jones-polynomial-only output, IDEA-050/073/108/220/225, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a diagram and implicit cube of exponent at most `0.45`, exact all-source recall,
zero false sources, no source-labelled resolution deck, full factor-log rank, 100 blind descents at
each large future toy size, and complete `lambda,mu<=0.45`.  Homology-class ambiguity, exponential
cube state, missed branch, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-234/khovanov_source_lift_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-234/resolution_cube_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-234/independent_khovanov_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-234/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative topological hypothesis.  A valid cube,
differential, homology group, Euler characteristic, toy source lift, relation, or toy scalar is not a
complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-234/khovanov_source_lift_theorem.md` proving a compact endpoint diagram with canonical point-source generator lifts or a resolution-deck/homology-basis obstruction.
