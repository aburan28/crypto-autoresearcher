#!/usr/bin/env python3
"""Blind re-derivation scratch for TASK-20260908-6f37e1 (joint J5).
Exact arithmetic only (fractions.Fraction, integers). No floating point in the
derivation. Q1: n=6 ellipticity quadratic. Q2: expected-meets arithmetic.
"""
from fractions import Fraction as F
import math
import sys
sys.set_int_max_str_digits(0)  # allow printing the exact (huge) rational for P(meets<=3)

def F_(x):
    return F(x)

# ---------- generic exact polynomial helpers (univariate, low-to-high lists) ----------
def poly_mul(p, q):
    r = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, bb in enumerate(q):
            r[i + j] += a * bb
    return r

def poly_add(p, q):
    r = [F(0)] * max(len(p), len(q))
    for i, a in enumerate(p):
        r[i] += a
    for i, a in enumerate(q):
        r[i] += a
    return r

def poly_eval(p, x):
    r = F(0)
    for a in reversed(p):
        r = r * x + a
    return r

def poly_sub(p, q):
    r = [F(0)] * max(len(p), len(q))
    for i, a in enumerate(p):
        r[i] += a
    for i, a in enumerate(q):
        r[i] -= a
    return r

def poly_deriv(p):
    if len(p) <= 1:
        return [F(0)]
    return [F(i) * p[i] for i in range(1, len(p))]

def trim(p):
    r = list(p)
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r

def poly_deg(p):
    t = trim(p)
    return len(t) - 1

# ---------- exact determinant (Bareiss) ----------
def bareiss(M):
    n = len(M)
    if n == 0:
        return F(1)
    if n == 1:
        return M[0][0]
    M = [row[:] for row in M]
    sign = F(1)
    prev = F(1)
    for k in range(n - 1):
        if M[k][k] == 0:
            swap = None
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    swap = i
                    break
            if swap is None:
                return F(0)
            M[k], M[swap] = M[swap], M[k]
            sign = -sign
        pivot = M[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * pivot - M[i][k] * M[k][j]) / prev
        prev = pivot
    return sign * M[n - 1][n - 1]

# ---------- resultant / discriminant ----------
def resultant(f, g):
    """Res(f, g) via Sylvester matrix. f, g low-to-high, trimmed."""
    f = trim(f)
    g = trim(g)
    m = len(f) - 1
    n = len(g) - 1
    if m < 0 or n < 0:
        # deg 0 edge: Res(const, g) = const^n ; Res(f, const) = const^m
        if m == 0 and n == 0:
            return F(1)
        if m == 0:
            return f[0] ** n
        if n == 0:
            return g[0] ** m
    size = m + n
    S = [[F(0)] * size for _ in range(size)]
    # first n rows: f shifted by 0..n-1
    for i in range(n):
        for j in range(m + 1):
            S[i][i + j] = f[j]
    # next m rows: g shifted by 0..m-1
    for i in range(m):
        for j in range(n + 1):
            S[n + i][i + j] = g[j]
    return bareiss(S)

