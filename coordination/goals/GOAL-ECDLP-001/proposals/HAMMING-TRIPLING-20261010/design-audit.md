# Fixed-curve Hamming-weight comparison audit

## Audit basis

- Idea: `IDEA-20261006-2a1db1`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the fixed-curve
  representation controls.

## Scientific boundary

This is a deterministic finite arithmetic check on one public curve and one
canonical point-selection rule. The proposal already states that it changes
neither an attack stage nor the ECDLP exponent. Its remaining value is
instrument correctness: exact curve membership, point selection, tripling,
integer representation, and independent formula agreement. A single weight
difference is not evidence of a distributional bias or a cryptanalytic
mechanism.

## Load-bearing repairs

1. Make the point-selection rule total and reproducible. State the field
   square-root algorithm, which root is “smaller,” how x ties are handled,
   and what happens if the first affine point has a y-sign tie. Record the
   complete enumeration prefix and the selected point, rather than only its
   x-coordinate.
2. Certify the curve cell. Recompute and record the discriminant using the
   exact characteristic-101 formula, verify the selected point on the curve,
   and check that the affine/infinity cases are handled before measuring the
   weight. A nonzero discriminant alone does not certify the selected point.
3. Specify both tripling implementations. Give the formulas, denominator
   inversion convention, exceptional cases, and independent representation
   used by the second implementation. Verify `[3]P` on the curve and compare
   the complete point, not only x, before accepting the weight row.
4. Freeze integer semantics. Reduce each x-coordinate to the canonical
   representative in `[0,p-1]`, use a specified binary encoding without
   leading zeros, and define Hamming weight for zero. Do not substitute a
   lifted integer, field limb encoding, or bit-count parity.
5. Keep the claim finite. The primary output is the exact tuple
   `(x(P),x([3]P),w(P),w([3]P),difference)` and an instrument-validity flag.
   The optional `p=103` arm is a separate comparison and must not be used to
   reinterpret the fixed `p=101` result.
6. Do not add unsupported null inference. If a broader comparison is desired,
   predeclare a curve/point sample, a uniform-x or random-point null, and an
   uncertainty analysis. The current single-point result cannot support a
   statement about typical tripling or a representation bias.

## Readiness and disposition

The proposal is nearly complete as a deterministic arithmetic control, but it
needs explicit square-root, point, formula, and encoding certificates. It is
not an attack experiment and should not be promoted beyond its fixed cell.

Disposition: **retain proposed as a conditional fixed-curve arithmetic
control; do not approve or dispatch as filed.** Repair the total point rule,
curve/point certificates, independent tripling formulas, and exact encoding
receipt. Recheck runnable state, dependencies, and approval capacity after a
complete contract exists.
