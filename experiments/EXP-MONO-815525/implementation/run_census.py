"""
EXP-MONO-815525 -- Stage 0 / Stage 1 / Stage 2.

Stage 0  verify the Q_e(T) construction derived by derive_s4.py:
         (a) degree 4 in T; (b) on base points where g splits completely,
         Q_e's roots are exactly the four sign-class x-coordinates
         x(P1 +- P2 +- P3) computed by ordinary curve-point arithmetic;
         (c) symmetry (permutation-invariance of the root triple, and
         F_p-rationality of Q_e when the root triple is Galois-stable).
Stage 1  census of the F_p-factorization degree pattern of Q_e(T) over
         base points where g(X) = X^3 - e1 X^2 + e2 X - e3 is irreducible.
Stage 2  full distribution, compared against the sole pre-registered
         prediction (pattern exactly (1,3) for every instance).

No CAS at runtime.  sympy is used only offline, by derive_s4.py, to produce
the monomial tables this script reads.
"""
import json
import os
import random
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()

SEED = 20260904002
SAMPLES_PER_CURVE = 300
EXHAUSTIVE_PRIME = 101
EXHAUSTIVE_BUDGET_S = 200.0

CURVES = [
    {"id": "C1", "p": 101,  "A": 2, "B": 3},
    {"id": "C2", "p": 1009, "A": 5, "B": 7},
    {"id": "C3", "p": 211,  "A": 3, "B": 11},
    {"id": "C4", "p": 1999, "A": 7, "B": 13},
    {"id": "C5", "p": 101,  "A": 37, "B": 29},
]


def log(m):
    print(m, flush=True)


# ------------------------------------------------------------ F_p[T] toolkit
def pnorm(a, p):
    while a and a[-1] % p == 0:
        a.pop()
    return [c % p for c in a]


def pdeg(a):
    return len(a) - 1


def padd(a, b, p):
    n = max(len(a), len(b))
    return pnorm([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                  for i in range(n)], p)


def psub(a, b, p):
    n = max(len(a), len(b))
    return pnorm([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)
                  for i in range(n)], p)


def pmul(a, b, p):
    if not a or not b:
        return []
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                r[i + j] += ai * bj
    return pnorm(r, p)


def pdivmod(a, b, p):
    a = a[:]
    db = pdeg(b)
    inv = pow(b[-1], -1, p)
    q = [0] * max(0, len(a) - db)
    while len(a) - 1 >= db and a:
        d = len(a) - 1 - db
        c = a[-1] * inv % p
        q[d] = c
        for i in range(db + 1):
            a[d + i] = (a[d + i] - c * b[i]) % p
        a = pnorm(a, p)
    return pnorm(q, p), a


def pgcd(a, b, p):
    a, b = pnorm(a[:], p), pnorm(b[:], p)
    while b:
        a, b = b, pdivmod(a, b, p)[1]
    if a:
        inv = pow(a[-1], -1, p)
        a = [c * inv % p for c in a]
    return a


def pderiv(a, p):
    return pnorm([(i * a[i]) for i in range(1, len(a))], p)


def ppowmod(base, e, mod, p):
    r, b = [1], pdivmod(base, mod, p)[1]
    while e:
        if e & 1:
            r = pdivmod(pmul(r, b, p), mod, p)[1]
        b = pdivmod(pmul(b, b, p), mod, p)[1]
        e >>= 1
    return r


def pmonic(a, p):
    inv = pow(a[-1], -1, p)
    return [c * inv % p for c in a]


def is_irreducible_cubic(g, p):
    """g monic degree 3: irreducible over F_p iff it has no root, iff
    gcd(T^p - T, g) == 1."""
    h = ppowmod([0, 1], p, g, p)
    return pdeg(pgcd(psub(h, [0, 1], p), g, p)) == 0 if psub(h, [0, 1], p) else False


def yun_squarefree(f, p):
    f = pmonic(f, p)
    fp = pderiv(f, p)
    if not fp:
        raise ValueError("derivative vanishes")
    a = pgcd(f, fp, p)
    b = pdivmod(f, a, p)[0]
    c = pdivmod(fp, a, p)[0]
    d = psub(c, pderiv(b, p), p)
    out, i = [], 1
    while pdeg(b) > 0:
        u = pgcd(b, d, p)
        if pdeg(u) > 0:
            out.append((u, i))
        b1 = pdivmod(b, u, p)[0]
        c1 = pdivmod(d, u, p)[0]
        d = psub(c1, pderiv(b1, p), p)
        b = b1
        i += 1
    return out


