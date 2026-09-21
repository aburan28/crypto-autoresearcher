# EXP-TTN-001 / candidate C2 (ledger family TTN)
# Tensor-network (tree) contraction of the recursive Semaev tensor with rank truncation.
# Measures: exact F_p bond ranks of balanced recursion-tree flattenings of S_m,
# recall of prefix-CUR rank-chi-truncated bond factorizations for solution counting,
# positive controls (S3 baseline, S4 cross-check, CUR exactness, contraction == direct
# definition at every grid tuple), negative controls (random tensors: full rank, recall).
# Deterministic: all randomness via seeded random.Random streams. Run from repo root:
#   sage experiments/EXP-TTN-001/ttn1_semaev_contraction.sage

import json, time, platform, random, sys, signal
import numpy as np

class SageCapTimeout(Exception):
    pass

def _alarm_handler(signum, frame):
    raise SageCapTimeout()

signal.signal(signal.SIGALRM, _alarm_handler)

OUT_PATH = "experiments/EXP-TTN-001/runs/RUN-TTN-001-b/raw.json"
PRIMES = [101, 431, 1009]
MS = [3, 4, 5]
SEEDS = [20260717, 20260718, 20260719]
FB_SIZE = {3: 24, 4: 14, 5: 9}
SIDE = {3: 3, 4: 5, 5: 9}
RECALL_TARGET = 0.99

T0 = time.time()

# ---------------------------------------------------------------- helpers

def inv_table(p):
    inv = [0] * p
    for v in range(1, p):
        inv[v] = pow(v, p - 2, p)
    return inv

def sylvester_det(f, g, p, inv):
    # formal-degree Sylvester resultant; f,g coeff lists descending degree, python ints
    mf, mg = len(f) - 1, len(g) - 1
    n = mf + mg
    M = []
    for i in range(mg):
        r = [0] * n
        for k, c in enumerate(f):
            r[i + k] = c % p
        M.append(r)
    for i in range(mf):
        r = [0] * n
        for k, c in enumerate(g):
            r[i + k] = c % p
        M.append(r)
    det = 1
    for col in range(n):
        piv = -1
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv < 0:
            return 0
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
            det = (-det) % p
        pv = M[col][col]
        det = det * pv % p
        ip = inv[pv]
        Mc = M[col]
        for r in range(col + 1, n):
            fac = M[r][col] * ip % p
            if fac:
                Mr = M[r]
                for cc in range(col + 1, n):
                    Mr[cc] = (Mr[cc] - fac * Mc[cc]) % p
    return det % p

def gen_curve(p, seed):
    rng = random.Random("curve-%d-%d" % (seed, p))
    while True:
        a = rng.randrange(p)
        b = rng.randrange(p)
        if (4 * a * a * a + 27 * b * b) % p != 0:
            return a, b

def gen_fb(p, a, b, m, seed):
    Fp = GF(p)
    avail = []
    for x in range(p):
        if Fp((x * x * x + a * x + b) % p).is_square():
            avail.append(x)
    d = FB_SIZE[m]
    rng = random.Random("fb-%d-%d-%d" % (seed, p, m))
    if len(avail) >= d:
        return sorted(rng.sample(avail, d)), None, len(avail)
    return sorted(avail), "fb_shortfall requested=%d got=%d" % (d, len(avail)), len(avail)

def s3_symbolic(R, u, v, w, a, b):
    return (u - v)**2 * w**2 - 2 * ((u + v) * (u * v + a) + 2 * b) * w + (u * v - a)**2 - 4 * b * (u + v)

