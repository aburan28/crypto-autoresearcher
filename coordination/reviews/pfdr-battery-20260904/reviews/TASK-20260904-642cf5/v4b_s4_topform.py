#!/usr/bin/env python3
"""V4(b): independent symbolic recomputation of the S_4 top form.

S_3 built from the formula in the task card; S_4 = Res_T(S_3(x1,x2,T), S_3(x3,xR,T))
with a, b, x_R symbolic over Z; extract the total-degree-12 homogeneous part in
(x1, x2, x3) and check it is the single monomial x1^4 x2^4 x3^4 with a constant
coefficient.  Then a numeric control at p = 65537: S_4 must vanish on random
planted 4-tuples (P1+P2+P3+P4 = O) and generically not vanish on random tuples.
"""
import random, sympy as sp

x1, x2, x3, T, a, b, xR = sp.symbols('x1 x2 x3 T a b x_R')

def S3(u, v, w):
    return ((u - v) ** 2 * w ** 2
            - 2 * ((u + v) * (u * v + a) + 2 * b) * w
            + (u * v - a) ** 2 - 4 * b * (u + v))

S4 = sp.resultant(sp.expand(S3(x1, x2, T)), sp.expand(S3(x3, xR, T)), T)
S4 = sp.expand(S4)
P = sp.Poly(S4, x1, x2, x3)
degs = [sp.degree(S4, v) for v in (x1, x2, x3)]
print("total degree of S_4 in (x1,x2,x3):", sp.Poly(S4, x1, x2, x3).total_degree())
print("per-variable degrees [x1, x2, x3]:", degs)
print("degree in x_R:", sp.degree(S4, xR))
print("number of monomials in (x1,x2,x3):", len(P.monoms()))
top = [(m, c) for m, c in zip(P.monoms(), P.coeffs()) if sum(m) == 12]
print("degree-12 homogeneous part in (x1,x2,x3):")
for m, c in top:
    print("   monomial x1^%d x2^%d x3^%d   coefficient = %s" % (m[0], m[1], m[2], sp.simplify(c)))
single = len(top) == 1 and top[0][0] == (4, 4, 4)
coeff = sp.simplify(top[0][1]) if top else None
print("single monomial x1^4 x2^4 x3^4:", single)
print("coefficient:", coeff, "| is a constant (free of a, b, x_R):",
      bool(top) and not (coeff.free_symbols & {a, b, xR}))
print("coefficient == 1:", coeff == 1)
print("S_4 is NOT identically zero:", S4 != 0)

# --- numeric control at p = 65537 -------------------------------------------
p = 65537
def legendre(n): return pow(n % p, (p - 1) // 2, p)
def sqrt_mod(n):
    n %= p
    if n == 0: return 0
    if legendre(n) != 1: return None
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while legendre(z) != p - 1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 % p; i += 1
        bb = pow(c, 1 << (m - i - 1), p); m, c = i, bb * bb % p
        t = t * c % p; r = r * bb % p
    return r
def ec_add(P_, Q_, A):
    if P_ is None: return Q_
    if Q_ is None: return P_
    (u1, v1), (u2, v2) = P_, Q_
    if u1 == u2 and (v1 + v2) % p == 0: return None
    if P_ == Q_:
        if v1 == 0: return None
        lam = (3 * u1 * u1 + A) * pow(2 * v1, p - 2, p) % p
    else:
        lam = (v2 - v1) * pow((u2 - u1) % p, p - 2, p) % p
    u3 = (lam * lam - u1 - u2) % p
    return (u3, (lam * (u1 - u3) - v1) % p)

rng = random.Random(4426420)
S4f = sp.lambdify((x1, x2, x3, xR, a, b), S4, "math")
S4_poly = sp.Poly(S4, x1, x2, x3, xR, a, b)
def eval_mod(vals):
    tot = 0
    for m, c in zip(S4_poly.monoms(), S4_poly.coeffs()):
        term = int(c) % p
        for e, v in zip(m, vals):
            term = term * pow(v, e, p) % p
        tot = (tot + term) % p
    return tot

planted_ok, random_nonzero = 0, 0
trials = 0
while trials < 8:
    A = rng.randrange(1, p); B = rng.randrange(1, p)
    if (4 * pow(A, 3, p) + 27 * pow(B, 2, p)) % p == 0: continue
    pts = []
    while len(pts) < 3:
        u = rng.randrange(p); y = sqrt_mod((pow(u, 3, p) + A * u + B) % p)
        if y is not None and y != 0: pts.append((u, y))
    S = None
    for Pt in pts: S = ec_add(S, Pt, A)
    if S is None: continue
    P4 = (S[0], (-S[1]) % p)                      # P4 = -(P1+P2+P3)  => sum = O
    trials += 1
    v = eval_mod([pts[0][0], pts[1][0], pts[2][0], P4[0], A, B])
    planted_ok += (v == 0)
    vr = eval_mod([pts[0][0], pts[1][0], pts[2][0], rng.randrange(p), A, B])
    random_nonzero += (vr != 0)
print()
print(f"numeric control at p = 65537 (rng seed 4426420, 8 random curves):")
print(f"   S_4 vanishes on the planted 4-tuple P1+P2+P3+P4 = O: {planted_ok}/8")
print(f"   S_4 nonzero on a random substituted x_R (negative control): {random_nonzero}/8")
