# Experiment Contract: TYPED-TT-TARGET-COMMON-BASIS-PREFLIGHT-V1

## Hypothesis

For a fixed curve and factor-base family, several target-conditioned locator tensors share source-side row or column spaces, so target-specialized TT advice can be amortized without a proportional rank explosion.

## Null hypothesis

Stacking target locator unfoldings expands the shared rank to the ambient or target-multiplied dimension, eliminating useful fixed-curve basis reuse.

## Parameters

- curves: the three frozen ordinary prime-field curves from `TYPED-FIVE-EC-V1`;
- families: `random_x`, `source_prf_x`, `x_interval`, and `rational_union`;
- targets: first relation target and first held-out descent target, deduplicated;
- source tensor: the exact affine five-source quadratic locator used by the exact-TT preflight;
- common basis: row-union and column-union ranks of the target-stacked middle unfoldings at cuts 2 and 3;
- source tuple enumeration: enabled for this diagnostic only.

## Metrics

- target count and target tensor entries;
- single-target and stacked row/column ranks;
- ambient and target-multiplied rank fractions;
- shared-basis payload estimates;
- affine group operations, modular elimination operations, memory, and wall time;
- tensor and rank digests.

## Positive control

Duplicating the same target must leave every shared rank equal to the single-target rank.

## Negative control

A deterministic pair of independent synthetic matrices must increase the stacked rank.

## Success criterion

At least one ordinary-curve family retains a shared middle-cut rank substantially below the target-multiplied ambient dimension while preserving a target-specializable basis.

## Falsification criterion

If target stacking reaches ambient rank at the relevant cuts across all rows, the common-basis hypothesis is a scoped negative for these tensors. This does not rule out target-independent nonlinear selectors or circuit-level representations.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_target_common_basis_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This is `TOY-EVIDENCE` and `MODEL-BOUND`. It does not measure relation collection, target descent, sparse linear algebra, online work, or a generic ECDLP improvement.
