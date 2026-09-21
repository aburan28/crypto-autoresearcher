# Experiment Contract: TYPED-TT-CIRCUIT-NATIVE-ACCOUNTING-V1

## Hypothesis

For the typed five-source predicate, target-independent source sums `(A+R0+R1)` and `(R2+R3)` can be retained as fixed-curve advice. The adaptive cut-3 skeleton then preserves exactness while replacing five direct point additions per queried entry with one online addition plus a separately charged source-preprocessing cost.

## Null hypothesis

The source-sum evaluator disagrees with the direct affine oracle, fails adaptive or held-out validation, requires advice comparable to the full tensor, or loses its cost advantage after all source preprocessing, online reads, predicate arithmetic, relation targets, and supported descent targets are charged.

## Parameters

- input: fresh seed `314159` fixture;
- curves: p = 947, 4027, and 16267;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- cut: `(A,R0,R1)|(R2,R3)`;
- adaptive stop: `max(4, floor(B/2))` dependent prefix fibers;
- validation: all relation targets, first held-out target, and every held-out target supported by both existing descent paths;
- baseline: direct five-addition affine oracle from the sealed adaptive fresh-seed receipt.

## Metrics

- source-advice construction point and field operations;
- advice entry counts, Python retained bytes, and logical payload bytes;
- online point/field operations and logical source-advice reads;
- relation and descent target validation mismatches;
- total charged source-native versus direct-baseline point additions;
- peak RSS, wall time, hashes, and rerun digest.

## Positive control

Every source-native value queried during construction and validation must agree with the direct affine oracle on the same fresh rows.

## Negative control

Run the same source-native evaluator with the existing lexicographic order control. It must reproduce the schedule-sensitive exactness failure rather than silently turning a failed adaptive stop into a success.

## Success criterion

All diagonal-order rows are exact; all supported relation/descent targets replay exactly; source preprocessing and online counters match; and total source-native point additions are strictly below the matched direct baseline for at least one row after advice construction is included.

## Falsification criterion

Any arithmetic mismatch, unsupported target replay, counter disagreement, advice omission, or no charged cost improvement falsifies this source-sum compiler for that row. A cost improvement is a constant-factor fixed-curve result unless a size sweep establishes a different exponent.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_circuit_native_accounting_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-ADAPTIVE-FRESH-SEED-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, and `MODEL-BOUND`. This is a fixed-curve source-evaluation improvement, not a generic ECDLP break or an exponent claim.
