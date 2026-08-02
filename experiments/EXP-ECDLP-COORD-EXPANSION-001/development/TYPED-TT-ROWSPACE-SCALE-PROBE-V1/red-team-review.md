# Red-Team Review: TYPED-TT-ROWSPACE-SCALE-PROBE-V1

## Verdict

Accept as a bounded construction and sampled-validation receipt. Do not promote the `x_interval` sampled match to full row-space exactness.

## Checks

1. The 64-prefix bound is explicit and every row stops because of that budget.
2. The sample is direct source-advice validation, not a self-consistency check against reconstructed values alone.
3. Three families fail sampled exactness, preventing a broad coordinate-family claim.
4. The `random_x` 16/32/64 controls show rank growth with budget and remain mismatched.
5. The independent verifier binds the producer, row-space helper, input fixture, and result digest.

## Remaining objections

- The scale probe does not build a complete basis or enumerate full support.
- `x_interval` has only sampled exactness on one 16-bit curve and is not a cryptographic-scale result.
- Pure-Python row reduction is a systems bottleneck and its timings are not an asymptotic field-operation theorem.
- No relation matrix, individual descent, or matched rho comparison is included.

## Required follow-up

Implement batched/compiled row reduction and a source-derived pivot order, then repeat with full rank and held-out target support. Keep the three failing families as negative controls and require complete fixed-curve cost accounting before promotion.
