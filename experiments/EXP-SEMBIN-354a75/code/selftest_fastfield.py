#!/usr/bin/env python3
"""Check the vectorised layer against the readable one, element by element.

`fastfield.py` exists only for speed, so the only thing that licenses using it
is agreement with `binary_field.py`, which is itself checked in
`selftest_binary_field.py` against the mathematical statements. The last two
checks are the load-bearing ones for this experiment:

  * the QUADRATIC TWIST really does carry exactly the x-values whose curve
    y-values fall in F_{q^2} \\ F_q, and
  * the map (x, y) -> (x, y + x u) from the twist into E(F_{q^2}) is a group
    homomorphism.

Everything the run says about Lemma 2 -- which solutions are usable relations,
which are the order-2 channel, and where the chained and single presentations
part company -- is computed through that pair of facts in F_q arithmetic rather
than in F_{q^2}, so they are verified here rather than assumed.
"""
from __future__ import annotations

import random
import sys

import numpy as np

from binary_field import BinaryCurve, GF2m, QuadraticExtension, INFINITY
from fastfield import FastCurve, FastField, twist_a

DEGREES = [12, 13, 15, 17, 19, 20, 21, 22, 24]


def check(name: str, ok: bool) -> None:
    if not ok:
        print(f"FAIL: {name}")
        raise SystemExit(1)
    print(f"ok: {name}")


def field_agreement(n: int, rng: random.Random, trials: int = 400) -> None:
    ff = FastField.get(n)
    sf = GF2m(n)
    check(f"deg {n}: same modulus as binary_field", ff.modulus == sf.modulus)
    idx = np.arange(1, ff.q, dtype=np.uint32)
    check(f"deg {n}: antilog/log tables are mutually inverse over all {ff.q - 1} "
          f"nonzero elements", bool(np.all(ff.antilog[ff.logt[idx]] == idx)))
    a = np.array([rng.randrange(ff.q) for _ in range(trials)], dtype=np.uint32)
    b = np.array([rng.randrange(ff.q) for _ in range(trials)], dtype=np.uint32)
    assert all(int(v) == sf.mul(int(x), int(y))
               for v, x, y in zip(ff.mul(a, b), a, b))
    assert all(int(v) == sf.sqrt(int(x)) for v, x in zip(ff.sqrt(a), a))
    assert all(int(v) == sf.trace(int(x)) for v, x in zip(ff.trace(a), a))
    nz = a[a != 0]
    assert all(int(v) == sf.inv(int(x)) for v, x in zip(ff.inv(nz), nz))
    for c in list(a[:120]):
        assert ff.solve_quadratic(int(c)) == sf.solve_quadratic(int(c))
    check(f"deg {n}: mul, inv, sqrt, trace and z^2+z=c agree with binary_field "
          f"on {trials} random elements", True)


def curve_agreement(n: int, rng: random.Random, trials: int = 300) -> None:
    ff = FastField.get(n)
    sf = GF2m(n)
    for b in (1, rng.randrange(1, ff.q)):
        fast = FastCurve(ff, 0, b)
        slow = BinaryCurve(sf, 0, b)
        pts, x = [], 0
        while len(pts) < 24 and x < ff.q:
            for y in fast.ys_for_x_scalar(x):
                assert y in slow.ys_for_x(x) or x == 0
                pts.append((x, y))
            x += 1
        X1, Y1, X2, Y2, exp = [], [], [], [], []
        for _ in range(trials):
            p, q = rng.choice(pts), rng.choice(pts)
            X1.append(p[0]); Y1.append(p[1]); X2.append(q[0]); Y2.append(q[1])
            exp.append(slow.add(p, q))
        z = np.zeros(len(X1), dtype=bool)
        X3, Y3, I3 = fast.add(np.array(X1, dtype=np.uint32),
                              np.array(Y1, dtype=np.uint32), z,
                              np.array(X2, dtype=np.uint32),
                              np.array(Y2, dtype=np.uint32), z)
        for got, want in zip(zip(X3, Y3, I3), exp):
            if want is INFINITY:
                assert got[2], "expected infinity"
            else:
                assert not got[2] and (int(got[0]), int(got[1])) == want
        # Identity handling in both argument positions.
        one = np.ones(1, dtype=bool)
        px = np.array([pts[3][0]], dtype=np.uint32)
        py = np.array([pts[3][1]], dtype=np.uint32)
        rx, ry, ri = fast.add(px, py, ~one, px, py, one)
        assert (int(rx[0]), int(ry[0]), bool(ri[0])) == (pts[3][0], pts[3][1], False)
        rx, ry, ri = fast.add(px, py, one, px, py, one)
        assert bool(ri[0])
    check(f"deg {n}: vectorised group law agrees with binary_field on "
          f"{trials} random pairs, including doubling, negation and infinity",
          True)


