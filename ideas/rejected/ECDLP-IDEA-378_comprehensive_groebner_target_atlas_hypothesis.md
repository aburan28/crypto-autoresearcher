# ECDLP-IDEA-378 — Comprehensive Gröbner target atlas

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_specialization_atlas_materializes_parametric_source_branches`
- Cohort: `20260718-s`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run preflight under `review_required`; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct specialized Gröbner basis or toy relation is not an ECDLP break.

## Falsifiable hypothesis

A comprehensive Gröbner system for the parameterized five-deck relation ideal partitions fresh targets into a subgate number of endpoint cells, each carrying a compact specialized basis whose triangular leaves return exact occurrence-labelled sources under arbitrary restrictions.

## Mechanism-new operation

The screened operation is **construct a finite specialization atlas over the target parameters, select the target cell, specialize its Gröbner basis, and triangularly lift one exact source point**. It is representation-changing only if the atlas and all specialization branches avoid materializing the dense relation ideal or its source quotient.

## Assumptions

1. The parameterized ideal encodes finite deck membership, signed complete charts, multiplicities, and occurrence labels biconditionally.
2. A comprehensive basis/branch atlas has total setup and state at most `B^(9/4)` and is target-independent.
3. Cell selection and basis specialization for a fresh target, including arbitrary dyadic restrictions, cost at most `B^(5/4)`.
4. Specialized triangular leaves return exact sources and do not merely certify existence, dimension, or relation validity.
5. Branch count, degrees, coefficients, reductions, output, rank, factor logs, blind descent, verification, bit time, and memory are charged.

## Semantic fingerprint

`parameterized_relation_ideal | comprehensive_Groebner_specialization_cells | target_basis_selection | triangular_occurrence_source_lift | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; full source construction and target descent remain mandatory.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`; represented elimination must retain exact source provenance and all cost.
3. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a compact source-resolving representation is unconstructed.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform generation remains the missing object.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`; source-product materialization is a no-promotion boundary.

## Closest primary literature

- Weispfenning, [Comprehensive Gröbner bases](https://doi.org/10.1016/0747-7171(92)90023-W), constructs bases valid under every parameter specialization of a supplied parametric ideal.
- Montes, [A new algorithm for discussing Gröbner bases with parameters](https://doi.org/10.1006/jsco.2001.0504), partitions parameter space for a supplied system but does not bound elliptic source branches.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives relation equations without a compact all-target specialization atlas.

No checked source proves subgate branch, degree, coefficient, or source-lift bounds here; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, five disjoint signed decks, complete-chart relation ideal, deck-indicator equations, target parameters, term order, branch policy, restrictions, masks, and verifier.
2. Construct a target-independent comprehensive Gröbner atlas within `B^(9/4)`, retaining every specialization, saturation, multiplicity, and occurrence label without source-product expansion.
3. On known-log targets, select a cell, specialize/reduce its basis, decide restricted existence, bisect deck restrictions, triangularly recover one tuple, and verify its group sum.
4. Collect at least `B` independent verified rows, charge duplicate/dependent rows, solve factor logs, and independently verify them.
5. Reuse the unchanged atlas and term order for fresh scalar-blind `Q+[t]P`, charging exceptional-cell resolution, ambiguity, and mask rebuilds.
6. Recover a tuple, substitute verified factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge ideal construction, every atlas branch, degrees, coefficients, basis reductions, restrictions, source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`; setup/state must be at most `B^(9/4+o(1))`, one complete fresh restricted query at most `B^(5/4+o(1))`, and promotion requires time exponent `lambda<=0.45` and memory exponent `mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

Comprehensive Gröbner systems organize all specializations of an already supplied parametric ideal; they do not shrink the quotient dimension, degree, or number of parameter branches. Finite deck membership injects `B` factors per source coordinate, and exact source labels force the specialized basis to retain the same large fibre. Exceptional cells and arbitrary restrictions can multiply branches, while ordinary Gröbner complexity restores the dense elimination boundary. This merges with IDEAs 060, 068, 098, 194, and 266 unless a new atlas-size/source-lift theorem is proved.

## Proof track

Prove subgate total branch/degree/coefficient bounds for the complete deck ideal, exact all-strata specialization and occurrence lift, and complete exponents at most `0.45`.

## Disproof track

Exhibit deck/target families with `B^3` or larger atlas state, specialization branch explosion, quotient bases of source size, or restriction-induced recomputation beyond the online gate.

## Positive and negative controls

- Positive: supplied low-degree parametric zero-dimensional ideals with known specialization cells and source-labelled roots.
- Negative: deck-indicator ideals, exceptional coefficient cancellations, repeated/nonreduced roots, equal elimination ideals with permuted occurrences, all strata, arbitrary restrictions, and blind targets.
- Baselines: IDEAs 060/068/098/194/266, ordinary Gröbner elimination, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact atlas and source-lift theorems, `1,000` independent verified rows, `100` blind descents, setup/state at most `B^(9/4)`, fresh query at most `B^(5/4)`, and `lambda,mu<=0.45`.
- Falsify on branch/source state above the setup cap, one missed specialization/stratum, source-label ambiguity, supergate restricted replay, or either exponent at least `0.50`.
- A correct specialized basis for a toy ideal is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-378/comprehensive_atlas_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-378/specialization_branch_cases.json`
- `ideas/artifacts/ECDLP-IDEA-378/source_lift_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-378/cost_analysis.md`

## Interpretation boundary

This rejects the screened compact-atlas claim, not comprehensive Gröbner bases. Every finite check would be toy, heuristic, model-bound, and novelty-unverified; basis correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-378/comprehensive_atlas_obligations.md` and bound the specialization branches introduced by one finite deck-indicator coordinate.

