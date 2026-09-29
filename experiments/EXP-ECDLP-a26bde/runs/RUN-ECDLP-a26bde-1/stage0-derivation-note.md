# Stage 0 derivation note (EXP-ECDLP-a26bde)

## Curve/point generation

Five global curves `y^2 = x^3 + a x + b` are generated deterministically
from seed `20260905` (per `specification.replication.seeds`) by a SHA-256
based keystream (`curves.seed_stream`), searching small integer triples
`(x0, y0, a)` with `|x0|, |y0|, |a| <= 12`, `y0 != 0`, setting
`b = y0^2 - x0^3 - a x0` so `(x0, y0)` is exactly on the curve, and
requiring the discriminant `-16(4a^3 + 27b^2) != 0` (nonsingular over
`Q`). Each curve is tagged `curve0` .. `curve4`.

## Prime selection

For each curve, four toy primes are searched (also from the seeded
keystream) in the union of bit-widths 10-14, requiring:

- `p > 3` (needed by the short-Weierstrass formulas used throughout);
- `p` does not divide the discriminant (good reduction);
- `2 y0` is a unit mod `p` (the reduced point `S` is not 2-torsion, so the
  tangent-line slope `(3x^2+a)/(2y)` is always defined);
- `S = (x0, y0) mod p` genuinely lies on the reduced curve;
- `n = ord(S)` in `E(F_p)`, computed by direct repeated addition, is
  **prime** and `#E(F_p) != p`.

**Deviation from the literal spec (recorded, not silently applied):** the
specification's mechanism section does not require `n` to be prime, only
`gcd(n, p) = 1` and `#E(F_p) != p`. This run additionally requires `n`
prime. Reason: the `m`-ladder digit instrument used here (see
`implementation.md`) computes `[n]` applied to a lift of `m S` via an
ordinary binary ladder; if `n` is composite and `m` shares a nontrivial
factor with `n`, `m S` has an actual order strictly dividing `n`, and the
ladder for `[n](mS)` then re-enters and re-exits the kernel of reduction
several times before finishing, each entry/exit consuming extra p-adic
precision. Requiring `n` prime makes `gcd(m, n) = 1` automatic for every
`m` in the ladder except when `n | m` (the case the specification already
anticipates and instructs to skip, counted under
"skipped multiples (n divides m) per instance"). No instance in this run's
ladder (`m` up to 256) triggered `n | m`, since every generated `n` exceeds
256; the skip path is implemented and reports an empty list for all 20
instances, which is recorded rather than treated as evidence the path is
untested.

## Anomalous curve

The anomalous control is found by the same seeded search over 30
additional curve candidates (`anom_candidate5` .. `anom_candidate34`),
searching bit-widths 10-14 for a prime `p` with `#E(F_p) == p` exactly.
The first hit (`anom_candidate5`, `p = 1531`) is used; see
`frozen-curves-and-primes.json` for the exact curve.

## Reproducibility

`curves.build_frozen_instances(20260905)` is deterministic (SHA-256 keyed
solely by `seed` and fixed string tags); re-running it reproduces the
identical curve/prime list, verified by re-running the driver twice during
this execution (see `implementation.md`, "reproducibility check").
