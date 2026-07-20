# ECDLP-IDEA-248 — Fiber-polytope coherent source section

## Status and claim labels

- Class: `polyhedral_representation`
- Risk band: `representation_changing`
- Top lane: `-`
- State: `merged_rejected_fiber_polytope_requires_source_projection_and_vertices`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A compact projection polytope associated with the elliptic relation fiber has a fiber polytope whose coherent subdivisions encode exact source branches.  A target-independent chamber functional would select a canonical coherent section and unrank it to signed factor points below rho and BSGS.

## Mechanism-new operation

The screened operation is **construct the relation projection's fiber polytope, select a coherent subdivision by a frozen chamber functional, and lift its cells to exact sources**.  Fiber polytopes package all coherent sections rather than choosing a post-hoc Monge optimum, but the ambient polytope, projection, and vertices are the source incidence deck.  The candidate merges with IDEA-059/143/206/239 once that construction and lift are charged.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. The ambient polytope and projection derive from compact public equations without a vertex or inequality per source tuple.
2. The fiber polytope, chamber location, coherent subdivision, and exact lift have sub-rho time and represented size.
3. The frozen functional selects every needed source branch without target-dependent tuning or missing boundary cells.
4. Construction, facets, cells, output, density, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_relation_projection | compact_fiber_polytope | coherent_subdivision_chamber | exact_cell_to_point_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate/polyhedral barrier.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1419-SYMMETRIC-SQUARE-NO-PROMOTION`, the aggregate divisor-fiber control.
4. `inputs/ledger_inventory.json` — imported `P1477`, the materialized recursive-state control.
5. `inputs/ledger_inventory.json` — imported `P1478`, the dense exact composition control.

## Closest primary literature

- Billera and Sturmfels, Fiber polytopes, [https://doi.org/10.2307/2946575](https://doi.org/10.2307/2946575), constructs coherent sections from a supplied polytope projection.
- Billera and Sturmfels, Iterated fiber polytopes, [https://doi.org/10.1112/S0025579300007440](https://doi.org/10.1112/S0025579300007440), packages flags of supplied projections but does not create elliptic source vertices.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies algebraic relations, not a compact integral projection polytope.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, derive the ambient/projection polytopes and their chamber fan from each endpoint without enumerating factor tuples, monomials, or source cells.
3. Select the frozen coherent subdivision, lift all accepted cells to exact signed factor points, preserve boundary ambiguity, and verify sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
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

A fiber polytope summarizes coherent subdivisions of a supplied projection.  For the elliptic fiber, a source-faithful vertex/facet description contains the monomial or tuple incidence being sought; removing it leaves only an aggregate Newton body.  A chamber functional selects among already represented cells and can be a post-hoc selector rather than a source constructor.

## Proof track

Give a sub-rho implicit projection/fiber-polytope representation and canonical all-source cell lift, then prove complete exponents at most 0.45.

## Disproof track

Reduce any faithful polytope oracle to source enumeration, exhibit equal projection data with different sources, or prove facet/cell/output or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: small supplied projections with independently enumerated fiber polytopes and coherent subdivisions.
- Negative controls: vertex permutations, source-erased Newton polytopes, IDEA-059, IDEA-143, IDEA-206, IDEA-239, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an implicit polytope oracle of exponent at most 0.45, exact all-cell source recall with zero false sources, no vertex/source deck, full rank and factor logs, blind descent, and complete lambda and mu at most 0.45.  Target-selected chambers, source facets, missed noncoherent branches, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-248/fiber_polytope_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-248/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-248/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-248/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-248/fiber_polytope_source_theorem.md` proving a compact endpoint projection and coherent exact-source section or a vertex/facet source-deck obstruction.
