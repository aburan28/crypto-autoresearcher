#!/usr/bin/env python3
"""sumpoly_check.py -- independent check that the summation polynomials this
experiment uses are the summation polynomials of the curve.

S_3 (boolsys.s3, Semaev eq. (14)) and S_4 (eq4sys.s4, built as the Sylvester
resultant) are asserted by the paper and by the recursion respectively.  Neither
is checked by the closure or F4 instruments, which would happily measure the
wrong polynomial.  This module checks them against the group law directly:

    P_1, ..., P_r random affine points of E: Y^2 + XY = X^3 + A X^2 + B over
    F_{2^n} with P_1 + ... + P_r = O  ==>  S_r(x(P_1), ..., x(P_r)) = 0,

and, as the discriminating half of the check, that a random tuple of x-coordinates
that does NOT come from such a relation does not vanish.  Without the second
half the zero polynomial would pass.

This is a control, not an instrument: it produces a pass/fail record, no metric.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boolsys  # noqa: E402
import eq4sys  # noqa: E402
from boolsys import GF2n  # noqa: E402


def solve_quadratic_w(F: GF2n, c: int) -> int | None:
    """Solve w^2 + w = c over F_{2^n} (returns one root, or None if none)."""
    # w -> w^2 + w is F_2-linear; solve by Gaussian elimination on its matrix.
    cols = []
    for j in range(F.n):
        e = 1 << j
        cols.append(F.mul(e, e) ^ e)
    # echelon with tracking
    rows = [(cols[j], 1 << j) for j in range(F.n)]
    basis: list[tuple[int, int]] = []
    for v, tag in rows:
        for bv, bt in basis:
            if v ^ bv < v:
                v ^= bv
                tag ^= bt
        if v:
            basis.append((v, tag))
            basis.sort(reverse=True)
    v, tag = c, 0
    for bv, bt in basis:
        if v ^ bv < v:
            v ^= bv
            tag ^= bt
    return tag if v == 0 else None


def random_point(F: GF2n, A: int, B: int, rng: random.Random):
    """Random affine point of Y^2 + XY = X^3 + A X^2 + B (x != 0)."""
    while True:
        x = rng.randrange(1, 1 << F.n)
        rhs = F.mul(F.mul(x, x), x) ^ F.mul(A, F.mul(x, x)) ^ B
        c = F.mul(rhs, F.inv(F.mul(x, x)))
        w = solve_quadratic_w(F, c)
        if w is not None:
            return (x, F.mul(x, w))


def add(F: GF2n, A: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 ^ y2 == x1:  # Q = -P
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.mul(lam, lam) ^ lam ^ A
        y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)
    lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
    x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


def neg(F: GF2n, P):
    return None if P is None else (P[0], P[1] ^ P[0])


def _const(v):
    return {0: v} if v else {}


def eval_s3(F, B, xs):
    return boolsys.s3(F, _const(xs[0]), _const(xs[1]), _const(xs[2]), B).get(0, 0)


def eval_s4(F, B, xs):
    return eq4sys.s4(F, _const(xs[0]), _const(xs[1]), _const(xs[2]), _const(xs[3]), B).get(0, 0)


def check(n: int, trials: int = 8, seed: int = 20260917) -> dict:
    """Run the identity check for S_3 and S_4 over F_{2^n}."""
    modulus, modulus_kind = boolsys.modulus_for(n)
    F = GF2n(n, modulus)
    rng = random.Random(boolsys.derive_seed("sumpoly_check", n, seed))
    A, B = 0, 1
    out = {"n": n, "modulus": modulus, "modulus_kind": modulus_kind, "A": A, "B": B,
           "trials": trials, "curve": "Y^2 + XY = X^3 + A X^2 + B"}
    for r, ev in ((3, eval_s3), (4, eval_s4)):
        vanish_on_relation = 0
        nonvanish_on_random = 0
        skipped = 0
        for _ in range(trials):
            pts = [random_point(F, A, B, rng) for _ in range(r - 1)]
            S = None
            for P in pts:
                S = add(F, A, S, P)
            last = neg(F, S)
            if last is None:  # the partial sum was O; no affine r-th point
                skipped += 1
                continue
            xs = [P[0] for P in pts] + [last[0]]
            if ev(F, B, xs) == 0:
                vanish_on_relation += 1
            rnd = [rng.randrange(1, 1 << n) for _ in range(r)]
            if ev(F, B, rnd) != 0:
                nonvanish_on_random += 1
        attempted = trials - skipped
        out[f"S_{r}"] = {
            "relations_tested": attempted,
            "vanished_on_relation": vanish_on_relation,
            "random_tuples_tested": attempted,
            "nonzero_on_random_tuple": nonvanish_on_random,
            "skipped_degenerate": skipped,
            "pass": attempted > 0 and vanish_on_relation == attempted and nonvanish_on_random == attempted,
        }
    out["pass"] = all(out[f"S_{r}"]["pass"] for r in (3, 4))
    return out


if __name__ == "__main__":
    import json
    for nn in (int(a) for a in (sys.argv[1:] or ["13", "17"])):
        print(json.dumps(check(nn), indent=2))
