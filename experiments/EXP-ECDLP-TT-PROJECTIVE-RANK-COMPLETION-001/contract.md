# Experiment Contract: 16-bit relation-batch rank completion

## Hypothesis

The 16-bit full-rank deficit is caused primarily by the registered relation batch containing only `B+1` generated targets. Increasing the target batch to `2B+1`, while keeping the projective locator, families, class budgets, and comparator cost model fixed, will restore the required `B+1` relation rank without changing zero support.

## Null hypothesis

Additional targets do not restore rank, or the extra relation work and memory erase the projective arithmetic advantage. A rank increase without full support, held-out witnesses, and charged target cost is not a positive result.

## Parameters

- field/curve family: one fresh deterministic ordinary prime-order 16-bit curve
- seed: `97531`
- families: `source_prf_x` candidate and `random_x` negative control
- relation target count: `2B+1` generated targets plus up to four supported held-out targets
- orbit budgets: `96`, `full`
- inversion weights: `10`, `50`, `100`, `200`
- comparators: same-fixture naive affine orbit quotient and original affine full predicate

## Metrics

- target count, full and sub-full support, held-out coverage, witnesses, and relation rank
- projective, naive, and original field multiplications, inversions, point additions, cache bytes, and lift queries
- weighted arithmetic cost and amortized cost per generated relation target
- relation equations, matrix operations, witness operations, and matched rho operations

## Positive control

The full projective candidate must pass exact support, witnesses, and rho. The candidate rank must reach `B+1=15` for both families, and the weighted projective cost must remain below both comparators after the larger target batch is charged.

## Negative control

`random_x` uses the same expanded target transcript and is not tuned after observing rank. The `96` class budget remains a strict sub-full control.

## Success criterion

This is a rank-completion signal only if the independent verifier confirms full target-matrix rank, exact support, held-out witnesses, homogeneous scaling, and weighted comparator advantage. It does not establish an individual-log descent or an exponent improvement.

## Falsification criterion

Failure to reach rank 15, any arithmetic/support mismatch, weighted cost reversal, or verifier failure falsifies the target-batch explanation for this curve and representation.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001 \
  --run-id RUN-TT-PROJECTIVE-RANK-COMPLETION-001 --seed 97531 -- \
  python3 experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-001/src/run_rank_completion_harness.py
```

## Claim boundary

This is a one-curve medium-toy relation-batch control. It does not claim a generic prime-field ECDLP break, a new asymptotic algorithm, deployed-key recovery, or individual-log descent.
