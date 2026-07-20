# ECDLP-IDEA-169 — Nested Hilbert-flag source unranking

## Status and claim labels

- Class: `algebraic-representation`
- Risk band: `representation-changing`
- Top lane: `none`
- State: `rejected_flag_orders_sources_without_compressing_abel_jacobi_fiber`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic no-go only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: finite checks would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a flag, tautological quotient, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The Abel-Jacobi fiber of five-source divisors admits a target-local nested Hilbert flag `Z_1 subset ... subset Z_5` with a canonical tautological filtration. Successive quotients unrank every exact signed factor-base point in sub-rho time and memory, yielding complete relations, factor logs, and masked target descent.

## Mechanism-new operation

The operation is **nested divisor-flag refinement followed by tautological source unranking**. It differs from IDEA-094's torus localization on an auxiliary surface. It qualifies only if the flag is constructed from endpoints without enumerating source orderings and its filtration canonically returns point identities.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta`, nested moduli problem, tautological filtration, masks, and verifier are frozen.
2. Target-local flags are constructed from compact equations without a source divisor or tuple.
3. Successive quotients canonically identify exact signed points, multiplicities, and exceptional strata.
4. Flag degree, ordering branches, unranking, output, and ambiguity remain sub-rho.
5. Construction, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`Abel_Jacobi_source_fiber | nested_Hilbert_flag | tautological_successive_quotients | canonical_point_unranking | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured source-ancestry barrier.
2. `inputs/ledger_inventory.json` — imported `ECFG-H686`, the fixed-curve compiler/advice boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1447`, a held-out source representation no-promotion result.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, the nearest representation/source boundary.
5. `inputs/ledger_inventory.json` — imported `P1476`, the m-ary complete-query exponent boundary.

## Closest primary literature

- Macdonald, [Symmetric products of an algebraic curve](https://doi.org/10.1016/0040-9383(62)90019-8), identifies the governing symmetric-product geometry.
- Graffeo et al., [The geometry of double nested Hilbert schemes of points on curves](https://arxiv.org/abs/2310.09230), supplies nearby nested-flag geometry, not an elliptic source compressor.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies the relation-fiber control.

No checked primary source supplies the proposed unranking pipeline; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the nested moduli equations, flag order, tautological filtration, factor base, masks, and verifier.
2. Construct each target-local flag from public endpoint data without source enumeration.
3. For known `R_j=[r_j]P`, compute successive quotients and unrank every signed point tuple.
4. Verify tuples; preserve ordering branches, collisions, multiplicities, infinity, misses, and output.
5. Collect rank `B`, solve and independently verify factor-base logs.
6. Apply the identical flag construction to fresh `Q+[t]P` masks.
7. Substitute logs, remove masks, retain every candidate, and verify `[x]P=Q`.
8. Charge moduli construction, branches, filtration, unranking, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. Let setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, flag construction/unranking `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Every flag ordering, tautological quotient, source output, and local multiplicity is charged.

## Likely fatal obstruction

For a smooth curve, `Hilb^m(E)=Sym^m(E)`. A nested flag merely orders or refines the same source divisor, adding up to `m!` branches while leaving the Abel-Jacobi fiber degree and source search unchanged. Constructing the flag from an endpoint therefore assumes or enumerates the sources.

## Proof track

An outside-scope successor must exhibit a genuinely compressed target-local flag, prove canonical point unranking, and derive `lambda,mu<=0.45`.

## Disproof track

Identify the flag with ordered symmetric-product data, show construction requires the source divisor, count unchanged fiber degree/output, or derive exponent at least `0.5`.

## Positive and negative controls

- Smooth-curve Hilbert/symmetric products with known divisors.
- Nested flags built from supplied source tuples.
- IDEA-094 localization and direct Abel-Jacobi enumeration controls.
- Exhaustive toy fibers, rho, BSGS, and blind-target checks.

## Quantitative promotion and falsification gates

This version is rejected. Reopening requires a new target-local compressed flag theorem and exact inverse with `lambda,mu<=0.45`. Symmetric-product equivalence, supplied divisors, unchanged fiber output, one lost source, or exponent at least `0.5` is falsifying.

## Artifact plan

- Scoped flag obstruction: `ideas/artifacts/ECDLP-IDEA-169/nested_flag_no_go.md`
- Prospective moduli specification: `ideas/artifacts/ECDLP-IDEA-169/flag_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-169/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-169/cost_analysis.md`

All paths are prospective; no experiment ran.

## Interpretation boundary

This is rejected, scoped, novelty-unverified evidence. Finite checks are toy and projections heuristic and model-bound. A valid flag or relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-169/nested_flag_no_go.md` proving the smooth-curve flag/symmetric-product equivalence and unchanged source-fiber cost.
