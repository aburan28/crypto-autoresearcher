#!/usr/bin/env python3
"""TASK-20260909-9e06b1 / REVIEW-PLAN-BATCH-2f2b56 / J1_blind_rederivation, PHASE 1.

Blind re-derivation of the n=6 ellipticity quadratic for three frozen (b,d)
pairs, from the statements and frozen parameters in blind-input.yaml ONLY.

Arithmetic discipline: exact rational arithmetic only (fractions.Fraction).
Polynomial arithmetic over Q and over Q[c] (c-polynomial coefficients of
degree <= 2) implemented by hand. Discriminants via the Sylvester-matrix
resultant with exact fraction Gaussian elimination. No binary floating point
in any exact quantity. No network.
"""
import math
from fractions import Fraction as F

# ---------------- exact polynomial arithmetic over Q (ascending coeffs) ----
def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p

def poly_mul(a, b):
    a, b = trim(a), trim(b)
    if not a or not b:
        return [F(0)]
    res = [F(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            res[i + j] += ai * bj
    return trim(res)

def poly_add(a, b):
    n = max(len(a), len(b))
    res = [F(0)] * n
    for i in range(n):
        res[i] = (a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
    return trim(res)

def poly_sub(a, b):
    n = max(len(a), len(b))
    res = [F(0)] * n
    for i in range(n):
        res[i] = (a[i] if i < len(a) else F(0)) - (b[i] if i < len(b) else F(0))
    return trim(res)

def poly_scale(a, s):
    return trim([s * ai for ai in a])

def poly_mod(a, m):
    """a mod m, m monic."""
    a = trim(a)
    m = trim(m)
    dm = len(m) - 1
    while len(a) > dm:
        lead = a[-1]
        if lead == 0:
            a.pop()
            continue
        shift = len(a) - len(m)
        for j in range(len(m)):
            a[shift + j] -= lead * m[j]
        a = trim(a)
    return a if a else [F(0)]

def poly_eval(p, x):
    r = F(0)
    for ai in reversed(trim(p)):
        r = r * x + ai
    return r

def poly_det(M):
    """Exact determinant, fraction Gaussian elimination with row swaps."""
    n = len(M)
    M = [row[:] for row in M]
    sign = F(1)
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            return F(0)
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
            sign = -sign
        pv = M[col][col]
        for r in range(col + 1, n):
            f = M[r][col] / pv
            if f != 0:
                for cc in range(col, n):
                    M[r][cc] -= f * M[col][cc]
    d = sign
    for i in range(n):
        d *= M[i][i]
    return d

def resultant(p, q):
    """Resultant of p, q (ascending coeff lists) via Sylvester matrix.

    Sylvester layout: m = deg q rows of p's DESCENDING coefficients shifted
    by 0..m-1; n = deg p rows of q's descending coefficients shifted by
    0..n-1. (Verified against Res(x^3-x, 3x^2-1) = -4 by hand.)
    """
    p, q = trim(p), trim(q)
    n, m = len(p) - 1, len(q) - 1
    if n < 0:
        return q[0] ** m
    if m < 0:
        return p[0] ** n
    pd = p[::-1]
    qd = q[::-1]
    S = [[F(0)] * (n + m) for _ in range(n + m)]
    for i in range(m):
        for j in range(n + 1):
            S[i][i + j] = pd[j]
    for i in range(n):
        for j in range(m + 1):
            S[m + i][i + j] = qd[j]
    return poly_det(S)

def poly_disc(p):
    """disc(p) = (-1)^(n(n-1)/2) * Res(p, p') / lc(p)^(2n-2)."""
    p = trim(p)
    n = len(p) - 1
    if n < 2:
        return None
    dp = [F(i) * p[i] for i in range(1, n + 1)]
    lc = p[n]
    res = resultant(p, dp)
    return (F(-1) ** (n * (n - 1) // 2)) * res / (lc ** (2 * n - 2))

def isqrt_or_none(n):
    if n < 0:
        return None
    r = math.isqrt(n)
    return r if r * r == n else None

def sqrt_rational(q):
    """sqrt of Fraction q >= 0 as Fraction if rational, else None."""
    if q < 0:
        return None
    rn = isqrt_or_none(q.numerator)
    rd = isqrt_or_none(q.denominator)
    if rn is not None and rd is not None:
        return F(rn, rd)
    return None

def rat_height(q):
    return max(abs(q.numerator), abs(q.denominator))

def fmt(q):
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"

# ---------------- c-polynomial arithmetic (coeffs = lists, deg <= 2) -------
def cadd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
            for i in range(n)]

def csub(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) - (b[i] if i < len(b) else F(0))
            for i in range(n)]

def cmul(a, b):
    res = [F(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            res[i + j] += ai * bj
    return res

def ctrim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a

def czero(a):
    return all(x == 0 for x in a)

def cmod(a, m):
    """a mod m over Q[c]; m monic with c-independent (constant) coefficients."""
    a = [list(x) for x in a]
    m = [list(x) for x in m]
    dm = len(m) - 1
    while len(a) > dm:
        lead = a[-1]
        if czero(lead):
            a.pop()
            continue
        shift = len(a) - len(m)
        for j in range(len(m)):
            a[shift + j] = csub(a[shift + j], cmul(lead, m[j]))
        a = [ctrim(x) for x in a]
        while a and czero(a[-1]):
            a.pop()
    return a if a else [[F(0)]]

def ceval(p, x):
    """Evaluate poly-in-x with c-polynomial coefficients at scalar x."""
    r = [F(0)]
    for ck in reversed(p):
        r = cadd([xi * x for xi in r], ck)
    return ctrim(r)

def csubstitute(ck, c):
    """Substitute c into a c-polynomial coefficient."""
    val = F(0)
    for power, coef in enumerate(ck):
        val += coef * (c ** power)
    return val

# ---------------- self-tests of the exact machinery ------------------------
def self_tests():
    # discriminant checks
    assert poly_disc([F(-2), F(0), F(1)]) == F(8), "disc x^2-2"
    assert poly_disc([F(0), F(-1), F(0), F(1)]) == F(4), "disc x^3-x"
    # quartic with known disc: x^4 - 1 has disc -256
    # (hand check: roots 1,-1,i,-i; prod (r_i-r_j)^2 = 4*(-2i)*(2i)*(2i)*(-2i)*(-4) = -256)
    assert poly_disc([F(-1), F(0), F(0), F(0), F(1)]) == F(-256), "disc x^4-1"
    # resultant check
    assert resultant([F(0), F(-1), F(0), F(1)], [F(-1), F(0), F(3)]) == F(-4)
    # mod check: (x^2+1)^2 mod (x^2+2) = x^4+2x^2+1 mod (x^2+2): x^2 = -2 -> 4+2(-2)+1 = 1
    assert poly_mod([F(1), F(0), F(2), F(0), F(1)], [F(2), F(0), F(1)]) == [F(1)]
    # sqrt_rational
    assert sqrt_rational(F(4, 9)) == F(2, 3)
    assert sqrt_rational(F(2)) is None
    assert sqrt_rational(F(0)) == F(0)
    print("self_tests: PASS")

# ---------------- Q1 main derivation ---------------------------------------
PAIRS = [
    (649,  [0, 1, 13, 8, 7, -5],      [22, 3, -3, 22, 3, -3]),
    (1299, [0, 1, -14, -2, 4, -20],   [165, 165, -165, 3, 3, -165]),
    (4995, [0, 1, -5, 16, -9, 12],    [10, 22, 10, -22, 22, -22]),
]

def derive_pair(b_index, b_int, d_int):
    b = [F(x) for x in b_int]
    d = [F(x) for x in d_int]
    n = 6

    # p(x) = prod (x - b_i), monic degree 6
    p = [F(1)]
    for bi in b:
        p = poly_mul(p, [F(-bi), F(1)])
    assert len(p) == 7 and p[6] == F(1)

    # Lagrange interpolant delta, degree <= 5
    delta = [F(0)]
    for i in range(n):
        Li = [F(1)]
        denom = F(1)
        for j in range(n):
            if j == i:
                continue
            Li = poly_mul(Li, [F(-b[j]), F(1)])
            denom *= (b[i] - b[j])
        Li = poly_scale(Li, d[i] / denom)
        delta = poly_add(delta, Li)
    delta = trim(delta)
    interp_ok = all(poly_eval(delta, b[i]) == d[i] for i in range(n))

    # q(x) = delta(x) * (x + c)^2 = delta*(x^2 + 2 c x + c^2), deg <= 7.
    # Coefficient of x^k in q: delta_k * c^2 + 2 delta_{k-1} * c + delta_{k-2}
    dl = [F(0)] * 6
    for i, ai in enumerate(delta):
        dl[i] = ai
    q = []
    for k in range(8):
        ck = [F(0), F(0), F(0)]
        if k < 6:
            ck[2] += dl[k]
        if 0 <= k - 1 < 6:
            ck[1] += 2 * dl[k - 1]
        if 0 <= k - 2 < 6:
            ck[0] += dl[k - 2]
        q.append(ck)

    # s(x) = q(x) mod p(x), symbolically in c (p monic, c-independent)
    pm = [[F(x)] for x in p]
    s = cmod(q, pm)
    assert len(s) <= 6, "remainder must have degree <= 5"

    # x^5 coefficient as polynomial in c
    x5 = ctrim(s[5]) if len(s) > 5 else [F(0)]
    A = x5[2] if len(x5) > 2 else F(0)   # coeff of c^2
    B = x5[1] if len(x5) > 1 else F(0)   # coeff of c
    D = x5[0] if len(x5) > 0 else F(0)   # constant
    is_quadratic = (A != 0)

    # solve A c^2 + B c + D = 0 exactly over Q
    roots = []
    solve_note = ""
    if A == 0:
        if B != 0:
            roots = [F(-D, 1) / B]
            solve_note = "degenerate: linear in c (A = 0)"
        else:
            solve_note = "degenerate: identically zero or constant nonzero (A = B = 0)"
    else:
        disc_c = B * B - F(4) * A * D
        sq = sqrt_rational(disc_c)
        if sq is None:
            solve_note = (f"quadratic discriminant B^2-4AD = {fmt(disc_c)} is not a "
                          f"rational square: no rational roots")
        else:
            r1 = (-B + sq) / (F(2) * A)
            r2 = (-B - sq) / (F(2) * A)
            roots = [r1] if r1 == r2 else [r1, r2]
            solve_note = f"quadratic discriminant B^2-4AD = {fmt(disc_c)} = ({fmt(sq)})^2"

    # forcing identity s(b_i) = d_i * g(b_i)^2, symbolically in c, all i
    forcing_ok = True
    forcing_detail = []
    for i in range(n):
        s_bi = ceval(s, b[i])
        rhs = [d[i] * b[i] * b[i], d[i] * 2 * b[i], d[i]]  # d_i*(b_i + c)^2
        diff = csub(s_bi, rhs)
        ok = czero(diff)
        forcing_ok = forcing_ok and ok
        forcing_detail.append(ok)

    # per-root data
    root_blocks = []
    for c in roots:
        r = [b[i] + c for i in range(n)]
        h_B = rat_height(c)
        h_A = max(rat_height(ri) for ri in r)
        g_nonzero = all(ri != 0 for ri in r)
        # s at this c
        s_at = trim([csubstitute(ck, c) for ck in s])
        deg_s = len(s_at) - 1
        disc_s = poly_disc(s_at) if deg_s >= 2 else None
        nonsingular = (deg_s in (3, 4)) and (disc_s is not None and disc_s != 0)
        membership = {}
        for T in (100, 1000, 10000):
            membership[f"h_A_le_{T}"] = bool(h_A <= T)
            membership[f"h_B_le_{T}"] = bool(h_B <= T)
        root_blocks.append({
            "c": fmt(c),
            "numerator": c.numerator,
            "denominator": c.denominator,
            "h_B": h_B,
            "r_vector": [fmt(ri) for ri in r],
            "h_A": h_A,
            "membership": membership,
            "g_bi_all_nonzero": bool(g_nonzero),
            "g_bi_values": [fmt(ri) for ri in r],
            "s_at_c_coefficients_ascending": [fmt(x) for x in s_at],
            "deg_s": deg_s,
            "disc_s": fmt(disc_s) if disc_s is not None else None,
            "nonsingular": bool(nonsingular),
            "nondegeneracy_pass": bool(g_nonzero and nonsingular),
        })

    return {
        "b_index": b_index,
        "b": b_int,
        "d": d_int,
        "p_coefficients_ascending": [fmt(x) for x in p],
        "delta_coefficients_ascending": [fmt(x) for x in delta],
        "delta_degree": len(delta) - 1,
        "delta_interpolation_check": "pass" if interp_ok else "FAIL",
        "s_remainder_coefficients_in_c_ascending": [
            [fmt(x) for x in ctrim(ck)] for ck in s
        ],
        "x5_coefficient_in_c": {
            "is_quadratic": bool(is_quadratic),
            "A_c2": fmt(A),
            "B_c": fmt(B),
            "D_const": fmt(D),
        },
        "solve_note": solve_note,
        "roots": root_blocks,
        "forcing_identity_check": "pass" if forcing_ok else "FAIL",
        "forcing_identity_per_i": forcing_detail,
    }

def main():
    self_tests()
    results = [derive_pair(bi, b, d) for (bi, b, d) in PAIRS]
    for res in results:
        print("=" * 78)
        print(f"b_index = {res['b_index']}   b = {res['b']}   d = {res['d']}")
        print(f"  p(x)  (asc) = {res['p_coefficients_ascending']}")
        print(f"  delta (asc) = {res['delta_coefficients_ascending']}  (deg {res['delta_degree']})")
        print(f"  delta(b_i) == d_i for all i: {res['delta_interpolation_check']}")
        x5 = res["x5_coefficient_in_c"]
        print(f"  x^5 coeff of s: A*c^2 + B*c + D = {x5['A_c2']}*c^2 + {x5['B_c']}*c + {x5['D_const']}  (quadratic: {x5['is_quadratic']})")
        print(f"  solve: {res['solve_note']}")
        for rb in res["roots"]:
            print(f"  root c = {rb['c']}  (num {rb['numerator']}, den {rb['denominator']})  h_B = {rb['h_B']}")
            print(f"    r = {rb['r_vector']}   h_A = {rb['h_A']}")
            print(f"    membership: {rb['membership']}")
            print(f"    g(b_i) all nonzero: {rb['g_bi_all_nonzero']}  (values {rb['g_bi_values']})")
            print(f"    s(c) (asc) = {rb['s_at_c_coefficients_ascending']}  deg s = {rb['deg_s']}  disc(s) = {rb['disc_s']}")
            print(f"    nonsingular: {rb['nonsingular']}   nondegeneracy_pass: {rb['nondegeneracy_pass']}")
        print(f"  forcing identity s(b_i) = d_i*g(b_i)^2 identically in c: {res['forcing_identity_check']}  per_i={res['forcing_identity_per_i']}")
    # machine-readable dump for transcription
    import json
    def default(o):
        if isinstance(o, F):
            return fmt(o)
        raise TypeError
    with open("/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909/coordination/goals/GOAL-ECRANK-002/batches/BATCH-2f2b56/reviews/TASK-20260909-9e06b1/scratch/q1_dump.json", "w") as f:
        json.dump(results, f, indent=2, default=default)
    print("=" * 78)
    print("dump written to scratch/q1_dump.json")

if __name__ == "__main__":
    main()
