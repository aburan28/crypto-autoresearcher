# bkkmv2_cert.sage — EXP-BKKMV-002 (candidate D2 continuation, ledger family BKKMV, task BKKM6)
# m=6 mixed-volume law check: exact sectioned supports and MV of the target-sectioned
# Semaev system at m=6 via the FIBERWISE engine (recursive resultant structure,
# research_directions_20260717.md line 670 mitigation) — no brute enumeration of S_6.
#
# Engine (frozen in specification.yaml): f_j(x_1..x_5) = Res_X(A, B_j) with
#   A(X) = S_5(x_1..x_4, X) (deg_X = 8),  B_j(X) = S_3(x_5, t_j, X) (deg_X = 2).
# Values of f_j on a 17^5 tensor grid via the exact formal-Sylvester identities
#   b2 != 0:      Res = b2^m * det(A(C_B))            (C_B companion matrix)
#   b2 = 0:       Res = a_lead * (-1)^m * b1^m * A(-b0/b1)
#   b2 = b1 = 0:  Res = a_lead^2 * b0^m               (m = deg_X A)
# (verified vs the formal Sylvester determinant in dev/probe_kernel.sage: K1/K2a/K2b pass),
# then exact tensor-grid interpolation mod p (K4 pass) -> exact coefficients -> support.
# Hull certificate: all 2^n corners present => conv(support) = box. MV by exact
# inclusion-exclusion over subset Minkowski sums of certified hull boxes, cross-checked
# by the box-permanent formula.
#
# Stages:
#   sage bkkmv2_cert.sage --stage validate --out <raw.json>
#       Engine cross-validation P4a (m=3,4,5 fiberwise vs symbolic, exact support equality,
#       3 seeds p=1000003 + lossy m=5 p=101), P1, P2, P4-two-prime (m=3,4,5), P4-QQ (m=3,4),
#       N1 (m=3,4,5), P5a value check (m=5 full grid).
#   sage bkkmv2_cert.sage --stage measure6 --out <raw.json> --seeds 20260717,20260718,20260719 \
#        --primes 1000003 --supports-dir <dir> [--det-recheck <ref_raw.json>]
#       m=6 measurement: 5 sections per instance, bitmaps + corners + MV + ratios.
#       --det-recheck: also recompute (seed 20260717, p=1000003, slot 1) and compare its
#       support sha256 against the reference run's raw.json (P4c).
#   sage bkkmv2_cert.sage --stage counts --out <raw.json>
#       BKK bound cross-checks at m<=5 (m=4 p=101 x3 seeds; m=5 p=101 seed 20260717),
#       N2 violation witness (m=3 p=431), N3 engine selfcheck (m=3 p=101).
#
# Functions gen_curve / is_qr / semaev_polys / supp_of / section_poly / pick_sections /
# random_poly_on_support / dense_support / count_torus / monom_list / count_torus_naive /
# mv_of_polys / hull_polyhedron / volume_from_support are COPIED UNCHANGED from
# experiments/EXP-BKKMV-001/bkkmv1_cert.sage (provenance; do not modify the original).

import sys, os, json, time, random, subprocess, hashlib
from datetime import datetime, timezone
from itertools import combinations, permutations, product as iproduct
import numpy as np

SEEDS_DEFAULT = [20260717, 20260718, 20260719]
P_CERT = [1000003, 1000033]
SOFT_BUDGET = float(540)
T0 = time.time()
NOTES = []

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def elapsed():
    return time.time() - T0

def time_left():
    return elapsed() < SOFT_BUDGET

def jsanitize(o):
    from sage.rings.integer import Integer
    from sage.rings.rational import Rational
    if isinstance(o, Integer):
        return int(o)
    if isinstance(o, Rational):
        return str(o) if o.denominator() != 1 else int(o)
    if isinstance(o, dict):
        return {str(k): jsanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsanitize(v) for v in o]
    if isinstance(o, (int, float, str, bool)) or o is None:
        return o
    try:
        return float(o)
    except Exception:
        return str(o)

def git_info():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        return commit, (len(dirty) > 0)
    except Exception as e:
        NOTES.append("git_info_failed: %s" % e)
        return None, None

# ---------------- curve / RNG streams (copied from bkkmv1) ----------------

def gen_curve(seed, p):
    rng = random.Random(int(seed * 10000007 + p))
    while True:
        A = rng.randrange(p)
        B = rng.randrange(p)
        if (4 * A**3 + 27 * B**2) % p != 0:
            return A, B

