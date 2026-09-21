# ECDLP-IDEA-289 — Hyperbolic-polynomial eigenvalue-cone source section

## Status and claim labels

- Class: `representation_changing`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_convex_eigenvalue_data_cannot_section_finite_field_source_fiber`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid hyperbolicity certificate, cone eigenvalue, relation, recovered label, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

A target-uniform real lift of each ECDLP source fiber admits a compact hyperbolic polynomial whose ordered eigenvalue data and hyperbolicity-cone geometry define a canonical section selecting the exact factor tuple.  Evaluating that section would produce relations and fresh-target descent with complete time and memory exponents below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile the finite-field source equations into a real homogeneous hyperbolic polynomial, follow its ordered directional roots inside a hyperbolicity cone, and decode a canonical eigenvalue-cone section to exact source factors**.  This is a convex representation change, not an interior-point solver substitution.  Güler shows that a supplied hyperbolic polynomial defines a convex cone and a self-concordant barrier; those structures optimize over the cone but do not invert a discrete modular fiber.  A polynomial or determinantal representation whose roots separately label all tuples materializes their product or a source-indexed matrix; a compact coefficient vector or eigenvalue list is symmetric and collides.  The operation merges with materialized-product, affine-pencil, and post-hoc-selector controls.

## Assumptions

1. Public source equations and endpoint canonically produce an exact order-preserving real lift and compact hyperbolic polynomial without enumerating source tuples.
2. Directional roots or cone faces distinguish every relevant tuple despite symmetric coefficients and loss of finite-field ordering.
3. A frozen endpoint-dependent cone section selects one branch and returns exact signed factor-base points on every stratum.
4. Lifting, polynomial degree and coefficients, determinantal size, root isolation, precision, cone navigation, branch output, factor logs, descent, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | real_hyperbolic_source_lift | directional_root_cone_geometry | canonical_source_section | exact_factor_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, the full-rank representation transform without source inversion.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the explicit source-root product control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the symmetric spectral summary without exact output.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1430-EXACT-AFFINE-PENCIL-SECANT-CONTROL`, the exact affine-pencil/eigenvalue control.

## Closest primary literature

- Güler, [Hyperbolic Polynomials and Interior Point Methods for Convex Programming](https://doi.org/10.1287/moor.22.2.350), proves convexity and barrier properties for hyperbolicity cones of supplied homogeneous polynomials; it does not construct a discrete source-fiber inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the modular multivariate source equations whose bounded solutions the real cone representation would have to preserve and return exactly.

No checked primary source gives an injective compact real-hyperbolic lift and canonical cone section for ECDLP source tuples; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source equations, real-lift compiler, hyperbolicity direction, root-order convention, cone section, masks, and verifier.
2. For random known-log endpoints, construct the compact hyperbolic polynomial and exact cone data without enumerating source tuples.
3. Isolate directional roots, apply the section, decode every accepted branch to exact signed factor points, and verify each resulting relation.
4. Collect independent relation rows, solve the row system, and independently verify every factor log.
5. Apply the identical frozen real lift, polynomial construction, and cone section to fresh masked targets `Q+[t]P` with hidden masks.
6. Decode all surviving eigenvalue/cone branches to a complete factorization or scalar residue, remove the mask, and verify the target endpoint.
7. Accept only exact `[x]P=Q`, charging real lifting, polynomial/determinantal construction, root isolation, precision, section ambiguity, source output, factor logs, fresh-target descent, and peak state.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one lift/polynomial/cone/decode attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, returned eigenvalue/source output be `N^o`, unresolved cone-section ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every lifted coefficient, polynomial monomial, matrix entry, directional root, isolation interval, precision bit, cone face, barrier evaluation, branch, factor point, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Hyperbolicity-cone geometry is real, convex, and continuous, whereas the source fiber is modular, discrete, and many-to-one.  Polynomial coefficients and unordered root data are symmetric summaries, so distinct tuple labelings collide; an ordering is external and cannot create missing arithmetic information.  Encoding one root, face, or eigenvector per tuple makes degree, determinantal size, or output source-sized, while a post-hoc cone direction that selects the desired tuple imports the witness.  Convex navigation therefore cannot supply a canonical exact finite-field section.

## Proof track

Construct an exact witness-free real lift, prove tuple injectivity through hyperbolic coefficients and ordered roots, prove a frozen canonical section with exact factor return, and certify complete `lambda,mu<=0.45` including degree and precision.

## Disproof track

Exhibit distinct source tuples with the same polynomial/eigenvalue data, prove polynomial degree, matrix size, isolation precision, or output at least `N^0.50`, show the lift or direction imports the tuple, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied toy hyperbolic polynomial with rational coefficients, simple labelled directional roots, and an independently certified cone.
- Negative controls: root permutations, repeated roots, modular inputs with identical real summaries, explicit source-root products, tuple-indexed determinantal pencils, post-hoc cone directions, interior-point solver swaps, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires an exact witness-free injective lift, frozen canonical all-strata section, exact factor return, blind fresh-target descent, and complete `lambda,mu<=0.45`.  A root/label collision, source-indexed polynomial, degree/matrix/precision/output exponent at least `0.50`, missing exact finite-field return, or either complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-289/hyperbolic_cone_section_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-289/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-289/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-289/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative representation-changing proposal.  Every finite hyperbolicity check would be toy and projections heuristic and model-bound.  A correct cone, eigenvalue, relation, or toy scalar does not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-289/hyperbolic_cone_section_theorem.md` proving compact exact source selection or the symmetry/degree/real-lift obstruction.