def discriminant(f):
    """disc(f) = (-1)^{m(m-1)/2} * (1/lead) * Res(f, f')."""
    f = trim(f)
    m = len(f) - 1
    if m < 2:
        return F(0)
    lead = f[m]
    fp = poly_deriv(f)
    res = resultant(f, fp)
    return ((F(-1) ** (m * (m - 1) // 2)) / lead) * res

# sanity checks on discriminant
assert discriminant([F(-1), F(0), F(1)]) == F(4), "quad x^2-1 disc"
assert discriminant([F(-1), F(0), F(1), F(0)]) == F(4), "cubic x^3-x disc"
# quartic x^4 - 1: disc(x^n-1) = (-1)^{(n-1)(n-2)/2} n^n = (-1)^3 * 256 = -256
assert discriminant([F(-1), F(0), F(0), F(0), F(1)]) == F(-256), "quartic x^4-1 disc"
print("discriminant sanity checks passed")

# =====================================================================
# Q1
# =====================================================================
b = [F(0), F(1), F(7), F(-14), F(16), F(-2)]
d = [F(-2310), F(30030), F(30030), F(-286), F(-286), F(-2310)]
n = 6

# p(x) = prod (x - b_i)
p = [F(1)]
for bi in b:
    p = poly_mul(p, [F(-bi), F(1)])
p = trim(p)
print("p(x) coeffs (low->high):", [str(c) for c in p])
assert poly_deg(p) == 6 and p[6] == 1

# delta via Lagrange
delta = [F(0)] * n
for i in range(n):
    num = [F(1)]
    for j in range(n):
        if j != i:
            num = poly_mul(num, [F(-b[j]), F(1)])
    den = F(1)
    for j in range(n):
        if j != i:
            den *= (b[i] - b[j])
    Li = [c / den for c in num]
    for k in range(len(Li)):
        delta[k] += d[i] * Li[k]
delta = trim(delta)
while len(delta) < 6:
    delta.append(F(0))
delta = delta[:6]
print("delta(x) coeffs (low->high):", [str(c) for c in delta])
# verify interpolation
for i in range(n):
    got = poly_eval(delta, b[i])
    assert got == d[i], (i, got, d[i])
print("delta(b_i) == d_i verified for all i")

# bivariate representation: dict {(xpow, cpow): coeff}
def to_biv(poly):
    return {(k, 0): F(c) for k, c in enumerate(poly) if c != 0}

delta_biv = to_biv(delta)
# (x+c)^2 = x^2 + 2c x + c^2
g2_biv = {(2, 0): F(1), (1, 1): F(2), (0, 2): F(1)}

def biv_add(a, bb):
    r = dict(a)
    for k, v in bb.items():
        r[k] = r.get(k, F(0)) + v
    return {k: v for k, v in r.items() if v != 0}

def biv_mul(a, bb):
    r = {}
    for (i, j), av in a.items():
        for (k, l), bv in bb.items():
            key = (i + k, j + l)
            r[key] = r.get(key, F(0)) + av * bv
    return {k: v for k, v in r.items() if v != 0}

prod = biv_mul(delta_biv, g2_biv)

# reduction relation from p: x^6 = 8x^5 + 221x^4 - 1376x^3 - 1988x^2 + 3136x
# (p = x^6 - 8x^5 - 221x^4 + 1376x^3 + 1988x^2 - 3136x)
x6rel = {5: F(8), 4: F(221), 3: F(-1376), 2: F(-1988), 1: F(3136)}

def reduce_mod_p(poly):
    r = dict(poly)
    while True:
        xs = [k[0] for k in r if r[k] != 0]
        if not xs or max(xs) < 6:
            break
        mx = max(xs)
        for cpow in sorted([k[1] for k in r if k[0] == mx and r[k] != 0]):
            coeff = r[(mx, cpow)]
            r[(mx, cpow)] = F(0)
            for xp, xc in x6rel.items():
                key = (mx - 6 + xp, cpow)
                r[key] = r.get(key, F(0)) + coeff * xc
        r = {k: v for k, v in r.items() if v != 0}
    return r

s_biv = reduce_mod_p(prod)
print("s(x) bivariate (xpow,cpow):coeff")
for k in sorted(s_biv):
    print("   x^%d c^%d : %s" % (k[0], k[1], s_biv[k]))

# x^5 coefficient as polynomial in c
f5 = {j: s_biv.get((5, j), F(0)) for j in range(3)}
print("x^5 coeff of s as poly in c: f(c) = %s + %s*c + %s*c^2" % (f5[0], f5[1], f5[2]))

# cross-check with closed form: f(c) = d5 c^2 + (2 d4 + 16 d5) c + (d3 + 8 d4 + 285 d5)
d3, d4, d5 = delta[3], delta[4], delta[5]
cf = {2: d5, 1: 2 * d4 + 16 * d5, 0: d3 + 8 * d4 + 285 * d5}
print("closed-form f(c) coeffs:", {j: str(cf[j]) for j in range(3)})
assert f5 == cf, "closed form mismatch"
print("closed-form cross-check PASSED")

A, Bc, C = f5[2], f5[1], f5[0]
print("A (c^2) =", A, " B (c) =", Bc, " C =", C)
is_quadratic = (A != 0)
print("is quadratic in c:", is_quadratic)

# solve A c^2 + B c + C = 0 over Q
roots = []
if is_quadratic:
    D = Bc * Bc - 4 * A * C
    print("discriminant D =", D)
    # check D is a perfect square in Q
    Dn, Dd = D.numerator, D.denominator
    sn = math.isqrt(Dn)
    sd = math.isqrt(Dd)
    perfect = (sn * sn == Dn) and (sd * sd == Dd)
    print("D perfect square in Q:", perfect, "(sqrt numerator=%d, sqrt denominator=%d)" % (sn, sd))
    if perfect:
        sqrtD = F(sn, sd)
        for sgn in (1, -1):
            r = (-Bc + sgn * sqrtD) / (2 * A)
            roots.append(r)
else:
    # linear or constant fallback (record as finding if reached)
    if Bc != 0:
        roots.append(-C / Bc)
    print("WARNING: not quadratic; handled as linear/constant")

print("rational roots c:")
for r in roots:
    # explicit verification that f(r) == 0
    fval = A * r * r + Bc * r + C
    num, den = r.numerator, r.denominator
    abs_c = abs(r)
    h = max(abs(num), abs(den))
    print("   c = %s/%s  f(c)=%s  |c| = %s  max(|num|,|den|) = %d  <=1e4(height): %s  |c|<=1e4: %s"
          % (num, den, fval, abs_c, h, h <= 10**4, abs_c <= 10**4))
    assert fval == 0, "root does not satisfy f(c)=0"
print("all roots verified: f(c) == 0 exactly")

# per-root checks
def univ_from_biv(biv, cval):
    # substitute c = cval, get univariate poly in x
    r = {}
    for (xp, cp), coeff in biv.items():
        r[xp] = r.get(xp, F(0)) + coeff * (cval ** cp)
    m = max(r) if r else 0
    return [r.get(i, F(0)) for i in range(m + 1)]

print("\nper-root checks:")
for r in roots:
    print("  root c =", r)
    # g(b_i) != 0
    gb = [b[i] + r for i in range(n)]
    all_nonzero = all(g != 0 for g in gb)
    print("    g(b_i) values:", [str(g) for g in gb], " all nonzero:", all_nonzero)
    s_univ = univ_from_biv(s_biv, r)
    s_univ = trim(s_univ)
    degs = poly_deg(s_univ)
    print("    s(x) coeffs (low->high):", [str(c) for c in s_univ])
    print("    deg s =", degs)
    disc = discriminant(s_univ)
    print("    disc(s) =", disc)
    # nondegeneracy: deg s in {3,4} and s nonsingular
    if degs == 4:
        nonsing = (disc != 0)
    elif degs == 3:
        nonsing = (disc != 0)
    else:
        nonsing = False
    print("    deg s in {3,4}:", degs in (3, 4), " nonsingular:", nonsing,
          " NONDEGENERATE:", (degs in (3, 4)) and nonsing)
    # verify identity s(b_i) = d_i g(b_i)^2
    ok = True
    for i in range(n):
        lhs = poly_eval(s_univ, b[i])
        rhs = d[i] * (b[i] + r) ** 2
        if lhs != rhs:
            ok = False
            print("    MISMATCH at i=%d: lhs=%s rhs=%s" % (i, lhs, rhs))
    print("    identity s(b_i)=d_i*g(b_i)^2 holds for all i:", ok)

# symbolic identity check (in c) for s(b_i) = d_i (b_i + c)^2
print("\nsymbolic identity check (in c):")
sym_ok = True
for i in range(n):
    # evaluate s_biv at x = b[i], keep c symbolic -> poly in c
    lhs = {}
    for (xp, cp), coeff in s_biv.items():
        lhs[cp] = lhs.get(cp, F(0)) + coeff * (b[i] ** xp)
    lhs = {k: v for k, v in lhs.items() if v != 0}
    # rhs = d_i (b_i + c)^2 = d_i (b_i^2 + 2 b_i c + c^2)
    bi = b[i]
    rhs = {0: d[i] * bi * bi, 1: d[i] * 2 * bi, 2: d[i]}
    rhs = {k: v for k, v in rhs.items() if v != 0}
    if lhs != rhs:
        sym_ok = False
        print("   i=%d MISMATCH lhs=%s rhs=%s" % (i, lhs, rhs))
print("symbolic identity holds for all i:", sym_ok)

# =====================================================================
# Q2
# =====================================================================
print("\n================ Q2 ================")
Na = 8000
Sabs = 1600
E = F(Na, Sabs)
print("E[meets] = N_a/|S| =", E)
p_ = F(1, Sabs)
q_ = 1 - p_
var = F(Na) * p_ * q_
print("variance = N p (1-p) =", var)
# simplify sd
# sd = sqrt(var) = sqrt(vn/vd) = sqrt(vn*vd)/vd = s_in*sqrt(r_in)/vd, then reduce s_in/vd
vn, vd = var.numerator, var.denominator
def squarefree(n):
    # return (s, r) with n = s^2 * r, r squarefree
    s = 1
    r = n
    f = 2
    while f * f <= r:
        while r % (f * f) == 0:
            s *= f
            r //= (f * f)
        f += 1
    return s, r
inner = vn * vd
s_in, r_in = squarefree(inner)
g = math.gcd(s_in, vd)
sd_num_prefactor = s_in // g
sd_den = vd // g
sd = ("sqrt(%d)" % r_in) if sd_num_prefactor == 1 else ("%d*sqrt(%d)" % (sd_num_prefactor, r_in))
sd = sd + "/%d" % sd_den
print("sd = sqrt(var) = sqrt(%d/%d) = %s" % (vn, vd, sd))
print("sd numeric ~", float(var) ** 0.5)

# P(meets <= 3) exact
# P = (1599/1600)^8000 * sum_{k=0}^3 C(8000,k)/1599^k
def C(n, k):
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r

bracket = F(1)
for k in range(1, 4):
    bracket += F(C(Na, k), 1599 ** k)
print("bracket sum_{k=0}^3 C(8000,k)/1599^k =", bracket)
base = F(1599, 1600) ** 8000
P_le3 = base * bracket
print("P(meets<=3) exact factored = (1599/1600)^8000 * %s" % bracket)
print("P(meets<=3) exact numerator digits:", len(str(P_le3.numerator)),
      " denominator digits:", len(str(P_le3.denominator)))
print("P(meets<=3) numeric ~", float(P_le3))
# high-precision decimal via integer arithmetic: P = num/den
from decimal import Decimal, getcontext
getcontext().prec = 40
P_dec = Decimal(P_le3.numerator) / Decimal(P_le3.denominator)
print("P(meets<=3) 40-digit decimal ~", P_dec)
# also individual terms for reference
for k in range(4):
    term = F(C(Na, k), 1) * (F(1, 1600) ** k) * (F(1599, 1600) ** (8000 - k))
    print("  P(meets==%d) ~ %s" % (k, float(term)))

# z-score of 3
import math as _m
mu = float(E)
sigma = float(var) ** 0.5
z = (3 - mu) / sigma
print("z-score of observed 3: (3 - %s)/%s ~ %s" % (mu, sigma, z))
print("P(meets<=3) ~", float(P_le3), " -> 3 is NOT an outlier (well within 1 sd of mean)")
