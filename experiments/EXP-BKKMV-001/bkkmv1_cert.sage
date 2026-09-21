# bkkmv1_cert.sage — EXP-BKKMV-001 (candidate D2, ledger family BKKMV)
# Exact Newton-polytope / mixed-volume certificate for the target-sectioned
# Semaev summation family, m in {3,4,5}, with BKK cross-check against
# brute-force F_p torus solution counts. Deterministic (seeded). Self-contained.
#
# Usage:
#   sage bkkmv1_cert.sage --stage poly      --out <raw.json>
#   sage bkkmv1_cert.sage --stage counts3   --out <raw.json>
#   sage bkkmv1_cert.sage --stage counts4   --out <raw.json>
#   sage bkkmv1_cert.sage --stage counts5   --out <raw.json> [--seeds 20260717,20260718] [--with-neg 20260717]
#
# System (frozen in specification.yaml): Sys_m = { S_m(x_1..x_{m-1}, t_j) = 0 },
# j = 1..m-1, n = m-1 equations in n unknowns; MV by exact inclusion-exclusion
# over subset-product Newton polytopes: n!*MV = sum_{S nonempty} (-1)^{n-|S|} Vol(NP(prod_{i in S} f_i)).

import sys, os, json, time, random, subprocess
from datetime import datetime, timezone
from itertools import combinations

SEEDS_DEFAULT = [20260717, 20260718, 20260719]
P_CERT = [1000003, 1000033]
P_COUNTS = [101, 431, 1009]
SOFT_BUDGET = float(540)  # seconds; finish current cell then stop, mark censored
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

# ---------------- curve / RNG streams ----------------

def gen_curve(seed, p):
    """Deterministic (A,B) in F_p^2, nonsingular. Returns python ints."""
    rng = random.Random(int(seed * 10000007 + p))
    while True:
        A = rng.randrange(p)
        B = rng.randrange(p)
        if (4 * A**3 + 27 * B**2) % p != 0:
            return A, B

