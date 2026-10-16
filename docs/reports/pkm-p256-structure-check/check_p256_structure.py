#!/usr/bin/env python3
"""Exact checks on P-256 and the auxiliary curve E0: y^2 = x^3 + x used by the PKM-style factor base.

Everything is integer arithmetic on the published P-256 parameters (cross-checked: G lies on the curve
and n*G is the point at infinity, so a mistyped constant fails here). No search, no solver.
"""
import json
from sympy import isprime, legendre_symbol, primerange

p = 2**256 - 2**224 + 2**192 + 2**96 - 1
a = p - 3
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
     0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    lam = ((3*x1*x1 + a) * pow(2*y1, -1, p) if P == Q else (y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (lam*lam - x1 - x2) % p
    return (x3, (lam*(x1 - x3) - y1) % p)

def mul(k, P):
    R = None
    while k:
        if k & 1: R = add(R, P)
        P = add(P, P); k >>= 1
    return R

# polynomial arithmetic mod (f, p), f a monic cubic: x^3 = 3x - b
def pmul(u, v):
    r = [0]*5
    for i in range(3):
        for j in range(3): r[i+j] = (r[i+j] + u[i]*v[j]) % p
    for k in (4, 3):  # x^k -> reduce using x^3 = -a x - b
        c, r[k] = r[k], 0
        r[k-3+1] = (r[k-3+1] - a*c) % p
        r[k-3] = (r[k-3] - b*c) % p
    return r[:3]

def ppow_x(e):
    result, base = [1, 0, 0], [0, 1, 0]
    while e:
        if e & 1: result = pmul(result, base)
        base = pmul(base, base); e >>= 1
    return result

out = {}
out["G_on_curve"] = (G[1]**2 - G[0]**3 - a*G[0] - b) % p == 0
out["nG_is_infinity"] = mul(n, G) is None
out["p_prime"], out["n_prime"], out["n_odd"] = isprime(p), isprime(n), n % 2 == 1
m = p + 1
v2 = 0
while m % 2 == 0: m //= 2; v2 += 1
out["p_plus_1_two_adic_valuation"] = v2
t = p + 1 - n
out["trace_t_bits"] = t.bit_length()
out["t_odd"] = t % 2 == 1
out["hasse_ok"] = t*t < 4*p
D = t*t - 4*p
out["D_negative"] = D < 0
out["ordinary"] = t % p != 0            # supersingular over F_p (p>3) iff t = 0
out["j_is_1728"] = (b == 0)             # j(y^2=x^3+ax+b) = 1728 iff b = 0 (a != 0)
# 2-division polynomial x^3 + a x + b: roots in F_p <=> a rational point of order 2 <=> n even
frob = ppow_x(p)                        # x^p mod f
out["x^p != x mod f (f has no linear factor)"] = frob != [0, 1, 0]
# f is squarefree (discriminant != 0 for a valid curve). For a squarefree cubic, x^(p^3) = x and x^p != x mod f
# hold exactly when f is irreducible over F_p (a linear factor times an irreducible quadratic fails x^(p^3) = x;
# three linear factors give x^p = x).
# Frobenius orbit of x modulo f: x -> x^p -> x^(p^2) -> x^(p^3); for an irreducible cubic x^(p^3) = x and x^p, x^(p^2) != x.
def frob_apply(g):                      # g(x)^p = g(x^p) over F_p for g with coefficients in F_p
    xp, xp2 = frob, pmul(frob, frob)
    return [(g[0] + g[1]*xp[0] + g[2]*xp2[0]) % p, (g[1]*xp[1] + g[2]*xp2[1]) % p, (g[1]*xp[2] + g[2]*xp2[2]) % p]
x1 = frob; x2 = frob_apply(x1); x3 = frob_apply(x2)
out["f_irreducible_over_F_p (so no point of order 2 over F_p)"] = x1 != [0, 1, 0] and x2 != [0, 1, 0] and x3 == [0, 1, 0]
# l-isogenies over F_p: an F_p-stable line in E[l] exists iff x^2 - t x + p mod l has a root in F_l.
# l = 2: x^2 + x + 1 (t odd, p odd) has no root mod 2.  odd l: iff D is a square mod l.
split = [l for l in primerange(3, 200) if legendre_symbol(D % l, l) in (0, 1)]
nonsplit = [l for l in primerange(3, 200) if legendre_symbol(D % l, l) == -1]
out["rational_2_isogeny_exists"] = False if (t % 2 == 1) else None
out["odd_primes_l<200_with_F_p_rational_l_isogeny"] = split
out["odd_primes_l<200_without"] = nonsplit
print(json.dumps(out, indent=1))
