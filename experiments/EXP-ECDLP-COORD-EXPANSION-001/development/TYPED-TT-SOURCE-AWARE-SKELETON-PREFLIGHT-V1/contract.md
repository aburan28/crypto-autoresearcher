# Experiment Contract: TYPED-TT-SOURCE-AWARE-SKELETON-PREFLIGHT-V1

## Hypothesis

A source-prefix-only basis search can discover the exact cut-3 row skeleton by evaluating fewer than all prefix fibers, then specialize multiple targets through selected suffix columns without materializing the full base tensor.

## Null hypothesis

The structured prefix order must inspect essentially every prefix fiber, fails to reach the exact rank, or target specialization requires full suffix tensors.

## Parameters

- curves: the three frozen ordinary prime-field curves from `TYPED-FIVE-EC-V1`;
- families: `random_x`, `source_prf_x`, `x_interval`, and `rational_union`;
- cut: 3, with prefix `(A,R0,R1)` and suffix `(R2,R3)`;
- rank budget: sealed exact-TT cut-3 rank per row;
- prefix order: diagonal source prefixes first, followed by lexicographic completion;
- targets: first eight relation targets plus first held-out target;
- source tuple enumeration: forbidden in construction; full tensor evaluation is a separately charged validation phase.

## Metrics

- candidate prefix fibers examined and basis fibers queried;
- source-aware construction queries and query ratio versus a full base tensor;
- exact skeleton rank, pivot columns, and basis storage;
- target-specialization selected-column queries;
- full validation mismatches for relation batches and held-out target;
- affine operations, field operations, memory, and wall time.

## Positive control

The sealed exact skeleton rank and a duplicated target must reconstruct exactly from the source-aware basis.

## Negative control

A requested rank above the exact cut rank must fail closed without claiming a construction.

## Success criterion

All target batches and the held-out target reconstruct exactly, and at least one row discovers its basis after querying strictly fewer than all prefix fibers and specializes each target with fewer than full tensor entries.

## Falsification criterion

Any construction failure, validation mismatch, full-prefix discovery, or full-target specialization falsifies this source-aware candidate for that row. This does not rule out a different prefix ordering, pivot rule, cut, or circuit-native representation.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_source_aware_skeleton_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  development/TYPED-EXACT-TT-FACTOR-PREFLIGHT-V1/RUN-001/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This is `TOY-EVIDENCE` and `MODEL-BOUND`. It is a source-aware tensor compiler preflight; it does not establish a generic ECDLP improvement, relation collection, matrix rank, or individual-log descent.