def is_qr(u, p):
    u %= p
    return u == 0 or pow(u, (p - 1) // 2, p) == 1

# ---------------- Semaev polynomials (copied from bkkmv1, mmax=5) ----------------

def semaev_polys(A, B, F, mmax=5):
    R = PolynomialRing(F, 6, 'x')
    g = R.gens()
    a, b = F(A), F(B)
    S3 = (g[0]*g[1] + g[0]*g[2] + g[1]*g[2] + a)**2 - 4*(g[0]*g[1]*g[2] - b)*(g[0] + g[1] + g[2])
    out = {3: S3}
    if mmax >= 4:
        s3a = S3.subs({g[2]: g[5]})
        s3b = S3.subs({g[0]: g[2], g[1]: g[3], g[2]: g[5]})
        out[4] = s3a.resultant(s3b, g[5])
    if mmax >= 5:
        S4 = out[4]
        s4a = S4.subs({g[3]: g[5]})
        s3c = S3.subs({g[0]: g[3], g[1]: g[4], g[2]: g[5]})
        out[5] = s4a.resultant(s3c, g[5])
    return out

def supp_of(f, nvars):
    pts = set()
    for e in f.exponents():
        for i in range(nvars, len(e)):
            assert e[i] == 0, "nonzero exponent outside kept coordinates: %s" % (e,)
        pts.add(tuple(int(v) for v in e[:nvars]))
    return pts

def section_poly(f, t, m):
    R = f.parent()
    g = R.gens()
    return f.subs({g[m-1]: R.base_ring()(t)})

# ---------------- exact polytope volume engine (copied from bkkmv1) ----------------

def volume_from_support(pts, n):
    if len(pts) == 0:
        return QQ(0), "empty", 0
    maxes = [max(e[i] for e in pts) for i in range(n)]
    full = 1
    for v in maxes:
        full *= (v + 1)
    if len(pts) == full:
        vol = 1
        for v in maxes:
            vol *= v
        return QQ(vol), "full_grid_box", (2 ** n if n <= 20 else None)
    d = max(sum(e) for e in pts)
    if all(sum(e) <= d for e in pts):
        from math import comb
        if len(pts) == comb(d + n, n):
            from math import factorial
            return QQ(Integer(d)**n) / factorial(n), "full_simplex", None
    if len(pts) <= 60000:
        Pp = Polyhedron(vertices=[list(e) for e in pts])
        return QQ(Pp.volume()), "polyhedron_%s" % str(Pp.backend()), len(Pp.vertices())
    try:
        from scipy.spatial import ConvexHull
        H = ConvexHull(np.array([list(e) for e in pts], dtype=float))
        NOTES.append("APPROXIMATE volume used (scipy), n_pts=%d" % len(pts))
        return float(H.volume), "scipy_approximate_FLAGGED", None
    except Exception as e:
        NOTES.append("volume FAILED for %d points: %s" % (len(pts), e))
        return None, "failed", None

def hull_polyhedron(pts, n):
    maxes = [max(e[i] for e in pts) for i in range(n)]
    full = 1
    for v in maxes:
        full *= (v + 1)
    if len(pts) == full:
        corners = [list(c) for c in iproduct(*[[0, v] for v in maxes])]
        return Polyhedron(vertices=corners), "full_grid_box"
    d = max(sum(e) for e in pts)
    if all(sum(e) <= d for e in pts):
        from math import comb
        if len(pts) == comb(d + n, n):
            verts = []
            for i in range(n):
                vv = [0] * n
                vv[i] = d
                verts.append(vv)
            verts.append([0] * n)
            return Polyhedron(vertices=verts), "full_simplex"
    return Polyhedron(vertices=[list(e) for e in pts]), "polyhedron"

def mv_of_polys(polys, n):
    k = len(polys)
    supps = [supp_of(f, n) for f in polys]
    hulls = []
    methods = {}
    for pts in supps:
        Pp, method = hull_polyhedron(pts, n)
        hulls.append(Pp)
        methods[method] = methods.get(method, 0) + 1
    subset_vols = {}
    total = QQ(0)
    for r in range(1, k + 1):
        for S in combinations(range(k), r):
            PS = hulls[S[0]]
            for i in S[1:]:
                PS = PS + hulls[i]
            vol = QQ(PS.volume())
            subset_vols[str(S)] = {"vol": str(vol), "n_vertices": len(PS.vertices())}
            total += ((-1) ** (k - r)) * vol
    mv = total
    return {"mv": str(mv), "mv_float": float(mv), "approximate": False,
            "subset_vols": subset_vols, "method_counts": methods,
            "support_sizes": [len(s) for s in supps]}, None

# ---------------- section selection (copied from bkkmv1; used for m<=5 cells) ----------------

def pick_sections(Sm, A, B, p, m, seed):
    rng = random.Random(int(seed * 10000033 + p * 131 + m))
    proj = set()
    for e in Sm.exponents():
        proj.add(tuple(int(v) for v in e[:m-1]))
    chosen, losses, tries = [], [], []
    for j in range(m - 1):
        best, best_supp, best_loss = None, None, None
        for attempt in range(12):
            t = rng.randrange(1, p)
            if t in chosen:
                continue
            if not is_qr((t**3 + A*t + B) % p, p):
                continue
            ft = section_poly(Sm, t, m)
            st = supp_of(ft, m - 1)
            loss = len(proj) - len(st)
            if loss == 0:
                best, best_supp, best_loss = t, st, 0
                break
            if best is None or len(st) > len(best_supp):
                best, best_supp, best_loss = t, st, loss
        assert best is not None, "no valid section candidate found"
        chosen.append(best)
        losses.append(int(best_loss))
        tries.append(int(attempt + 1))
    return chosen, losses, tries, len(proj)

# ---------------- random same-support / dense polynomials (copied from bkkmv1) ----------------

def random_poly_on_support(R, supp, rng):
    p = R.base_ring().order()
    f = R(0)
    g = R.gens()
    for e in sorted(supp):
        c = rng.randrange(1, p)
        mon = R(1)
        for i, v in enumerate(e):
            if v:
                mon *= g[i]**v
        f += c * mon
    return f

def dense_support(n, d):
    out = []
    def rec(prefix, left, dim):
        if dim == 0:
            out.append(tuple(prefix))
            return
        for v in range(left + 1):
            rec(prefix + [v], left - v, dim - 1)
    rec([], d, n)
    return set(out)

# ---------------- numpy torus counting engine (copied from bkkmv1) ----------------

def count_torus(polys_monomials, n, p, count_boundary=True):
    import numpy as np
    dt = np.uint32
    vals = np.arange(1, p, dtype=dt)
    grids = np.meshgrid(*([vals] * (n - 1)), indexing='ij')
    X = [gr.reshape(-1) for gr in grids]
    N = X[0].shape[0]
    pp = dt(p)
    Cs = []
    for monoms in polys_monomials:
        dmax = max(e[n - 1] for e, c in monoms)
        C = [np.zeros(N, dtype=dt) for _ in range(dmax + 1)]
        powtab = {}
        for i in range(n - 1):
            dmax_i = max(e[i] for e, c in monoms)
            pw = [np.ones(N, dtype=dt)]
            for e in range(1, dmax_i + 1):
                pw.append((pw[-1] * X[i]) % pp)
            powtab[i] = pw
        skip_mods = (p ** n) < 2**32
        for e, c in monoms:
            W = np.full(N, dt(c % p), dtype=dt)
            if skip_mods:
                for i in range(n - 1):
                    if e[i]:
                        W = W * powtab[i][e[i]]
                W = W % pp
            else:
                for i in range(n - 1):
                    if e[i]:
                        W = (W * powtab[i][e[i]]) % pp
            C[e[n - 1]] = (C[e[n - 1]] + W) % pp
        Cs.append(C)
    torus = 0
    for u in range(1, p):
        uu = dt(u)
        mask = None
        for C in Cs:
            acc = C[-1]
            for k in range(len(C) - 2, -1, -1):
                acc = (acc * uu + C[k]) % pp
            z = (acc == 0)
            mask = z if mask is None else (mask & z)
        torus += int(mask.sum())
    boundary = 0
    if count_boundary:
        mask = None
        for C in Cs:
            z = (C[0] == 0)
            mask = z if mask is None else (mask & z)
        boundary = int(mask.sum())
    return {"torus": torus, "boundary_xn_zero": boundary, "outer_points": int(N)}

def monom_list(f, n, p):
    d = f.dict()
    out = []
    for e, c in d.items():
        ee = tuple(int(v) for v in e[:n])
        for i in range(n, len(e)):
            assert int(e[i]) == 0
        out.append((ee, int(c) % p))
    return out

def count_torus_naive(polys, n, p):
    F = GF(p)
    torus = 0
    boundary = 0
    import itertools as it
    for pt in it.product(range(1, p), repeat=n - 1):
        subs_map = {}
        R = polys[0].parent()
        g = R.gens()
        for i in range(n - 1):
            subs_map[g[i]] = F(pt[i])
        rems = [f.subs(subs_map) for f in polys]
        for u in range(p):
            ok = True
            for fr in rems:
                if fr.subs({g[n-1]: F(u)}) != 0:
                    ok = False
                    break
            if ok:
                if u == 0:
                    boundary += 1
                else:
                    torus += 1
    return {"torus": torus, "boundary_xn_zero": boundary}

# ================= fiberwise engine (new in bkkmv2) =================

def inv_vandermonde(G, p):
    """G x G inverse Vandermonde mod p on nodes 1..G, as int64 numpy array."""
    Fp = GF(p)
    V = Matrix(Fp, G, G, lambda i, j: Fp(i + 1)**j)
    W = V.inverse()
    return np.array([[int(W[i, j]) for j in range(G)] for i in range(G)], dtype=np.int64)

def power_table(G, dmax, p):
    """pw[c, e] = (c+1)^e mod p, c=0..G-1, e=0..dmax."""
    pw = np.ones((G, dmax + 1), dtype=np.int64)
    for c in range(G):
        v = (c + 1) % p
        for e in range(1, dmax + 1):
            pw[c, e] = (pw[c, e - 1] * v) % p
    return pw

def tensor_from_poly(f, var_positions, degs, p):
    """Dense int64 tensor from a 6-variate sage poly over GF(p).
    var_positions: ring-gen indices for tensor axes; degs: max degree per axis.
    Asserts all exponents outside var_positions are zero."""
    T = np.zeros([d + 1 for d in degs], dtype=np.int64)
    keep = set(var_positions)
    for e, c in f.dict().items():
        idx = tuple(int(e[pos]) for pos in var_positions)
        for pos in range(6):
            if pos not in keep:
                assert int(e[pos]) == 0, "nonzero exponent outside tensor axes: %s" % (e,)
        T[idx] = int(c) % p
    return T

def eval_a_coeffs(T, p, G):
    """T: tensor with axes (x_1..x_k exponents, X exponent). Contracts the first k
    axes on the grid nodes 1..G. Returns array with axes (X-exp, c_1..c_k)."""
    k = T.ndim - 1
    tmp = T
    for j in range(k):
        pw = power_table(G, T.shape[j] - 1, p)
        tmp = np.tensordot(pw, tmp, axes=([1], [0])) % p   # -> (c_j, remaining axes)
        tmp = np.moveaxis(tmp, 0, -1)                       # grid axis to the end
    return tmp   # axes: (X-exp, c_1..c_k)

def resultant_values(Aflat, b_vals, m, p):
    """Aflat: (mdeg+1, Ggrid) int64 values of a_0..a_mdeg on the flat (m-2)-dim grid.
    b_vals: (3, G) int64 values of b_0,b_1,b_2 on the last grid axis.
    Returns V shape (Ggrid, G): formal (mdeg,2) Sylvester resultant values.
    Identities verified in dev/probe_kernel.sage (K1/K2a/K2b)."""
    mdeg = Aflat.shape[0] - 1
    G = b_vals.shape[1]
    V = np.zeros((Aflat.shape[1], G), dtype=np.int64)
    Fp = GF(p)
    sgn = (p - 1) if (mdeg % 2) else 1   # (-1)^mdeg mod p
    for c in range(G):
        b0, b1, b2 = int(b_vals[0, c]), int(b_vals[1, c]), int(b_vals[2, c])
        if b2 != 0:
            c0 = int(Fp(b0) / Fp(b2)); c1 = int(Fp(b1) / Fp(b2))
            C = np.array([[0, -c0], [1, -c1]], dtype=np.int64)
            L = np.zeros((4, mdeg + 1), dtype=np.int64)
            Cp = np.eye(2, dtype=np.int64)
            for i in range(mdeg + 1):
                L[0, i] = Cp[0, 0] % p; L[1, i] = Cp[0, 1] % p
                L[2, i] = Cp[1, 0] % p; L[3, i] = Cp[1, 1] % p
                Cp = (Cp @ C) % p
            Ment = (L @ Aflat) % p
            det = (Ment[0] * Ment[3] - Ment[1] * Ment[2]) % p
            V[:, c] = (det * pow(b2, mdeg, p)) % p
        elif b1 != 0:
            beta = int(-Fp(b0) / Fp(b1))
            bp = np.array([pow(beta, i, p) for i in range(mdeg + 1)], dtype=np.int64)
            Aval = (bp @ Aflat) % p
            factor = (sgn * pow(b1, mdeg, p)) % p
            V[:, c] = ((Aflat[mdeg] * Aval) % p * factor) % p
        else:
            V[:, c] = ((Aflat[mdeg] * Aflat[mdeg]) % p * pow(b0, mdeg, p)) % p
    return V

def interpolate_values(Vgrid, W, p):
    """Vgrid: (G,)^n value tensor; W: GxG inverse Vandermonde int64 mod p.
    Returns exact coefficient tensor (G,)^n mod p."""
    n = Vgrid.ndim
    G = Vgrid.shape[0]
    rec = Vgrid
    for j in range(n):
        rec = np.moveaxis(rec, j, 0).reshape(G, -1)
        rec = (W @ rec) % p
        rec = rec.reshape([G] * n)
        rec = np.moveaxis(rec, 0, j)
    return rec

def support_from_coeffs(C):
    return set(tuple(int(v) for v in idx) for idx in zip(*np.nonzero(C)))

def a_tensor_for(m, polys, p):
    """A = S_{m-1}(x_1..x_{m-2}, X) dense tensor (axes x_1..x_{m-2}, X).
    m=3: S_2(x_1, X) = x_1 - X built inline."""
    if m == 3:
        T = np.zeros((2, 2), dtype=np.int64)
        T[1, 0] = 1          # a_0 = x_1
        T[0, 1] = p - 1      # a_1 = -1
        return T
    R = polys[3].parent()
    g = R.gens()
    if m == 4:
        fA = polys[3].subs({g[2]: g[5]})
        return tensor_from_poly(fA, [0, 1, 5], [2, 2, 2], p)
    if m == 5:
        fA = polys[4].subs({g[3]: g[5]})
        return tensor_from_poly(fA, [0, 1, 2, 5], [4, 4, 4, 4], p)
    if m == 6:
        fA = polys[5].subs({g[4]: g[5]})
        return tensor_from_poly(fA, [0, 1, 2, 3, 5], [8, 8, 8, 8, 8], p)
    raise ValueError("m out of range")

def b_tensor_for(S3, t, m, p):
    """B = S_3(x_{m-1}, t, X) dense tensor (axes x_{m-1}, X), degrees (2,2)."""
    R = S3.parent()
    g = R.gens()
    fB = S3.subs({g[0]: g[m-2], g[1]: R.base_ring()(t), g[2]: g[5]})
    return tensor_from_poly(fB, [m-2, 5], [2, 2], p)

def sylvester_det_generic(a, b, mdeg, p):
    """Formal (mdeg,2) Sylvester determinant for A = sum a[i] X^i, B = b[2]X^2+b[1]X+b[0].
    Ground truth for value spot-checks (K1-verified definition)."""
    Fp = GF(p)
    M = Matrix(Fp, mdeg + 2, mdeg + 2, 0)
    for k in range(2):
        for j in range(mdeg + 1):
            M[k, k + j] = Fp(int(a[mdeg - j]))
    for r in range(mdeg):
        for j in range(3):
            M[2 + r, r + j] = Fp(int(b[2 - j]))
    return M.determinant()

def fiber_section_support(Aflat, b_vals, W, m, p, G):
    """Full engine pipeline for one section: values -> interpolation -> support dict."""
    n = m - 1
    V = resultant_values(Aflat, b_vals, m, p).reshape([G] * n)
    C = interpolate_values(V, W, p)
    bitmap = (C != 0)
    nz = np.nonzero(bitmap)
    maxes = [int(nz[i].max()) for i in range(n)]
    corners_missing = []
    for c in iproduct(*[[0, mx] for mx in maxes]):
        if not bitmap[c]:
            corners_missing.append([int(v) for v in c])
    full_box = 1
    for mx in maxes:
        full_box *= (mx + 1)
    sha = hashlib.sha256(bitmap.tobytes()).hexdigest()
    totdeg = int(np.array(nz).sum(axis=0).max()) if supp_nonempty(nz) else 0
    return {"bitmap": bitmap, "support_size": int(bitmap.sum()),
            "maxes": maxes, "corners_missing": corners_missing,
            "corners_total": 2 ** n, "full_box_size": int(full_box),
            "losses_vs_full_box": int(full_box - bitmap.sum()),
            "totdeg_max": totdeg, "bitmap_sha256": sha,
            "coeff_sha256": hashlib.sha256(C.tobytes()).hexdigest()}

def supp_nonempty(nz):
    return len(nz[0]) > 0

def mv_from_boxes(boxes, n):
    """Exact normalized MV of axis boxes by inclusion-exclusion over subset Minkowski
    sums (definition, as in bkkmv1), cross-checked by the box permanent."""
    k = len(boxes)
    total = 0
    subset_vols = {}
    for r in range(1, k + 1):
        for S in combinations(range(k), r):
            vol = 1
            for i in range(n):
                vol *= sum(boxes[j][i] for j in S)
            subset_vols[str(S)] = int(vol)
            total += ((-1) ** (k - r)) * vol
    perm = 0
    for sigma in permutations(range(n)):
        term = 1
        for j in range(k):
            term *= boxes[j][sigma[j]]
        perm += term
    return int(total), int(perm), subset_vols

# ================= stage: validate =================

def stage_validate(out_path, seeds):
    rec = {"stage": "validate", "cells": [], "controls": []}
    p0 = P_CERT[0]
    # ---- P1 dense simplex (curve-independent) ----
    for (n, d) in [(2, 2), (2, 4), (3, 4), (4, 8)]:
        rng = random.Random(int(900000000 + n * 1000 + d))
        R = PolynomialRing(GF(p0), n, 'y')
        supp = dense_support(n, d)
        pols = [random_poly_on_support(R, supp, rng) for _ in range(n)]
        mvres, err = mv_of_polys(pols, n)
        assert err is None, err
        ok = (QQ(mvres["mv"]) == d ** n)
        rec["controls"].append({"id": "P1_dense_simplex", "n": n, "d": d, "pass": bool(ok),
                                "mv": mvres["mv"], "expected": d ** n})
    # ---- per-seed P4a engine cross-validation (m=3,4,5) + P2 + N1 ----
    for seed in seeds:
        p_list = [(p0, "cert")] + ([(101, "lossy")] if seed == seeds[0] else [])
        for (p, tag) in p_list:
            A, B = gen_curve(seed, p)
            F = GF(p)
            tp = time.time()
            polys = semaev_polys(A, B, F, 5)
            uns = {str(m): len(supp_of(polys[m], m)) for m in [3, 4, 5]}
            cell = {"seed": seed, "p": p, "tag": tag, "A": A, "B": B,
                    "unsectioned_support_sizes": uns,
                    "semaev_build_seconds": round(time.time() - tp, 3), "m": {}}
            for m in [3, 4, 5]:
                n = m - 1
                Sm = polys[m]
                ts, losses, tries, proj_size = pick_sections(Sm, A, B, p, m, seed)
                fsec = [section_poly(Sm, t, m) for t in ts]
                sym_supps = [supp_of(fsec[j], n) for j in range(n)]
                mvres, err = mv_of_polys(fsec, n)
                assert err is None, err
                mvq = QQ(mvres["mv"])
                G = 2 ** (m - 2) + 1
                W = inv_vandermonde(G, p)
                te = time.time()
                TA = a_tensor_for(m, polys, p)
                A_vals = eval_a_coeffs(TA, p, G)
                Aflat = A_vals.reshape(A_vals.shape[0], -1)
                eng_supps = []
                eng_boxes_ok = True
                for t in ts:
                    TB = b_tensor_for(polys[3], t, m, p)
                    b_vals = eval_a_coeffs(TB, p, G)
                    sec = fiber_section_support(Aflat, b_vals, W, m, p, G)
                    eng_supps.append(support_from_coeffs(sec["bitmap"].astype(np.int64)))
                    if sec["corners_missing"]:
                        eng_boxes_ok = False
                eng_secs = round(time.time() - te, 3)
                match = all(eng_supps[j] == sym_supps[j] for j in range(n))
                rec["controls"].append({
                    "id": "P4a_engine_crossvalidation", "seed": seed, "p": p, "m": m,
                    "pass": bool(match),
                    "sym_sizes": [len(s) for s in sym_supps],
                    "eng_sizes": [len(s) for s in eng_supps],
                    "section_losses": losses, "engine_seconds": eng_secs,
                    "engine_hull_boxes_ok": bool(eng_boxes_ok)})
                cell["m"][str(m)] = {"targets_t": ts, "section_losses": losses,
                                     "sym_support_sizes": [len(s) for s in sym_supps],
                                     "mv_symbolic": mvres["mv"],
                                     "mv_expected": {3: 8, 4: 384, 5: 98304}[m],
                                     "mv_matches_law": bool(mvq == {3: 8, 4: 384, 5: 98304}[m])}
                if m == 3:
                    ok = (mvres["support_sizes"] == [9, 9]) and (mvq == 8)
                    rec["controls"].append({"id": "P2_hand_value_m3", "seed": seed, "p": p,
                                            "pass": bool(ok), "mv": mvres["mv"],
                                            "support_sizes": mvres["support_sizes"]})
                rng = random.Random(int(seed * 10000061 + p * 137 + m))
                R6 = Sm.parent()
                frnd = [random_poly_on_support(R6, sym_supps[j], rng) for j in range(n)]
                mvres2, err2 = mv_of_polys(frnd, n)
                assert err2 is None, err2
                rec["controls"].append({"id": "N1_same_support_MV", "seed": seed, "p": p, "m": m,
                                        "pass": bool(QQ(mvres2["mv"]) == mvq),
                                        "mv_semaev": mvres["mv"], "mv_random": mvres2["mv"]})
            rec["cells"].append(cell)
            sys.stderr.write("validate cell done seed=%d p=%d t=%.1fs\n" % (seed, p, elapsed()))
            sys.stderr.flush()
    # ---- P4 two-prime literal support stability (m=3,4,5) ----
    for seed in seeds:
        supps_by_prime = {}
        for p in P_CERT:
            A, B = gen_curve(seed, p)
            polys = semaev_polys(A, B, GF(p), 5)
            supps_by_prime[p] = {m: supp_of(polys[m], m) for m in [3, 4, 5]}
        stab = all(supps_by_prime[P_CERT[0]][m] == supps_by_prime[P_CERT[1]][m] for m in [3, 4, 5])
        rec["controls"].append({"id": "P4_two_prime_support_stability_m345", "seed": seed,
                                "pass": bool(stab)})
    # ---- P4 QQ cross-check (m=3,4) ----
    for seed in seeds:
        A0, B0 = gen_curve(seed, P_CERT[0])
        qpolys = semaev_polys(A0, B0, QQ, 4)
        fpolys = semaev_polys(A0, B0, GF(P_CERT[0]), 4)
        q_ok = all(supp_of(qpolys[m], m) == supp_of(fpolys[m], m) for m in [3, 4])
        rec["controls"].append({"id": "P4_QQ_support_check", "seed": seed, "m": [3, 4],
                                "pass": bool(q_ok)})
    # ---- P5a value check: m=5, seeds[0], p=1000003, section 1, full 9^4 grid ----
    seed, p, m = seeds[0], p0, 5
    A, B = gen_curve(seed, p)
    F = GF(p)
    polys = semaev_polys(A, B, F, 5)
    g = polys[3].parent().gens()
    ts, _, _, _ = pick_sections(polys[5], A, B, p, 5, seed)
    t = ts[0]
    G = 9
    TA = a_tensor_for(m, polys, p)
    A_vals = eval_a_coeffs(TA, p, G)
    Aflat = A_vals.reshape(A_vals.shape[0], -1)
    TB = b_tensor_for(polys[3], t, m, p)
    b_vals = eval_a_coeffs(TB, p, G)
    V = resultant_values(Aflat, b_vals, m, p).reshape([G, G, G, G])
    S4A = polys[4].subs({g[3]: g[5]})                                   # S_4(x1..x3, X)
    Bpoly = polys[3].subs({g[0]: g[3], g[1]: F(t), g[2]: g[5]})         # S_3(x4, t, X)
    mdeg = 4
    mismatches = 0
    checked = 0
    tchk = time.time()
    for c1 in range(G):
        for c2 in range(G):
            for c3 in range(G):
                for c4 in range(G):
                    fx = S4A.subs({g[0]: F(c1 + 1), g[1]: F(c2 + 1), g[2]: F(c3 + 1)})
                    a = [fx.monomial_coefficient(g[5]**i) for i in range(mdeg + 1)]
                    bx = Bpoly.subs({g[3]: F(c4 + 1)})
                    b = [bx.monomial_coefficient(g[5]**j) for j in range(3)]
                    det = sylvester_det_generic(a, b, mdeg, p)
                    checked += 1
                    if F(int(V[c1, c2, c3, c4])) != det:
                        mismatches += 1
                        if mismatches < 4:
                            NOTES.append("P5a mismatch at %s: engine=%s sylvester=%s" %
                                         ((c1, c2, c3, c4), int(V[c1, c2, c3, c4]), str(det)))
    rec["controls"].append({"id": "P5_value_spotcheck_m5_fullgrid", "seed": seed, "p": p,
                            "section_t": t, "grid": "9^4", "checked": checked,
                            "mismatches": mismatches, "pass": bool(mismatches == 0),
                            "seconds": round(time.time() - tchk, 3)})
    return rec

# ================= stage: measure6 =================

def measure6_instance(seed, p, supports_dir, p5b_points, rec):
    from math import factorial
    m, n, G = 6, 5, 17
    t0 = time.time()
    A, B = gen_curve(seed, p)
    F = GF(p)
    polys = semaev_polys(A, B, F, 5)
    g = polys[3].parent().gens()
    TA = a_tensor_for(6, polys, p)
    A_vals = eval_a_coeffs(TA, p, G)
    Aflat = A_vals.reshape(9, -1)
    W = inv_vandermonde(G, p)
    build_secs = time.time() - t0
    rng = random.Random(int(seed * 10000033 + p * 131 + m))
    chosen, slot_tries = [], []
    sections = []
    union_bitmap = np.zeros([G] * n, dtype=bool)
    for j in range(n):
        accepted, last_t, last_sec, tries = None, None, None, 0
        for attempt in range(12):
            t = rng.randrange(1, p)
            tries = attempt + 1
            if t in chosen:
                continue
            if not is_qr((t**3 + A * t + B) % p, p):
                continue
            last_t = t
            TB = b_tensor_for(polys[3], t, m, p)
            b_vals = eval_a_coeffs(TB, p, G)
            sec = fiber_section_support(Aflat, b_vals, W, m, p, G)
            last_sec = sec
            if not sec["corners_missing"]:
                accepted = (t, sec)
                break
            NOTES.append("corner deficit seed=%d p=%d slot=%d t=%d missing=%d" %
                         (seed, p, j, t, len(sec["corners_missing"])))
        if accepted is None:
            accepted = (last_t, last_sec)
            NOTES.append("slot %d seed=%d p=%d accepted WITH corner deficit after 12 candidates" %
                         (j, seed, p))
        t_j, sec = accepted
        chosen.append(t_j)
        slot_tries.append(tries)
        fname = "sec%d_seed%d_p%d.npy" % (j, seed, p)
        np.save(os.path.join(supports_dir, fname), np.packbits(sec["bitmap"].reshape(-1)))
        sections.append({"slot": j, "t": int(t_j), "tries": tries,
                         "support_size": sec["support_size"], "maxes": sec["maxes"],
                         "corners_missing_count": len(sec["corners_missing"]),
                         "corners_missing_first8": sec["corners_missing"][:8],
                         "losses_vs_full_box": sec["losses_vs_full_box"],
                         "totdeg_max": sec["totdeg_max"],
                         "bitmap_file": "supports/" + fname, "bitmap_shape": [G] * n,
                         "bitmap_sha256": sec["bitmap_sha256"],
                         "coeff_sha256": sec["coeff_sha256"],
                         "hull_is_box": bool(not sec["corners_missing"])})
        union_bitmap |= sec["bitmap"]
    hulls_ok = all(s["hull_is_box"] for s in sections)
    boxes = [s["maxes"] for s in sections]
    if hulls_ok:
        mv, perm, subset_vols = mv_from_boxes(boxes, n)
        mv_ok = bool(mv == perm)
    else:
        mv, perm, subset_vols, mv_ok = None, None, None, None
        NOTES.append("MV not certified by box path for seed=%d p=%d (corner deficit)" % (seed, p))
    unz = np.nonzero(union_bitmap)
    union_size = int(union_bitmap.sum())
    d_tot = int(np.array(unz).sum(axis=0).max())
    bez_total = d_tot ** n
    bez_box = factorial(n)
    for v in boxes[0]:
        bez_box *= v
    inst = {"seed": seed, "p": p, "m": m, "n": n, "A": A, "B": B,
            "targets_t": chosen, "section_tries": slot_tries,
            "sections": sections, "hulls_all_box": hulls_ok,
            "union_support_size": union_size, "union_missing_vs_fullbox": int(G ** n - union_size),
            "d_total_sectioned": d_tot, "bezout_total": int(bez_total), "bezout_box": int(bez_box),
            "mv_exact": mv, "mv_permanent_crosscheck": perm, "mv_ieq_eq_perm": mv_ok,
            "mv_prediction": 125829120,
            "mv_matches_prediction": (bool(mv == 125829120) if mv is not None else None),
            "ratio_mv_bezout_box": (float(mv) / bez_box if mv is not None else None),
            "ratio_mv_bezout_total": (float(mv) / bez_total if mv is not None else None),
            "ratio_mv_bezout_total_exact": (str(QQ(mv) / QQ(bez_total)) if mv is not None else None),
            "build_seconds": round(build_secs, 3),
            "instance_seconds": round(time.time() - t0, 3)}
    # ---- P5b value spot-check on slot 0 (first instance only) ----
    if p5b_points > 0:
        S5A = polys[5].subs({g[4]: g[5]})
        t0sec = sections[0]["t"]
        Bpoly0 = polys[3].subs({g[0]: g[4], g[1]: F(t0sec), g[2]: g[5]})
        TB0 = b_tensor_for(polys[3], t0sec, m, p)
        b_vals0 = eval_a_coeffs(TB0, p, G)
        V0 = resultant_values(Aflat, b_vals0, m, p).reshape([G] * n)
        rngs = random.Random(int(777000 + seed))
        pts = set()
        while len(pts) < p5b_points:
            pts.add(tuple(rngs.randrange(G) for _ in range(n)))
        mism, checked = 0, 0
        tchk = time.time()
        for pt in sorted(pts):
            if not time_left() and checked < 16:
                NOTES.append("P5b reduced to %d points (soft budget)" % checked)
                break
            fx = S5A.subs({g[0]: F(pt[0] + 1), g[1]: F(pt[1] + 1), g[2]: F(pt[2] + 1),
                           g[3]: F(pt[3] + 1)})
            a = [fx.monomial_coefficient(g[5]**i) for i in range(9)]
            bx = Bpoly0.subs({g[4]: F(pt[4] + 1)})
            b = [bx.monomial_coefficient(g[5]**j) for j in range(3)]
            det = sylvester_det_generic(a, b, 8, p)
            checked += 1
            if F(int(V0[pt])) != det:
                mism += 1
                if mism < 4:
                    NOTES.append("P5b mismatch at %s: engine=%s sylvester=%s" %
                                 (pt, int(V0[pt]), str(det)))
        rec["controls"].append({"id": "P5_value_spotcheck_m6", "seed": seed, "p": p,
                                "section_t": t0sec, "sampled": len(pts), "checked": checked,
                                "mismatches": mism,
                                "pass": bool(mism == 0 and checked >= 16),
                                "seconds": round(time.time() - tchk, 3)})
    return inst

def stage_measure6(out_path, seeds, primes, supports_dir, det_recheck):
    rec = {"stage": "measure6", "instances": [], "controls": [], "censored": [],
           "predictions": {"mv6": 125829120, "bezout_box": 125829120,
                           "bezout_total": 3276800000, "ratio_mv_bezout_box": 1.0,
                           "ratio_mv_bezout_total": 0.0384,
                           "sectioned_support_full_box": 1419857, "d_total": 80}}
    for p in primes:
        for seed in seeds:
            if not time_left():
                rec["censored"].append({"seed": seed, "p": p, "reason": "soft budget"})
                continue
            p5b = 48 if (seed == seeds[0] and p == primes[0]) else 0
            inst = measure6_instance(seed, p, supports_dir, p5b, rec)
            rec["instances"].append(inst)
            sys.stderr.write("measure6 instance done seed=%d p=%d mv=%s t=%.1fs\n" %
                             (seed, p, str(inst["mv_exact"]), elapsed()))
            sys.stderr.flush()
            if out_path:
                with open(out_path + ".partial", "w") as fh:
                    json.dump(jsanitize(rec), fh)
    # ---- P4c determinism recheck vs a previous run's raw.json ----
    if det_recheck:
        try:
            ref = json.load(open(det_recheck))
            ref_inst = [i for i in ref["instances"]
                        if i["seed"] == 20260717 and i["p"] == 1000003][0]
            ref_sec = ref_inst["sections"][0]
            seed, p, m, G = 20260717, 1000003, 6, 17
            A, B = gen_curve(seed, p)
            F = GF(p)
            polys = semaev_polys(A, B, F, 5)
            TA = a_tensor_for(6, polys, p)
            A_vals = eval_a_coeffs(TA, p, G)
            Aflat = A_vals.reshape(9, -1)
            W = inv_vandermonde(G, p)
            rng = random.Random(int(seed * 10000033 + p * 131 + m))
            sec, t = None, None
            for attempt in range(12):
                cand = rng.randrange(1, p)
                if not is_qr((cand**3 + A * cand + B) % p, p):
                    continue
                t = cand
                TB = b_tensor_for(polys[3], cand, m, p)
                b_vals = eval_a_coeffs(TB, p, G)
                sec = fiber_section_support(Aflat, b_vals, W, m, p, G)
                if not sec["corners_missing"]:
                    break
            ok = (sec["bitmap_sha256"] == ref_sec["bitmap_sha256"] and t == ref_sec["t"])
            rec["controls"].append({"id": "P4c_determinism", "pass": bool(ok),
                                    "ref_run": det_recheck, "t": t, "ref_t": ref_sec["t"],
                                    "sha": sec["bitmap_sha256"],
                                    "ref_sha": ref_sec["bitmap_sha256"]})
        except Exception as e:
            rec["controls"].append({"id": "P4c_determinism", "pass": False, "error": str(e)})
    return rec

# ================= stage: counts =================

def count_cell(seed, p, m):
    n = m - 1
    A, B = gen_curve(seed, p)
    F = GF(p)
    polys = semaev_polys(A, B, F, m)
    Sm = polys[m]
    ts, losses, tries, proj_size = pick_sections(Sm, A, B, p, m, seed)
    fsec = [section_poly(Sm, t, m) for t in ts]
    tmv = time.time()
    mvres, err = mv_of_polys(fsec, n)
    assert err is None, err
    mvq = QQ(mvres["mv"])
    monoms = [monom_list(f, n, p) for f in fsec]
    tc = time.time()
    cnt = count_torus(monoms, n, p)
    return {"seed": seed, "p": p, "m": m, "n": n, "A": A, "B": B,
            "targets_t": ts, "section_losses": losses,
            "section_support_sizes": mvres["support_sizes"],
            "mv_exact": mvres["mv"], "count_torus": cnt["torus"],
            "count_boundary_xn_zero": cnt["boundary_xn_zero"],
            "bkk_bound_holds": bool(cnt["torus"] <= mvq),
            "mv_seconds": round(time.time() - tmv, 3),
            "count_seconds": round(time.time() - tc, 3)}

def stage_counts(out_path, seeds):
    rec = {"stage": "counts", "cells": [], "controls": [], "censored": []}
    for seed in seeds:
        if not time_left():
            rec["censored"].append({"m": 4, "p": 101, "seed": seed, "reason": "soft budget"})
            continue
        r = count_cell(seed, 101, 4)
        rec["cells"].append(r)
        rec["controls"].append({"id": "P3_bkk_bound", "m": 4, "p": 101, "seed": seed,
                                "pass": bool(r["bkk_bound_holds"]),
                                "count": r["count_torus"], "mv": r["mv_exact"]})
        sys.stderr.write("count cell m=4 p=101 seed=%d done t=%.1fs\n" % (seed, elapsed()))
        sys.stderr.flush()
    if time_left():
        r = count_cell(seeds[0], 101, 5)
        rec["cells"].append(r)
        rec["controls"].append({"id": "P3_bkk_bound", "m": 5, "p": 101, "seed": seeds[0],
                                "pass": bool(r["bkk_bound_holds"]),
                                "count": r["count_torus"], "mv": r["mv_exact"]})
        sys.stderr.write("count cell m=5 p=101 seed=%d done t=%.1fs\n" % (seeds[0], elapsed()))
        sys.stderr.flush()
    else:
        rec["censored"].append({"m": 5, "p": 101, "seed": seeds[0], "reason": "soft budget"})
    # N2 violation witness (m=3, p=431, repeated section -> positive-dimensional)
    seed, p, m = seeds[0], 431, 3
    A, B = gen_curve(seed, p)
    F = GF(p)
    polys = semaev_polys(A, B, F, 3)
    Sm = polys[3]
    ts, _, _, _ = pick_sections(Sm, A, B, p, m, seed)
    f1 = section_poly(Sm, ts[0], m)
    rep = [f1, f1]
    mvres3, err3 = mv_of_polys(rep, 2)
    assert err3 is None, err3
    monoms3 = [monom_list(f1, 2, p)] * 2
    cnt3 = count_torus(monoms3, 2, p)
    rec["controls"].append({"id": "N2_violation_witness", "m": 3, "p": 431, "seed": seed,
                            "pass": bool(cnt3["torus"] > QQ(mvres3["mv"])),
                            "count": cnt3["torus"], "mv": mvres3["mv"]})
    # N3 engine selfcheck (m=3, p=101, numpy vs naive)
    seed, p, m = seeds[0], 101, 3
    A, B = gen_curve(seed, p)
    F = GF(p)
    polys = semaev_polys(A, B, F, 3)
    Sm = polys[3]
    ts, _, _, _ = pick_sections(Sm, A, B, p, m, seed)
    fsec = [section_poly(Sm, t, m) for t in ts]
    monoms = [monom_list(f, 2, p) for f in fsec]
    c_fast = count_torus(monoms, 2, p)
    c_naive = count_torus_naive(fsec, 2, p)
    rec["controls"].append({"id": "N3_engine_selfcheck", "m": 3, "p": 101, "seed": seed,
                            "pass": bool(c_fast["torus"] == c_naive["torus"] and
                                         c_fast["boundary_xn_zero"] == c_naive["boundary_xn_zero"]),
                            "numpy": c_fast["torus"], "naive": c_naive["torus"]})
    return rec

# ---------------- main ----------------

def main():
    args = sys.argv[1:]
    def getarg(flag, default=None):
        if flag in args:
            i = args.index(flag)
            return args[i + 1]
        return default
    stage = getarg("--stage", "validate")
    out_path = getarg("--out", None)
    seeds = [int(s) for s in getarg("--seeds", ",".join(str(s) for s in SEEDS_DEFAULT)).split(",")]
    primes = [int(s) for s in getarg("--primes", str(P_CERT[0])).split(",")]
    supports_dir = getarg("--supports-dir", None)
    det_recheck = getarg("--det-recheck", None)
    commit, dirty = git_info()
    started = now_iso()
    if stage == "validate":
        rec = stage_validate(out_path, seeds)
    elif stage == "measure6":
        assert supports_dir, "--supports-dir required"
        rec = stage_measure6(out_path, seeds, primes, supports_dir, det_recheck)
    elif stage == "counts":
        rec = stage_counts(out_path, seeds)
    else:
        raise ValueError("unknown stage %s" % stage)
    commit2, dirty2 = git_info()
    rec["run_meta"] = {
        "stage": stage, "seeds": seeds, "primes": primes,
        "sage_version": str(subprocess.check_output(["sage", "--version"], text=True).strip()),
        "numpy_version": str(np.__version__),
        "started_at": started, "finished_at": now_iso(),
        "wall_seconds": round(float(elapsed()), 3),
        "git_commit": commit2, "git_dirty": dirty2,
        "notes": NOTES,
        "soft_budget_seconds": SOFT_BUDGET,
    }
    data = jsanitize(rec)
    if out_path:
        with open(out_path, "w") as fh:
            json.dump(data, fh, indent=1)
        print("WROTE %s" % out_path)
    n_cells = len(data.get("cells", data.get("instances", [])))
    n_ctrl = len(data.get("controls", []))
    n_pass = sum(1 for c in data.get("controls", []) if c.get("pass"))
    print(json.dumps(jsanitize({"stage": stage, "wall_seconds": round(float(elapsed()), 3),
                                "n_cells": n_cells, "controls_pass": "%d/%d" % (n_pass, n_ctrl),
                                "notes": NOTES})))

main()
