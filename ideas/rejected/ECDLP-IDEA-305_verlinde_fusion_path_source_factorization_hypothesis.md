# ECDLP-IDEA-305 — Verlinde fusion-path source factorization

## Status and claim labels

- Class: `categorical_representation`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_fusion_coefficients_aggregate_supplied_labelled_paths`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a modular identity, correct fusion coefficient, relation, or toy factor path is not an ECDLP break.

## Falsifiable hypothesis

Factor points and signs can be compiled into simple objects of a finite modular category so that elliptic addition is fusion, the modular `S` matrix diagonalizes endpoint convolution, and an inverse Verlinde transform canonically returns every exact source fusion path for relations and blind target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **compile factor atoms as simple objects, represent endpoint addition by fusion, diagonalize fusion through the modular `S` matrix, and invert conformal-block/fusion-path coefficients to exact factor points**. Verlinde diagonalizes a supplied fusion ring and returns aggregate multiplicities. A path-faithful basis or one simple-object label per factor point imports a source-sized category/deck. The operation merges with IDEAs 072, 095, 127, 225, and 287.

## Assumptions

1. A finite-field, target-uniform modular category is constructible without source-labelled simples.
2. Its fusion product is biconditional with signed elliptic factor addition on every stratum.
3. Modular data canonically separates fusion paths and lifts them to exact factor points.
4. Category construction, ranks, `S` matrices, path output, relation rank, factor logs, descent, verification, time, and memory are charged.

## Semantic fingerprint

`elliptic_factor_modular_category | fusion_endpoint_product | Verlinde_S_diagonalization | fusion_path_exact_factor_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `TRANSFER-H008`, the supplied categorical/Jacobian transfer control.
2. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-054`, the same-hard-factor representation boundary.
3. `inputs/ledger_inventory.json` — imported `PO96`, the realization and pushforward control.
4. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate expansion boundary.
5. `inputs/ledger_inventory.json` — imported `P1479`, the composed-transition/source-return control.

## Closest primary literature

- Verlinde, [Fusion rules and modular transformations in 2D conformal field theory](https://doi.org/10.1016/0550-3213(88)90603-7), relates fusion coefficients to modular transformation data for supplied primary labels.
- Beauville, [Conformal blocks, fusion rules and the Verlinde formula](https://arxiv.org/abs/alg-geom/9405001), gives an algebro-geometric treatment of conformal-block dimensions and fusion.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies endpoint equations without a modular category or labelled fusion inverse.

No checked source gives the hypothesized elliptic compiler, point-faithful inverse, or full sub-rho path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, category, simple-object map, modular data, masks, and verifier.
2. Compile random known-log endpoints into fusion objects without enumerating factor tuples.
3. Apply Verlinde diagonalization, invert every accepted fusion path to exact signed points, and verify relations.
4. Collect independent rows, solve and verify the complete factor-log system.
5. Apply the identical fusion compiler/inverse to fresh masked targets `Q+[t]P`.
6. Substitute factor logs, remove masks, preserve multiplicity and ambiguity, and return candidates.
7. Accept only exact `[x]P=Q`, charging category state, modular matrices, path bases, outputs, failures, rows, logs, descent, verification, and memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, base `N^beta`, reciprocal densities `N^delta,N^delta_t`, one fusion/Verlinde/inverse `N^q,N^q_m`, rank gain `N^r`, output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes exact path inverse and verification; `o` includes all fusion paths. Rho has expected time exponent `1/2` with negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Fusion multiplicities count channels but do not name basis paths or elliptic points. A source-faithful modular category needs factor-point-labelled simples, conformal-block basis vectors, or equivalent incidence, making category rank, modular data, or path output source-sized. Modular diagonalization changes basis after that data exists.

## Proof track

Construct a compact target-uniform category, prove a fusion/source biconditional and canonical path inverse for every stratum, then prove row rank, factor logs, blind descent, and full `lambda,mu<=0.45`.

## Disproof track

Exhibit distinct factor paths with the same fusion object/modular data, or prove any point-separating refinement requires one simple/basis vector per source atom/path and reaches rho-or-worse state/output.

## Positive and negative controls

- Positive: a supplied finite fusion category with labelled paths must reproduce known coefficients and path lifts.
- Negative: basis-permuted conformal blocks with identical modular data must not pass exact point recovery.
- Baselines: explicit fusion-path enumeration, IDEAs 072/095/127/225/287, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with independent all-strata proofs, 1,000 verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if category/path state or output reaches `N^0.50`, point labels are supplied, modular data is path-ambiguous, or any source stratum is absent.
- Exponents in `(0.45,0.50)` remain inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-305/verlinde_source_biconditional.md`
- `ideas/artifacts/ECDLP-IDEA-305/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-305/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-305/cost_analysis.md`

## Interpretation boundary

This is a preserved semantic merge, not a no-go for all modular-category encodings. A correct fusion rule or relation does not provide the required exact point inverse, factor logs, blind descent, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-305/verlinde_source_biconditional.md` proving a compact modular-category path-to-point inverse or the scoped path-basis/source-size obstruction before any code.
