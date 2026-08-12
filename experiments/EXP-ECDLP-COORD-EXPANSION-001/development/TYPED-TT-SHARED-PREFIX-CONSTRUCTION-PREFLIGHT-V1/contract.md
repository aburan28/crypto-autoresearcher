# Experiment Contract: TYPED-TT-SHARED-PREFIX-CONSTRUCTION-PREFLIGHT-V1

## Hypothesis

The cut-3 source-prefix row space can be represented by one exact base-target skeleton and reused for multiple target locators, reducing target-specialization entries below a full target tensor while preserving exact reconstruction.

## Null hypothesis

The base-target skeleton fails on larger target batches or the held-out target, or its charged basis/discovery cost dominates any specialization saving.

## Parameters

- curves: the three frozen ordinary prime-field curves from `TYPED-FIVE-EC-V1`;
- families: `random_x`, `source_prf_x`, `x_interval`, and `rational_union`;
- cut: source cut 3, dimensions `[A,R0,R1] x [R2,R3]`;
- base target: first relation target;
- target batches: first `K` relation targets for `K in {1,2,4,8}`;
- held-out check: first held-out descent target, excluded from the relation batch when distinct;
- skeleton: exact independent prefix rows and pivot suffix columns over `F_p`;
- source tuple enumeration: enabled for discovery and exact validation only.

## Metrics

- skeleton rank and basis/core entries;
- base discovery entries and affine field operations;
- per-target selected-column specialization entries;
- full target tensor entries and specialization ratio;
- batch reconstruction mismatches and held-out mismatches;
- rank growth, modular elimination, memory, and wall time.

## Positive control

Duplicated base targets must reconstruct exactly from the same skeleton at every batch size.

## Negative control

A deterministic synthetic target matrix with an extra independent row direction must be rejected by the base skeleton.

## Success criterion

All batches and the held-out target reconstruct exactly, and at least one ordinary-curve row has specialization entries strictly below a full target tensor after the fixed skeleton is retained.

## Falsification criterion

Any mismatch, rank growth beyond the selected skeleton, or specialization cost at or above full tensor cost falsifies this shared-prefix construction for that row. This does not rule out a different cut, nonlinear basis, or circuit-native compiler.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_shared_prefix_construction_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This is `TOY-EVIDENCE` and `MODEL-BOUND`. It is a fixed-curve tensor representation preflight, not a relation generator, individual-log algorithm, or generic-prime-field ECDLP break.
