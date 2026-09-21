# Revision history v2

## Preserved v1 status

V1 remains `REVIEW_REQUIRED` and received theory verdict `REVISE`. It is not
implementation-authorized and must not be used for a canonical run.

## V2 repairs

1. Corrected trace-zero `Z2` coefficient from `X_Q^2` to
   `X_Q^2+nY_Q^2`.
2. Replaced right-only exact recompression with a left-to-right sweep followed
   by a right-to-left sweep.
3. Froze nonzero scalar rank-preservation and tagged zero semantics.
4. Added `A+(-A)` and common-prefix direct-sum controls.
5. Added six nonzero-trace `GENERAL_TRACE_Q00` controls to exercise `XY`.
6. Added mutation `M10` deleting `nY_Q^2`; shifted accounting and provenance
   mutations to `M11` through `M13`.
7. Changed the source-family wording from exactly five-dimensional to at most
   five-dimensional.
8. Required separate streamed-prefix, left-sweep, and right-sweep ledgers.

## Execution effect

No source implementation or run exists. Confirmatory status is reset to
`REVIEW_REQUIRED`; the target schedule increases from 18 to 24 TTs and the
mutation count from 12 to 13.
