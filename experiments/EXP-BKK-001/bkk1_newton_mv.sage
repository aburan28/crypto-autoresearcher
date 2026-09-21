# EXP-BKK-001 executor: Newton polytopes, mixed volume, and sparse-vs-dense solve cost
# of the target-sectioned Semaev family (candidate B2, TASK-20260717-B2).
#
# Protocol: experiments/EXP-BKK-001/specification.yaml (frozen).
#   p in {101,431,1009}; m in {3,4,5}; seeds 20260717..20260719.
#   Stage 0: exact supports, Newton polytopes, MV vs multigraded Bezout n!*D^n.
#   Solve: dense composed-resultant route vs support-aware route, counted F_p ops.
#   Controls: POS-1..POS-5, NEG-1..NEG-2 (see specification.yaml).
#
# Usage:
#   sage bkk1_newton_mv.sage --ms 3,4 --ps 101,431,1009 --seeds 20260717,20260718,20260719 \
#        --runid RUN-BKK-001-a --out runs/RUN-BKK-001-a/raw.json
#
# All arithmetic in the measured solver paths goes through counted helpers (M/A/S/INV).
# Convention (predeclared): 1 F_p op = 1 mod-mul or mod-add/sub; 1 inversion = 10 muls
# in totals; data movement/indexing/curve-arithmetic/RNG uncounted.

import sys, os, json, time, argparse, random as pyrandom
import itertools
from itertools import product
from sage.all import GF, QQ, Integer, EllipticCurve, Polyhedron, set_random_seed, factorial

# ---------------- counted F_p arithmetic ----------------
class Counter:
    def __init__(self):
        self.mul = 0; self.add = 0; self.inv = 0
    def total(self, inv_weight=10):
        return self.mul + self.add + inv_weight * self.inv
    def snap(self):
        return {"mul": self.mul, "add": self.add, "inv": self.inv,
                "total_w10": self.total()}

CTR = None  # active Counter or None

def M(a, b, p):
    if CTR is not None: CTR.mul += 1
    return (a * b) % p

def A(a, b, p):
    if CTR is not None: CTR.add += 1
    return (a + b) % p

def S(a, b, p):
    if CTR is not None: CTR.add += 1
    return (a - b) % p

def INV(a, p):
    if CTR is not None: CTR.inv += 1
    return pow(a % p, p - 2, p)

# ---------------- dense n-d polynomial machinery (nested lists, box [0,D]^n) ----------------

def dmake(n, D):
    if n == 1:
        return [0] * (D + 1)
    return [dmake(n - 1, D) for _ in range(D + 1)]

def dset(poly, exp, val):
    node = poly
    for e in exp[:-1]:
        node = node[e]
    node[exp[-1]] = val

def fold_last(poly, n, D, x, p):
    """Fold the innermost (last) variable at value x. Returns poly in n-1 vars."""
    if n == 1:
        acc = 0
        for e in range(D, -1, -1):
            acc = A(M(acc, x, p), poly[e], p)
        return acc
    return [fold_last(sub, n - 1, D, x, p) for sub in poly]

def deval_all(poly, n, D, xs, p):
    """Dense nested-Horner evaluation of all n variables. Counted."""
    cur = poly
    for k in range(n - 1, -1, -1):
        cur = fold_last(cur, k + 1, D, xs[k], p)
    return cur

def extract_at_last(poly, n, eX):
    """Coefficient (as (n-1)-var poly) of last-var^eX. Uncounted data movement."""
    if n == 1:
        return poly[eX]
    return [extract_at_last(sub, n - 1, eX) for sub in poly]

def partial_eval_keep_last(poly, n, D, vals, p):
    """Evaluate first n-1 vars at vals; return univariate (list len D+1) in last var."""
    out = []
    for eX in range(D + 1):
        sub = extract_at_last(poly, n, eX)
        out.append(deval_all(sub, n - 1, D, vals, p))
    return out

def extract_support(poly, n, D, p):
    supp = []
    for exp in product(range(D + 1), repeat=n):
        node = poly
        for e in exp:
            node = node[e]
        if node % p != 0:
            supp.append(tuple(int(e) for e in exp))
    return sorted(supp)

def poly_eq(P1, P2, n, D, p):
    for exp in product(range(D + 1), repeat=n):
        n1, n2 = P1, P2
        for e in exp:
            n1 = n1[e]; n2 = n2[e]
        if (n1 - n2) % p != 0:
            return False
    return True

# ---------------- formal-degree Sylvester resultant (counted) ----------------

