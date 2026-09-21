#!/usr/bin/env python3
"""rt_semaev_control.py -- known-answer CONTROL for the instrument used in
joint R1 of TASK-20260904-6681da.

rt_degree_probe.py measures the total degree of S_{m+1} at m = 4 and m = 5,
where this program has no independent reference value (EXP-PFDR-5726af only
reached S_4, and harness/semaev.py's s4_expr carries the confirmed
variable-collision bug of KN-OPEN-5b3a08 -- which is why neither that harness
function nor any sympy substitution is used here).

The control: build a real curve over F_p, take random points P_1, ..., P_{n-1}
and set P_n = -(P_1 + ... + P_{n-1}), so the n points sum to the identity.
A correct S_n must vanish at their x-coordinates.  Failure would mean the
constructed polynomial is not the summation polynomial and the degree
measurement means nothing.

Standard library only.  Deterministic (seeded).  Touches no ECDLP instance and
solves nothing: it evaluates a polynomial at known points.
"""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_degree_probe import P, s3_eval, s4_eval, s5_eval, s6_eval  # noqa: E402


def sqrt_mod(v, p=P):
    assert p % 4 == 3
    r = pow(v, (p + 1) // 4, p)
    return r if r * r % p == v % p else None


def rand_point(a, b, rng, p=P):
    while True:
        x = rng.randrange(1, p)
        y = sqrt_mod((x * x % p * x + a * x + b) % p, p)
        if y is not None:
            return (x, y)


def add(Pt, Q, a, p=P):
    if Pt is None:
        return Q
    if Q is None:
        return Pt
    (x1, y1), (x2, y2) = Pt, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if Pt == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def main():
    rng = random.Random(6681)
    a = rng.randrange(1, P)
    x0, y0 = rng.randrange(1, P), rng.randrange(1, P)
    b = (y0 * y0 - x0 * x0 % P * x0 - a * x0) % P
    print(f"curve y^2 = x^3 + a x + b over F_p, p = 2^61-1; a = {a}; b = {b}")

    ok = {3: 0, 4: 0, 5: 0, 6: 0}
    tries = {3: 0, 4: 0, 5: 0, 6: 0}
    for n in (3, 4, 5, 6):
        for _ in range(5):
            pts = [rand_point(a, b, rng) for _ in range(n - 1)]
            acc = None
            for Q in pts:
                acc = add(acc, Q, a)
            if acc is None:
                continue
            last = (acc[0], (-acc[1]) % P)     # negate: sum of all n is O
            xs = [q[0] for q in pts] + [last[0]]
            if len(set(xs)) != n:
                continue
            tries[n] += 1
            if n == 3:
                v = s3_eval(xs[0], xs[1], xs[2], a, b)
            elif n == 4:
                v = s4_eval(xs[0], xs[1], xs[2], xs[3], a, b)
            elif n == 5:
                v = s5_eval(xs[0], xs[1], xs[2], xs[3], xs[4], a, b)
            else:
                v = s6_eval(xs[0], xs[1], xs[2], xs[3], xs[4], xs[5], a, b)
            ok[n] += (v % P == 0)
        # negative control: the same polynomial at RANDOM x-coordinates must
        # NOT vanish
        xs = [rng.randrange(1, P) for _ in range(n)]
        if n == 3:
            vneg = s3_eval(xs[0], xs[1], xs[2], a, b)
        elif n == 4:
            vneg = s4_eval(xs[0], xs[1], xs[2], xs[3], a, b)
        elif n == 5:
            vneg = s5_eval(xs[0], xs[1], xs[2], xs[3], xs[4], a, b)
        else:
            vneg = s6_eval(xs[0], xs[1], xs[2], xs[3], xs[4], xs[5], a, b)
        print(f"S_{n}: vanishes on {ok[n]}/{tries[n]} genuine zero-sum tuples; "
              f"nonzero at a random tuple: {vneg % P != 0}")


if __name__ == "__main__":
    main()
