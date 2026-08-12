# Experiment Contract: TYPED-TT-STREAMING-BATCH-ACCOUNTING-V1

## Hypothesis

If target specialization is scheduled by prefix rather than by target, one streamed `A+R0+R1` state can serve several target locators before advancing. The resulting charged prefix work per target should decrease with batch size while exact adaptive, relation, and supported-descent replay remains unchanged.

## Null hypothesis

Prefix batching either does not reuse the streamed state, increases charged work after all advice and construction costs, or changes the exact operator and breaks relation/descent replay.

## Parameters

- input: fresh seed `314159` fixture;
- curves: `p = 947`, `4027`, and `16267`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- source split: `(A,R0,R1)|(R2,R3)`;
- batches: `balanced_1`, `balanced_2`, `balanced_4`, `balanced_8`, and `full`;
- each balanced batch contains the first `k` relation targets and first `k` held-out targets supported by both existing descent paths;
- full batch contains all eight relation targets and every supported held-out target;
- every batch uses full tensor validation.

## Metrics

- retained streaming advice and separately reported source-input payload;
- prefix recomputations and total prefix fibers;
- charged point/field operations including source preprocessing, adaptive construction, and target batch work;
- per-target charged work and direct-reference work;
- relation/descent exactness, direct-reference mismatches, measured toy rho reference, hashes, and rerun digest.

## Positive control

The diagonal schedule must preserve exact values for every target in every batch. Prefix recomputations must equal one traversal of the prefix fibers, rather than multiplying by the target count.

## Negative control

The same batched loop under lexicographic prefix order must preserve direct-reference arithmetic while reproducing the existing schedule-sensitive adaptive exactness failure.

## Success criterion

All diagonal batches and full relation/descent replay pass independent verification; every row shows lower retained advice than materialized advice; prefix recomputation count equals the prefix-fiber count; and charged point-add ratio or per-target work decreases from the two-target batch to the larger batches.

## Falsification criterion

Any batch mismatch, missing relation/descent target, direct-reference mismatch, prefix-reuse failure, advice omission, or verifier failure falsifies this batching claim. A small constant-factor target-batch gain remains a fixed-curve implementation result unless a larger size sweep changes the fitted exponent.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_streaming_batch_accounting_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-CIRCUIT-NATIVE-ACCOUNTING-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is a fixed-curve target-batching and advice-accounting result. It is not a generic ECDLP break, an exponent claim, or a complete rho comparison.
