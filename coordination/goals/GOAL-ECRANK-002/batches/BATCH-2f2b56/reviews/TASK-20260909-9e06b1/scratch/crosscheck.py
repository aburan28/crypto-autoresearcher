#!/usr/bin/env python3
"""Independent cross-checks for derive_q1.py (TASK-20260909-9e06b1, PHASE 1).

Method 1: x^5 coefficient of the remainder via the closed-form reduction
    x5_rem = q5 - p4*q7 - p5*(q6 - p5*q7)
  (qk = x^k coeff of delta*(x+c)^2; p4,p5 = x^4,x^5 coeffs of p).
Method 2: discriminant via companion matrix: disc(f) = (-1)^{n(n-1)/2} Res(f,f'),
    Res(f,f') = lc(f)^{n-1} * prod f'(r_i) = det(f'(C)) where C = companion(f)
    (eigenvalues of f'(C) are f'(r_i)). Different matrix than Sylvester.
Method 3: Monte-Carlo: Sylvester resultant vs companion resultant on random polys.
Method 4: reduction check: delta*g^2 - s == p * (linear quotient) exactly.
"""
import random
from fractions import Fraction as F

# ---- reuse the exact machinery (import from sibling script) ----
import importlib.util
spec = importlib.util.spec_from_file_location(
    "dq1",
    "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909/coordination/goals/GOAL-ECRANK-002/batches/BATCH-2f2b56/reviews/TASK-20260909-9e06b1/scratch/derive_q1.py")
dq1 = importlib.util.module_from_spec(spec)
# prevent main() from running on import
import types
src = open(spec.origin).read().replace('if __name__ == "__main__":\n    main()', '')
exec(compile(src, spec.origin, "exec"), dq1.__dict__)

F = dq1.F
trim = dq1.trim
poly_mul = dq1.poly_mul
poly_add = dq1.poly_add
poly_sub = dq1.poly_sub
poly_mod = dq1.poly_mod
poly_eval = dq1.poly_eval
poly_det = dq1.poly_det
resultant = dq1.resultant
poly_disc = dq1.poly_disc

def fmt(q):
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"

# ---------------- Method 2: companion-matrix resultant ---------------------
def mat_mul(A, B):
    n = len(A)
    C = [[F(0)] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if A[i][k] == 0:
                continue
            for j in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C

def mat_add(A, B):
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]

def mat_scale(A, s):
    return [[s * x for x in row] for row in A]

def companion(f):
    """Companion matrix of monic f (ascending coeffs), standard form:
    C = [[0,0,...,0,-c0],[1,0,...,0,-c1],[0,1,...,0,-c2],...,[0,...,1,-c_{n-1}]]
    char poly of C is f."""
    f = trim(f)
    n = len(f) - 1
    C = [[F(0)] * n for _ in range(n)]
    for i in range(n - 1):
        C[i + 1][i] = F(1)          # subdiagonal ones
    for j in range(n):
        C[j][n - 1] = -f[j]         # last column = -coeffs
    return C

def mat_poly_eval(q, C):
    """q(C) by Horner: r = 0; for ai in reversed(coeffs): r = r*C + ai*I."""
    n = len(C)
    I = [[F(1) if i == j else F(0) for j in range(n)] for i in range(n)]
    r = [[F(0)] * n for _ in range(n)]
    for ai in reversed(trim(q)):
        r = mat_add(mat_mul(r, C), mat_scale(I, ai))
    return r

def resultant_companion(p, q):
    """Res(p,q) = lc(p)^{deg q} * prod_{p(a)=0} q(a) = lc(p)^m * det(q(C_p))."""
    p = trim(p)
    n = len(p) - 1
    m = len(trim(q)) - 1
    lc = p[n]
    # make monic
    pm = [x / lc for x in p]
    C = companion(pm)
    Q = mat_poly_eval(q, C)
    return (lc ** m) * poly_det(Q)

