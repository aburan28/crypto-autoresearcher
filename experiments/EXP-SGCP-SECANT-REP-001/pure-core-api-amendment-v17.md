# Pure Mathematical Core API Amendment V17

## Status and precedence

Status: `review_required`.

This file narrowly clarifies the factor-base coordinate-validation precedence in
`pure-core-api-v6.md` and `pure-core-api-amendment-v7.md`. It takes precedence
only for the order defined below. It does not authorize source writing, test
writing, parsing, import, compilation, analysis, testing, or execution.

## Complete coordinate precedence

For each point in increasing factor-base index, validation is field-complete in
this exact order:

1. the point object has exact type `AffinePoint`;
2. `x` has exact type `int`;
3. `x` satisfies `0 <= x < p`;
4. `y` has exact type `int`;
5. `y` satisfies `0 <= y < p`.

Only after all five checks pass does validation continue to the next point.
Thus the phrase "`x` before `y`" means complete validation of `x` before any
validation of `y`; it does not mean a type sweep followed by a range sweep.

The existing error codes and indices remain unchanged:

- a wrong point object uses `TYPE_MISMATCH` and `(3,i)`;
- a wrong `x` exact type uses `TYPE_MISMATCH` and `(3,i,0)`;
- a noncanonical integer `x` uses `NONCANONICAL_POINT` and `(i,)`;
- a wrong `y` exact type uses `TYPE_MISMATCH` and `(3,i,1)`;
- a noncanonical integer `y` uses `NONCANONICAL_POINT` and `(i,)`.

In particular, a point `AffinePoint(-1, False)` fails at its `x` range check
with `NONCANONICAL_POINT` and `(i,)`. It does not reach the `y` type check.

## Accounting

All five checks are uncharged domain validation. A coordinate failure retains
the exact operation prefix accumulated through discriminant validation. This
clarification changes no successful output, successful `CoreOps` field,
mathematical result, factor-base requirement, or later phase.

## Authorized repair shape

A later exact Coordinator decision may authorize only:

- in the protected source, move the existing `x` range check before the
  existing `y` type check without changing either check body;
- in the independent test source, add combined-invalid public assertions that
  distinguish complete `x`-before-`y` validation, including
  `AffinePoint(-1, False)`;
- retain every existing V15/V16 table, independence, coverage, and zero-runtime
  lock.

No broader source or test revision follows from this amendment.
