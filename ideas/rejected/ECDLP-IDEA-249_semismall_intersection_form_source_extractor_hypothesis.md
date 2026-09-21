# ECDLP-IDEA-249 — Semismall intersection-form source extractor

## Status and claim labels

- Class: `derived_geometric_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_semismall_decomposition_aggregates_supplied_strata`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A semismall resolution of the endpoint relation fiber has relevant strata indexed by exact source types, and nondegenerate intersection forms canonically split the direct image into source summands.  Computing those summands and lifting their supports would recover exact factor points below rho and BSGS.

## Mechanism-new operation

The screened operation is **build a semismall resolution, diagonalize its relevant-stratum intersection forms, and invert the decomposition-theorem summands to exact source points**.  Intersection forms are a different extractor from IDEA-080's characteristic cycle and IDEA-232's exit-path stalks, but all require a resolution and stratification already separating the source components.  Their perverse summands are isomorphism-class aggregates without preferred finite-field point labels.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. A compact semismall resolution and target-uniform relevant stratification are derived from public equations without source-labelled exceptional components.
2. Intersection matrices and decomposition summands have sub-rho dimension, arithmetic, and represented state over the prime field.
3. Each summand has a canonical rational support-to-factor-point inverse, including singular and nonreduced fibers.
4. Resolution construction, strata, matrices, output, rank, factor logs, descent, verification, and memory are fully charged.

## Semantic fingerprint

`endpoint_relation_resolution | semismall_map | relevant_strata_intersection_forms | perverse_source_summands | exact_point_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the closed coordinate source-predicate lane.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the closed arithmetic source-generator lane.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.

## Closest primary literature

- de Cataldo and Migliorini, The Hard Lefschetz Theorem and the topology of semismall maps, [https://arxiv.org/abs/math/0006187](https://arxiv.org/abs/math/0006187), relates decomposition to intersection forms for a supplied semismall map.
- de Cataldo and Migliorini, The Douady space of a complex surface, [https://arxiv.org/abs/math/9811159](https://arxiv.org/abs/math/9811159), decomposes a supplied Hilbert-Chow/Douady map, not elliptic sources.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies relation equations but no semismall source resolution.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct the semismall resolution, relevant strata, and intersection forms from the endpoint without one exceptional component or basis vector per source tuple.
3. Split the direct image, map every rational summand/support to exact signed factor points, preserve multiplicities, and verify sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
4. Collect independently verified rows until rank `B`, charge rank loss and output, solve all factor logs, and independently verify every `[log_P(S)]P=S`.
5. Apply the identical frozen constructor and source inverse to fresh masks `Q+[t]P`, with no known-log-only branch, target-selected parameter, or post-hoc source advice.
6. Substitute verified factor logs, subtract `t`, retain every candidate caused by source ambiguity, and accept only `x` satisfying `[x]P=Q`; serialize complete time and peak-memory accounting.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let setup time and memory be `N^a,N^a_m`, reciprocal relation and target success densities
be `N^delta,N^delta_t`, one mechanism evaluation plus exact source inverse cost
`N^q,N^q_m`, independent-rank gain be `N^r`, source output and target ambiguity be
`N^o,N^u`, and factor-log completion be `N^ell,N^ell_m`.  The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every constructor coefficient, represented state, preprocessing query, failed target, branch,
source output, relation row, rank defect, factor log, masked descent, verifier call, bit operation,
and live byte is charged.  Promotion requires both complete exponents at most `0.45`; correctness
or relation validity alone has no performance meaning.

## Likely fatal obstruction

The addition map E^m to E is not semismall for m greater than one because its generic fiber is positive-dimensional over the codimension-zero stratum.  Restricting to the finite factor deck removes that geometry and leaves a finite sheaf whose component summands are the explicit source states.  In either case, intersection forms aggregate supplied strata and have no preferred rational-point basis.

## Proof track

Construct a source-blind sub-rho semismall map and prove canonical summand-to-point recovery on every stratum with complete exponents at most 0.45.

## Disproof track

Show every source-faithful stratification factors through explicit components, exhibit equal intersection-form data with different point sources, or prove resolution/matrix/output or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied semismall resolutions with independently known relevant strata and intersection forms.
- Negative controls: basis changes, source-label permutations, IDEA-080, IDEA-126, IDEA-222, IDEA-232, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a compact source-blind resolution, exact summand-to-point recall with zero false sources, no source-labelled strata, full rank and factor logs, blind descent, and complete lambda and mu at most 0.45.  Supplied components, basis-dependent output, missed singular strata, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-249/semismall_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-249/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-249/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-249/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-249/semismall_source_theorem.md` proving an endpoint-derived semismall source decomposition or a relevant-stratum/source-component factorization no-go.
