# Experiment Contract: TYPED-TT-SAMPLED-LOCATOR-V1

## Hypothesis

A deterministic subset of predicted suffix columns can recover the exact
projected typed-D4 `a`-support (and the held-out expected witness) while
charging substantially less reconstruction work than the full predicted
suffix scan.

## Null hypothesis

Sampled suffix columns miss projected materialized support or relation rank
before the full `B^2` budget, or the full-budget control does not exactly replay
the committed relation transcript.

## Parameters

- input: committed typed-TT relation transcripts for `p=947` and `p=4027`;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- budgets: `1, 2, 4, 8, 16, 32, 64, B^2` columns, clipped to `B^2`;
- row-space: the same adaptive dependent-prefix skeleton as the relation
  transcript;
- candidate: shared fixed-curve source-sum cache plus sampled predicted-zero
  columns;
- baseline: materialized D4 hits already recorded in the committed relation
  transcript;
- controls: full-budget exact-support control and p4027 `source_prf_x` rank
  deficient family.

## Metrics

- sampled predicted entries and fraction of the full tensor;
- candidate hit count, materialized support recall, false-positive count;
- row-space reconstruction field operations;
- source point additions and cache bytes;
- row-space rank and relation rank after sampled hits;
- held-out support and expected-witness coverage.

## Positive control

The full `B^2` suffix budget must reproduce every baseline projected support
hit, valid candidate witness, held-out expected witness, and relation rank for
the committed transcript. Multiple valid `R^4` witnesses for one `a` are
counted separately as extra witnesses, not as projected support mismatches.

## Negative control

Budgeted sampling must report misses when it does not recover support; the
p4027 `source_prf_x` row must preserve its known 8/9 relation rank failure.

## Success criterion

Only a budget below `B^2` that preserves exact projected support, held-out coverage,
and relation rank while reducing charged reconstruction entries is a positive
locator signal. It remains toy, fixed-fixture evidence and is not an ECDLP
break.

## Falsification criterion

Any support miss, false positive, or rank loss at a sub-full budget falsifies
that budget for the tested row. A full-budget mismatch falsifies the producer
or the transcript binding.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/typed_tt_sampled_locator.py \
  development/TYPED-TT-SAMPLED-LOCATOR-V1/RUN-001/relation-input.json \
  development/TYPED-ADAPTIVE-FRESH-SEED-FIXTURE-V1/RUN-001/raw-result.json \
  --budgets 1 2 4 8 16 32 64 full \
  --families random_x source_prf_x x_interval rational_union
```
