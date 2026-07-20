# ECDLP-IDEA-250 — Frobenius-split source strata

## Status and claim labels

- Class: `arithmetic_geometric_representation`
- Risk band: `high_risk`
- Top lane: `high_risk`
- State: `rejected_generic_etale_frobenius_splitting_has_no_source_section`
- Cohort: `20260718-h`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: retired `review_required` theorem preflight; unapproved and zero-run
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; correctness, a local identity, a source tuple, relation validity, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform Frobenius splitting of a compact relation-fiber compactification compatibly splits every exact source stratum.  Iterating the splitting and evaluating its residues would canonically separate rational factor tuples and enable complete descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **construct a compatible Frobenius splitting of all source strata and use splitting residues as an exact rational-point section**.  Compatible splitting is not the same invariant as IDEA-094's torus fixed cells or IDEA-197's Frobenius trace.  The generic admitted relation fiber is finite etale, however, so absolute Frobenius is already an automorphism and splitting is tautological; a splitting that distinguishes points must contain the primitive idempotents/source ideals.  A solver swap,
parameter change, same-field isogeny variant, explicit large-prime/source table, post-hoc selector,
dense resultant, or relation-only certificate receives no mechanism credit.

## Assumptions

1. A compactification and splitting section are derived uniformly from public elliptic equations without enumerating source ideals.
2. The splitting compatibly distinguishes every rational source stratum, including diagonals, signs, infinity, and nonreduced exceptional fibers.
3. Iteration, residue evaluation, and point lifting have sub-rho time and represented state.
4. Compactification, splitting data, output, density, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`relation_fiber_compactification | compatible_frobenius_splitting | source_strata_residues | exact_rational_point_section | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the coordinate source-predicate frontier.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic source-generator frontier.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-state boundary.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-044`, the hidden factor-base advantage under cover smoothness.

## Closest primary literature

- Mehta and Ramanathan, Frobenius splitting and cohomology vanishing for Schubert varieties, [https://doi.org/10.2307/1971368](https://doi.org/10.2307/1971368), constructs splittings and vanishing results for supplied varieties and strata.
- Ramanathan, Equations defining Schubert varieties and Frobenius splittings of diagonals, [https://doi.org/10.1007/BF02698935](https://doi.org/10.1007/BF02698935), gives compatible diagonal splittings in a structured supplied geometry.
- Semaev, Summation polynomials and the discrete logarithm problem, [https://eprint.iacr.org/2004/031](https://eprint.iacr.org/2004/031), supplies the relation equations but no source-separating splitting.

These sources were checked as primary records for the named supplied-input operation.  None gives
the endpoint-only compiler, exact point-source inverse, factor-log calibration, and fresh masked
descent required here.  No ECDLP novelty is claimed; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze public `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, arity, public colours/auxiliary choices, masks, tie rules, and the independent verifier before targets.
2. For each known-log endpoint `R=[r]P`, construct the compactification and splitting section from each public endpoint without source ideals, primitive idempotents, or point-labelled boundary divisors.
3. Evaluate splitting residues, enumerate every compatibly split rational point stratum and signed lift, preserve multiplicities, and verify sums. Preserve every failure, duplicate, ambiguity branch, repeated point, infinity chart, nonreduced case, and rejected candidate.
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

On a reduced finite etale fiber over F_p, Frobenius is an automorphism and a module splitting carries no canonical ordering or source separation.  Compatibility with individual points is equivalent to knowing their prime ideals/idempotents; arbitrary factor-base strata need not be compatibly split, and supersingular elliptic curves provide a hostile family for global splitting claims.  On nonreduced fibers, splitting may fail or discard nilpotents rather than recover multiplicity.

## Proof track

Construct a source-free compatible splitting whose residues uniquely identify every point and multiplicity and derive complete exponents at most 0.45.

## Disproof track

Prove generic etale splitting is point-blind, exhibit split fibers with permuted sources, show compatible point ideals require root finding, or derive data/output or either complete exponent at least 0.50.

## Positive and negative controls

- Positive control: supplied compatibly split Schubert/diagonal fixtures and explicit finite reduced algebras with known idempotents.
- Negative controls: source permutations, generic etale algebras, nilpotent fibers, IDEA-094, IDEA-197, IDEA-222, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-free compatible splitting, exact point and multiplicity recall with zero false sources, no primitive-idempotent table, full rank and factor logs, blind descent, and complete lambda and mu at most 0.45.  Tautological etale splitting, source ideals, lost nilpotents, or exponent at least 0.50 falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-250/frobenius_split_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-250/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-250/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-250/cost_analysis.md`

All paths are prospective; no artifact root exists and no contract or experiment ran.

## Interpretation boundary

This is a novelty-unverified rejected/scoped-negative hypothesis.  Every finite check would be toy and every complexity projection remains
heuristic and model-bound.  A correct identity, canonical form, decomposition, valid relation,
recovered source tuple, or toy scalar is not a complete generic ECDLP algorithm, crypto-scale
validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-250/frobenius_split_source_theorem.md` proving a source-separating compatible splitting or the finite-etale point-blindness and nonreduced-multiplicity no-go.
