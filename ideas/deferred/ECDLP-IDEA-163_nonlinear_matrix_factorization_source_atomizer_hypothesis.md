# ECDLP-IDEA-163 — Nonlinear matrix-factorization source atomizer

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `representation-changing-theorem-gated`
- Top lane: `none`
- State: `deferred_needs_low_rank_factorization_and_source_summand_theorem`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: theorem-deferred; no contract or run is authorized
- Scale labels: any computation is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a matrix factorization, summand, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The target-specialized five-source relation hypersurface has a compact genuinely nonlinear 2-periodic matrix factorization constructible directly from public endpoint equations. Its canonical indecomposable summands are biconditional to exact signed factor-base atoms, including nonreduced strata, and can be built, split, and used for complete descent below rho and BSGS.

## Mechanism-new operation

The operation is **pre-expansion nonlinear matrix-factorization construction followed by canonical source-summand atomization**. It differs from IDEA-115's strict square-linear Ulrich/Chow map and IDEA-152's BGG/Tate kernel only if the 2-periodic object is constructed without dense relation expansion and its indecomposables, not an arbitrary kernel basis, identify sources. A matrix factorization of an already materialized hypersurface or solver substitution is a control.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta` and one compact hypersurface/circuit presentation are frozen.
2. A target-uniform nonlinear matrix factorization has sub-rho rank and coefficient payload.
3. It is constructed from endpoint equations without enumerating source tuples or a dense Macaulay object.
4. A canonical decomposition recovers every exact source identity and local multiplicity.
5. Construction, splitting, output, rank, factor logs, masked descent, and memory are charged.

## Semantic fingerprint

`target_relation_hypersurface | compact_nonlinear_2_periodic_factorization | canonical_indecomposable_atomization | exact_nonreduced_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing endpoint-to-source compiler.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where exact matrices stay full rank.
3. `inputs/ledger_inventory.json` — imported `P1477`, whose source-faithful state polynomials materialize.
4. `inputs/ledger_inventory.json` — imported `P1478`, where exact norm composition becomes dense.
5. `inputs/ledger_inventory.json` — imported `P1480`, the solver-substitution control.

## Closest primary literature

- Eisenbud, [Homological algebra on a complete intersection](https://doi.org/10.1090/S0002-9947-1980-0570778-7), establishes matrix factorizations but no compact elliptic source atomizer.
- Orlov, [Triangulated categories of singularities](https://arxiv.org/abs/math/0302304), supplies the categorical interpretation, not a canonical point-source decomposition.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives the neighboring relation hypersurfaces.

No checked primary source supplies the complete operation; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the hypersurface circuit, factorization ranks, grading, targets, masks, strata, and verifier.
2. Construct the target-independent factorization recipe without expanding the relation fiber.
3. Specialize at known `R_j=[r_j]P` and canonically split the 2-periodic object.
4. Invert every summand to exact signed sources; verify tuples and preserve misses, false atoms, multiplicity, and basis dependence.
5. Collect rank `B`, solve factor-base logs, and verify them.
6. Apply the identical construction/splitting to fresh `Q+[t]P` masks.
7. Substitute factor logs, remove masks, retain every candidate, and verify `[x]P=Q`.
8. Report matrix ranks, coefficients, splitting, output, retries, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let factorization setup cost `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, specialization/splitting/source inversion `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Ranks, coefficients, categorical decomposition, primary-local data, and outputs are all charged.

## Likely fatal obstruction

Constructing or decomposing the factorization can be the original relation-fiber factorization. Its rank or category may track the Jacobian/Milnor algebra, and indecomposable summands need not be canonical or point-labelled; recovering labels can restore dense source state.

## Proof track

Prove a compact direct construction, target-uniform rank bounds, canonical reduced/nonreduced summand atoms, and complete `lambda,mu<=0.45` descent.

## Disproof track

Reduce construction to a dense relation algebra, show rank/output exponent at least `0.5`, exhibit basis-dependent or source-colliding summands, or lose one exceptional stratum.

## Positive and negative controls

- Classical small matrix factorizations with known indecomposables.
- IDEA-115 square-linear and IDEA-152 Tate/kernel controls.
- Dense Macaulay and already-materialized hypersurface controls.
- Exhaustive toy fibers, rho, BSGS, and independent source verification.

## Quantitative promotion and falsification gates

Remain deferred. Promotion requires explicit construction/rank and canonical source-summand theorems plus `lambda,mu<=0.45`. A later approved toy preflight needs 100% source/multiplicity recovery and zero false atoms. Dense construction, noncanonical atoms, a missed source, or exponent at least `0.5` falsifies this version.

## Artifact plan

- Factorization/source theorem: `ideas/artifacts/ECDLP-IDEA-163/matrix_factorization_source_theorem.md`
- Compact construction specification: `ideas/artifacts/ECDLP-IDEA-163/factorization_spec.md`
- Fixtures, verifier, and cost receipt: `ideas/artifacts/ECDLP-IDEA-163/fixtures.json`, `ideas/artifacts/ECDLP-IDEA-163/independent_verifier.py`, and `ideas/artifacts/ECDLP-IDEA-163/cost_analysis.md`

All paths are prospective; no experiment is authorized.

## Interpretation boundary

This is deferred, novelty-unverified representation research. Finite evidence is toy and projections heuristic and model-bound. A correct factorization or relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-163/matrix_factorization_source_theorem.md` proving compact rank and canonical all-strata summand/source bounds before computing any factorization.
