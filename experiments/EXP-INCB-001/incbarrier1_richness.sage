# EXP-INCB-001 executor: candidate D3 -- incidence-richness ceiling for EC chord arrangements.
# For p in {211,1009,4099}: one seeded ordinary toy curve; B grid = round_half_up of
# n^(1/4), n^(1/3), n^(2/5), deduped, B >= 8 (A2 rule). FB = x-set of size B; point set =
# ALL lifts (both +/- y), M = 2B. Arrangement = all distinct lines through pairs of
# distinct points (verticals included, tangents excluded). c_r = # lines with exactly r
# points. tau_hat = - OLS slope of log c_r vs log r over {r>=2: c_r>0} (null if <2 points).
# Controls per instance (matched M): uniform random points (negative null; exact
# first-moment check) and deterministic integer grid (positive sensitivity control).
# Seeds 20260717..20260722. Deterministic. JSON to stdout; progress to stderr.
import time, json, sys
from math import log, sqrt, ceil, comb

PRIMES = [211, 1009, 4099]
SEEDS = [20260717, 20260718, 20260719, 20260720, 20260721, 20260722]
CURVE_SEED = 20260717
RAND_SEED_OFFSET = 10**9

def round_half_up(x):
    return int(x + 0.5)

def b_grid(n):
    vals = sorted(set(round_half_up(n ** f) for f in (0.25, 1.0 / 3.0, 0.4)))
    return [b for b in vals if b >= 8]

def make_curve(p):
    F = GF(p); set_random_seed(CURVE_SEED)
    while True:
        a = F(randint(1, p - 1)); b = F(randint(1, p - 1))
        if 4 * a**3 + 27 * b**2 != 0:
            E = EllipticCurve(F, [a, b])
            n = int(E.order())
            if (p + 1 - n) % p != 0:        # ordinary: trace != 0 mod p
                return E, n, int(a), int(b)

def lifting_x_count(E):
    F = E.base_field(); cnt = 0
    for x in F:
        try:
            E.lift_x(x); cnt += 1
        except Exception:
            pass
    return cnt

def ec_points(E, B, seed):
    F = E.base_field(); p = int(F.characteristic())
    set_random_seed(seed)
    xs = []; seen = set()
    while len(xs) < B:
        xi = randint(0, p - 1)
        if xi in seen: continue
        seen.add(xi)
        try:
            E.lift_x(F(xi))
        except Exception:
            continue
        xs.append(xi)
    pts = set()
    for xi in xs:
        P = E.lift_x(F(xi))
        pts.add((int(P[0]), int(P[1])))
        Q = -P
        pts.add((int(Q[0]), int(Q[1])))
    return sorted(pts), xs

def random_points(p, M, seed):
    set_random_seed(seed)
    pts = set()
    while len(pts) < M:
        pts.add((randint(0, p - 1), randint(0, p - 1)))
    return sorted(pts)

def grid_points(p, M):
    a = int(ceil(sqrt(M)))
    pts = []
    for j in range(a):
        for i in range(a):
            pts.append((i, j))
            if len(pts) >= M: return pts
    return pts

def richness(pts, p):
    F = GF(p)
    line_set = {}
    m = len(pts)
    for i in range(m):
        x1, y1 = pts[i]
        for j in range(i + 1, m):
            x2, y2 = pts[j]
            if x1 == x2:
                key = (1, 0, x1)                          # vertical: x = x1
            else:
                s = (F(y2) - F(y1)) / (F(x2) - F(x1))
                c = F(y1) - s * F(x1)
                key = (0, int(s), int(c))                 # y = s*x + c
            line_set[key] = True
    hist = {}; total_inc = 0
    for key in line_set:
        if key[0] == 1:
            cnt = sum(1 for (x, y) in pts if x == key[2])
        else:
            s = F(key[1]); c = F(key[2])
            cnt = sum(1 for (x, y) in pts if F(y) == s * F(x) + c)
        hist[cnt] = hist.get(cnt, 0) + 1
        total_inc += cnt
    return hist, len(line_set), total_inc

def fit_tau(hist):
    rs = sorted(r for r, c in hist.items() if r >= 2 and c > 0)
    if len(rs) < 2: return None
    xs = [log(float(r)) for r in rs]
    ys = [log(float(hist[r])) for r in rs]
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0.0: return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return -(sxy / sxx)

def stats(vals):
    k = len(vals)
    if k == 0: return {"k": 0, "mean": None, "sd": None, "se": None}
    m = sum(vals) / k
    if k == 1: return {"k": 1, "mean": m, "sd": None, "se": None}
    sd = sqrt(sum((v - m) ** 2 for v in vals) / (k - 1))
    return {"k": k, "mean": m, "sd": sd, "se": sd / sqrt(k)}

def zsep(a, b):
    if a["mean"] is None or b["mean"] is None: return None
    if a["se"] in (None, 0) or b["se"] in (None, 0): return None
    return abs(a["mean"] - b["mean"]) / sqrt(a["se"] ** 2 + b["se"] ** 2)

