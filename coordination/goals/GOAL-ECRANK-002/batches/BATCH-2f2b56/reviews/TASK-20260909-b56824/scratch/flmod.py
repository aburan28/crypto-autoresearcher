#!/usr/bin/env python3
"""F_l reduction machinery over F_l for the Weierstrass model.
Exact, stdlib only. Used to determine the Q-rank of the 8 forced points."""
from math import gcd

def w_add_l(a2, a4, a6, l, P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % l == 0: return None
        lam = (3*x1*x1 + 2*a2*x1 + a4) * pow(2*y1 % l, -1, l) % l
    else:
        lam = (y2 - y1) * pow((x2 - x1) % l, -1, l) % l
    x3 = (lam*lam - a2 - x1 - x2) % l
    y3 = (lam*(x1 - x3) - y1) % l
    return (x3 % l, y3 % l)

def w_neg_l(l, P):
    if P is None: return None
    return (P[0], (-P[1]) % l)

def w_mul_l(a2, a4, a6, l, m, P):
    if m < 0:
        P = w_neg_l(l, P); m = -m
    R = None; Q = P
    while m:
        if m & 1: R = w_add_l(a2, a4, a6, l, R, Q)
        Q = w_add_l(a2, a4, a6, l, Q, Q)
        m >>= 1
    return R

def tonelli_shanks(n, p):
    n %= p
    if n == 0: return 0
    if pow(n, (p-1)//2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p+1)//4, p)
    Q = p - 1; S = 0
    while Q % 2 == 0:
        Q //= 2; S += 1
    z = 2
    while pow(z, (p-1)//2, p) != p-1:
        z += 1
    c = pow(z, Q, p)
    R = pow(n, (Q+1)//2, p)
    t = pow(n, Q, p)
    m = S
    while t != 1:
        i = 1
        t2i = (t*t) % p
        while t2i != 1:
            t2i = (t2i*t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        R = (R*b) % p
        c = (c*c) % p
        t = (t*c*c) % p
        m = i
    return R

def sqrt_mod(n, p):
    if p % 4 == 3:
        r = pow(n, (p+1)//4, p)
        return r if (r*r) % p == n % p else None
    return tonelli_shanks(n, p)

def count_points(a2, a4, a6, l):
    """Return (N, finite_points) for Y^2 = X^3 + a2 X^2 + a4 X + a6 over F_l."""
    pts = []
    for x in range(l):
        rhs = (x*x*x + a2*x*x + a4*x + a6) % l
        y = sqrt_mod(rhs, l)
        if y is not None:
            pts.append((x, y))
            if y != 0:
                pts.append((x, (-y) % l))
    return len(pts) + 1, pts

def factorize(n):
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d; e += 1
            out.append((d, e))
        d += 1 if d == 2 else 2
    if n > 1:
        out.append((n, 1))
    return out

def point_order(a2, a4, a6, l, P, N, factorization):
    if P is None: return 1
    order = N
    for p, e in factorization:
        while order % p == 0:
            cand = order // p
            if w_mul_l(a2, a4, a6, l, cand, P) is None:
                order = cand
            else:
                break
    return order
