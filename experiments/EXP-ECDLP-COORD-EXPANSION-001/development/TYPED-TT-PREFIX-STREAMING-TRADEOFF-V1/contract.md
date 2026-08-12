# Experiment Contract: TYPED-TT-PREFIX-STREAMING-TRADEOFF-V1

## Hypothesis

For the typed five-source predicate, the materialized `A+R0+R1` prefix table can be replaced by a streaming prefix state that retains only the current prefix and the fixed `R2+R3` suffix table. The tradeoff should reduce retained fixed-curve advice while charging the two prefix additions whenever a new prefix is reached.

## Null hypothesis

Streaming prefix state either disagrees with the direct affine oracle, breaks relation or supported held-out descent replay, fails to reduce retained advice, or hides the extra prefix additions from the charged source cost.

## Parameters

- input: fresh seed `314159` fixture;
- curves: `p = 947`, `4027`, and `16267`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- cut: `(A,R0,R1)|(R2,R3)`;
- adaptive stop: `max(4, floor(B/2))` dependent-prefix plateau;
- validation: all relation targets, first held-out target, and every held-out target supported by both existing descent paths;
- baselines: sealed direct affine evaluator and the materialized source-advice receipt.

## Metrics

- streaming suffix and current-prefix entry counts;
- retained Python advice bytes and logical payload bytes;
- source input points and their separately reported payload bytes;
- prefix recomputations and charged point/field operations;
- relation and supported-descent mismatches;
- direct-reference mismatches and sealed baseline bindings;
- rerun digest, hashes, and wall time.

## Positive control

Every streaming source-native value queried during construction and validation must agree with the direct affine oracle on the same fresh rows. The retained advice must be smaller than the corresponding materialized prefix-plus-suffix advice.

## Negative control

Run the same streaming evaluator with lexicographic prefix order. It must preserve the schedule-sensitive adaptive exactness failure while retaining direct-reference arithmetic exactness.

## Success criterion

All diagonal rows are exact; relation and supported held-out descent targets replay exactly; all verifier checks pass; and every row reports lower retained advice than the materialized receipt with prefix recomputation operations included in charged online cost.

## Falsification criterion

Any arithmetic mismatch, unsupported target replay, memory comparison failure, source-operation omission, hash mismatch, or verifier failure falsifies this streaming compiler for that row. A retained-memory reduction is a fixed-curve tradeoff result, not an asymptotic claim.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_streaming_prefix_tradeoff_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-ADAPTIVE-FRESH-SEED-V1/RUN-001/raw-result.json \
  development/TYPED-TT-CIRCUIT-NATIVE-ACCOUNTING-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

`OBSERVATION`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is a fixed-curve advice/memory tradeoff, not a generic ECDLP break and not a claim of beating Pollard rho for a complete attack.