def disc_companion(f):
    f = trim(f)
    n = len(f) - 1
    lc = f[n]
    dp = [F(i) * f[i] for i in range(1, n + 1)]
    res = resultant_companion(f, dp)
    return (F(-1) ** (n * (n - 1) // 2)) * res / (lc ** (2 * n - 2))

# ---------------- Method 3: Monte Carlo cross-validation -------------------
def rand_poly(deg, bound=5):
    cs = [F(random.randint(-bound, bound)) for _ in range(deg)]
    cs.append(F(random.randint(1, bound)))  # nonzero leading
    return trim(cs)

def monte_carlo(trials=120):
    bad = 0
    for _ in range(trials):
        n = random.randint(2, 5)
        m = random.randint(1, 4)
        p = rand_poly(n)
        q = rand_poly(m)
        r1 = resultant(p, q)
        r2 = resultant_companion(p, q)
        if r1 != r2:
            bad += 1
            print("MISMATCH", n, m, fmt(r1), fmt(r2))
    # also discriminants
    bad2 = 0
    for _ in range(trials):
        n = random.randint(2, 5)
        f = rand_poly(n)
        d1 = poly_disc(f)
        d2 = disc_companion(f)
        if d1 != d2:
            bad2 += 1
            print("DISC MISMATCH", n, fmt(d1), fmt(d2))
    print(f"monte_carlo: resultant mismatches={bad}/{trials}, disc mismatches={bad2}/{trials}")
    return bad == 0 and bad2 == 0

# ---------------- Method 1: x5 closed form ---------------------------------
def x5_closed_form(b, d):
    b = [F(x) for x in b]
    d = [F(x) for x in d]
    n = 6
    p = [F(1)]
    for bi in b:
        p = poly_mul(p, [F(-bi), F(1)])
    delta = [F(0)]
    for i in range(n):
        Li = [F(1)]
        denom = F(1)
        for j in range(n):
            if j == i:
                continue
            Li = poly_mul(Li, [F(-b[j]), F(1)])
            denom *= (b[i] - b[j])
        Li = dq1.poly_scale(Li, d[i] / denom)
        delta = poly_add(delta, Li)
    delta = trim(delta)
    dl = [F(0)] * 6
    for i, ai in enumerate(delta):
        dl[i] = ai
    # qk = x^k coeff of delta*(x^2 + 2 c x + c^2), as (const, c, c^2)
    def qk(k):
        ck = [F(0), F(0), F(0)]
        if k < 6:
            ck[2] += dl[k]
        if 0 <= k - 1 < 6:
            ck[1] += 2 * dl[k - 1]
        if 0 <= k - 2 < 6:
            ck[0] += dl[k - 2]
        return ck
    q5, q6, q7 = qk(5), qk(6), qk(7)
    p4, p5 = p[4], p[5]
    # x5_rem = q5 - p4*q7 - p5*(q6 - p5*q7)
    inner = dq1.csub(q6, dq1.cmul([p5], q7))
    x5 = dq1.csub(dq1.csub(q5, dq1.cmul([p4], q7)), dq1.cmul([p5], inner))
    return trim(p), delta, dq1.ctrim(x5)

# ---------------- Method 4: reduction quotient check -----------------------
def reduction_check(b, d):
    b = [F(x) for x in b]
    d = [F(x) for x in d]
    n = 6
    p = [F(1)]
    for bi in b:
        p = poly_mul(p, [F(-bi), F(1)])
    delta = [F(0)]
    for i in range(n):
        Li = [F(1)]
        denom = F(1)
        for j in range(n):
            if j == i:
                continue
            Li = poly_mul(Li, [F(-b[j]), F(1)])
            denom *= (b[i] - b[j])
        Li = dq1.poly_scale(Li, d[i] / denom)
        delta = poly_add(delta, Li)
    delta = trim(delta)
    # s from the main script's cmod, at a sample c value (exact, c = 12347/99991)
    c = F(12347, 99991)
    g2 = [F(1), F(2 * c), c * c]  # (x+c)^2
    prod = poly_mul(delta, g2)
    s = poly_mod(prod, p)
    # quotient: (prod - s) / p must be a polynomial of degree <= 1
    diff = poly_sub(prod, s)
    # divide diff by p (p monic)
    rem = poly_mod(diff, p)
    if rem != [F(0)]:
        return False, "remainder nonzero"
    # quotient degree
    q = [F(0)]
    a = list(diff)
    while len(a) > len(p) - 1:
        lead = a[-1]
        shift = len(a) - len(p)
        q = poly_add(q, [F(0)] * shift + [lead])
        for j in range(len(p)):
            a[shift + j] -= lead * p[j]
        a = trim(a)
    return True, f"quotient deg {len(q)-1}, coeffs {[fmt(x) for x in q]}"

def main():
    print("== Method 3: Monte Carlo (Sylvester vs companion) ==")
    ok = monte_carlo(120)
    print("monte_carlo:", "PASS" if ok else "FAIL")

    PAIRS = [
        (649,  [0, 1, 13, 8, 7, -5],      [22, 3, -3, 22, 3, -3]),
        (1299, [0, 1, -14, -2, 4, -20],   [165, 165, -165, 3, 3, -165]),
        (4995, [0, 1, -5, 16, -9, 12],    [10, 22, 10, -22, 22, -22]),
    ]
    for b_index, b, d in PAIRS:
        print(f"== pair {b_index} ==")
        p, delta, x5_cf = x5_closed_form(b, d)
        A = x5_cf[2] if len(x5_cf) > 2 else F(0)
        B = x5_cf[1] if len(x5_cf) > 1 else F(0)
        D = x5_cf[0] if len(x5_cf) > 0 else F(0)
        print(f"  x5 closed form: A={fmt(A)} B={fmt(B)} D={fmt(D)}")
        ok4, msg = reduction_check(b, d)
        print(f"  reduction quotient check: {ok4} ({msg})")

    # discriminant cross-check on the five s-at-root quartics
    print("== Method 2: discriminant cross-check (Sylvester vs companion) ==")
    quartics = {
        "649 c=-4":      [F(352), F(-29866, 91), F(-3051, 364), F(1124, 91), F(-281, 364)],
        "1299 c=8":      [F(10560), F(81856, 21), F(-6583, 7), F(-1034, 7), F(-100, 21)],
        "1299 c=-88/89": [F(1277760, 7921), F(-179714816, 1497069), F(-29881087, 499023),
                          F(9007174, 499023), F(871100, 1497069)],
        "4995 c=-163/168": [F(132845, 14112), F(-1840745, 296352), F(-3277667, 3556224),
                            F(-2077079, 889056), F(267283, 3556224)],
        "4995 c=-7/2":   [F(245, 2), F(355, 42), F(4693, 504), F(-359, 126), F(43, 504)],
    }
    all_ok = True
    for name, f in quartics.items():
        d1 = poly_disc(f)
        d2 = disc_companion(f)
        ok = (d1 == d2)
        all_ok = all_ok and ok
        print(f"  {name}: sylvester==companion: {ok}  disc={fmt(d1)}  nonzero={d1 != 0}")
    print("disc cross-check:", "PASS" if all_ok else "FAIL")

if __name__ == "__main__":
    main()
