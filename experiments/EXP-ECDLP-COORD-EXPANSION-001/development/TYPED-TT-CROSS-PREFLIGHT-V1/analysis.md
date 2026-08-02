# Analysis: TYPED-TT-CROSS-PREFLIGHT-V1

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

## Result

The pilot-guided cross-unfolding compiler failed its strict success criterion on all 12 rows. At cuts 2 and 3, seeded random suffix-column choices failed to span the requested exact ranks on every row within 16 trials. Cuts 1 and 4 passed their 64 holdouts, but their requested ranks equal the smaller ambient dimension, so their selected fibers cover the full tensor in charged query count.

The unique oracle-query ratio was exactly `1.0` for every row. Thus this implementation did not obtain a query reduction despite avoiding an explicit `B^5` product loop. The distinction matters: a structurally non-enumerative source path can still pay full tensor evaluation cost through its selected fibers.

## Interpretation

This is a scoped negative for the pilot-guided random cross skeleton. It identifies two concrete obstructions:

1. near-ambient exact ranks make cross payload/query savings disappear at end cuts;
2. random column selection is not a reliable rank-revealing mechanism for the middle cuts of these locator tensors.

It does not rule out max-volume pivoting, structured elliptic fibers, shared bases across targets, approximate compression, or a circuit-level contraction that never evaluates the full unfolding. It also does not weaken the preceding exact-factorization observation: raw closure bonds remain far above exact ranks.

## Accounting

All oracle queries were cached and charged, along with affine group operations, field inversions, field multiplications, modular elimination, holdout checks, wall time, and peak RSS. The pilot rank budget came from the sealed exact factorization receipt and was not treated as free attack work.

## Next action

Do not repeat random cross retries. Test a structured pivot candidate using source-prefix fibers or a shared target-independent basis, with an explicit requirement that unique queried tuples are strictly below full tensor entries before any claim of non-enumerative progress is recorded.
