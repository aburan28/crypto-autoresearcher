# TASK-20260913-37e26e ranking

Four object-framed proposals for `RQ-ECDLP-002` under `GOAL-ECDLP-001`.
Each pairs an R1 affine representation with `Sigma = {[2]}` (not full
translation), sits in the coordinate-dependent class of
`IDEA-20260806-c5d183`, and names a frozen Stage-0 identity with REAL,
known-false, null, and invalid-input cells. `novelty_status: unverified`.
`established_exponent_gain: 0` on every record. No run is authorized.

| ID | class | claim (one line) | novelty | cost |
| --- | --- | --- | --- | --- |
| IDEA-20260913-768066 | mechanism | Affine doubling-Jacobian det is either a unary `<[2]>`-cocycle or only a 2x2 chain-rule identity | unverified | low / low |
| IDEA-20260913-904d99 | representation | Affine product `xy` either closes under doubling or is a branching joint coordinate (open ffe1df nonlinear family) | unverified | low / low |
| IDEA-20260913-fa01b7 | representation | Two low bits of the integer lift of `y` either form a 4-letter doubling function or mix under reduction mod `p` | unverified | low / low |
| IDEA-20260913-1eb65c | representation | Cubic residue of `y` either closes under doubling or is a branching family-D character (not a pairing) | unverified | low / low |

## First test

Test **IDEA-20260913-768066** first.

Its Stage-0 identity is a single 2x2 determinant product
`det D[4]_P = det D[2]_{[2]P} * det D[2]_P` on one frozen toy point.
That is the cheapest valid discriminator in this batch: it is an exact
field-arithmetic equality, it has a named REAL cell, a known-false
constant `det D[4]=1`, a random-matrix null, and a `y=0` reject, and it
does not require a full-curve census to decide the identity bit. The
unary-closure census is optional and can follow only if the product
identity holds. The other three ideas need the same doubling of
`P=(2,3)` on `y^2 = x^3 + x - 1 / F_19` plus a census to decide
closure; 768066's identity cell is strictly smaller and, if it fails,
is a procedure defect rather than a statement about those coordinates.

A negative on 768066's identity cell does not close the other three
objects. A negative on its unary-closure cell (expected Outcome B)
records `(L, b)` and leaves `xy`, `y`-bits, and `chi_3(y)` open.

## Ranking rationale

Expected information gain is highest on 768066 per unit of work: the
2x2 product either holds or the differential object is mis-specified,
and that decision costs a handful of `F_p` operations. 904d99 is
second because it is the cleanest lossy cut of the inventor-protocol
`(Delta, Pi)` example (retain only `Pi`) and re-uses the same frozen
point. fa01b7 and 1eb65c are cheaper than any walk but need a census
to decide closure; they are ranked below because 84755b already
measured related x-side panels under translation, so their added
information is the y-side / doubling pairing, which is real but
narrower than a new differential object.
