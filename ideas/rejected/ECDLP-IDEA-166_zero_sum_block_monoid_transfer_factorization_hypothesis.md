# ECDLP-IDEA-166 — Zero-sum block-monoid transfer factorization

## Status and claim labels

- Class: `algebraic-algorithm`
- Risk band: `high-risk`
- Top lane: `none`
- State: `rejected_scoped_transfer_requires_orientation_or_original_factorization`
- Cohort: `20260718-b`
- Evidence scale: primary-literature and semantic no-go only; no experiment ran
- Contract posture: rejected evidence; no contract or run is authorized
- Scale labels: finite checks would be `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a monoid factorization, zero-sum sequence, relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The signed factor-base block monoid admits a public ECDLP-specific transfer to a factorial or bounded-class monoid whose prime factors invert canonically to exact source atoms. Factoring endpoint classes there would generate complete relations and masked target decompositions below rho and BSGS without scalar labels.

## Mechanism-new operation

The operation is **source-preserving transfer to uniquely factorable atoms followed by inverse transfer**. Standard Krull transfers preserve nonunique factorization and are controls. The new claim requires evaluating the class map from public points, factoring without the original zero-sum search, and returning exact signed sources.

## Assumptions

1. Public `E,P,N,Q,F,B=N^beta` and the signed block monoid are frozen without discrete-log labels.
2. A compact public transfer homomorphism is computable directly from point data.
3. Target factorization has bounded class group, length, ambiguity, and exact atom inverse.
4. No Davenport-scale atom enumeration or hidden scalar orientation is used.
5. Transfer construction, factoring, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`factor_base_zero_sum_block_monoid | public_transfer_homomorphism | bounded_unique_factorization | exact_inverse_source_atoms | masked_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H629`, the nearest algebraic factorization hypothesis.
2. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
3. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the complete source/descent gate.
4. `inputs/ledger_inventory.json` — imported `P1479`, where public features miss scalar orientation.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry barrier.

## Closest primary literature

- Olson, [A combinatorial problem on finite Abelian groups I](https://doi.org/10.1016/0022-314X(69)90021-3), supplies zero-sum/Davenport boundaries.
- Geroldinger, Kainrath, and Reinhart, [Arithmetic of transfer Krull monoids](https://arxiv.org/abs/2104.13788), supplies transfer-factorization controls, not an ECDLP source map.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies neighboring relation search.

No checked primary source supplies the claimed transfer pipeline; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the block monoid, transfer, target monoid, atom normalization, factor base, masks, and verifier.
2. Compute transfer images from public points without scalar labels or source tuples.
3. Factor known endpoints `R_j=[r_j]P` in the target monoid and inverse-transfer every atom.
4. Verify each signed tuple; preserve nonunique factorizations, misses, long atoms, and ambiguity.
5. Collect rank `B`, solve and verify factor-base logs.
6. Apply the same factorization to fresh `Q+[t]P` masks.
7. Substitute logs, remove masks, retain all candidates, and verify `[x]P=Q`.
8. Report class-map construction, factorization length, output, rank, descent, time, and memory.

## Full rho/BSGS cost model

Pollard rho is `N^(1/2+o(1))` time; BSGS is `N^(1/2+o(1))` time and memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, factorization/inverse transfer `N^q,N^q_m`, output/ambiguity `N^o,N^u`, and factor-log algebra `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

These are the complete time and peak-memory exponents.

Davenport length, all factorizations, and class-map orientation are charged.

## Likely fatal obstruction

Evaluating a useful class/transfer map on `<P>` requires scalar labels or another DLP. For `C_N` the Davenport/atom scale reaches `N`, and factoring a zero-sum class into factor-base atoms is the original source search rather than a compression.

## Proof track

An outside-scope successor must give a scalar-blind transfer, bounded factorization theorem, exact inverse, and `lambda,mu<=0.45`.

## Disproof track

Reduce class evaluation to DLP, exhibit atoms of length `N`, prove inverse transfer is the original zero-sum problem, or derive an exponent at least `0.5`.

## Positive and negative controls

- Standard transfer Krull monoids with supplied class labels.
- Small cyclic groups with exhaustive zero-sum atoms.
- Supplied scalar-labelled factor bases as forbidden advice.
- Direct relation search, rho, BSGS, and blind-target checks.

## Quantitative promotion and falsification gates

This version is rejected. Reopening requires a new scalar-blind transfer and bounded exact inverse with `lambda,mu<=0.45`. Scalar labels, Davenport-scale atoms, original zero-sum factoring, one missed source, or exponent at least `0.5` is falsifying.

## Artifact plan

- Scoped obstruction: `ideas/artifacts/ECDLP-IDEA-166/block_monoid_transfer_no_go.md`
- Prospective transfer specification: `ideas/artifacts/ECDLP-IDEA-166/transfer_spec.md`
- Prospective verifier and cost receipt: `ideas/artifacts/ECDLP-IDEA-166/independent_verifier.py` and `ideas/artifacts/ECDLP-IDEA-166/cost_analysis.md`

All paths are prospective; no experiment ran.

## Interpretation boundary

This is rejected, scoped, novelty-unverified evidence. Finite checks are toy and cost claims heuristic and model-bound. A correct factorization or relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-166/block_monoid_transfer_no_go.md` formalizing the class-orientation and Davenport-length obstruction without enumerating atoms.
