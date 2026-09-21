# Analysis: TYPED-TT-SHARED-PREFIX-CONSTRUCTION-PREFLIGHT-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

An exact cut-3 row skeleton built from the first relation target reconstructed every relation target in batches `K in {1,2,4,8}` and the first held-out descent target for all 12 curve/factor-base rows. All synthetic controls passed and the committed verifier replay is exact.

The skeleton ranks were `15` or `14` for B=5, `36` for B=8, and `55` for B=10. The charged per-target selected-column specialization cost was `0.60`, `0.56`, `0.562`, and `0.55` of a full cut-3 tensor for the corresponding rows. This ratio was independent of batch size because the same source-prefix skeleton was reused. The full run materialized nine target tensors per row, took approximately 59.8 seconds, and used approximately 83 MiB peak RSS.

## Interpretation

This is a constructive fixed-curve representation signal: a target-independent source-prefix skeleton can support exact target specialization on the tested relation and held-out targets. It strengthens the earlier cut-3 row-space observation because it produces explicit basis rows, pivot columns, and exact coefficients rather than only ranks.

The result is still not a cryptanalytic improvement. Skeleton discovery and validation enumerated all target tensors; the reported `0.55-0.60` specialization ratio is a hypothetical per-target application cost after the skeleton exists. The experiment does not compile the skeleton from the RCB circuit, charge persistent advice bytes or memory bandwidth in a deployed setting, collect relations, solve a relation matrix, or perform an individual logarithm.

## Next action

Replace the enumerative base-target skeleton discovery with a circuit-native or source-aware constructor. Then run fresh seeds and compare fixed-curve offline work, retained advice, memory traffic, target count, success probability, relation rank, target descent, and optimized rho under one field-operation cost model.
