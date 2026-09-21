# ECDLP-IDEA-220 — Twisted Reidemeister-torsion source factorization

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `merged_rejected_torsion_consumes_source_complex_and_aggregates_bases`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: retired zero-run `review_required` theorem preflight
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a torsion determinant, twisted polynomial, or valid relation is not an ECDLP break.

## Falsifiable hypothesis

There is a public finite chain complex and scalar-blind twist attached to an elliptic endpoint whose Reidemeister torsion factors into primitive terms indexed biconditionally by exact signed factor-base sources. Canonical factor return would produce relation rows and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **twisted chain torsion followed by primitive determinant-factor return**, not Fox differentiation alone. It merges/rejects because torsion is computed from a supplied based chain complex and is invariant only up to basis/units; it aggregates cells and paths. A point-labelled complex or twist that separates factors already contains the source relator, source edges, or scalar orientation.

## Assumptions

1. Public `E/F_p`, prime-order `G`, factor base `F` of size `B=N^beta`, endpoint, finite complex, and twist are target-independently defined.
2. The complex is constructible without a source tuple, relation graph, dense fiber ideal, or scalar-labelled representation.
3. Torsion factorization returns every exact point, sign, repeat, and multiplicity canonically on all strata.
4. Complex construction, bases, determinants, factorization, output, rank, factor logs, blind descent, verification, and memory are charged.

## Semantic fingerprint

`endpoint_based_chain_complex | scalar_blind_twist | Reidemeister_torsion_determinant | primitive_factor_to_exact_points | factor_logs | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing endpoint-to-source generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the source-generator boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the ancestry-state floor.
4. `inputs/ledger_inventory.json` — imported `P1478`, the determinant/resultant composition control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge boundary.

## Closest primary literature

- Milnor, [Whitehead torsion](https://doi.org/10.1090/S0002-9904-1966-11484-2), develops torsion for supplied based chain complexes and its basis indeterminacy.
- Wada, [Twisted Alexander polynomial for finitely presentable groups](https://doi.org/10.1016/0040-9383(94)90013-2), forms determinant invariants from a supplied presentation and representation.
- Fox, [Free differential calculus I](https://doi.org/10.2307/2372190), is the source-relator derivative control already exposed by IDEA-208.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations without the required based complex/source inverse.

No checked source constructs the elliptic complex and exact factor return. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the endpoint complex, bases, twist, torsion normalization, factor inverse, masks, and verifier.
2. Construct the complex for known endpoints without source-labelled cells and compute normalized torsion.
3. Factor torsion into every exact signed factor point and independently verify each elliptic relation.
4. Collect full rank, solve and verify the factor-base logarithms.
5. Reuse the identical construction on fresh `Q+[t]P`, return every source factor, substitute logs, and subtract `t`.
6. Preserve unit/basis ambiguity and accept only `[x]P=Q`, charging all determinant, output, rank, descent, verification, and memory costs.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup cost `N^a,N^a_m`, reciprocal base/target densities `N^delta,N^delta_t`, torsion plus exact factor return `N^q,N^q_m`, independent rank gain `N^r`, output/unit ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Chain cells, matrix entries, representations, units, determinant factors, and output are never free. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Torsion begins with bases and boundary matrices, and changing bases changes representatives by units while preserving only an aggregate invariant. A scalar-sensitive twist is a character/orientation of the prime-order group; a source-sensitive boundary matrix lists the relation cells. Determinant factorization is noncanonical and cannot recover which exact source cells produced the same torsion value without retaining their labels.

## Proof track

Define a source-free endpoint complex and canonical twist, prove a primitive-factor/source biconditional modulo torsion units, and derive complete `lambda,mu<=0.45`.

## Disproof track

Show basis-equivalent complexes or distinct source fibers have identical torsion, prove the twist imports scalar orientation, or show the boundary matrices contain explicit source edges or square-root-scale state.

## Positive and negative controls

- Positive control: a planted based complex with supplied source-labelled cells and independently factored torsion.
- Negative controls: basis changes, acyclic expansions, shuffled twists, ordinary Alexander/Fox invariants, IDEA-208, explicit source graphs, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires a canonical source-free complex and twist, 100% factor-to-point recall, zero false factors across basis/unit changes, and complete `lambda,mu<=0.45`. Source-labelled cells, scalar orientation, one torsion collision, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-220/twisted_torsion_source_theorem.md`
- Prospective collision set: `ideas/artifacts/ECDLP-IDEA-220/torsion_basis_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-220/independent_torsion_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-220/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected mechanism analysis. Finite checks would be toy and projections heuristic and model-bound. A torsion calculation, factorization, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-220/twisted_torsion_source_theorem.md` proving a basis-independent exact factor-to-point inverse for a source-free endpoint complex or recording a basis/source collision that closes the direct construction.
