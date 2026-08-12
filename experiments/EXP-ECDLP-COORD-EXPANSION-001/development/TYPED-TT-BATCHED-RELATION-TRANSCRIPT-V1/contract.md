# Experiment Contract: TYPED-TT-BATCHED-RELATION-TRANSCRIPT-V1

## Hypothesis

A target-independent source-sum cache can be carried through an exact typed
row-space locator to produce witness-bearing quotient relation rows for a
fixed-curve target batch, with the same support and matrix rank as a
target-separated control.

## Null hypothesis

The source-sum saving disappears once exact witness validation, D4 support
comparison, quotient matrix insertion, and all source/predicate/reconstruction
costs are charged.

## Parameters

- input: committed `TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1` raw fixture;
- curve: the smallest committed ordinary prime-order fixture,
  `recursive-toy-p947-a659-b11-q971`;
- coordinate families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- target stream: six `family.run_seed xor 0x13198A2E` relation targets plus up
  to four supported held-out targets from the fixture;
- row-space: adaptive cut-3 dependent-prefix construction, with no imported
  rank target;
- locator: all predicted suffix columns, with direct source queries only at
  pivot columns and at the adaptive build prefixes;
- candidate: source sums shared across the entire target batch;
- control: source sums separated by target and discarded after each target;
- baseline: independently rebuilt materialized typed D4 support and witnesses.

## Metrics

- candidate and control source point additions, field operations, cache bytes,
  and unique source sums;
- target predicate and row-space reconstruction operations;
- exact candidate witness count and direct witness-validation operations;
- D4 baseline build/query operations;
- candidate/control quotient matrix rank and insertion operations;
- support equality, direct reference mismatches, and row-space ranks;
- wall time for orientation only.

## Positive control

The exact small-curve row-space fixture has already passed full support and
witness replay. The shared cache should preserve those exact witnesses and the
recorded held-out witnesses while reducing repeated target-independent source
additions.

## Negative controls

- target-separated source sums use the same query schedule but cannot reuse
  source points across target indices;
- all four public coordinate families are compared on every curve;
- matrix rank and support equality are required, not inferred from source
  predicate zeros alone.

## Success criterion

Both modes must produce valid witnesses, identical per-target support, and the
same quotient rank. The shared mode must show a strict source point-add saving
at full batch width. This is a fixed-curve relation/compiler observation only.

## Falsification criterion

Any support mismatch, invalid witness, direct reference mismatch, rank loss, or
failure to reduce source work falsifies the batching hypothesis for that row.
No source saving may promote the method without matrix/descent and matched-rho
accounting.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_batched_relation_transcript.py \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --curve-id recursive-toy-p947-a659-b11-q971 \
  --families random_x source_prf_x x_interval rational_union
```
