# Experiment Contract: TYPED-EXACT-TT-FACTOR-PREFLIGHT-V1

## Hypothesis

Exact finite-field TT factorization of a toy recursive-coordinate locator tensor can reduce the raw direct-sum/Kronecker bond schedule while preserving every tensor entry.

## Null hypothesis

Exact factorization does not reduce the raw closure payload, or reconstruction fails on one or more entries.

## Parameters

- field/curve family: the three frozen ordinary prime-field curves from `TYPED-FIVE-EC-V1`;
- sizes: all three curve instances and all four factor-base families;
- seeds: frozen by the input receipt; one recorded target per family;
- tensor: `h(A,R0,R1,R2,R3) = (x(S)-x(Q))^2 - nu (y(S)-y(Q))^2` over `F_p`, with `S=A+R0+R1+R2+R3`;
- factorization: exact sequential TT rank factorization over `F_p` using modular Gaussian elimination;
- baseline: raw direct-sum/Kronecker shape schedule from the preceding preflight;
- source tuple enumeration: enabled for this diagnostic only.

## Metrics

- exact TT bond ranks at all four cuts;
- raw and exact core payload entries using the actual tensor dimensions;
- exact-to-raw compression ratio;
- enumerated tensor entries and affine group-operation counters;
- finite-field elimination operations and peak RSS;
- reconstruction mismatches and tensor/core digests.

## Positive control

A rank-one tensor with the same mode dimensions must factor with all internal TT bonds equal to one and reconstruct exactly.

## Negative control

A deterministic rank-two synthetic tensor must produce an internal bond greater than one at a prescribed middle cut.

## Success criterion

All rows reconstruct exactly, the positive control passes, and at least one ordinary-curve row has an exact payload strictly below its raw closure payload.

## Falsification criterion

Any reconstruction mismatch, failed control, or no payload reduction across all rows falsifies this toy compression hypothesis for the tested tensors. This does not rule out approximate, cross, common-basis, or non-enumerative compression.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_exact_tt_factor_preflight.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union
```

## Claim boundary

This is `TOY-EVIDENCE` and `MODEL-BOUND`. It measures a materialized locator tensor, not relation generation, factor-base construction, sparse linear algebra, target descent, or a generic-prime-field ECDLP algorithm.