def uresultant(f, df, g, dg, p):
    """Resultant of f (list len df+1, coeff of X^i at i) and g, FORMAL degrees df,dg
    (leading zeros allowed and significant). Counted Gaussian elimination."""
    s = df + dg
    Mat = [[0] * s for _ in range(s)]
    for i in range(dg):
        for j in range(df + 1):
            Mat[i][i + j] = f[df - j] % p
    for i in range(df):
        for j in range(dg + 1):
            Mat[dg + i][i + j] = g[dg - j] % p
    det = 1; sign = 1
    for col in range(s):
        piv = -1
        for r in range(col, s):
            if Mat[r][col] % p != 0:
                piv = r; break
        if piv == -1:
            return 0
        if piv != col:
            Mat[col], Mat[piv] = Mat[piv], Mat[col]
            sign = -sign
        pv = Mat[col][col] % p
        det = M(det, pv, p)
        invpv = INV(pv, p)
        for r in range(col + 1, s):
            if Mat[r][col] % p == 0:
                continue
            factor = M(Mat[r][col], invpv, p)
            for c in range(col, s):
                Mat[r][c] = S(Mat[r][c], M(factor, Mat[col][c], p), p)
    return det % p if sign == 1 else (-det) % p

# ---------------- Newton finite-difference interpolation (counted) ----------------

def make_invfacts(D, p):
    f = 1; invf = [1] * (D + 1)
    for k in range(1, D + 1):
        f = M(f, k, p)
        invf[k] = INV(f, p)          # exact: (k!)^-1 ; k<=8 < p so invertible
    return invf

def interp_fd(vals, D, p, invf):
    """vals[j] = f(j) for j = 0..D; return monomial coeffs [c0..cD]. Counted."""
    fd = [v % p for v in vals]
    newt = [fd[0]]
    for k in range(1, D + 1):
        fd = [S(fd[i + 1], fd[i], p) for i in range(len(fd) - 1)]
        newt.append(fd[0])
    coeff = [0] * (D + 1)
    basis = [1] + [0] * D
    for k in range(D + 1):
        c = M(newt[k], invf[k], p)
        for j in range(k + 1):
            if basis[j]:
                coeff[j] = A(coeff[j], M(c, basis[j], p), p)
        if k < D:  # basis *= (x - k), only needed while another term follows
            nb = [0] * (D + 1)
            for j in range(k + 1):
                if basis[j]:
                    nb[j + 1] = A(nb[j + 1], basis[j], p)
                    nb[j] = S(nb[j], M(k, basis[j], p), p)
            basis = nb
    return coeff

def interp_last_everywhere(grid, n, D, p, invf):
    if n == 1:
        return interp_fd(grid, D, p, invf)
    return [interp_last_everywhere(sub, n - 1, D, p, invf) for sub in grid]

def take_coeff(node, depth, e):
    if depth == 0:
        return node[e]
    return [take_coeff(sub, depth - 1, e) for sub in node]

def reassemble(result_list, depth):
    if depth == 0:
        return list(result_list)
    return [reassemble([r[i] for r in result_list], depth - 1)
            for i in range(len(result_list[0]))]

def interp_nd(grid, n, D, p, invf):
    """grid[e0]...[e_{n-1}] = f(e0,...,e_{n-1}) on 0..D per var; return dense coeffs."""
    if n == 1:
        return interp_fd(grid, D, p, invf)
    pref = interp_last_everywhere(grid, n, D, p, invf)
    pieces = [interp_nd(take_coeff(pref, n - 1, e), n - 1, D, p, invf)
              for e in range(D + 1)]
    return reassemble(pieces, n - 1)

# ---------------- sparse support-constrained interpolation (counted) ----------------

def monom_eval(exp, tup, p):
    term = 1
    for k in range(len(exp)):
        x = tup[k] % p
        for _ in range(exp[k]):
            term = M(term, x, p)
    return term

