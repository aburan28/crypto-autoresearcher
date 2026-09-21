# Experiment Contract: TYPED-TT-RELATION-DESCENT-BINDING-V1

## Hypothesis

The exact adaptive tensor operator can be bound to actual typed relation targets and to all held-out targets that the existing materialized-D4 and R+D3 descent paths support.

## Null hypothesis

Target labels do not match the relation/descent transcripts, relation witnesses are absent, or the operator fails when replayed on supported held-out targets.

## Parameters

- input: fresh seed 314159 fixture;
- rows: 12;
- relation targets: first eight target transcript entries;
- descent targets: every held-out transcript entry supported by both descent paths;
- validation: full tensor replay per bound target.

## Metrics

- independent relation equation count and witness presence;
- supported descent target count and success probability;
- specialization and validation queries;
- exact mismatches for relation and supported descent targets.

## Success criterion

All target bindings, relation witnesses, relation replays, and supported descent replays pass with zero mismatches, while breakthrough and promotion flags remain false.

## Falsification criterion

Any label mismatch, absent witness, unsupported target replay, or nonzero mismatch falsifies this binding for that row.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_relation_descent_binding_preflight.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  development/TYPED-TT-ADAPTIVE-FRESH-SEED-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This binds exact toy tensor replay to existing relation/descent transcripts. It does not solve the relation matrix, recover a new discrete logarithm, or establish an ECDLP improvement.
