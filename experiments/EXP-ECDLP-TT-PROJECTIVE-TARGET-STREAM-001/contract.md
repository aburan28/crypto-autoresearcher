# Experiment Contract: streaming target-cache rank extension

## Hypothesis

Replacing the target-local cache for all targets with a one-target-at-a-time cache preserves exact projective relation behavior while reducing peak memory enough to process a `3B+1` target batch and recover full rank on the second 16-bit curve.

## Null hypothesis

Streaming target-local values either changes support/witness semantics, fails to reduce the resource bottleneck, or does not recover full rank for the `random_x` control.

## Parameters

- field/curve family: one fresh deterministic ordinary prime-order 16-bit curve
- seed: `86420`
- families: `source_prf_x` candidate and `random_x` negative control
- generated targets: `3B+1 = 43`, plus up to four supported held-out targets, for 47 rows
- orbit budgets: `96`, `full`
- inversion weights: `10`, `50`, `100`, `200`
- target cache mode: `streaming-one-target-at-a-time`
- comparators: same-fixture naive affine orbit quotient and original affine full predicate

## Metrics

- exact support, held-out coverage, witnesses, target count, and relation rank
- projective, affine comparator, source-cache, target-cache, and peak-memory counters
- weighted arithmetic cost, wall time, CPU time, relation-matrix operations, and matched rho operations

## Positive control

The streaming candidate must reproduce the full `2B+1` result on the same seed before the `3B+1` extension is interpreted. The full `3B+1` run must preserve exact support and witnesses for both families.

## Success criterion

The independent verifier confirms streaming/full exactness, homogeneous scaling, weighted advantage, memory compliance, and `random_x` rank `15/15` or records a precise rank-negative without any semantic mismatch.

## Falsification criterion

Any support or witness mismatch, target-dependent scaling mismatch, verifier failure, rho failure, weighted reversal, memory-budget violation, or streaming cache leak falsifies the streaming implementation.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001 \
  --run-id RUN-TT-PROJECTIVE-TARGET-STREAM-001 --seed 86420 -- \
  python3 experiments/EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001/src/run_target_stream_harness.py
```

## Claim boundary

This is a target-cache and relation-batch systems experiment on one 16-bit curve. It does not claim a generic prime-field ECDLP break, an asymptotic improvement, fixed-curve preprocessing advantage, individual-log descent, or deployed-key recovery.