def sparse_interp(support, tuples, values, p):
    """Solve M c = v with M[i][j] = monomial_j(tuple_i) over F_p. Counted.
    Returns coeff list aligned with support, or None if singular."""
    K = len(support)
    Mat = []
    for t in tuples:
        Mat.append([monom_eval(e, t, p) for e in support])
    v = [x % p for x in values]
    for col in range(K):
        piv = -1
        for r in range(col, K):
            if Mat[r][col] % p != 0:
                piv = r; break
        if piv == -1:
            return None
        if piv != col:
            Mat[col], Mat[piv] = Mat[piv], Mat[col]
            v[col], v[piv] = v[piv], v[col]
        pv = Mat[col][col] % p
        invpv = INV(pv, p)
        for r in range(col + 1, K):
            if Mat[r][col] % p == 0:
                continue
            factor = M(Mat[r][col], invpv, p)
            for c in range(col, K):
                Mat[r][c] = S(Mat[r][c], M(factor, Mat[col][c], p), p)
            v[r] = S(v[r], M(factor, v[col], p), p)
    c = [0] * K
    for r in range(K - 1, -1, -1):
        acc = v[r]
        for cc in range(r + 1, K):
            acc = S(acc, M(Mat[r][cc], c[cc], p), p)
        c[r] = M(acc, INV(Mat[r][r], p), p)
    return c

# ---------------- Semaev closed forms (ledger formula, EXP-FB-001/fb_structure.sage) ----------------

def S3_closed(x1, x2, x3, a, b, p):
    """Closed-form S_3 exactly as the ledger harvester. Counted."""
    t1 = M(S(x1, x2, p), S(x1, x2, p), p)          # (x1-x2)^2
    t1 = M(t1, M(x3, x3, p), p)                    # * x3^2
    u = M(A(x1, x2, p), A(M(x1, x2, p), a, p), p)  # (x1+x2)(x1x2+a)
    u = A(u, M(2, b, p), p)                        # + 2b
    t2 = M(M(2, u, p), x3, p)                      # 2*(...)*x3
    v = S(M(x1, x2, p), a, p)                      # (x1x2-a)
    t3 = M(v, v, p)
    t4 = M(M(4, b, p), A(x1, x2, p), p)            # 4b(x1+x2)
    return A(S(t1, t2, p), S(t3, t4, p), p)        # t1 - t2 + t3 - t4

def build_T3_dense(a, b, p):
    """Unsectioned T_3(x1,x2,X) dense array (D=2, 3 vars) from closed form. Counted."""
    D = 2
    T = dmake(3, D)
    xR2 = M(0, 0, p)  # placeholder, unused
    # coefficients as polynomials in (a,b) evaluated once, counted
    c_202 = 1 % p
    c_112 = (-2) % p
    c_022 = 1 % p
    c_211 = (-2) % p
    c_121 = (-2) % p
    c_101 = M(-2, a, p)
    c_011 = M(-2, a, p)
    c_001 = M(-4, b, p)
    c_220 = 1 % p
    c_110 = M(-2, a, p)
    c_000 = M(a, a, p)
    c_100 = M(-4, b, p)
    c_010 = M(-4, b, p)
    for exp, c in [((2,0,2),c_202), ((1,1,2),c_112), ((0,2,2),c_022),
                   ((2,1,1),c_211), ((1,2,1),c_121), ((1,0,1),c_101),
                   ((0,1,1),c_011), ((0,0,1),c_001), ((2,2,0),c_220),
                   ((1,1,0),c_110), ((0,0,0),c_000), ((1,0,0),c_100),
                   ((0,1,0),c_010)]:
        dset(T, exp, c % p)
    return T

def build_S3_sectioned(a, b, xR, p):
    """S_3(x1,x2;xR) dense 2-var array (D=2) from closed form. Counted."""
    D = 2
    T = dmake(2, D)
    xR2 = M(xR, xR, p)
    coeffs = {
        (2, 2): 1 % p,
        (2, 1): M(-2, xR, p),
        (1, 2): M(-2, xR, p),
        (2, 0): xR2,
        (0, 2): xR2,
        (1, 1): S(M(-2, xR2, p), M(2, a, p), p),
        (1, 0): S(M(-2, M(a, xR, p), p), M(4, b, p), p),
        (0, 1): S(M(-2, M(a, xR, p), p), M(4, b, p), p),
        (0, 0): S(M(a, a, p), M(4, M(b, xR, p), p), p),
    }
    for exp, c in coeffs.items():
        dset(T, exp, c % p)
    return T

# ---------------- recursive construction by evaluation-interpolation ----------------

def build_S4_sectioned(T3, a, b, xR, p, invf4):
    """S_4(x1,x2,x3;xR) = Res_X(T_3(x1,x2,X), T_3(x3,xR,X)); grid 5^3. Counted."""
    D = 4
    grid = [[[0] * (D + 1) for _ in range(D + 1)] for _ in range(D + 1)]
    for v1 in range(D + 1):
        for v2 in range(D + 1):
            f = partial_eval_keep_last(T3, 3, 2, [v1, v2], p)
            for v3 in range(D + 1):
                g = partial_eval_keep_last(T3, 3, 2, [v3, xR], p)
                grid[v1][v2][v3] = uresultant(f, 2, g, 2, p)
    return interp_nd(grid, 3, D, p, invf4)