def main():
    t_start = time.time()
    out = {
        "experiment": "EXP-INCB-001", "hypothesis_id": "H-INCB-001",
        "script": "experiments/EXP-INCB-001/incbarrier1_richness.sage",
        "python": sys.version.split()[0],
        "sage_version": None,
        "primes": PRIMES, "seeds": SEEDS, "curve_seed": CURVE_SEED,
        "rand_seed_offset": RAND_SEED_OFFSET,
        "b_grid_rule": "round_half_up(n^1/4), round_half_up(n^1/3), round_half_up(n^2/5); dedupe; keep >= 8",
        "fb_semantics": "x-set of size B; point set = all lifts (+/- y); M = 2B unless y=0 hit",
        "arrangement": "all distinct lines through pairs of distinct points; verticals included; tangents excluded",
        "exponent_fit": "tau = - OLS slope of log c_r vs log r over {r>=2: c_r>0}; null if <2 support points",
        "curves": [], "cells": []
    }
    try:
        from sage.env import SAGE_VERSION
        out["sage_version"] = str(SAGE_VERSION)
    except Exception:
        pass
    for p in PRIMES:
        E, n, ai, bi = make_curve(p)
        L = lifting_x_count(E)
        Bs = b_grid(n)
        out["curves"].append({"p": p, "a": ai, "b": bi, "n": n, "trace": p + 1 - n,
                              "lifting_x": L, "b_grid": [int(b) for b in Bs]})
        print(f"p={p} a={ai} b={bi} n={n} trace={p+1-n} lifting_x={L} B_grid={Bs}",
              file=sys.stderr, flush=True)
        for B in Bs:
            cell = {"p": p, "B": int(B), "instances": []}
            for seed in SEEDS:
                pts_ec, xs = ec_points(E, B, seed)
                M = len(pts_ec)
                fam_pts = [("ec", pts_ec),
                           ("random", random_points(p, M, seed + RAND_SEED_OFFSET)),
                           ("grid", grid_points(p, M))]
                for fam, pts in fam_pts:
                    t0 = time.time()
                    hist, nl, inc = richness(pts, p)
                    tau = fit_tau(hist)
                    T = sum(c * comb(r, 3) for r, c in hist.items() if r >= 3)
                    inst = {"seed": seed, "family": fam, "M": len(pts),
                            "num_lines": nl,
                            "hist": {str(r): hist[r] for r in sorted(hist)},
                            "max_richness": max(hist) if hist else 0,
                            "total_incidences": inc, "triples_T": int(T),
                            "tau": tau,
                            "wall_ms": round(float(time.time() - t0) * 1000.0, 3)}
                    if fam == "random":
                        inst["pred_T_random"] = comb(M, 3) * (p - 2) / float(p * p - 2)
                    if fam == "ec":
                        inst["pred_c3_ec"] = comb(M, 2) * (B / float(L)) / 3.0
                        inst["x_set"] = [int(v) for v in xs]
                    cell["instances"].append(inst)
                print(f"p={p} B={B} seed={seed} M={M} done", file=sys.stderr, flush=True)
            summ = {"p": p, "B": int(B)}
            for fam in ("ec", "random", "grid"):
                fi = [i for i in cell["instances"] if i["family"] == fam]
                taus = [i["tau"] for i in fi if i["tau"] is not None]
                summ[fam] = {
                    "tau": stats(taus), "tau_n_null": len(fi) - len(taus),
                    "c3": stats([float(i["hist"].get("3", 0)) for i in fi]),
                    "T": stats([float(i["triples_T"]) for i in fi]),
                    "num_lines": stats([float(i["num_lines"]) for i in fi]),
                    "max_richness": stats([float(i["max_richness"]) for i in fi]),
                    "total_incidences": stats([float(i["total_incidences"]) for i in fi]),
                }
            preds_T = [i["pred_T_random"] for i in cell["instances"] if i["family"] == "random"]
            preds_c3 = [i["pred_c3_ec"] for i in cell["instances"] if i["family"] == "ec"]
            summ["predictions"] = {
                "pred_T_random_mean": sum(preds_T) / len(preds_T),
                "pred_c3_ec_mean": sum(preds_c3) / len(preds_c3),
            }
            summ["z_ec_vs_random"] = zsep(summ["ec"]["tau"], summ["random"]["tau"])
            summ["z_grid_vs_random"] = zsep(summ["grid"]["tau"], summ["random"]["tau"])
            nc = {"pred_T_random_mean": summ["predictions"]["pred_T_random_mean"],
                  "measured_T_mean": summ["random"]["T"]["mean"],
                  "measured_T_se": summ["random"]["T"]["se"],
                  "within_3se": None}
            if nc["measured_T_mean"] is not None and nc["measured_T_se"] not in (None, 0):
                nc["deviation_se"] = abs(nc["measured_T_mean"] - nc["pred_T_random_mean"]) / nc["measured_T_se"]
                nc["within_3se"] = bool(nc["deviation_se"] <= 3)
            summ["negative_control"] = nc
            m_ec = summ["ec"]["c3"]["mean"]; m_rd = summ["random"]["c3"]["mean"]
            summ["excess_ratio_c3_ec_over_random"] = (m_ec / m_rd) if (m_ec is not None and m_rd) else None
            cell["summary"] = summ
            out["cells"].append(cell)
    gate_cells = []
    for c in out["cells"]:
        z = c["summary"]["z_ec_vs_random"]
        gate_cells.append({"p": c["p"], "B": c["B"], "z_ec_vs_random": z,
                           "gt3": bool(z is not None and z > 3)})
    out["gate"] = {
        "definition": "z = |mean_tau_ec - mean_tau_random| / sqrt(se_ec^2 + se_random^2); candidate D3 promotion gate: z > 3 at all three sizes p",
        "per_cell": gate_cells,
        "per_p_min_z": {str(p): min([g["z_ec_vs_random"] for g in gate_cells if g["p"] == p and g["z_ec_vs_random"] is not None] or [None]) for p in PRIMES},
        "all_sizes_gt3": bool(all(g["gt3"] for g in gate_cells)) if gate_cells else None,
    }
    out["wall_seconds_total"] = round(float(time.time() - t_start), 3)
    def _ser(o):
        import numbers
        if isinstance(o, numbers.Integral): return int(o)
        try: return float(o)
        except Exception: return str(o)
    print(json.dumps(out, default=_ser))

main()
