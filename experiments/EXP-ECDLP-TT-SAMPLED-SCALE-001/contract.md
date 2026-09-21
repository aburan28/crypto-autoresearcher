# Experiment Contract: EXP-ECDLP-TT-SAMPLED-SCALE-001

## Hypothesis

The hash-ranked sampled suffix selector that retained projected relation support
on smaller fixtures also retains support and quotient rank at the next fresh
ordinary curve, `p=16267`, while reducing predicted-suffix work below the full
`A B^4` scan.

## Null hypothesis

Every sub-full suffix budget either misses projected D4 support, loses held-out
coverage or quotient rank, or fails to reduce fully charged source/reconstruction
work after matched Pollard-rho accounting.

## Parameters

- fixture: seed `314159`, curve `recursive-toy-p16267-a10934-b358-q16057`;
- dimensions: `A=12`, `B=10`, four public families;
- targets: `B+1` deterministic relation targets plus up to four supported held-out targets;
- suffix budgets: `8,16,32,64,full`, where `full=B^2=100`;
- candidate: adaptive cut-3 row-space reconstruction with a shared source-sum cache;
- baseline: independently materialized typed D4 support, not the candidate tensor;
- generic baseline: harness Pollard-rho on every public target, with direct point verification.

## Controls

- full suffix budget is an exact replay control;
- all four coordinate families are retained, including the prior rank-deficient
  `source_prf_x` family as a negative control;
- matched rho is run on the same curve, generator, and public targets;
- a separate verifier regenerates the D4 transcript, checks every candidate
  witness/support record, recomputes quotient-rank metadata, and reruns direct
  rho certificate checks.

## Metrics

- projected support recall and missed/false-positive `a` indices;
- held-out expected-witness coverage and candidate witness validity;
- row-space rank and quotient relation rank;
- sampled/full predicted-entry fraction;
- source point additions, cache bytes, reconstruction field operations;
- rho solved count and total group operations;
- wall time, CPU time, and peak RSS from the harness runner.

## Success criterion

At least one sub-full budget must preserve exact projected support, held-out
coverage, valid witnesses, and relation rank on a fresh p16267 row while
reducing charged predicted entries and source/reconstruction work. This is a
locator optimization signal only; it is not an ECDLP or exponent claim.

## Falsification criterion

The full-budget control fails, or all sub-full budgets miss support/held-out
coverage, lose rank, or provide no cost reduction after the complete accounting.

## Reproduction

```bash
PYTHONPATH=src python3 -m crypto_autoresearcher run \
  --repo . \
  --experiment-dir experiments/EXP-ECDLP-TT-SAMPLED-SCALE-001 \
  --run-id RUN-TT-SAMPLED-001 \
  --seed 314159 \
  --allow-dirty \
  -- \
  python3 experiments/EXP-ECDLP-TT-SAMPLED-SCALE-001/src/run_sampled_scale_harness.py
```