def order_agreement(n: int, rng: random.Random) -> None:
    ff = FastField.get(n)
    for b in (1, rng.randrange(1, ff.q)):
        e = FastCurve(ff, 0, b)
        et = FastCurve(ff, twist_a(ff, 0), b)
        ne, nt = e.group_order(), et.group_order()
        assert ne + nt == 2 * ff.q + 2, (ne, nt, ff.q)
        assert abs(ne - (ff.q + 1)) <= 2 * int(ff.q ** 0.5) + 1
        assert ne % 2 == 0 and nt % 2 == 0
        if n <= 15:
            slow = BinaryCurve(GF2m(n), 0, b)
            assert slow.order() == ne, (slow.order(), ne)
    check(f"deg {n}: #E counted directly, #E + #E' = 2q + 2, Hasse-consistent"
          + (", and equal to the brute-forced order" if n <= 15 else ""), True)


def twist_correspondence(n: int, rng: random.Random, sample: int = 60) -> None:
    """The twist carries exactly the F_{q^2}\\F_q y-values, homomorphically."""
    ff = FastField.get(n)
    sf = GF2m(n)
    ext = QuadraticExtension(sf)
    b = rng.randrange(1, ff.q)
    e = FastCurve(ff, 0, b)
    et = FastCurve(ff, twist_a(ff, 0), b)
    e_ext = BinaryCurve(ext, ext.embed(0), ext.embed(b))

    def psi(p):
        """(x, y) on the twist  ->  (x, y + x u) on E over F_{q^2}."""
        x, y = p
        return (ext.embed(x), ext.add(ext.embed(y), ext.mul(ext.embed(x), (0, 1))))

    tw_pts, x = [], 1
    while len(tw_pts) < sample and x < ff.q:
        on_e = bool(e.ys_for_x_scalar(x))
        on_t = bool(et.ys_for_x_scalar(x))
        assert on_e != on_t, f"x={x} lies on both or neither curve"
        if on_t:
            y = et.ys_for_x_scalar(x)[0]
            img = psi((x, y))
            assert e_ext.is_on_curve(img), "twist point does not map onto E"
            assert not ext.in_base(img[1]), "image y should leave F_q"
            tw_pts.append((x, y))
        x += 1
    for _ in range(sample):
        p, q = rng.choice(tw_pts), rng.choice(tw_pts)
        X, Y, I = et.add(np.array([p[0]], dtype=np.uint32),
                         np.array([p[1]], dtype=np.uint32), np.zeros(1, bool),
                         np.array([q[0]], dtype=np.uint32),
                         np.array([q[1]], dtype=np.uint32), np.zeros(1, bool))
        lhs = INFINITY if bool(I[0]) else psi((int(X[0]), int(Y[0])))
        rhs = e_ext.add(psi(p), psi(q))
        assert lhs == rhs, f"psi is not a homomorphism at {p}, {q}"
        # Lemma 2 part 1 as arithmetic: a twist sum re-enters E(F_q) exactly
        # when it is infinity or the shared 2-torsion point.
        in_base = (rhs is INFINITY) or ext.in_base(rhs[1])
        is_two_torsion = (rhs is INFINITY) or (int(X[0]) == 0)
        assert in_base == is_two_torsion
    check(f"deg {n}: twist carries exactly the F_(q^2)\\F_q y-values; "
          f"(x,y)->(x,y+xu) is a homomorphism into E(F_(q^2)); a twist sum "
          f"re-enters E(F_q) iff it is infinity or the 2-torsion point", True)


def main() -> int:
    rng = random.Random(20260913202)
    for n in DEGREES:
        field_agreement(n, rng)
    for n in (12, 13, 15, 17, 21, 24):
        curve_agreement(n, rng)
    for n in DEGREES:
        order_agreement(n, rng)
    for n in (12, 13, 17, 21):
        twist_correspondence(n, rng)
    print("\nALL FASTFIELD CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
