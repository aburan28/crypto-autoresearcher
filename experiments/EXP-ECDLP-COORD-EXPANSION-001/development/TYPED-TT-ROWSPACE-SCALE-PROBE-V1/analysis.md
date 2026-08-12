# Analysis: TYPED-TT-ROWSPACE-SCALE-PROBE-V1

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

On the 16-bit fixture with `A=14` and `B=14`, a 64-prefix budget reached rank `64` exactly in all four families and therefore stopped on the explicit prefix budget, not on a dependent-prefix plateau. The probe sampled `164,640` entries per row, or `2.04%` of the full target tensor. `x_interval` had zero sampled mismatches; `random_x`, `source_prf_x`, and `rational_union` had `82,192`, `82,176`, and `82,192` mismatches respectively.

The `random_x` budget controls show rank tracking the budget rather than saturating: rank/mismatches were `16/123,432`, `32/82,256`, and `64/82,192` at prefix budgets `16`, `32`, and `64`. This does not rule out a larger exact rank or a different basis order; it establishes that the current early-prefix construction cannot be treated as complete at this scale.

## Interpretation

The family split is informative but not promotable. The exact sampled result for `x_interval` is a positive structural lead, while the mismatches for the other three families and the absence of a plateau are a scoped negative for this source-aware prefix order and budget. No support or relation claim is made because the probe intentionally avoids full suffix reconstruction.

## Next action

Use `x_interval` as a positive control for a source-derived pivot search, and use `random_x`/`source_prf_x` as negative controls. Move rank construction to a compiled or batched linear-algebra kernel, then test whether a target-parametric transposed operator can exploit the exact family without enumerating all suffix columns.