def build_T4_unsectioned(T3, p, invf4):
    """T_4(x1..x4) = Res_X(T_3(x1,x2,X), T_3(x3,x4,X)); grid 5^4. Counted."""
    D = 4
    grid = [[[[0] * (D + 1) for _ in range(D + 1)] for _ in range(D + 1)]
            for _ in range(D + 1)]
    for v1 in range(D + 1):
        for v2 in range(D + 1):
            f = partial_eval_keep_last(T3, 3, 2, [v1, v2], p)
            for v3 in range(D + 1):
                for v4 in range(D + 1):
                    g = partial_eval_keep_last(T3, 3, 2, [v3, v4], p)
                    grid[v1][v2][v3][v4] = uresultant(f, 2, g, 2, p)
    return interp_nd(grid, 4, D, p, invf4)

def build_S5_sectioned(T4, T3, xR, p, invf8):
    """S_5(x1..x4;xR) = Res_X(T_4(x1,x2,x3,X), T_3(x4,xR,X)); grid 9^4. Counted."""
    D = 8
    grid = [[[[0] * (D + 1) for _ in range(D + 1)] for _ in range(D + 1)]
            for _ in range(D + 1)]
    for v1 in range(D + 1):
        for v2 in range(D + 1):
            for v3 in range(D + 1):
                f = partial_eval_keep_last(T4, 4, 4, [v1, v2, v3], p)
                for v4 in range(D + 1):
                    g = partial_eval_keep_last(T3, 3, 2, [v4, xR], p)
                    grid[v1][v2][v3][v4] = uresultant(f, 4, g, 2, p)
    return interp_nd(grid, 4, D, p, invf8)

# ---------------- Newton polytope / mixed volume (exact) ----------------

def int_tuple(v):
    return tuple(Integer(c) for c in v)

