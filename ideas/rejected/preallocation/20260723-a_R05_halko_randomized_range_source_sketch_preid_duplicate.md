# Pre-ID duplicate draft — Halko randomized-range source sketch

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R05`; no canonical ID allocated.
- Disposition: `merged_rejected_approximate_low_rank_source_sketch`.
- Class/risk: representation / representation-changing.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; low reconstruction error, a valid row, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, an endpoint-only source operator has numerical rank at most
`N^0.20`; a randomized range finder captures its exact action and a small core factorization
returns signed factor-base occurrences. The complete relation, log, and 100-target descent costs
have time and memory exponents at most `0.45`.

## Mechanism-new operation

The native operation multiplies a supplied matrix by random test vectors, orthogonalizes the
sampled range, and factors the reduced matrix. It counts only if public endpoints provide
operator products without source state and the sampled range preserves exact rare support,
signs, and arbitrary restrictions. Randomized SVD on a materialized source matrix is a control.

## Assumptions

1. The endpoint operator has a provable exact rank gap, not merely spectral decay.
2. Matrix-vector products avoid tuple enumeration, scalar labels, and hidden source dictionaries.
3. Oversampling, power iterations, precision, and failure probability satisfy both caps.
4. The reduced factorization has a charged exact inverse to signed occurrences.
5. Frozen random state is target-independent and valid for fresh masked targets without leakage.

## Semantic fingerprint

`public_endpoint_source_operator | random_test_range_capture | reduced_low_rank_factorization | exact_signed_source_inverse | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-b_B10_cur_skeleton_source_matrix_preid_duplicate.md` — low-rank skeletons consume supplied matrix entries and lose rare rows.
2. `ideas/rejected/preallocation/20260719-b_B11_frequent_directions_source_sketch_preid_duplicate.md` — spectral sketches preserve aggregate energy, not occurrence identity.
3. `ideas/rejected/preallocation/20260721-a_I04_johnson_lindenstrauss_exact_margin_preid_duplicate.md` — approximate random projection does not give exact support.
4. `ideas/rejected/ECDLP-IDEA-341_butterfly_complementary_low_rank_source_transform_hypothesis.md` — structured low rank needs a public operator and exact inverse.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted source return remains the missing owner.

## Closest primary literature

- Halko, Martinsson, and Tropp, [Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions](https://doi.org/10.1137/090771806), samples a supplied matrix to construct approximate low-rank decompositions.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not the required operator products or rank gap.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), is the generic baseline.

Approximate matrix decomposition does not provide exact source semantics; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, operator, random map, oversampling, power schedule, precision, restrictions, strata, and verifier.
2. Build target-independent operator access and sampled basis within `B^(9/4+o(1))`, forbidding source rows and scalar-bearing samples.
3. For each known-log target, factor the reduced operator, replay signed points, and verify the elliptic sum before admitting a row.
4. Collect at least `max(d_FB+32,1000)` verified independent rows, require rank `d_FB`, and solve all factor logs.
5. Reuse byte-identical state on 100 fresh masked targets, recover points, subtract masks, and verify every scalar.
6. Charge operator products, random bits, orthogonalization, power iterations, failure repetitions, reduced solves, replay, rank, logs, bits, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal densities
`N^delta,N^delta_t`; sketch/query work and workspace `N^q,N^q_m`; rank credit `N^r`;
output `N^o`; ambiguity/failure `N^u`; and factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and online work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS retain exponent `0.50`.

## Likely fatal obstruction

Randomized range finding preserves dominant spectral action, not exact singleton support. A rare
source can lie in the residual while all norm tests pass. Exact operator products already encode
the source matrix, and preserving occurrence labels in the basis restores the forbidden state.

## Proof track

Prove endpoint-only products, exact low rank with a restriction-uniform gap, zero-error subcap
range capture, and a signed inverse through full-rank relation collection and blind descent.

## Disproof track

Plant a rare source in the discarded subspace, expose one source-bearing product, show
target-dependent resampling, source-label loss, precision blowup, or exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied exact low-rank toy matrices with planted labelled source factors.
- Negative: low-norm rare rows, equal singular spectra with different sources, empty fibres,
  exceptional strata, seed selection, and fresh blind targets.
- Baselines: CUR, Frequent Directions, JL, P1553 R4, rho, and BSGS.
- Low approximation error is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors at four sizes/all strata, an exact rank theorem,
  full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one discarded true source, approximate-only bound, source-bearing product,
  cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r05_operator_product_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r05_rare_residual_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r05_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not randomized matrix approximation. Spectral accuracy or a valid
relation remains toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Insert one planted singleton source into the orthogonal residual of a toy endpoint operator and test whether the frozen range sketch certifies its existence without source labels.
