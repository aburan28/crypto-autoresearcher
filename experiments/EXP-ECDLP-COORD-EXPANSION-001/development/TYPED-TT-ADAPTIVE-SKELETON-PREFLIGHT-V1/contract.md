# Experiment Contract: TYPED-TT-ADAPTIVE-SKELETON-PREFLIGHT-V1

## Hypothesis

An adaptive source-prefix fiber search can stop on a preregistered rank plateau, discover the exact cut-3 skeleton without an imported rank budget, and preserve exact target specialization.

## Null hypothesis

The plateau rule stops before a later independent prefix direction, reaches all prefix fibers, or produces a skeleton that fails target or held-out reconstruction.

## Parameters

- curves: the three frozen ordinary prime-field curves from `TYPED-FIVE-EC-V1`;
- families: `random_x`, `source_prf_x`, `x_interval`, and `rational_union`;
- cut: 3, prefix `(A,R0,R1)`, suffix `(R2,R3)`;
- rank discovery: no exact-rank input; stop after `max(4, floor(B/2))` consecutive dependent prefix fibers after the latest rank increase;
- prefix order: diagonal source prefixes followed by lexicographic completion;
- targets: first eight relation targets plus first held-out target;
- validation: full toy tensor entry replay, separately charged from construction.

## Metrics

- discovered rank and plateau window;
- prefix fibers examined and construction query count;
- target-specialization selected-column queries;
- exact validation mismatches;
- affine operations, field operations, memory, wall time, and stopping reason.

## Positive control

A rank-one synthetic oracle must stop after its plateau and reconstruct exactly.

## Negative control

A synthetic oracle with a delayed independent direction must either continue until that direction is found or fail validation; it must not claim success from the plateau alone.

## Success criterion

All relation and held-out targets reconstruct exactly, the adaptive rank equals the independently recorded exact rank, and at least one row stops after fewer than all prefix fibers with specialization below full tensor cost.

## Falsification criterion

Any delayed-direction mismatch, full-prefix scan, rank disagreement, or target mismatch falsifies this stopping rule for that row. This does not rule out a different adaptive certificate or circuit-native rank test.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_adaptive_skeleton_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This is `TOY-EVIDENCE` and `MODEL-BOUND`. It is an adaptive tensor skeleton preflight, not a generic ECDLP algorithm or relation attack.