def build_Sm(p, a, b, m):
    # returns (S_m symbolic over GF(p), ring, total ring vars, wall seconds, censored flag)
    Fp = GF(p)
    t0 = time.time()
    censored = False
    if m == 3:
        R = PolynomialRing(Fp, names=['x1', 'x2', 'x3'])
        x1, x2, x3 = R.gens()
        S = s3_symbolic(R, x1, x2, x3, a, b)
        nvars = 3
    elif m == 4:
        R = PolynomialRing(Fp, names=['x1', 'x2', 'x3', 'x4', 'X'])
        x1, x2, x3, x4, X = R.gens()
        S = s3_symbolic(R, x1, x2, X, a, b).resultant(s3_symbolic(R, X, x3, x4, a, b), X)
        nvars = 5
    else:
        R = PolynomialRing(Fp, names=['x1', 'x2', 'x3', 'x4', 'x5', 'X', 'Z'])
        x1, x2, x3, x4, x5, X, Z = R.gens()
        S4 = s3_symbolic(R, X, x3, Z, a, b).resultant(s3_symbolic(R, Z, x4, x5, a, b), Z)
        nvars = 7
        try:
            signal.alarm(300)
            S = s3_symbolic(R, x1, x2, X, a, b).resultant(S4, X)
            signal.alarm(0)
        except SageCapTimeout:
            signal.alarm(0)
            S = None
            censored = True
    return S, R, nvars, time.time() - t0, censored

def tensor_from_poly(S, m, n, nvars):
    T = np.zeros((n,) * m, dtype=np.int64)
    for mono, coeff in S.dict().items():
        for k in range(m, nvars):
            assert mono[k] == 0, "eliminated variable survives"
        T[tuple(int(e) for e in mono[:m])] = int(coeff)
    return T

