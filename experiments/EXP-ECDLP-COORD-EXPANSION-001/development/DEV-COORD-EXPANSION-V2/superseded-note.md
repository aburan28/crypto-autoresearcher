# Development V2: Superseded Summary

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`DEVELOPMENT_SUPERSEDED_REPORTING_ONLY`.

The exact run completed successfully from source commit `58c61cf1`. It
validated 582 configurations across 10, 12, and 14-bit curves, including
point-only witness recovery, independent D2/D3 versus D5 support equality,
canonical formal-class totals, and factor-base hash immutability.

No candidate/sign cell crossed the frozen Stage-A gate. This is not yet the
canonical development result because the summary grouped exploratory fitted
slopes by each stochastic draw label. That produced a large, noisy collection
of 31 slopes per null family rather than one draw-aggregated family slope.
The underlying per-configuration arithmetic records are unchanged and are
preserved in `raw-result.json`.

## Scope

This reporting defect does not create a false arithmetic pass. It does make
the summary unsuitable as the durable comparison table. The source was
changed only to aggregate null-family scaling points and to distinguish an
eligible development scoped negative from an insufficient-sample result.

## Next concrete action

Rerun the exact frozen sweep from the reporting-fix commit and preserve the
new raw result, compact comparison table, and independent result review.
