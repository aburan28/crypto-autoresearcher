# Experiment Contract: second 16-bit relation-batch rank completion

## Hypothesis

The `2B+1` expanded relation batch restores the missing 16-bit projective relation rank on a second fresh ordinary prime-order curve while preserving exact support, held-out witnesses, and weighted arithmetic advantage.

## Null hypothesis

The second curve fails full rank or held-out support, or the extra targets erase the projective weighted advantage after all registered costs are charged.

## Parameters

- field/curve family: one fresh deterministic ordinary prime-order 16-bit curve
- seed: `86420`
- families: `source_prf_x` candidate and `random_x` negative control
- relation targets: `2B+1` generated targets plus up to four supported held-out targets
- orbit budgets: `96`, `full`
- inversion weights: `10`, `50`, `100`, `200`
- comparators: same-fixture naive affine orbit quotient and original affine full predicate

## Metrics

- exact support, held-out coverage, witnesses, target count, and relation rank
- field multiplications, inversions, point additions, cache bytes, lift queries, and relation-matrix operations
- weighted arithmetic cost, wall time, CPU time, and peak RSS
- matched Pollard-rho group operations

## Success criterion

The independent verifier must confirm full support, held-out witnesses, rank `15/15` for both families, homogeneous scaling, weighted projective advantage, and matched rho completion without exceeding the registered `6 GB` memory budget.

## Falsification criterion

Any verifier failure, rank below `15`, loss of held-out support, weighted reversal, rho failure, or memory-budget violation falsifies replication of the first-curve signal.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002 \
  --run-id RUN-TT-PROJECTIVE-RANK-COMPLETION-002 --seed 86420 -- \
  python3 experiments/EXP-ECDLP-TT-PROJECTIVE-RANK-COMPLETION-002/src/run_rank_completion_harness.py
```

## Claim boundary

This is a second one-curve medium-toy replication. It does not claim a generic prime-field ECDLP break, an asymptotic improvement, fixed-curve preprocessing advantage, individual-log descent, or deployed-key recovery.