def det_int(rows):
    """Bareiss fraction-free determinant of integer matrix (list of rows)."""
    n = len(rows)
    Mat = [[Integer(x) for x in row] for row in rows]
    sign = 1
    prev = Integer(1)
    for k in range(n - 1):
        if Mat[k][k] == 0:
            sw = -1
            for r in range(k + 1, n):
                if Mat[r][k] != 0:
                    sw = r; break
            if sw == -1:
                return Integer(0)
            Mat[k], Mat[sw] = Mat[sw], Mat[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                Mat[i][j] = (Mat[i][j] * Mat[k][k] - Mat[i][k] * Mat[k][j]) // prev
        prev = Mat[k][k]
    return sign * Mat[n - 1][n - 1]

def triangulate_pulling(P):
    """Deterministic pulling triangulation from the lex-min vertex. Exact."""
    d = P.dim()
    verts = [int_tuple(v) for v in P.vertices()]
    if len(verts) == d + 1:
        return [verts]
    v0 = min(verts)
    out = []
    for F in P.faces(d - 1):
        FP = F.as_polyhedron()
        fverts = set(int_tuple(v) for v in FP.vertices())
        if v0 in fverts:
            continue
        for s in triangulate_pulling(FP):
            out.append([v0] + s)
    return out

def pulling_volume(P, n):
    simps = triangulate_pulling(P)
    total = Integer(0)
    for s in simps:
        rows = [[Integer(s[j + 1][i]) - Integer(s[0][i]) for i in range(n)]
                for j in range(n)]
        total += abs(det_int(rows))
    return QQ(total) / QQ(factorial(n)), len(simps)

def polytope_mv(support, n, D, p):
    """Return dict with exact volume, MV=n!*Vol, Bezout=n!*D^n, rho. Exact."""
    bezout = int(factorial(n)) * (D ** n)
    box_size = (D + 1) ** n
    res = {"n": n, "D": D, "bezout_mh": bezout, "box_size": box_size}
    if len(support) == box_size:
        vol = QQ(D ** n)
        mv = int(factorial(n)) * (D ** n)
        res.update({"path": "box_shortcircuit", "n_vertices": 2 ** n,
                    "volume": str(vol), "mv": mv,
                    "rho": str(QQ(mv) / QQ(bezout)), "rho_float": float(QQ(mv) / QQ(bezout)),
                    "logmv_logbez": None if mv <= 1 else float(QQ(mv).log() / QQ(bezout).log()),
                    "volume_methods": {"identity": "Vol(box)=D^n (support == full box)"},
                    "volumes_agree": True})
        return res
    P = Polyhedron(vertices=[list(e) for e in support], base_ring=QQ)
    if P.dim() < n:
        res.update({"path": "degenerate_dim", "volume": "0", "mv": 0,
                    "rho": "0", "rho_float": 0.0, "logmv_logbez": None,
                    "n_vertices": P.n_vertices(),
                    "volume_methods": {"dimension": "dim < n"},
                    "volumes_agree": True})
        return res
    vol_pull, n_simps = pulling_volume(P, n)
    methods = {"pulling_triangulation": str(vol_pull),
               "n_simplices": n_simps}
    agree = True
    try:
        vol_sage = QQ(P.volume())
        methods["sage_polyhedron_volume"] = str(vol_sage)
        if vol_sage != vol_pull:
            agree = False
    except Exception as e:
        methods["sage_polyhedron_volume"] = "unavailable: %s" % type(e).__name__
        try:
            import numpy as np
            from scipy.spatial import ConvexHull
            V = np.array([[float(c) for c in e] for e in support])
            vol_sp = float(ConvexHull(V).volume)
            methods["scipy_convexhull_float"] = vol_sp
            if abs(vol_sp - float(vol_pull)) > 1e-6 * max(1.0, abs(vol_sp)):
                agree = False
        except Exception as e2:
            methods["scipy_convexhull_float"] = "unavailable: %s" % type(e2).__name__
            agree = None  # no second method available
    mv = int(factorial(n)) * vol_pull
    rho = QQ(mv) / QQ(bezout)
    res.update({"path": "hull", "n_vertices": P.n_vertices(),
                "volume": str(vol_pull), "mv": int(mv),
                "rho": str(rho), "rho_float": float(rho),
                "logmv_logbez": float(QQ(mv).log() / QQ(bezout).log()),
                "volume_methods": methods, "volumes_agree": agree})
    return res

# ---------------- machinery self-tests (POS-5 + resultant + interpolation) ----------------

def selftests(p):
    out = {}
    # (a) resultant: Res(x^2-3x+2, x^2-7x+12) = +-12
    global CTR
    CTR = Counter()
    val = uresultant([2, -3, 1], 2, [12, -7, 1], 2, p)
    CTR = None
    out["uresultant_known_value"] = (val % p in (12 % p, (-12) % p))
    # (b) pulling-triangulation volumes on known shapes
    shapes = {
        "triangle": ([[0, 0], [2, 0], [0, 2]], 2, QQ(2)),
        "cut_square": ([[0, 0], [2, 0], [0, 2], [2, 1], [1, 2]], 2, QQ(7) / 2),
        "simplex3": ([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 3, QQ(1) / 6),
        "box3": ([[i, j, k] for i in (0, 2) for j in (0, 2) for k in (0, 2)], 3, QQ(8)),
    }
    st = {}
    for name, (verts, n, expect) in shapes.items():
        P = Polyhedron(vertices=verts, base_ring=QQ)
        vol, ns = pulling_volume(P, n)
        st[name] = {"computed": str(vol), "expected": str(expect), "ok": bool(vol == expect)}
    out["pulling_volume"] = st
    out["pulling_volume_all_ok"] = all(v["ok"] for v in st.values())
    # (c) interpolation machinery recovers T_3 closed form on a test curve
    a0, b0 = 7 % p, 11 % p
    T3 = build_T3_dense(a0, b0, p)
    invf2 = make_invfacts(2, p)
    grid = [[[0] * 3 for _ in range(3)] for _ in range(3)]
    CTR = Counter()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                grid[i][j][k] = S3_closed(i, j, k, a0, b0, p)
    T3r = interp_nd(grid, 3, 2, p, invf2)
    CTR = None
    out["interp_recovers_T3"] = poly_eq(T3, T3r, 3, 2, p)
    out["all_ok"] = (out["uresultant_known_value"] and out["pulling_volume_all_ok"]
                     and out["interp_recovers_T3"])
    return out

# ---------------- FB solve + harvest ----------------

def solve_fb_dense(Sarr, n, D, FBx, p):
    global CTR
    CTR = Counter()
    sols = []
    for tup in product(FBx, repeat=n):
        if deval_all(Sarr, n, D, list(tup), p) == 0:
            sols.append(tuple(int(x) for x in tup))
    ops = CTR.snap()
    CTR = None
    return sorted(sols), ops

def solve_fb_sparse(support, coeff_of, n, FBx, p):
    """Support-restricted evaluation: per tuple, per-var power towers (counted)
    then one product per monomial. coeff_of: dict exp->coeff."""
    global CTR
    CTR = Counter()
    maxe = [max(e[k] for e in support) for k in range(n)]
    sols = []
    for tup in product(FBx, repeat=n):
        towers = []
        for k in range(n):
            tw = [1] * (maxe[k] + 1)
            for e in range(1, maxe[k] + 1):
                tw[e] = M(tw[e - 1], tup[k], p)
            towers.append(tw)
        acc = 0
        for e in support:
            term = coeff_of[e]
            for k in range(n):
                if e[k]:
                    term = M(term, towers[k][e[k]], p)
            acc = A(acc, term, p)
        if acc % p == 0:
            sols.append(tuple(int(x) for x in tup))
    ops = CTR.snap()
    CTR = None
    return sorted(sols), ops

def harvest(E, FB, R, n):
    xs = [int(P.xy()[0]) for P in FB]
    sols = []
    d = len(FB)
    for idxs in product(range(d), repeat=n):
        hit = False
        for signs in product((1, -1), repeat=n):
            acc = E(0)
            for i, s in zip(idxs, signs):
                acc = acc + (FB[i] if s == 1 else -FB[i])
            if acc == R or acc == -R:
                hit = True
                break
        if hit:
            sols.append(tuple(xs[i] for i in idxs))
    return sorted(sols)

# ---------------- curve / FB / targets ----------------

def seeded_curve(F, p):
    while True:
        a = F.random_element()
        b = F.random_element()
        if a == 0 or b == 0:
            continue
        if 4 * a ** 3 + 27 * b ** 2 != 0:
            return EllipticCurve(F, [a, b])

def build_fb(E, d, p):
    F = E.base_field()
    pts = []; seen = set()
    tries = 0
    while len(pts) < d and tries < 40 * d:
        tries += 1
        xv = int(F.random_element())
        if xv in seen:
            continue
        try:
            P = E.lift_x(GF(p)(xv))
            if P.is_zero():
                continue
            pts.append(P); seen.add(xv)
        except Exception:
            pass
    return pts

# ---------------- per-config driver ----------------

FB_SIZES = {3: 12, 4: 10, 5: 8}

def run_config(p, m, seed, log):
    global CTR
    n = m - 1
    D = 2 ** (m - 2)
    d = FB_SIZES[m]
    t0 = time.time()
    set_random_seed(seed)
    F = GF(p)
    E = seeded_curve(F, p)
    N = int(E.order())
    a = E.a4(); b = E.a6()
    ai, bi = int(a), int(b)
    # targets
    R_main = E.random_point()
    while R_main.is_zero() or int(R_main.xy()[0]) == 0:
        R_main = E.random_point()
    FB = build_fb(E, d, p)
    if len(FB) < d:
        return {"p": p, "m": m, "seed": seed, "skipped": True,
                "reason": "factor base too small (%d < %d)" % (len(FB), d)}
    R_wit = None; wit_window = None
    for start in range(0, d - n + 1):
        acc = E(0)
        for i in range(start, start + n):
            acc = acc + FB[i]
        if not acc.is_zero():
            R_wit = acc; wit_window = [start, start + n - 1]; break
    wit_fallback = False
    if R_wit is None:
        R_wit = R_main; wit_fallback = True
    FBx = [int(P.xy()[0]) for P in FB]

    cfg = {"p": p, "m": m, "seed": seed, "n": n, "D": D,
           "curve": {"a": ai, "b": bi, "order": N},
           "fb_size": d, "fb_x": FBx,
           "targets": {"main_xR": int(R_main.xy()[0]),
                        "wit_xR": int(R_wit.xy()[0]),
                        "wit_window": wit_window, "wit_fallback": wit_fallback},
           "skipped": False}

    # base objects
    CTR = Counter()
    T3 = build_T3_dense(ai, bi, p)
    ops_T3 = CTR.snap(); CTR = None
    cfg["T3_construction_ops"] = ops_T3
    T4 = None; ops_T4 = None
    if m >= 5:
        CTR = Counter()
        invf4 = make_invfacts(4, p)
        T4 = build_T4_unsectioned(T3, p, invf4)
        ops_T4 = CTR.snap(); CTR = None
        cfg["T4_unsectioned_construction_ops"] = ops_T4
        cfg["T4_support_size"] = len(extract_support(T4, 4, 4, p))

    stage0_done = False
    cfg["per_target"] = {}
    for tname, R in [("main", R_main), ("wit", R_wit)]:
        xR = int(R.xy()[0])
        tcons0 = time.time()
        CTR = Counter()
        if m == 3:
            Sarr = build_S3_sectioned(ai, bi, xR, p)
        elif m == 4:
            invf4b = make_invfacts(4, p)
            Sarr = build_S4_sectioned(T3, ai, bi, xR, p, invf4b)
        else:
            invf8 = make_invfacts(8, p)
            Sarr = build_S5_sectioned(T4, T3, xR, p, invf8)
        ops_cons = CTR.snap(); CTR = None
        tcons = time.time() - tcons0
        support = extract_support(Sarr, n, D, p)
        coeff_of = {e: int(Sarr[e[0]][e[1]] if n == 2 else
                            Sarr[e[0]][e[1]][e[2]] if n == 3 else
                            Sarr[e[0]][e[1]][e[2]][e[3]]) for e in support}
        rec = {"xR": xR, "dense_construction_ops": ops_cons,
               "construction_seconds": tcons,
               "support_size": len(support), "box_size": (D + 1) ** n,
               "fill": len(support) / float((D + 1) ** n),
               "per_var_maxdeg": [max(e[k] for e in support) for k in range(n)],
               "total_degree_max": max(sum(e) for e in support),
               "support": [list(e) for e in support]}
        # symmetry check (sectioned S_m must be symmetric in x_1..x_{m-1})
        sset = set(support)
        sym = True
        for e in support:
            for perm in itertools.permutations(range(n)):
                if tuple(e[perm[k]] for k in range(n)) not in sset:
                    sym = False; break
            if not sym:
                break
        rec["support_symmetric"] = sym

        # stage 0: exact Newton polytope + MV for this target's sectioned polynomial
        pmv = polytope_mv(support, n, D, p)
        rec["polytope"] = pmv
        if tname == "main":
            stage0_done = True

        # sparse route (support-aware construction)
        K = len(support)
        if K <= 200:
            rng = pyrandom.Random(int(seed * 100003 + m * 101 + (0 if tname == "main" else 1)))
            attempts = 0; coeffs_sp = None
            while attempts < 5 and coeffs_sp is None:
                attempts += 1
                tuples = [[rng.randrange(0, p) for _ in range(n)] for _ in range(K)]
                CTR = Counter()
                vals = []
                for t in tuples:
                    if m == 3:
                        vals.append(S3_closed(t[0], t[1], xR, ai, bi, p))
                    elif m == 4:
                        f = partial_eval_keep_last(T3, 3, 2, [t[0], t[1]], p)
                        g = partial_eval_keep_last(T3, 3, 2, [t[2], xR], p)
                        vals.append(uresultant(f, 2, g, 2, p))
                    else:
                        f = partial_eval_keep_last(T4, 4, 4, [t[0], t[1], t[2]], p)
                        g = partial_eval_keep_last(T3, 3, 2, [t[3], xR], p)
                        vals.append(uresultant(f, 4, g, 2, p))
                ops_sparse_oracle = CTR.snap()
                coeffs_sp = sparse_interp(support, tuples, vals, p)
                ops_sparse = CTR.snap(); CTR = None
            if coeffs_sp is None:
                rec["sparse_mode"] = "failed_singular_5_attempts"
                CTR = None
            else:
                sparse_dict = {e: coeffs_sp[i] % p for i, e in enumerate(support)}
                pos2 = all(sparse_dict[e] == coeff_of[e] for e in support)
                rec["sparse_mode"] = "measured"
                rec["sparse_construction_ops"] = ops_sparse
                rec["sparse_oracle_ops_included"] = ops_sparse_oracle
                rec["sparse_attempts"] = attempts
                rec["pos2_poly_identical"] = bool(pos2)
        else:
            est = (K ** 3) // 3
            rec["sparse_mode"] = "fallback_analytic"
            rec["sparse_ops_analytic_estimate_K3_over_3"] = est
            rec["sparse_fallback_note"] = ("generic support-constrained interpolation "
                                           "infeasible by budget at |supp|=%d; analytic "
                                           "estimate K^3/3 labeled estimate, not measured" % K)

        # FB solve, both routes
        tsol0 = time.time()
        sols_dense, ops_sd = solve_fb_dense(Sarr, n, D, FBx, p)
        sols_sparse, ops_ss = solve_fb_sparse(support, coeff_of, n, FBx, p)
        tsol = time.time() - tsol0
        tharv0 = time.time()
        sols_harv = harvest(E, FB, R, n)
        tharv = time.time() - tharv0
        rec["solve"] = {"n_tuples": d ** n, "dense_eval_ops": ops_sd,
                        "sparse_eval_ops": ops_ss,
                        "n_roots_dense": len(sols_dense),
                        "n_roots_sparse": len(sols_sparse),
                        "n_roots_harvest": len(sols_harv),
                        "roots_dense": [list(t) for t in sols_dense],
                        "roots_harvest": [list(t) for t in sols_harv],
                        "solve_seconds": tsol, "harvest_seconds": tharv}
        rec["controls"] = {
            "pos1_dense_eq_harvest": bool(sols_dense == sols_harv),
            "pos1_sparse_eq_harvest": bool(sols_sparse == sols_harv),
            "pos4_nonempty": bool(len(sols_harv) > 0),
        }
        # negative control: random same-support system
        rng2 = pyrandom.Random(int(seed * 9176 + m * 131 + (3 if tname == "main" else 7)))
        rand_coeff = {e: rng2.randrange(1, p) for e in support}
        pmv_rand = polytope_mv(support, n, D, p)  # same support => same hull; executed to log it
        rec["controls"]["neg1_mv_equal"] = bool(pmv_rand["mv"] == rec["polytope"]["mv"])
        rec["controls"]["neg1_mv_value"] = pmv_rand["mv"]
        if m <= 4:
            sols_rand, ops_rand = solve_fb_sparse(support, rand_coeff, n, FBx, p)
            rec["controls"]["neg2_rand_solve_ops"] = ops_rand
            rec["controls"]["neg2_ops_equal"] = bool(ops_rand["total_w10"] == ops_ss["total_w10"])
            rec["controls"]["neg2_sets_differ"] = bool(sorted(sols_rand) != sols_sparse)
            rec["controls"]["neg2_rand_n_roots"] = len(sols_rand)
        else:
            rec["controls"]["neg2_note"] = "m=5 random-fill solve omitted (predeclared); op counts structurally identical"
        cfg["per_target"][tname] = rec
        log("  p=%d m=%d seed=%d target=%s: |supp|=%d/%d fill=%.3f cons_ops=%d roots=%d" %
            (p, m, seed, tname, len(support), (D + 1) ** n, rec["fill"],
             ops_cons["total_w10"], len(sols_dense)))

    # cross-target support stability (stage-0 object should be target-generic)
    sm = cfg["per_target"]["main"]["support"]
    sw = cfg["per_target"]["wit"]["support"]
    cfg["support_wit_equals_main"] = bool(sm == sw)
    cfg["wall_seconds"] = time.time() - t0
    return cfg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ms", required=True)
    ap.add_argument("--ps", required=True)
    ap.add_argument("--seeds", default="20260717,20260718,20260719")
    ap.add_argument("--runid", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ms = [int(x) for x in args.ms.split(",")]
    ps = [int(x) for x in args.ps.split(",")]
    seeds = [int(x) for x in args.seeds.split(",")]

    def log(msg):
        print(msg, file=sys.stderr, flush=True)

    started = time.time()
    out = {"experiment_id": "EXP-BKK-001", "run_id": args.runid,
           "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
           "parameters": {"ms": ms, "ps": ps, "seeds": seeds,
                          "fb_sizes": {str(k): int(v) for k, v in FB_SIZES.items()},
                          "inv_weight": 10},
           "sage_version": str(__import__("sage.version", fromlist=["version"]).version) if False else None,
           "python_version": sys.version,
           "platform": sys.platform}
    try:
        from sage.version import version as sagever
        out["sage_version"] = sagever
    except Exception:
        out["sage_version"] = "unknown"

    log("selftests...")
    out["selftests"] = selftests(101)
    log("selftests: %s" % ("PASS" if out["selftests"]["all_ok"] else "FAIL"))
    if not out["selftests"]["all_ok"]:
        out["fatal"] = "selftests failed"
        with open(args.out, "w") as fh:
            json.dump(out, fh, default=str)
        sys.exit(2)

    out["configs"] = []
    for p in ps:
        for seed in seeds:
            for m in ms:
                log("config p=%d m=%d seed=%d" % (p, m, seed))
                cfg = run_config(p, m, seed, log)
                out["configs"].append(cfg)

    finished = time.time()
    out["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(finished))
    out["wall_seconds"] = finished - started
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, default=str)
    log("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]))

main()