def is_qr(u, p):
    u %= p
    return u == 0 or pow(u, (p - 1) // 2, p) == 1

# ---------------- Semaev polynomials ----------------

def semaev_polys(A, B, F, mmax=5):
    """S_3..S_mmax over F in a 6-variate ring (x1..x5, X). Returns dict m -> poly."""
    R = PolynomialRing(F, 6, 'x')
    g = R.gens()  # g[0..4] = x1..x5, g[5] = X
    a, b = F(A), F(B)
    S3 = (g[0]*g[1] + g[0]*g[2] + g[1]*g[2] + a)**2 - 4*(g[0]*g[1]*g[2] - b)*(g[0] + g[1] + g[2])
    out = {3: S3}
    if mmax >= 4:
        s3a = S3.subs({g[2]: g[5]})                          # S_3(x1,x2,X)
        s3b = S3.subs({g[0]: g[2], g[1]: g[3], g[2]: g[5]})  # S_3(x3,x4,X)
        out[4] = s3a.resultant(s3b, g[5])
    if mmax >= 5:
        S4 = out[4]
        s4a = S4.subs({g[3]: g[5]})                          # S_4(x1,x2,x3,X)
        s3c = S3.subs({g[0]: g[3], g[1]: g[4], g[2]: g[5]})  # S_3(x4,x5,X)
        out[5] = s4a.resultant(s3c, g[5])
    return out

def supp_of(f, nvars):
    """Exponent set of f restricted to the first nvars coordinates.
    Asserts f has zero exponents outside those coordinates."""
    pts = set()
    for e in f.exponents():
        for i in range(nvars, len(e)):
            assert e[i] == 0, "nonzero exponent outside kept coordinates: %s" % (e,)
        pts.add(tuple(int(v) for v in e[:nvars]))
    return pts

def section_poly(f, t, m):
    """S_m(x_1..x_{m-1}, t): substitute g[m-1] = t."""
    R = f.parent()
    g = R.gens()
    return f.subs({g[m-1]: R.base_ring()(t)})

# ---------------- exact polytope volume engine ----------------

def volume_from_support(pts, n):
    """Exact lattice-polytope volume (Euclidean) of conv(pts), pts in Z^n.
    Returns (volume_as_Rational_or_float, method, n_vertices_or_None)."""
    if len(pts) == 0:
        return QQ(0), "empty", 0
    maxes = [max(e[i] for e in pts) for i in range(n)]
    # layer 1: full axis box proof by counting
    full = 1
    for v in maxes:
        full *= (v + 1)
    if len(pts) == full:
        vol = 1
        for v in maxes:
            vol *= v
        return QQ(vol), "full_grid_box", (2 ** n if n <= 20 else None)
    # layer 1b: full simplex proof by counting (dense total-degree support)
    d = max(sum(e) for e in pts)
    if all(sum(e) <= d for e in pts):
        from math import comb
        if len(pts) == comb(d + n, n):
            from math import factorial
            return QQ(Integer(d)**n) / factorial(n), "full_simplex", None
    # layer 2: exact Polyhedron
    if len(pts) <= 60000:
        P = Polyhedron(vertices=[list(e) for e in pts])
        return QQ(P.volume()), "polyhedron_%s" % str(P.backend()), len(P.vertices())
    # layer 3: flagged float fallback (not expected to trigger)
    try:
        import numpy as np
        from scipy.spatial import ConvexHull
        H = ConvexHull(np.array([list(e) for e in pts], dtype=float))
        NOTES.append("APPROXIMATE volume used (scipy), n_pts=%d" % len(pts))
        return float(H.volume), "scipy_approximate_FLAGGED", None
    except Exception as e:
        NOTES.append("volume FAILED for %d points: %s" % (len(pts), e))
        return None, "failed", None

def hull_polyhedron(pts, n):
    """Exact convex hull of support points as a Sage Polyhedron.
    Uses fast provable paths for full boxes / full simplices (avoids feeding
    huge point sets); otherwise exact Polyhedron on the points."""
    from itertools import product as iproduct
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
    """Normalized mixed volume (BKK bound) via inclusion-exclusion over Minkowski
    sums of Newton polytopes: MV_norm = sum_{nonempty S} (-1)^{n-|S|} Vol(sum_{i in S} NP(f_i)).
    Convention: MV_norm(P,..,P) = n!*Vol(P); generic torus root count = MV_norm.
    Minkowski sums are taken on the exact hull polytopes (never on point sets)."""
    k = len(polys)
    supps = [supp_of(f, n) for f in polys]
    hulls = []
    methods = {}
    for pts in supps:
        P, method = hull_polyhedron(pts, n)
        hulls.append(P)
        methods[method] = methods.get(method, 0) + 1
    subset_vols = {}
    total = QQ(0)
    for r in range(1, k + 1):
        for S in combinations(range(k), r):
            PS = hulls[S[0]]
            for i in S[1:]:
                PS = PS + hulls[i]   # exact Minkowski sum of polytopes
            vol = QQ(PS.volume())
            subset_vols[str(S)] = {"vol": str(vol), "n_vertices": len(PS.vertices())}
            total += ((-1) ** (k - r)) * vol
    mv = total  # normalized mixed volume = BKK bound (no division by n!)
    return {"mv": str(mv), "mv_float": float(mv), "approximate": False,
            "subset_vols": subset_vols, "method_counts": methods,
            "support_sizes": [len(s) for s in supps]}, None

# ---------------- section selection ----------------

def pick_sections(Sm, A, B, p, m, seed):
    """Choose t_1..t_{m-1}: nonzero, valid curve x-coord, distinct; prefer lossless
    sections (sectioned support == projection of unsectioned support). Up to 12
    candidates per slot; if none lossless, keep maximal-support candidate."""
    rng = random.Random(int(seed * 10000033 + p * 131 + m))
    # Projection of the unsectioned support onto the first m-1 coordinates.
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

# ---------------- random same-support / dense polynomials ----------------

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

# ---------------- numpy torus counting engine ----------------

def count_torus(polys_monomials, n, p, count_boundary=True):
    """polys_monomials: list of n polys, each a list of ((e_1..e_n), coeff) with
    coeff already reduced mod p. Counts (x_1..x_n) in (F_p^*)^n with all polys 0.
    Also counts solutions with x_1..x_{n-1} != 0, x_n == 0 (boundary).
    All arithmetic mod p in uint32 (values < p^2 + p < 2^21 for p <= 1009)."""
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
        # Safe to skip intermediate mods only if c * prod(powtab values) < 2^32;
        # worst case p^n (c<p, each powtab<p). Guard exactly; else mod each step.
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
    """Reference brute force: full enumeration, polynomial subs. Small cells only."""
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
        # remaining variable g[n-1]; test all u in F_p
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

# ---------------- stage: poly (certificate) ----------------

def stage_poly(out_path, seeds):
    rec = {"stage": "poly", "instances": [], "controls": [], "growth": []}
    Fbig = GF(P_CERT[0])
    for seed in seeds:
        inst = {"seed": seed, "curves": {}, "m": {}}
        # support stability across two large primes
        supps_by_prime = {}
        for p in P_CERT:
            A, B = gen_curve(seed, p)
            inst["curves"][str(p)] = {"A": A, "B": B}
            tp = time.time()
            polys = semaev_polys(A, B, GF(p), 5)
            supps_by_prime[p] = {}
            for m in [3, 4, 5]:
                Sm = polys[m]
                supp_m = supp_of(Sm, m)
                supps_by_prime[p][m] = supp_m
                inst["m"].setdefault(str(m), {})[str(p)] = {
                    "unsectioned_support_size": len(supp_m),
                    "deg_per_var": [int(Sm.degree(Sm.parent().gens()[i])) for i in range(m)],
                    "total_degree": int(Sm.total_degree()),
                    "compute_seconds": round(time.time() - tp, 3),
                }
        # P4: two-prime support stability
        stab = all(supps_by_prime[P_CERT[0]][m] == supps_by_prime[P_CERT[1]][m] for m in [3, 4, 5])
        rec["controls"].append({"id": "P4_two_prime_support_stability", "seed": seed, "pass": bool(stab)})
        # P4b: QQ cross-check for m=3,4 with same integer A,B as p=1000003
        A0, B0 = gen_curve(seed, P_CERT[0])
        tq = time.time()
        qpolys = semaev_polys(A0, B0, QQ, 4)
        q_ok = True
        for m in [3, 4]:
            qsupp = supp_of(qpolys[m], m)
            fsupp = supps_by_prime[P_CERT[0]][m]
            if qsupp != fsupp:
                q_ok = False
                NOTES.append("QQ-vs-Fp support mismatch seed=%d m=%d: |Q|=%d |Fp|=%d" % (seed, m, len(qsupp), len(fsupp)))
        rec["controls"].append({"id": "P4_QQ_support_check", "seed": seed, "m": [3, 4],
                                "pass": bool(q_ok), "seconds": round(time.time() - tq, 3)})
        # canonical sections + MV per m at p=1000003
        polys_big = semaev_polys(A0, B0, Fbig, 5)
        for m in [3, 4, 5]:
            n = m - 1
            Sm = polys_big[m]
            ts, losses, tries, proj_size = pick_sections(Sm, A0, B0, P_CERT[0], m, seed)
            fsec = [section_poly(Sm, t, m) for t in ts]
            tmv = time.time()
            mvres, err = mv_of_polys(fsec, n)
            assert err is None, err
            d_tot = max(int(f.total_degree()) for f in fsec)
            degs_per_var = [int(fsec[0].degree(fsec[0].parent().gens()[i])) for i in range(n)]
            bez_total = d_tot ** n
            from math import factorial
            box = 1
            for v in degs_per_var:
                box *= v
            bez_box = factorial(n) * box
            mvq = QQ(mvres["mv"])
            cell = {
                "seed": seed, "p": P_CERT[0], "m": m, "n": n,
                "targets_t": ts, "section_losses": losses, "section_tries": tries,
                "unsectioned_support": int(mvres["support_sizes"][0]) if False else None,
                "projection_support_size": int(proj_size),
                "section_support_sizes": mvres["support_sizes"],
                "mv_exact": mvres["mv"], "mv_float": mvres["mv_float"],
                "mv_approximate": mvres["approximate"],
                "volume_methods": mvres["method_counts"],
                "subset_vols": mvres["subset_vols"],
                "d_total_sectioned": d_tot, "deg_per_var_sectioned": degs_per_var,
                "bezout_total": int(bez_total), "bezout_box": int(bez_box),
                "ratio_mv_bezout_total": float(mvq / bez_total),
                "ratio_mv_bezout_box": float(mvq / bez_box),
                "mv_seconds": round(time.time() - tmv, 3),
            }
            rec["growth"].append(cell)
            # P2: hand value at m=3
            if m == 3:
                ok = (mvres["support_sizes"] == [9, 9]) and (mvq == 8)
                rec["controls"].append({"id": "P2_hand_value_m3", "seed": seed, "pass": bool(ok),
                                        "support_sizes": mvres["support_sizes"], "mv": mvres["mv"]})
            # N1: random same-support systems -> same MV
            rng = random.Random(int(seed * 10000061 + P_CERT[0] * 137 + m))
            R6 = Sm.parent()
            frnd = [random_poly_on_support(R6, supp_of(fsec[i], n), rng) for i in range(n)]
            mvres2, err2 = mv_of_polys(frnd, n)
            assert err2 is None, err2
            same = (QQ(mvres2["mv"]) == mvq)
            rec["controls"].append({"id": "N1_same_support_MV", "seed": seed, "m": m,
                                    "pass": bool(same), "mv_semaev": mvres["mv"], "mv_random": mvres2["mv"]})
        # unsectioned polytope volumes for m=3,4 (cheap dims)
        for m in [3, 4]:
            n = m
            pts = supps_by_prime[P_CERT[0]][m]
            vol, method, nv = volume_from_support(pts, n)
            inst["m"][str(m)]["unsectioned_polytope_volume"] = str(vol)
            inst["m"][str(m)]["unsectioned_volume_method"] = method
        inst["m"]["5"]["unsectioned_full_box"] = (len(supps_by_prime[P_CERT[0]][5]) == 9**5)
        inst["m"]["4"]["unsectioned_full_box"] = (len(supps_by_prime[P_CERT[0]][4]) == 5**4)
        inst["m"]["3"]["unsectioned_full_box"] = (len(supps_by_prime[P_CERT[0]][3]) == 3**3)
        rec["instances"].append(inst)
    # P1: dense simplex controls (curve-independent), at p=1000003
    p = P_CERT[0]
    for (n, d) in [(2, 2), (2, 4), (3, 4), (4, 8)]:
        rng = random.Random(int(900000000 + n * 1000 + d))
        R = PolynomialRing(GF(p), n, 'y')
        supp = dense_support(n, d)
        pols = [random_poly_on_support(R, supp, rng) for _ in range(n)]
        mvres, err = mv_of_polys(pols, n)
        assert err is None, err
        expect = d ** n
        ok = (QQ(mvres["mv"]) == expect)
        rec["controls"].append({"id": "P1_dense_simplex", "n": n, "d": d, "pass": bool(ok),
                                "mv": mvres["mv"], "expected": expect,
                                "methods": mvres["method_counts"]})
    return rec

# ---------------- stage: counts ----------------

def run_count_cell(seed, p, m, with_neg, with_n2, engine_selfcheck=False, neg_only=False):
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
    if neg_only:
        cnt = {"torus": None, "boundary_xn_zero": None, "outer_points": None}
    else:
        cnt = count_torus(monoms, n, p)
    cell = {
        "seed": seed, "p": p, "m": m, "n": n, "A": A, "B": B,
        "targets_t": ts, "section_losses": losses, "section_tries": tries,
        "projection_support_size": int(proj_size),
        "section_support_sizes": mvres["support_sizes"],
        "mv_exact": mvres["mv"], "mv_float": mvres["mv_float"],
        "mv_approximate": mvres["approximate"],
        "volume_methods": mvres["method_counts"],
        "count_torus": cnt["torus"], "count_boundary_xn_zero": cnt["boundary_xn_zero"],
        "outer_points_enumerated": cnt["outer_points"],
        "bkk_bound_holds": (bool(cnt["torus"] <= mvq) if cnt["torus"] is not None else None),
        "semaev_count_skipped_neg_only": neg_only,
        "count_over_mv": (float(cnt["torus"] / mvq) if (mvq > 0 and cnt["torus"] is not None) else None),
        "mv_seconds": round(time.time() - tmv, 3),
        "count_seconds": round(time.time() - tc, 3),
    }
    if engine_selfcheck:
        naive = count_torus_naive(fsec, n, p)
        cell["engine_selfcheck"] = {"numpy": cnt["torus"], "naive": naive["torus"],
                                    "pass": bool(naive["torus"] == cnt["torus"] and
                                                 naive["boundary_xn_zero"] == cnt["boundary_xn_zero"])}
    out = {"cell": cell, "neg": None, "n2": None}
    if with_neg:
        rng = random.Random(int(seed * 10000061 + p * 137 + m))
        R6 = Sm.parent()
        frnd = [random_poly_on_support(R6, supp_of(fsec[i], n), rng) for i in range(n)]
        mvres2, err2 = mv_of_polys(frnd, n)
        assert err2 is None, err2
        monoms2 = [monom_list(f, n, p) for f in frnd]
        tc2 = time.time()
        cnt2 = count_torus(monoms2, n, p)
        out["neg"] = {
            "mv_exact": mvres2["mv"], "mv_equals_semaev": bool(QQ(mvres2["mv"]) == mvq),
            "count_torus": cnt2["torus"], "count_boundary_xn_zero": cnt2["boundary_xn_zero"],
            "bkk_bound_holds": bool(cnt2["torus"] <= QQ(mvres2["mv"])),
            "count_seconds": round(time.time() - tc2, 3),
        }
    if with_n2:
        f1 = fsec[0]
        rep = [f1] * n
        mvres3, err3 = mv_of_polys(rep, n)
        assert err3 is None, err3
        monoms3 = [monom_list(f1, n, p)] * n
        tc3 = time.time()
        cnt3 = count_torus(monoms3, n, p)
        out["n2"] = {
            "mv_exact": mvres3["mv"], "count_torus": cnt3["torus"],
            "violation_observed_as_expected": bool(cnt3["torus"] > QQ(mvres3["mv"])),
            "count_seconds": round(time.time() - tc3, 3),
        }
    sys.stderr.write("cell done m=%d p=%d seed=%d t=%.1fs\n" % (m, p, seed, elapsed()))
    sys.stderr.flush()
    return out

def stage_counts(out_path, seeds, m_list, p_list, with_neg_seeds, n2_cells, selfcheck, neg_only=False):
    rec = {"stage": "counts", "m_list": m_list, "neg_only": neg_only, "cells": [], "censored": []}
    for m in m_list:
        for p in p_list:
            if m == 5 and p != 101:
                continue  # pre-registered scope (specification.yaml count_scope)
            for seed in seeds:
                if not time_left():
                    rec["censored"].append({"m": m, "p": p, "seed": seed, "reason": "soft budget"})
                    continue
                wneg = seed in with_neg_seeds
                wn2 = (m, p) in n2_cells
                sc = selfcheck and (m, p, seed) == (3, 101, seeds[0])
                r = run_count_cell(seed, p, m, wneg, wn2, engine_selfcheck=sc, neg_only=neg_only)
                rec["cells"].append(r)
    return rec

# ---------------- main ----------------

def main():
    args = sys.argv[1:]
    def getarg(flag, default=None):
        if flag in args:
            i = args.index(flag)
            return args[i + 1]
        return default
    stage = getarg("--stage", "poly")
    out_path = getarg("--out", None)
    seeds = [int(s) for s in getarg("--seeds", ",".join(str(s) for s in SEEDS_DEFAULT)).split(",")]
    with_neg = set(int(s) for s in getarg("--with-neg", "").split(",") if s)
    neg_only = "--neg-only" in args
    commit, dirty = git_info()
    started = now_iso()
    if stage == "poly":
        rec = stage_poly(out_path, seeds)
    elif stage == "counts3":
        rec = stage_counts(out_path, seeds, [3], P_COUNTS, with_neg, n2_cells={(3, 431)}, selfcheck=True, neg_only=neg_only)
    elif stage == "counts4":
        rec = stage_counts(out_path, seeds, [4], P_COUNTS, with_neg, n2_cells={(4, 101)}, selfcheck=False, neg_only=neg_only)
    elif stage == "counts5":
        rec = stage_counts(out_path, seeds, [5], [101], with_neg, n2_cells=set(), selfcheck=False, neg_only=neg_only)
    else:
        raise ValueError("unknown stage %s" % stage)
    commit2, dirty2 = git_info()
    rec["run_meta"] = {
        "stage": stage, "seeds": seeds, "with_neg": sorted(with_neg), "neg_only": neg_only,
        "sage_version": str(subprocess.check_output(["sage", "--version"], text=True).strip()),
        "started_at": started, "finished_at": now_iso(),
        "wall_seconds": round(elapsed(), 3),
        "git_commit": commit2, "git_dirty": dirty2,
        "notes": NOTES,
        "soft_budget_seconds": SOFT_BUDGET,
    }
    data = jsanitize(rec)
    if out_path:
        with open(out_path, "w") as fh:
            json.dump(data, fh, indent=1)
        print("WROTE %s" % out_path)
    print(json.dumps(jsanitize({"stage": stage, "wall_seconds": round(float(elapsed()), 3),
                      "n_cells": len(data.get("cells", data.get("growth", []))),
                      "notes": NOTES})))

main()
