#!/usr/bin/env python3
"""Independent re-checks of binary_field.py, run before any count is taken.

Every decomposition count in EXP-SEMBIN-354a75 flows through this arithmetic, so
a silent defect here is indistinguishable from a property of Semaev's eq. (11).
The checks below are written against the MATHEMATICAL statements (field axioms,
the trace dichotomy, the group law, Lemma 2's two-roots-or-none structure) and
not against the implementation's internal structure, so passing them is evidence
about the field rather than about the code's self-consistency.

Exit status is 0 on success and 1 on the first failure, with the failing
statement printed; nothing here writes into the run directory.
"""
from __future__ import annotations

import random
import sys

from binary_field import (BinaryCurve, GF2m, QuadraticExtension, INFINITY,
                          _is_irreducible, modulus_for)

CELL_DEGREES = [12, 13, 15, 17, 19, 20, 21, 22, 24]


def check(name: str, ok: bool) -> None:
    if not ok:
        print(f"FAIL: {name}")
        raise SystemExit(1)
    print(f"ok: {name}")


def field_axioms(n: int, rng: random.Random, trials: int = 200) -> None:
    f = GF2m(n)
    check(f"deg {n}: searched modulus {hex(f.modulus)} is irreducible",
          _is_irreducible(n, f.modulus))
    for _ in range(trials):
        a = rng.randrange(1, f.size)
        b = rng.randrange(1, f.size)
        c = rng.randrange(0, f.size)
        assert f.mul(a, b) == f.mul(b, a)
        assert f.mul(a, f.mul(b, c)) == f.mul(f.mul(a, b), c)
        assert f.mul(a, f.add(b, c)) == f.add(f.mul(a, b), f.mul(a, c))
        assert f.mul(a, f.inv(a)) == 1
        assert f.sqr(f.sqrt(a)) == a and f.sqrt(f.sqr(a)) == a
        assert f.pow(a, f.size - 1) == 1
        # Trace is F_2-linear, lands in {0,1}, and is onto.
        assert f.trace(f.add(a, b)) == f.trace(a) ^ f.trace(b)
        assert f.trace(f.sqr(a)) == f.trace(a)
    # Onto-ness is sampled across the whole field: the low 64 elements of
    # F_{2^12} all happen to have trace 0, so a small-window check reports a
    # defect that is not there.
    traces = {f.trace(rng.randrange(f.size)) for _ in range(200)}
    check(f"deg {n}: field axioms, squaring bijective, trace F_2-linear and onto",
          traces == {0, 1})


def quadratic_dichotomy(n: int, rng: random.Random, trials: int = 200) -> None:
    f = GF2m(n)
    ext = QuadraticExtension(f)
    check(f"deg {n}: delta = {ext.delta} has absolute trace 1",
          f.trace(ext.delta) == 1)
    solved_in_base = 0
    for _ in range(trials):
        c = rng.randrange(0, f.size)
        z = f.solve_quadratic(c)
        if f.trace(c) == 0:
            assert z is not None and f.sqr(z) ^ z == c
            assert f.sqr(z ^ 1) ^ (z ^ 1) == c      # the second root is z + 1
            solved_in_base += 1
        else:
            assert z is None
        roots = ext.solve_quadratic_over_base(c)
        assert len(roots) == 2 and roots[0] != roots[1]
        for r in roots:
            assert ext.add(ext.sqr(r), r) == ext.embed(c)
        # Lemma 2's dichotomy: both roots in F_q, or both outside it.
        assert len({ext.in_base(r) for r in roots}) == 1
        assert ext.in_base(roots[0]) == (f.trace(c) == 0)
    check(f"deg {n}: z^2+z=c solvable in F_q iff Tr(c)=0; in F_(q^2) always, "
          f"two roots, both in F_q or both outside ({solved_in_base}/{trials} "
          f"in base)", True)


def extension_axioms(n: int, rng: random.Random, trials: int = 100) -> None:
    f = GF2m(n)
    ext = QuadraticExtension(f)
    for _ in range(trials):
        x = (rng.randrange(f.size), rng.randrange(f.size))
        y = (rng.randrange(f.size), rng.randrange(f.size))
        if x == ext.zero:
            continue
        assert ext.mul(x, y) == ext.mul(y, x)
        assert ext.mul(x, ext.inv(x)) == ext.one
        assert ext.sqr(x) == ext.mul(x, x)
        assert ext.in_base(ext.embed(x[0])) and ext.pull_back(ext.embed(x[0])) == x[0]
        # F_q embeds as b = 0 and the embedding respects multiplication.
        assert ext.mul(ext.embed(x[0]), ext.embed(y[0])) == ext.embed(f.mul(x[0], y[0]))
    check(f"deg {n}: F_(q^2) = F_q[u]/(u^2+u+delta) is a field and F_q embeds at b=0",
          True)


def curve_group_law(n: int, rng: random.Random, trials: int = 120) -> None:
    f = GF2m(n)
    for b in (1, rng.randrange(1, f.size)):
        e = BinaryCurve(f, 0, b)
        pts = []
        x = 0
        while len(pts) < 12 and x < f.size:
            for y in e.ys_for_x(x):
                pts.append((x, y))
            x += 1
        assert all(e.is_on_curve(p) for p in pts)
        for p in pts:
            assert e.add(p, e.negate(p)) is INFINITY
            assert e.add(p, INFINITY) == p
        for _ in range(trials):
            p, q, r = (rng.choice(pts) for _ in range(3))
            assert e.add(p, q) == e.add(q, p)
            assert e.add(e.add(p, q), r) == e.add(p, e.add(q, r))
            s = e.add(p, q)
            if s is not INFINITY:
                assert e.is_on_curve(s)
            assert e.mul_scalar(p, 3) == e.add(e.add(p, p), p)
        t2 = (0, f.sqrt(b))
        assert e.is_on_curve(t2) and e.add(t2, t2) is INFINITY
    check(f"deg {n}: group law commutative and associative on E, (0,sqrt(b)) is "
          f"the unique affine 2-torsion point", True)


def small_curve_order(n: int = 7) -> None:
    """Brute-force order against Hasse, at a degree small enough to enumerate."""
    f = GF2m(n)
    for b in (1, 3, 5):
        e = BinaryCurve(f, 0, b)
        order = e.order()
        bound = 2 * int(f.size ** 0.5) + 1
        assert abs(order - (f.size + 1)) <= bound, (order, f.size)
        assert order % 2 == 0                       # the 2-torsion point is rational
        pts = e.affine_points()
        assert len(pts) + 1 == order
        for p in pts:
            assert e.mul_scalar(p, order) is INFINITY
    check(f"deg {n}: brute-forced #E in the Hasse interval, even, and N*P = O "
          f"for every affine point", True)


def main() -> int:
    rng = random.Random(20260913201)
    for n in CELL_DEGREES:
        field_axioms(n, rng)
    for n in (12, 13, 15, 17, 21, 24):
        quadratic_dichotomy(n, rng)
        extension_axioms(n, rng)
    for n in (12, 13, 17, 21):
        curve_group_law(n, rng)
    small_curve_order(7)
    small_curve_order(9)
    print("\nALL BINARY_FIELD CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
