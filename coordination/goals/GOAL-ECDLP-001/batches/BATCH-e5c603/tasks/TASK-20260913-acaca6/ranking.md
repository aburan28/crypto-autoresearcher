# TASK-20260913-acaca6 ranking

Four object-framed proposals for `RQ-ECDLP-002` under `GOAL-ECDLP-001`.
Each pairs an R1 affine representation with `Sigma = {[2]}` (not full
translation), sits in the coordinate-dependent class of
`IDEA-20260806-c5d183`, and names a frozen Stage-0 identity with REAL,
known-false, null, and invalid-input cells. The four already-designed
2026-09-13 objects (DBLJAC, XYPROD, YLOW2, CHI3Y) are not repeated.
`novelty_status: unverified`. `established_exponent_gain: 0` on every
record. No run is authorized.

| ID | class | Stage-0 identity | trichotomy | established_exponent_gain |
| --- | --- | --- | --- | --- |
| IDEA-20260913-d76b38 | representation | chi_2(x), chi_2(x') = (18, 1) | coordinate-dependent | 0 |
| IDEA-20260913-6011b8 | representation | (x_Z mod 4, x'_Z mod 4) = (2, 0) | coordinate-dependent | 0 |
| IDEA-20260913-4efec0 | representation | (lambda, lambda') = (18, 3); x' = 16 | coordinate-dependent | 0 |
| IDEA-20260913-1c047d | representation | (x+y, x'+y') = (5, 8) | coordinate-dependent | 0 |

## First test

Test **IDEA-20260913-4efec0** first.

Its Stage-0 identity is the only one of the four that is not a
readout of the already-named coordinates of `P=(2,3)` and
`[2]P=(16,11)`. `chi_2(x)`, `x mod 4`, and `x+y` are functions of
those two points; they cannot fail if `[2]P` is correct. `lambda`
requires an independent evaluation of `(3x^2+A)/(2y)` at both
points and the reconstruction `x' = lambda^2 - 2x`. That is still
a handful of `F_19` operations, and it is the cheapest valid
discriminator that can expose a mis-specified object (wrong
formula, projective chart, or confusion with `768066`'s Jacobian
det). The unary-closure census is optional and can follow only if
the slope pair holds.

A negative on `4efec0`'s identity cell does not close the other
three objects. A negative on its unary-closure cell (expected
Outcome B) records `(L, b)` and leaves `chi_2(x)`, `x`-bits, and
`x+y` open.

## Ranking rationale

Expected information gain is highest on `4efec0` per unit of work:
the slope pair either holds or the tangent object is
mis-specified, and that decision costs a few field operations.
`1c047d` is second because it is the complementary lossy cut of
the inventor-protocol `(Delta, Pi)` example (retain only `Delta`)
and re-uses the same frozen point as `904d99`. `d76b38` and
`6011b8` are cheaper than any walk but are x-side twins of already
designed y-side / translation panels (`1eb65c`, `fa01b7`,
`84755b` P2/P5); their added information is the doubling pairing,
which is real but narrower than a new differential-adjacent scalar.
