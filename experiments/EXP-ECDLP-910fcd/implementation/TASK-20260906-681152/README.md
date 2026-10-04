# EXP-ECDLP-910fcd implementation adapter

This is a **partial** implementation-only package for `TASK-20260906-681152`. It does not
create fixtures, enumerate curves, construct a selected field, run Miller's
algorithm, search for a scientific `T`, execute controls, measure timing, or
write a run directory. Its default action is a dry-run coverage record.

The frozen source is `experiments/EXP-ECDLP-910fcd/specification.yaml`, SHA-256
`75148fa8dc182d14f0894b3e525418c72fc939338b6a60d2c07cd2fc9df32555`, from
snapshot `1a7917e234dd599e9fec58fe93299652a5c019ce`. The additive approval is
`DEC-20260906-f73475`. The nearest listed pairing records,
`EXP-PAIR-29e078`, `EXP-PAIR-521450`, and `EXP-PAIR-a5c19e`, contain
specifications but no reusable local Tate/Miller implementation.

`driver.py` provides the following reviewable interfaces:

- `stream_digest`, `rejection_draw`, and `fisher_yates` implement the frozen
  SHA-256 JSON stream and rejection sampling rule.
- `bounded_monic_polynomials` and `select_irreducible_polynomial` preserve
  increasing integer `I`, constant-coefficient-first encoding, skipping
  `a0=0`, and the 4096 tested-polynomial cap. The future runner supplies an
  irreducibility certificate provider. `irreducibility_certificate` emits
  required Rabin/Frobenius witness metadata only; it does not compute witnesses.
- `PolynomialField` implements coefficient-vector polynomial-basis arithmetic
  modulo the selected monic polynomial. `ShortWeierstrassCurve` implements the
  frozen short-Weierstrass group law. `miller_function_at` and
  `shifted_divisor_miller` implement binary Miller evaluation at
  `(T+shift)-(shift)` and report a pole instead of manufacturing a value.
- `select_second_argument` records rejected/exceptional candidates and stops
  at 128. It does not turn a pole into zero or swap in a different point.
- `public_reduced_tate` calls the supplied Miller/divisor evaluator and
  `reduced_tate` applies the mandatory final exponent `(p**k-1)//r` to its
  result. The source-documented calibration fixture is represented exactly as
  `p=103, E=[1,18], G=(33,91), r=19, k=6`, as data only; it is not evaluated in
  this task. `multiplicative_bsgs` and `additive_bsgs` explicitly use
  `m=ceil(sqrt(r))`, baby powers/points `0..m-1`, giant steps `0..m`, exact
  collision handling, and an independent final verifier. No general
  discrete-log API or full lookup table is present.
- `PublicTarget` deliberately has `Q` only; `evaluator_decode` receives no
  scalar label. Labels and exhaustive verifier tables remain outside the
  producer-facing interface.
- `CostLedger` keeps deterministic fixture work shared and field/T/character
  setup unique to the character arm, matching the frozen cost model.

Run the bounded synthetic checks once:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests.py
PYTHONDONTWRITEBYTECODE=1 python3 driver.py --dry-run
```

`--launch-lock PATH` parses a prospective JSON lock shape and then fails closed:
this package has no content, runtime, or signature verifier. Caller-supplied
Boolean fields and nonempty strings never constitute lock verification. This
adapter has no launch path by design.

Before any measurement, the missing irreducibility-witness, extension-field
square-root/coordinate, deterministic T-and-shift, isolation, control, timing,
and persistence code must
be implemented and then the Coordinator must archive these five exact files,
obtain an independent implementation review covering field/Miller/divisor
handling, all controls, RNG, BSGS bounds and cost accounting, and allocate a
new run handoff plus a genuine runtime/code lock. The future runner must also
implement the frozen finite fixture selection, a certified irreducibility
test and polynomial-basis field, Miller evaluation with documented shifted
divisors, and all required artifact persistence. Those are launch
prerequisites, not failures of the mathematical hypothesis.