def ddf_degrees(f, p):
    """f monic squarefree -> list of irreducible factor degrees (multiset)."""
    out, i, h, fs = [], 1, [0, 1], f[:]
    while pdeg(fs) >= 2 * i:
        h = ppowmod(h, p, fs, p)
        g = pgcd(psub(h, [0, 1], p), fs, p)
        if pdeg(g) > 0:
            out += [i] * (pdeg(g) // i)
            fs = pdivmod(fs, g, p)[0]
            h = pdivmod(h, fs, p)[1] if pdeg(fs) > 0 else [0]
        i += 1
    if pdeg(fs) > 0:
        out.append(pdeg(fs))
    return out


def factor_pattern(f, p):
    f = pnorm(f[:], p)
    if pdeg(f) <= 0:
        return []
    degs = []
    for sf, mult in yun_squarefree(f, p):
        degs += ddf_degrees(pmonic(sf, p), p) * mult
    return sorted(degs)


# ------------------------------------------------------------ F_{p^3} toolkit
class F3:
    """F_p[X]/(g),  g = X^3 - e1 X^2 + e2 X - e3  (irreducible)."""

    def __init__(self, p, e1, e2, e3):
        self.p = p
        # X^3 = e1 X^2 - e2 X + e3
        self.r3 = [e3 % p, (-e2) % p, e1 % p]
        # X^4 = e1 X^3 - e2 X^2 + e3 X
        r4 = [0, e3 % p, (-e2) % p]
        for i in range(3):
            r4[i] = (r4[i] + e1 * self.r3[i]) % p
        self.r4 = r4

    def mul(self, a, b):
        p = self.p
        a0, a1, a2 = a
        b0, b1, b2 = b
        c0 = a0 * b0
        c1 = a0 * b1 + a1 * b0
        c2 = a0 * b2 + a1 * b1 + a2 * b0
        c3 = a1 * b2 + a2 * b1
        c4 = a2 * b2
        r3, r4 = self.r3, self.r4
        return ((c0 + c3 * r3[0] + c4 * r4[0]) % p,
                (c1 + c3 * r3[1] + c4 * r4[1]) % p,
                (c2 + c3 * r3[2] + c4 * r4[2]) % p)

    def add(self, a, b):
        p = self.p
        return ((a[0] + b[0]) % p, (a[1] + b[1]) % p, (a[2] + b[2]) % p)

    def smul(self, k, a):
        p = self.p
        return (k * a[0] % p, k * a[1] % p, k * a[2] % p)

    def pw(self, a, e):
        r = (1, 0, 0)
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r


# ------------------------------------------------------------ curve arithmetic
def pt_add(p, A, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def pt_neg(p, P):
    return None if P is None else (P[0], (-P[1]) % p)


def curve_order(p, A, B):
    n = p + 1
    for x in range(p):
        v = (x * x * x + A * x + B) % p
        if v == 0:
            continue
        n += 1 if pow(v, (p - 1) // 2, p) == 1 else -1
    return n


def j_invariant(p, A, B):
    d = (4 * A ** 3 + 27 * B ** 2) % p
    if d == 0:
        return None
    return 1728 * 4 * A ** 3 % p * pow(d, -1, p) % p


def points_with_x(p, A, B, xs):
    out = []
    for x in xs:
        v = (x * x * x + A * x + B) % p
        if v == 0:
            out.append(None)
            continue
        y = None
        for c in range(1, p):
            if c * c % p == v:
                y = c
                break
        out.append((x, y) if y is not None else None)
    return out


# ------------------------------------------------------------ Q_e construction
S4T = json.load(open(os.path.join(HERE, "s4_monomials.json")))
S3T = json.load(open(os.path.join(HERE, "s3_monomials.json")))
SYMT = json.load(open(os.path.join(HERE, "s4_symmetric_coeffs.json")))


def compile_s4(p, A, B):
    """ordered-base S_4 -> {x4-exponent d: [((a,b,c), coeff in F_p), ...]}"""
    tab = {d: {} for d in range(5)}
    for k, co in S4T["terms"].items():
        a, b, c, d, i, j = [int(t) for t in k.split(",")]
        v = co % p * pow(A, i, p) % p * pow(B, j, p) % p
        if v:
            tab[d][(a, b, c)] = (tab[d].get((a, b, c), 0) + v) % p
    return {d: [(k, v) for k, v in tab[d].items() if v] for d in range(5)}


def compile_s3(p, A, B):
    tab = {}
    for k, co in S3T["terms"].items():
        a, b, c, i, j = [int(t) for t in k.split(",")]
        v = co % p * pow(A, i, p) % p * pow(B, j, p) % p
        if v:
            tab[(a, b, c)] = (tab.get((a, b, c), 0) + v) % p
    return [(k, v) for k, v in tab.items() if v]


def compile_sym(p, A, B):
    """symmetric-base Q_e -> {k: [((i,j,l), coeff in F_p), ...]} in e1,e2,e3"""
    out = {}
    for k, terms in SYMT["coeffs"].items():
        tab = {}
        for key, co in terms.items():
            i, j, l, ia, ib = [int(t) for t in key.split(",")]
            v = co % p * pow(A, ia, p) % p * pow(B, ib, p) % p
            if v:
                tab[(i, j, l)] = (tab.get((i, j, l), 0) + v) % p
        out[int(k)] = [(kk, vv) for kk, vv in tab.items() if vv]
    return out


def qe_from_sym(symtab, p, e1, e2, e3):
    """Q_e(T) coefficients in F_p, via the symmetric-base descent (fast path)."""
    P1 = [pow(e1, i, p) for i in range(5)]
    P2 = [pow(e2, i, p) for i in range(5)]
    P3 = [pow(e3, i, p) for i in range(5)]
    out = []
    for k in range(5):
        s = 0
        for (i, j, l), v in symtab[k]:
            s += v * P1[i] % p * P2[j] % p * P3[l]
        out.append(s % p)
    return pnorm(out, p)


def qe_from_ordered(s4tab, F, X1, X2, X3):
    """Q_e(T) coefficients in F_{p^3}, via the ordered-base S_4 (Stage-1
    spec path): substitute the three roots of g as F_{p^3} elements."""
    pw1 = [(1, 0, 0)]
    pw2 = [(1, 0, 0)]
    pw3 = [(1, 0, 0)]
    for _ in range(4):
        pw1.append(F.mul(pw1[-1], X1))
        pw2.append(F.mul(pw2[-1], X2))
        pw3.append(F.mul(pw3[-1], X3))
    out = []
    for d in range(5):
        acc = (0, 0, 0)
        for (a, b, c), v in s4tab[d]:
            acc = F.add(acc, F.smul(v, F.mul(F.mul(pw1[a], pw2[b]), pw3[c])))
        out.append(acc)
    return out


def qe_from_resultant(s3tab, F, X1, X2, X3):
    """Q_e(T) via an INDEPENDENT runtime elimination: Res_U(S_3(x1,x2,U),
    S_3(x3,T,U)) as a 4x4 Sylvester determinant over F_{p^3}[T].  Does not
    read the derived S_4 table at all."""
    p = F.p

    def s3_coeffs(V1, V2):
        """S_3(V1,V2,U) as [c0,c1,c2] in U, entries in F_{p^3}."""
        pw = {}
        for V, idx in ((V1, 0), (V2, 1)):
            e = [(1, 0, 0)]
            for _ in range(2):
                e.append(F.mul(e[-1], V))
            pw[idx] = e
        out = [(0, 0, 0)] * 3
        for (a, b, c), v in s3tab:
            out[c] = F.add(out[c], F.smul(v, F.mul(pw[0][a], pw[1][b])))
        return out

    # first quadratic: entries constant in T
    P = [[ci] for ci in s3_coeffs(X1, X2)]          # list over U-degree of T-polys
    # second: S_3(x3, T, U); expand in U with T-polynomial coefficients
    pw3 = [(1, 0, 0), X3, F.mul(X3, X3)]
    Q = [[(0, 0, 0)] * 3 for _ in range(3)]         # Q[u_deg][t_deg]
    for (a, b, c), v in s3tab:
        Q[c][b] = F.add(Q[c][b], F.smul(v, pw3[a]))
    Qp = [[Q[u][t] for t in range(3)] for u in range(3)]

    def tp_norm(a):
        while a and a[-1] == (0, 0, 0):
            a.pop()
        return a

    def tp_add(a, b):
        n = max(len(a), len(b))
        return tp_norm([F.add(a[i] if i < len(a) else (0, 0, 0),
                              b[i] if i < len(b) else (0, 0, 0))
                        for i in range(n)])

    def tp_mul(a, b):
        if not a or not b:
            return []
        r = [(0, 0, 0)] * (len(a) + len(b) - 1)
        for i, ai in enumerate(a):
            if ai == (0, 0, 0):
                continue
            for j, bj in enumerate(b):
                if bj == (0, 0, 0):
                    continue
                r[i + j] = F.add(r[i + j], F.mul(ai, bj))
        return tp_norm(r)

    def tp_neg(a):
        return [F.smul(p - 1, c) for c in a]

    # Sylvester matrix of two U-quadratics: 4x4, rows [P,P,Q,Q]
    prow = [P[2], P[1], P[0]]                      # leading-first
    qrow = [tp_norm(Qp[2][:]), tp_norm(Qp[1][:]), tp_norm(Qp[0][:])]
    M = [[[] for _ in range(4)] for _ in range(4)]
    for s in range(2):
        for k in range(3):
            M[s][s + k] = prow[k]
    for s in range(2):
        for k in range(3):
            M[2 + s][s + k] = qrow[k]

    def det(mat):
        n = len(mat)
        if n == 1:
            return mat[0][0]
        acc = []
        for j in range(n):
            if not mat[0][j]:
                continue
            sub = [row[:j] + row[j + 1:] for row in mat[1:]]
            t = tp_mul(mat[0][j], det(sub))
            acc = tp_add(acc, t if j % 2 == 0 else tp_neg(t))
        return acc

    res = det(M)
    while len(res) < 5:
        res.append((0, 0, 0))
    return res[:5]


def classify(qe, p):
    """Full descriptive classification of one specialized Q_e(T).

    `factor_degrees`     literal F_p-irreducible factor degrees of the affine
                         polynomial Q_e(T)  -- this is what M1 is scored on,
                         exactly as pre-registered.
    `projective_degrees` the same, with (4 - deg Q_e) roots at T = infinity
                         restored as F_p-rational points of the fibre.  A
                         DESCRIPTIVE statistic only (M2), reported separately
                         and never substituted for M1.
    """
    deg = pdeg(qe)
    pat = factor_pattern(qe, p) if deg > 0 else []
    inf_mult = 4 - deg if deg >= 0 else 4
    proj = sorted([1] * max(0, inf_mult) + pat)
    return {
        "degree_in_T": deg,
        "roots_at_infinity_multiplicity": max(0, inf_mult),
        "factor_degrees": pat,
        "pattern": "deg%d:%s" % (deg, "+".join(str(d) for d in pat)),
        "projective_degrees": proj,
        "projective_pattern": "+".join(str(d) for d in proj),
        "matches_prediction_1_3_literal": bool(deg == 4 and pat == [1, 3]),
        "matches_1_3_projective": bool(proj == [1, 3]),
    }


def to_fp(coeffs3, p):
    """F_{p^3} coefficient vector -> F_p list, or None if not F_p-rational."""
    out = []
    for c in coeffs3:
        if c[1] % p or c[2] % p:
            return None
        out.append(c[0] % p)
    return out


# ------------------------------------------------------------ main
def main():
    rng = random.Random(SEED)
    report = {"seed": SEED, "stage_0": {}, "stage_1": {}, "stage_2": {},
              "derivation_checks": json.load(
                  open(os.path.join(HERE, "derivation_checks.json")))}

    log("=== EXP-MONO-815525 run RUN-MONO-815525-1 ===")
    log("derivation checks (from derive_s4.py): %s"
        % report["derivation_checks"])

    # ---- curve admissibility
    curve_meta = []
    for C in CURVES:
        p, A, B = C["p"], C["A"], C["B"]
        j = j_invariant(p, A, B)
        n = curve_order(p, A, B)
        t = p + 1 - n
        m = dict(C, j_invariant=j, order=n, trace=t,
                 ordinary=bool(t % p != 0),
                 j_not_special=bool(j not in (0, 1728 % p)),
                 nonsingular=bool((4 * A ** 3 + 27 * B ** 2) % p != 0))
        curve_meta.append(m)
        log("curve %s: p=%d A=%d B=%d  j=%s  #E=%d t=%d ordinary=%s j_ok=%s"
            % (C["id"], p, A, B, j, n, t, m["ordinary"], m["j_not_special"]))
    report["curves"] = curve_meta
    if not all(m["ordinary"] and m["j_not_special"] and m["nonsingular"]
               for m in curve_meta):
        log("FATAL: a declared curve is not an admissible ordinary curve")
        report["fatal"] = "curve_admissibility"
        json.dump(report, open(sys.argv[1], "w"), indent=1)
        return 2

    compiled = {}
    for C in curve_meta:
        p, A, B = C["p"], C["A"], C["B"]
        compiled[C["id"]] = (compile_s4(p, A, B), compile_s3(p, A, B),
                             compile_sym(p, A, B))

    # ================================================== STAGE 0
    log("\n--- STAGE 0: construction verification ---")
    s0 = {"check_a_degree4": {"instances": [], "pass": None},
          "check_b_split_baseline": {"instances": [], "pass": None},
          "check_c_symmetry": {"instances": [], "pass": None},
          "check_s3_against_group_law": {"instances": [], "pass": None},
          "check_paths_agree": {"instances": [], "pass": None}}

    # --- S_3 itself against ordinary point arithmetic (foundation of S_4)
    for C in curve_meta:
        p, A, B = C["p"], C["A"], C["B"]
        s3tab = compiled[C["id"]][1]
        pts = [q for q in points_with_x(p, A, B, range(2, min(p, 400)))
               if q is not None and q[1] != 0][:6]
        ok = True
        for i in range(len(pts)):
            for k in range(i + 1, len(pts)):
                P, Q = pts[i], pts[k]
                for sgn in (1, -1):
                    R = pt_add(p, A, P, Q if sgn == 1 else pt_neg(p, Q))
                    if R is None:
                        continue
                    v = 0
                    for (a, b, c), co in s3tab:
                        v += co * pow(P[0], a, p) % p * pow(Q[0], b, p) % p \
                             * pow(R[0], c, p)
                    if v % p != 0:
                        ok = False
        s0["check_s3_against_group_law"]["instances"].append(
            {"curve": C["id"], "pass": ok, "n_points_used": len(pts)})
        log("  S_3 vanishes on all x(P +- Q) for %s: %s" % (C["id"], ok))
    s0["check_s3_against_group_law"]["pass"] = all(
        i["pass"] for i in s0["check_s3_against_group_law"]["instances"])

    # --- (b) split-g baseline against the sign-class sums, + (a) + (c)
    for C in curve_meta:
        p, A, B = C["p"], C["A"], C["B"]
        s4tab, s3tab, symtab = compiled[C["id"]]
        pts = [q for q in points_with_x(p, A, B, range(2, p))
               if q is not None and q[1] != 0]
        tested = 0
        idx = 0
        while tested < 60 and idx + 3 <= len(pts):
            P1, P2, P3 = pts[idx], pts[idx + 1], pts[idx + 2]
            idx += 1
            xs = [P1[0], P2[0], P3[0]]
            if len(set(xs)) != 3:
                continue
            e1 = sum(xs) % p
            e2 = (xs[0] * xs[1] + xs[0] * xs[2] + xs[1] * xs[2]) % p
            e3 = (xs[0] * xs[1] * xs[2]) % p
            # the four sign classes, eps1 = +1 fixed
            sums = []
            for s2 in (1, -1):
                for s3 in (1, -1):
                    Racc = pt_add(p, A, P1, P2 if s2 == 1 else pt_neg(p, P2))
                    Racc = pt_add(p, A, Racc, P3 if s3 == 1 else pt_neg(p, P3))
                    sums.append("INF" if Racc is None else Racc[0])
            qe = qe_from_sym(symtab, p, e1, e2, e3)
            n_inf = sums.count("INF")
            deg = pdeg(qe)
            rec = {"curve": C["id"], "e": [e1, e2, e3], "xs": xs,
                   "signed_sums": sums, "qe": qe, "degree_in_T": deg,
                   "n_sign_classes_at_infinity": n_inf}
            # (a) the SPECIALIZED degree in T must be 4 minus the number of
            # sign classes whose sum is the point at infinity (a root of the
            # homogenised quartic at T = infinity).  deg_T S_4 = 4 as a
            # polynomial identity is checked symbolically in derive_s4.py.
            a_pass = bool(deg == 4 - n_inf)
            s0["check_a_degree4"]["instances"].append(
                {"curve": C["id"], "e": [e1, e2, e3], "degree_in_T": deg,
                 "n_sign_classes_at_infinity": n_inf, "pass": a_pass})
            # (b) the finite sign-class x-coordinates must be exactly the
            # roots of Q_e, with multiplicity.
            finite = [r for r in sums if r != "INF"]
            target = [1]
            for r in finite:
                target = pmul(target, [(-r) % p, 1], p)
            if deg != len(finite):
                rec["baseline_pass"] = False
                rec["baseline_note"] = "degree does not match finite-root count"
            else:
                lead = qe[-1]
                monic = [c * pow(lead, -1, p) % p for c in qe]
                rec["baseline_pass"] = bool(monic == target)
                rec["monic_qe"] = monic
                rec["prod_T_minus_finite_signed_sums"] = target
            s0["check_b_split_baseline"]["instances"].append(rec)
            # (c) symmetry: permuting the ordered roots must not move Q_e,
            # and the ordered-base path must agree with the symmetric path.
            tested += 1
        log("  split-g baseline instances on %s: %d" % (C["id"], tested))
    s0["check_a_degree4"]["pass"] = all(
        i["pass"] for i in s0["check_a_degree4"]["instances"])
    bres = [i["baseline_pass"] for i in s0["check_b_split_baseline"]["instances"]]
    s0["check_b_split_baseline"]["pass"] = bool(bres) and all(bres)
    s0["check_b_split_baseline"]["n_compared"] = len(bres)
    s0["check_b_split_baseline"]["n_skipped"] = 0
    s0["check_a_degree4"]["n_probes_with_a_sign_class_at_infinity"] = sum(
        1 for i in s0["check_a_degree4"]["instances"]
        if i["n_sign_classes_at_infinity"] > 0)
    s0["check_a_degree4"]["symbolic_deg_T_S4_is_4"] = bool(
        report["derivation_checks"]["s4_degree_4_in_each_var"])
    log("  (a) deg_T Q_e == 4 - #(sign classes at infinity) on all split-g "
        "probes: %s   [symbolic deg_T S_4 = 4: %s]"
        % (s0["check_a_degree4"]["pass"],
           s0["check_a_degree4"]["symbolic_deg_T_S4_is_4"]))
    log("      (%d of %d split-g probes had >=1 sign class at infinity)"
        % (s0["check_a_degree4"]["n_probes_with_a_sign_class_at_infinity"],
           len(s0["check_a_degree4"]["instances"])))
    log("  (b) Q_e roots == finite sign-class sums on %d split-g probes: %s"
        % (len(bres), s0["check_b_split_baseline"]["pass"]))

    # --- (c) symmetry + path agreement, on g-irreducible base points
    for C in curve_meta:
        p, A, B = C["p"], C["A"], C["B"]
        s4tab, s3tab, symtab = compiled[C["id"]]
        got = 0
        tries = 0
        while got < 10 and tries < 20000:
            tries += 1
            e1, e2, e3 = rng.randrange(p), rng.randrange(p), rng.randrange(p)
            g = [(-e3) % p, e2 % p, (-e1) % p, 1]
            if not is_irreducible_cubic(g, p):
                continue
            got += 1
            F = F3(p, e1, e2, e3)
            X1 = (0, 1, 0)
            X2 = F.pw(X1, p)
            X3 = F.pw(X2, p)
            perms = [(X1, X2, X3), (X2, X3, X1), (X3, X1, X2),
                     (X2, X1, X3), (X1, X3, X2), (X3, X2, X1)]
            vals = [qe_from_ordered(s4tab, F, *pm) for pm in perms]
            perm_ok = all(v == vals[0] for v in vals)
            rational = to_fp(vals[0], p)
            fast = qe_from_sym(symtab, p, e1, e2, e3)
            resu = qe_from_resultant(s3tab, F, X1, X2, X3)
            resu_fp = to_fp(resu, p)
            agree = bool(rational is not None
                         and pnorm(rational[:], p) == fast
                         and resu_fp is not None
                         and pnorm(resu_fp[:], p) == fast)
            s0["check_c_symmetry"]["instances"].append(
                {"curve": C["id"], "e": [e1, e2, e3],
                 "permutation_invariant": bool(perm_ok),
                 "lands_in_Fp": bool(rational is not None)})
            s0["check_paths_agree"]["instances"].append(
                {"curve": C["id"], "e": [e1, e2, e3], "pass": agree,
                 "ordered_base_Fp": rational, "symmetric_base": fast,
                 "runtime_resultant_Fp": resu_fp})
        log("  symmetry/path-agreement probes on %s: %d" % (C["id"], got))
    s0["check_c_symmetry"]["pass"] = all(
        i["permutation_invariant"] and i["lands_in_Fp"]
        for i in s0["check_c_symmetry"]["instances"])
    s0["check_paths_agree"]["pass"] = all(
        i["pass"] for i in s0["check_paths_agree"]["instances"])
    log("  (c) permutation-invariant and F_p-rational: %s"
        % s0["check_c_symmetry"]["pass"])
    log("  three independent construction paths agree: %s"
        % s0["check_paths_agree"]["pass"])

    s0["all_pass"] = bool(s0["check_a_degree4"]["pass"]
                          and s0["check_a_degree4"]["symbolic_deg_T_S4_is_4"]
                          and s0["check_b_split_baseline"]["pass"]
                          and s0["check_c_symmetry"]["pass"]
                          and s0["check_s3_against_group_law"]["pass"]
                          and s0["check_paths_agree"]["pass"])
    report["stage_0"] = s0
    log("STAGE 0 OVERALL: %s" % ("PASS" if s0["all_pass"] else "FAIL"))
    if not s0["all_pass"]:
        report["disposition"] = "failed_infrastructure"
        json.dump(report, open(sys.argv[1], "w"), indent=1)
        return 3

    # ================================================== STAGE 1
    log("\n--- STAGE 1: g-irreducible cycle-type census ---")
    instances = []
    per_curve = {}
    for C in curve_meta:
        p, A, B = C["p"], C["A"], C["B"]
        s4tab, s3tab, symtab = compiled[C["id"]]
        kept, draws = 0, 0
        pat_count = {}
        while kept < SAMPLES_PER_CURVE:
            draws += 1
            e1, e2, e3 = rng.randrange(p), rng.randrange(p), rng.randrange(p)
            g = [(-e3) % p, e2 % p, (-e1) % p, 1]
            if not is_irreducible_cubic(g, p):
                continue
            kept += 1
            F = F3(p, e1, e2, e3)
            X1 = (0, 1, 0)
            X2 = F.pw(X1, p)
            X3 = F.pw(X2, p)
            ordered = qe_from_ordered(s4tab, F, X1, X2, X3)
            qfp = to_fp(ordered, p)
            fast = qe_from_sym(symtab, p, e1, e2, e3)
            lands = qfp is not None
            agree = bool(lands and pnorm(qfp[:], p) == fast)
            qe = fast
            cl = classify(qe, p)
            key = cl["pattern"]
            pat_count[key] = pat_count.get(key, 0) + 1
            rec = {"curve": C["id"], "p": p, "A": A, "B": B,
                   "e1": e1, "e2": e2, "e3": e3,
                   "g": "X^3 - %dX^2 + %dX - %d" % (e1, e2, e3),
                   "Qe_coeffs_low_to_high": qe,
                   "lands_in_Fp": lands,
                   "ordered_and_symmetric_paths_agree": agree,
                   "source": "random_sample"}
            rec.update(cl)
            rec["matches_prediction_1_3"] = cl["matches_prediction_1_3_literal"]
            instances.append(rec)
        per_curve[C["id"]] = {"kept": kept, "draws": draws,
                              "rejected_reducible_g": draws - kept,
                              "patterns": pat_count}
        log("  %s: %d qualifying instances from %d draws (%d rejected, g reducible)"
            % (C["id"], kept, draws, draws - kept))
        log("      patterns: %s" % pat_count)

    report["stage_1"] = {"sampling": per_curve,
                         "samples_per_curve_target": SAMPLES_PER_CURVE}

    # ---- exhaustive sweep at the smallest prime, time-capped, deterministic
    log("\n  exhaustive lexicographic sweep over (e1,e2,e3) in F_%d^3 ..."
        % EXHAUSTIVE_PRIME)
    exh = []
    for C in curve_meta:
        if C["p"] != EXHAUSTIVE_PRIME:
            continue
        p, A, B = C["p"], C["A"], C["B"]
        s4tab, s3tab, symtab = compiled[C["id"]]
        pat_count = {}
        proj_count = {}
        scanned = irr = 0
        deviations = []
        completed = True
        t_start = time.time()
        last = (0, 0, 0)
        for e1 in range(p):
            if time.time() - t_start > EXHAUSTIVE_BUDGET_S:
                completed = False
                break
            for e2 in range(p):
                for e3 in range(p):
                    scanned += 1
                    last = (e1, e2, e3)
                    g = [(-e3) % p, e2 % p, (-e1) % p, 1]
                    if not is_irreducible_cubic(g, p):
                        continue
                    irr += 1
                    qe = qe_from_sym(symtab, p, e1, e2, e3)
                    cl = classify(qe, p)
                    pat_count[cl["pattern"]] = pat_count.get(cl["pattern"], 0) + 1
                    proj_count[cl["projective_pattern"]] = \
                        proj_count.get(cl["projective_pattern"], 0) + 1
                    if not cl["matches_prediction_1_3_literal"]:
                        d = {"curve": C["id"], "p": p, "A": A, "B": B,
                             "e": [e1, e2, e3], "Qe": qe}
                        d.update(cl)
                        deviations.append(d)
        exh.append({"curve": C["id"], "p": p, "A": A, "B": B,
                    "completed": completed, "last_triple_scanned": list(last),
                    "triples_scanned": scanned, "g_irreducible_count": irr,
                    "patterns": pat_count, "projective_patterns": proj_count,
                    "n_literal_deviations": len(deviations),
                    "n_projective_deviations": sum(
                        v for k, v in proj_count.items() if k != "1+3"),
                    "deviations_all": deviations,
                    "wall_seconds": round(time.time() - t_start, 1)})
        log("  exhaustive %s: completed=%s scanned=%d irreducible-g=%d"
            % (C["id"], completed, scanned, irr))
        log("      literal patterns:    %s" % pat_count)
        log("      projective patterns: %s" % proj_count)

    report["stage_1"]["exhaustive_sweep"] = exh
    report["stage_1"]["instances"] = instances
    report["stage_1"]["n_instances_sampled"] = len(instances)

    # ================================================== STAGE 2
    log("\n--- STAGE 2: distribution vs the sole pre-registered prediction ---")
    dist = {}
    for r in instances:
        dist[r["pattern"]] = dist.get(r["pattern"], 0) + 1
    pdist = {}
    for r in instances:
        pdist[r["projective_pattern"]] = pdist.get(r["projective_pattern"], 0) + 1
    dev = [r for r in instances if not r["matches_prediction_1_3_literal"]]
    pdev = [r for r in instances if not r["matches_1_3_projective"]]
    log("  sampled census (%d instances, 4 curves, 4 primes):" % len(instances))
    for k in sorted(dist, key=lambda z: -dist[z]):
        log("    %-14s %6d  (%.4f)" % (k, dist[k], dist[k] / len(instances)))
    log("  sampled projective distribution: %s" % pdist)
    log("  M1 LITERAL (every sampled Q_e factors as (linear)(irred cubic)): %s"
        % (not dev))
    log("  M1 PROJECTIVE (fibre incl. roots at infinity is 1+3): %s" % (not pdev))
    log("  deviating sampled instances: %d" % len(dev))
    for r in dev[:40]:
        log("    DEVIATION curve=%s p=%d A=%d B=%d  g=%s  Qe=%s  pattern=%s"
            % (r["curve"], r["p"], r["A"], r["B"], r["g"],
               r["Qe_coeffs_low_to_high"], r["pattern"]))
    for E in exh:
        log("  exhaustive census %s (p=%d, %d g-irreducible base points, "
            "complete=%s):" % (E["curve"], E["p"], E["g_irreducible_count"],
                               E["completed"]))
        n = max(1, E["g_irreducible_count"])
        for k in sorted(E["patterns"], key=lambda z: -E["patterns"][z]):
            log("    literal    %-14s %7d  (%.6f)"
                % (k, E["patterns"][k], E["patterns"][k] / n))
        for k in sorted(E["projective_patterns"],
                        key=lambda z: -E["projective_patterns"][z]):
            log("    projective %-14s %7d  (%.6f)"
                % (k, E["projective_patterns"][k],
                   E["projective_patterns"][k] / n))
        for r in E["deviations_all"][:10]:
            log("    LITERAL-DEVIATION p=%d A=%d B=%d e=%s Qe=%s literal=%s "
                "projective=%s" % (r["p"], r["A"], r["B"], r["e"], r["Qe"],
                                   r["pattern"], r["projective_pattern"]))
    report["stage_2"] = {
        "sampled_distribution": dist,
        "n_sampled": len(instances),
        "M1_all_instances_are_1_3_literal_sampled": bool(not dev),
        "n_deviations_sampled": len(dev),
        "deviations_sampled": dev,
        "sampled_projective_distribution": pdist,
        "M1_all_instances_are_1_3_projective_sampled": bool(not pdev),
        "n_projective_deviations_sampled": len(pdev),
        "exhaustive": [{k: v for k, v in E.items() if k != "deviations_all"}
                       for E in exh],
        "M1_all_instances_are_1_3_literal_exhaustive":
            all(E["n_literal_deviations"] == 0 for E in exh),
        "M1_all_instances_are_1_3_projective_exhaustive":
            all(E["n_projective_deviations"] == 0 for E in exh),
        "prediction": "cycle type exactly (1,3) for every g-irreducible instance",
    }
    report["disposition"] = ("completed_valid")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    report["wall_seconds"] = round(time.time() - T0, 1)
    report["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 1)
    report["peak_rss_bytes"] = int(ru.ru_maxrss)
    report["python_version"] = sys.version.split()[0]
    log("\ntotal wall seconds: %.1f  cpu %.1f  peak RSS %d bytes"
        % (report["wall_seconds"], report["cpu_seconds"],
           report["peak_rss_bytes"]))
    json.dump(report, open(sys.argv[1], "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