def flatten(T, left_axes):
    m = T.ndim
    right = [ax for ax in range(m) if ax not in left_axes]
    P = np.transpose(T, axes=list(left_axes) + right)
    sL = 1
    for a in left_axes:
        sL *= T.shape[a]
    sR = int(P.size // sL)
    return P.reshape(sL, sR), right

def unflatten(Marr, T_shape, left_axes, right):
    shp = [T_shape[a] for a in left_axes] + [T_shape[a] for a in right]
    P = Marr.reshape(shp)
    order = list(left_axes) + right
    inv_order = [order.index(ax) for ax in range(len(order))]
    return np.transpose(P, axes=inv_order)

def sage_rank(arr, p):
    return matrix(GF(p), [[int(v) % p for v in row] for row in arr]).rank()

def cur_pivots(M):
    # deterministic Gaussian elimination (first available row per column).
    # Prefix property: M[pr[:k], pc[:k]] is invertible for every k.
    A, B = M.nrows(), M.ncols()
    Mc = copy(M)
    pr, pc = [], []
    used = set()
    for j in range(B):
        piv = None
        for i in range(A):
            if i not in used and Mc[i, j] != 0:
                piv = i
                break
        if piv is None:
            continue
        pr.append(piv)
        pc.append(j)
        used.add(piv)
        invv = Mc[piv, j]**-1
        for r in range(A):
            if r != piv and Mc[r, j] != 0:
                Mc[r, :] -= Mc[r, j] * invv * Mc[piv, :]
    return pr, pc

def cur_truncate(M, pr, pc, chi):
    R = pr[:chi]
    C = pc[:chi]
    Mhat = M.matrix_from_columns(C) * M.matrix_from_rows_and_columns(R, C).inverse() * M.matrix_from_rows(R)
    return np.array([[int(v) for v in row] for row in Mhat.rows()], dtype=np.int64)

def contract_eval(T, V, p):
    # contract original axes from last to first; tensordot appends V's grid axis
    # at the end, so position k always still holds original axis k. Result (d,)*m
    # with axes in original variable order.
    E = T
    for k in range(T.ndim - 1, -1, -1):
        E = np.tensordot(E, V, axes=([k], [1])) % p
    return E

def s3_coeff_arrays(X1, X2, a, b, p):
    # vectorized coefficients of S3(x1,x2,X); int64-safe for p < 2^21
    c2 = (X1 - X2) ** 2 % p
    c1 = (-2 * ((X1 + X2) * (X1 * X2 + a) + 2 * b)) % p
    c0 = ((X1 * X2 - a) ** 2 - 4 * b * (X1 + X2)) % p
    return c0, c1, c2

def direct_eval_tensor(m, p, a, b, fb, T4, inv):
    # independent path: per-tuple formal Sylvester resultant (m=4,5) / closed form (m=3)
    d = len(fb)
    n = SIDE[m]
    XA = np.array(fb, dtype=np.int64)
    if m == 3:
        X1, X2, X3 = np.meshgrid(XA, XA, XA, indexing='ij')
        E = ((X1 - X2) ** 2 * X3 ** 2
             - 2 * ((X1 + X2) * (X1 * X2 + a) + 2 * b) * X3
             + (X1 * X2 - a) ** 2 - 4 * b * (X1 + X2)) % p
        return E.astype(np.int64)
    if m == 4:
        c0, c1, c2 = s3_coeff_arrays(XA[:, None], XA[None, :], a, b, p)
        e0, e1, e2 = c0.copy(), c1.copy(), c2.copy()
        E = np.zeros((d, d, d, d), dtype=np.int64)
        for i1 in range(d):
            for i2 in range(d):
                f = [int(c2[i1, i2]), int(c1[i1, i2]), int(c0[i1, i2])]
                for i3 in range(d):
                    for i4 in range(d):
                        g = [int(e2[i3, i4]), int(e1[i3, i4]), int(e0[i3, i4])]
                        E[i1, i2, i3, i4] = sylvester_det(f, g, p, inv)
        return E
    # m == 5
    V5 = np.zeros((d, 5), dtype=np.int64)
    for j in range(d):
        v = 1
        for e in range(5):
            V5[j, e] = v
            v = v * XA[j] % p
    G = T4
    for _ in range(3):
        G = np.tensordot(V5, G, axes=([1], [3])) % p   # -> (d3,d4,d5, Xcoeff)
    c0, c1, c2 = s3_coeff_arrays(XA[:, None], XA[None, :], a, b, p)
    E = np.zeros((d, d, d, d, d), dtype=np.int64)
    for i1 in range(d):
        for i2 in range(d):
            f = [int(c2[i1, i2]), int(c1[i1, i2]), int(c0[i1, i2])]
            for i3 in range(d):
                for i4 in range(d):
                    for i5 in range(d):
                        g = [int(G[i3, i4, i5, k]) for k in (4, 3, 2, 1, 0)]
                        E[i1, i2, i3, i4, i5] = sylvester_det(f, g, p, inv)
    return E

def fit_slope(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    return None if den == 0 else num / den

def log2(x):
    return float(log(RR(x), 2))

def sanitize(o):
    if isinstance(o, dict):
        return {str(k): sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if o is None or isinstance(o, (int, float, str)):
        return o
    try:
        f = float(o)   # sage Integer / RealDoubleElement and friends
        i = int(o)
        return i if f == i else f
    except Exception:
        return str(o)

# ---------------------------------------------------------------- main

result = {
    "experiment_id": "EXP-TTN-001",
    "run_id": "RUN-TTN-001-a",
    "parameters": {"primes": PRIMES, "m_values": MS, "seeds": SEEDS,
                   "fb_size_by_m": {str(k): v for k, v in FB_SIZE.items()},
                   "recall_target": RECALL_TARGET,
                   "bond_family": "balanced split {x1..x_floor(m/2)}|rest; m=5 child {x1,x2,x3}|{x4,x5}; {x1}|rest context"},
    "cells": [],
    "deviations": [],
}

p1_fail = []

for p in PRIMES:
    inv = inv_table(p)
    Fp = GF(p)
    for seed in SEEDS:
        a, b = gen_curve(p, seed)
        E_curve = EllipticCurve(Fp, [a, b])
        # ---- P1: S3 baseline on 20 random point pairs
        rng1 = random.Random("p1-%d-%d" % (seed, p))
        ok1 = 0
        tries = 0
        while ok1 < 20 and tries < 400:
            tries += 1
            def rand_pt():
                while True:
                    x = rng1.randrange(p)
                    rhs = (x * x * x + a * x + b) % p
                    if Fp(rhs).is_square():
                        return E_curve(x, Fp(rhs).sqrt())
            P = rand_pt()
            Q = rand_pt()
            Rpt = -(P + Q)
            c0, c1, c2 = s3_coeff_arrays(np.int64(P[0]), np.int64(Q[0]), a, b, p)
            val = (int(c2) * pow(int(Rpt[0]), 2, p) + int(c1) * int(Rpt[0]) + int(c0)) % p
            if val == 0:
                ok1 += 1
            else:
                p1_fail.append({"p": p, "seed": seed, "P": str(P), "Q": str(Q)})
        p1_ok = (ok1 == 20)

        for m in MS:
            cell = {"p": p, "seed": seed, "m": m}
            tcell = time.time()
            # ---- factor base
            fb, dev, n_avail = gen_fb(p, a, b, m, seed)
            cell["curve"] = {"a": a, "b": b, "n_xcoords_available": n_avail}
            cell["fb_size"] = len(fb)
            if dev:
                cell["deviation"] = dev
                result["deviations"].append({"p": p, "seed": seed, "m": m, "dev": dev})
            d = len(fb)
            n = SIDE[m]
            # ---- symbolic S_m + tensor (dense baseline)
            S, R, nvars, t_dense, censored = build_Sm(p, a, b, m)
            cell["t_dense_symbolic_s"] = t_dense
            cell["dense_censored_300s"] = censored
            if censored:
                cell["valid"] = False
                cell["invalid_reason"] = "failed_infrastructure: symbolic S5 exceeded 300 s cap"
                result["cells"].append(cell)
                continue
            cell["n_terms"] = len(S.monomials())
            t0 = time.time()
            T = tensor_from_poly(S, m, n, nvars)
            cell["t_tensor_extract_s"] = time.time() - t0
            # ---- P4: contraction == direct definition on every grid tuple
            XA = np.array(fb, dtype=np.int64)
            V = np.zeros((d, n), dtype=np.int64)
            for j in range(d):
                v = 1
                for e in range(n):
                    V[j, e] = v
                    v = v * XA[j] % p
            t0 = time.time()
            E_contract = contract_eval(T, V, p)
            cell["t_contract_full_s"] = time.time() - t0
            t0 = time.time()
            T4 = None
            if m == 5:
                S4poly, R4, nv4, _, _ = build_Sm(p, a, b, 4)
                T4 = tensor_from_poly(S4poly, 4, 5, nv4)
            E_direct = direct_eval_tensor(m, p, a, b, fb, T4, inv)
            cell["t_direct_verify_s"] = time.time() - t0
            mism = int((E_contract != E_direct).sum())
            cell["P4_contraction_eq_direct"] = (mism == 0)
            cell["P4_mismatches"] = mism
            Z = (E_contract == 0)
            exact_count = int(Z.sum())
            cell["exact_count"] = exact_count
            # ---- P2: S4 definition cross-check (m=4 cells)
            if m == 4:
                rng2 = random.Random("p2-%d-%d-%d" % (seed, p, m))
                ok2 = 0
                for _ in range(200):
                    pt = [rng2.randrange(p) for _ in range(4)]
                    sval = int(S.subs({R.gens()[i]: pt[i] for i in range(4)}))
                    c0v, c1v, c2v = s3_coeff_arrays(np.int64(pt[0]), np.int64(pt[1]), a, b, p)
                    e0v, e1v, e2v = s3_coeff_arrays(np.int64(pt[2]), np.int64(pt[3]), a, b, p)
                    dval = sylvester_det([int(c2v), int(c1v), int(c0v)],
                                         [int(e2v), int(e1v), int(e0v)], p, inv)
                    if sval % p == dval % p:
                        ok2 += 1
                cell["P2_S4_crosscheck"] = (ok2 == 200)
                cell["P2_agreements"] = ok2
            # ---- bonds
            if m == 3:
                bond_spec = {"growth": [0]}
                context_spec = {}
            elif m == 4:
                bond_spec = {"growth": [0, 1]}
                context_spec = {"single_var": [0]}
            else:
                bond_spec = {"growth": [0, 1], "child": [0, 1, 2]}
                context_spec = {"single_var": [0]}
            cell["bonds"] = {}
            cell["P3_cur_exact_all"] = True
            for bname, laxes in list(bond_spec.items()) + list(context_spec.items()):
                Mflat, right = flatten(T, laxes)
                Mrank = sage_rank(Mflat, p)
                rec = {"left_axes": laxes, "shape": [int(Mflat.shape[0]), int(Mflat.shape[1])],
                       "rank": int(Mrank), "full_dim": int(min(Mflat.shape))}
                Msage = matrix(GF(p), [[int(v) % p for v in row] for row in Mflat])
                pr, pc = cur_pivots(Msage)
                assert len(pr) == Mrank, "pivot count != rank"
                # P3: CUR exact at full rank
                That = cur_truncate(Msage, pr, pc, Mrank)
                if not np.array_equal(unflatten(That, T.shape, laxes, right) % p, T % p):
                    cell["P3_cur_exact_all"] = False
                # recall curve on growth/child bonds with true solutions present
                if bname in bond_spec and exact_count > 0:
                    curve_pts = []
                    for chi in range(1, Mrank + 1):
                        Mh = cur_truncate(Msage, pr, pc, chi)
                        Th = unflatten(Mh, T.shape, laxes, right) % p
                        Eh = contract_eval(Th.astype(np.int64), V, p)
                        Zh = (Eh == 0)
                        found = int((Zh & Z).sum())
                        fpos = int((Zh & ~Z).sum())
                        curve_pts.append({"chi": chi, "recall": found / exact_count,
                                          "found": found, "true": exact_count,
                                          "false_pos": fpos})
                    rec["recall_curve"] = curve_pts
                cell["bonds"][bname] = rec
            # ---- negative control: random tensor, same shape
            rngn = random.Random("neg-%d-%d-%d" % (seed, p, m))
            Trand = np.array([rngn.randrange(p) for _ in range(int(T.size))],
                             dtype=np.int64).reshape(T.shape)
            laxes = bond_spec["growth"]
            Mr_flat, Mr_right = flatten(Trand, laxes)
            Mr_rank = sage_rank(Mr_flat, p)
            neg = {"growth_bond_rank": int(Mr_rank), "full_dim": int(min(Mr_flat.shape))}
            if Mr_rank < min(Mr_flat.shape):
                # chance deficiency (rate ~1/p): one documented deterministic redraw
                rngn2 = random.Random("neg2-%d-%d-%d" % (seed, p, m))
                Trand = np.array([rngn2.randrange(p) for _ in range(int(T.size))],
                                 dtype=np.int64).reshape(T.shape)
                Mr_flat, Mr_right = flatten(Trand, laxes)
                Mr_rank = sage_rank(Mr_flat, p)
                neg["redrawn"] = True
                neg["growth_bond_rank_redraw"] = int(Mr_rank)
            neg["N1_full_rank"] = bool(Mr_rank == min(Mr_flat.shape))
            Msage_r = matrix(GF(p), [[int(v) % p for v in row] for row in Mr_flat])
            prr, pcr = cur_pivots(Msage_r)
            That_r = cur_truncate(Msage_r, prr, pcr, Mr_rank)
            neg["P3_cur_exact_random"] = bool(np.array_equal(
                unflatten(That_r, Trand.shape, laxes, Mr_right) % p, Trand % p))
            # random recall at Semaev full-rank chi (and its own chi if larger not needed)
            chi_matched = int(cell["bonds"]["growth"]["rank"])
            Zr = (contract_eval(Trand, V, p) == 0)
            true_r = int(Zr.sum())
            neg["random_exact_count"] = true_r
            if true_r > 0:
                Mh_r = cur_truncate(Msage_r, prr, pcr, chi_matched)
                Th_r = unflatten(Mh_r, Trand.shape, laxes, Mr_right) % p
                Zh_r = (contract_eval(Th_r.astype(np.int64), V, p) == 0)
                neg["recall_at_semaev_full_chi"] = int((Zh_r & Zr).sum()) / true_r
                neg["chi_matched"] = chi_matched
            cell["negative_control"] = neg
            cell["P1_S3_baseline"] = p1_ok
            cell["t_cell_s"] = time.time() - tcell
            result["cells"].append(cell)
            print("cell p=%d seed=%d m=%d done: rank(growth)=%s count=%d t=%.1fs" %
                  (p, seed, m, str(cell["bonds"]["growth"]["rank"]), exact_count, cell["t_cell_s"]))
            sys.stdout.flush()

# ---------------------------------------------------------------- summary / fits
summary = {"per_p_m": [], "controls": {}}
for p in PRIMES:
    for m in MS:
        cells = [c for c in result["cells"] if c["p"] == p and c["m"] == m and "bonds" in c]
        ranks = sorted(c["bonds"]["growth"]["rank"] for c in cells)
        chi_full_med = ranks[len(ranks) // 2]
        # pooled recall per chi
        pool = {}
        tot_true = 0
        for c in cells:
            rc = c["bonds"]["growth"].get("recall_curve")
            if rc:
                tot_true += rc[-1]["true"]
                for pt in rc:
                    pool.setdefault(pt["chi"], [0, 0])
                    pool[pt["chi"]][0] += pt["found"]
                    pool[pt["chi"]][1] += pt["true"]
        chi_needed = None
        pooled_curve = []
        if tot_true > 0:
            for chi in sorted(pool):
                rec = pool[chi][0] / pool[chi][1]
                pooled_curve.append({"chi": chi, "pooled_recall": rec,
                                     "found": pool[chi][0], "true": pool[chi][1]})
                if chi_needed is None and rec >= RECALL_TARGET:
                    chi_needed = chi
        summary["per_p_m"].append({
            "p": p, "m": m, "d_degree": 2 ** (m - 2),
            "chi_full_per_seed": ranks, "chi_full_median": chi_full_med,
            "chi_needed_pooled": chi_needed,
            "pooled_recall_curve": pooled_curve,
            "exact_counts_per_seed": [c["exact_count"] for c in cells],
            "t_dense_symbolic_s": [float(c["t_dense_symbolic_s"]) for c in cells],
            "n_terms": [c["n_terms"] for c in cells],
            "neg_rank": [c["negative_control"]["growth_bond_rank"] for c in cells],
            "neg_full_dim": cells[0]["negative_control"]["full_dim"],
            "neg_recall_at_semaev_full_chi": [c["negative_control"].get("recall_at_semaev_full_chi") for c in cells],
        })

# growth exponent alpha per p (balanced-split family, m in {3,4,5}, d = 2^(m-2))
fits = []
for p in PRIMES:
    rows = [r for r in summary["per_p_m"] if r["p"] == p]
    xs = [log2(r["d_degree"]) for r in rows]
    ys_full = [log2(r["chi_full_median"]) for r in rows]
    alpha_full = fit_slope(xs, ys_full)
    need = [r["chi_needed_pooled"] for r in rows]
    alpha_need = fit_slope(xs, [log2(v) for v in need]) if all(need) else None
    # two-point root-bond-only slope (m=4 -> m=5)
    alpha_root2 = (log2(rows[2]["chi_full_median"]) - log2(rows[1]["chi_full_median"]))
    fits.append({"p": p, "alpha_chi_full_vs_degree": alpha_full,
                 "alpha_chi_needed_vs_degree": alpha_need,
                 "alpha_rootbond_twopoint_m4_m5": alpha_root2,
                 "points": [(r["d_degree"], r["chi_full_median"], r["chi_needed_pooled"]) for r in rows]})
# field-size dependence beta per m
betas = []
for m in MS:
    rows = [r for r in summary["per_p_m"] if r["m"] == m]
    xs = [log2(r["p"]) for r in rows]
    ys = [log2(r["chi_full_median"]) for r in rows]
    betas.append({"m": m, "beta_chi_full_vs_logp": fit_slope(xs, ys)})
summary["fits"] = fits
summary["betas_field_size"] = betas

# controls rollup
allcells = [c for c in result["cells"] if "bonds" in c]
summary["controls"] = {
    "P1_S3_baseline_all": all(c["P1_S3_baseline"] for c in allcells),
    "P2_S4_crosscheck_all": all(c.get("P2_S4_crosscheck", True) for c in allcells),
    "P3_cur_exact_all": all(c["P3_cur_exact_all"] for c in allcells) and
                        all(c["negative_control"]["P3_cur_exact_random"] for c in allcells),
    "P4_contraction_eq_direct_all": all(c["P4_contraction_eq_direct"] for c in allcells),
    "N1_random_full_rank_all": all(c["negative_control"]["N1_full_rank"] for c in allcells),
    "p1_failures": p1_fail,
}
summary["n_cells"] = len(allcells)
summary["n_cells_censored"] = len([c for c in result["cells"] if c.get("dense_censored_300s")])
summary["wall_seconds_script"] = time.time() - T0
summary["sage_version"] = str(sage.version.version)
summary["python_version"] = platform.python_version()
summary["platform"] = platform.platform()
summary["numpy_version"] = np.__version__
result["summary"] = summary

with open(OUT_PATH, "w") as fh:
    json.dump(sanitize(result), fh, indent=1)
print("WROTE %s  cells=%d  wall=%.1fs" % (OUT_PATH, len(allcells), summary["wall_seconds_script"]))
