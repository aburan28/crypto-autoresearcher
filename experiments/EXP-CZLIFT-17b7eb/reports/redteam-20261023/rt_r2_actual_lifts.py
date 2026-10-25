"""R2: exact nulls conditioned on the ACTUAL sampled curve lifts.

run.py measure_curve builds the full lift list (lift_classes) from rng = Random(seed*1_000_003 + p)
before any point is drawn, so the lift coefficients are regenerated here from run.py's draw order
alone (no harness import).  Validation: per-lift class and v_p(Delta j) must equal the rows'
recorded class and v_dj (rows are stored lift by lift, 36 per lift), and the D=-43 p=11 boundary
draws must equal the validator's (r1, r2) = (1, 8) [seed 20261009] and (9, 6) [seed 20261010].

For each actual degenerate lift, exact success probability over uniform P != O and d in [2, p-2]:
naive and teichmuller exhaustively; hensel_random exhaustively over (eps_P, eps_Q) for p <= 43,
else 1/(p+1).  Then observed vs exact expected success counts (frozen/CORR definition: all v>=2 rows).
"""
import json, math, random, sys
from collections import Counter
import numpy as np
sys.path.insert(0, '.')
from rt_padic import *

K = 8
curves = json.load(open('curves_from_raw.json'))
RUNS = {20261009: "../../runs/RUN-CZLIFT-041d05/raw-result.json",
        20261010: "../../runs/RUN-CZLIFT-6709c9/raw-result.json"}


def lift_classes(p, A, B, j_cm, rng, per_class=2):  # transcribed from run.py (read scope)
    out = [("canonical", A, B, None)]
    for _ in range(per_class):
        t = rng.randrange(1, p)
        s = 1 + p * t
        out.append(("isomorphic", A * s * s, B * s * s * s, (t,)))
    for _ in range(per_class):
        if j_cm == 0:
            r1 = rng.randrange(1, p); r2 = rng.randrange(0, p)
            out.append(("pert_p", p * r1, B + p * r2, (r1, r2)))
            r1b = rng.randrange(1, p); r2b = rng.randrange(0, p)
            out.append(("pert_p2", p * p * r1b, B + p * r2b, (r1b, r2b)))
        else:
            r1 = rng.randrange(1, p); r2 = rng.randrange(1, p)
            out.append(("pert_p", A + p * r1, B + p * r2, (r1, r2)))
            r1b = rng.randrange(1, p); r2b = rng.randrange(1, p)
            out.append(("pert_p2", A + p * p * r1b, B + p * p * r2b, (r1b, r2b)))
    return out


def tables(p, A2, B2, L, section, eps_list=(0,)):
    E = ZpK(p, K, A2, B2)
    T = []
    for k in range(1, p):
        row = []
        for eps in eps_list:
            z = E.z_mult(p, E.lift(L[k], section, eps))
            vv = vp(z, p, K)
            row.append((vv, (z // p ** vv) % p if vv < K else -1))
        T.append(row)
    return T


def exact_rate(p, T):
    succ = 0.0
    for d in range(2, p - 1):
        for k in range(1, p):
            q = d * k % p
            cQ = Counter(T[q - 1])
            nP = len(T[k - 1])
            s = 0
            for (vv, uu) in T[k - 1]:
                if vv < K:
                    s += cQ.get((vv, d * uu % p), 0)
            succ += s / (nP * len(T[q - 1]))
    return succ / ((p - 1) * (p - 3))


rate_cache = {}
validation = {"class_vdj_mismatch": 0, "lifts_checked": 0, "boundary_draws": []}
obs = {}
for seed, path in RUNS.items():
    raw = json.load(open(path))
    rows_by_p = {(c["D"], c["p"]): c["rows"] for c in raw["raw"]["curves"]}
    acc = {}
    for c in curves:
        p, A, B, jcm, D, e = c["p"], c["A"], c["B"], c["j_cm"], c["D"], c["e"]
        rng = random.Random(seed * 1_000_003 + p)
        lifts = lift_classes(p, A, B, jcm, rng)
        rows = rows_by_p[(D, p)]
        assert len(rows) == 36 * len(lifts)
        L, N = cyclic_enumeration(p, A % p, B % p)
        for i, (cls, A2, B2, draw) in enumerate(lifts):
            blk = rows[36 * i: 36 * (i + 1)]
            vdj = vp_frac(j_inv(A2, B2) - jcm, p)
            vdj_rec = blk[0]["v_dj"]
            validation["lifts_checked"] += 1
            if any(r["class"] != cls for r in blk) or min(vdj, 8) != vdj_rec:
                validation["class_vdj_mismatch"] += 1
            if D == -43 and p == 11 and cls == "pert_p" and vdj >= 2:
                validation["boundary_draws"].append({"seed": seed, "lift_index": i, "draw": draw, "v_dj": vdj})
            if vdj < 2 * e:
                continue  # non-degenerate lift
            for sec in ("naive", "teichmuller", "hensel_random"):
                key = (p, A2, B2, sec)
                if key not in rate_cache:
                    if sec == "hensel_random":
                        rate_cache[key] = exact_rate(p, tables(p, A2, B2, L, sec, tuple(range(p)))) if p <= 43 else 1 / (p + 1)
                    else:
                        rate_cache[key] = exact_rate(p, tables(p, A2, B2, L, sec))
                rate = rate_cache[key]
                sel = [r for r in blk if r["section"] == sec]
                assert all(r["vP"] >= 2 for r in sel)
                k = sum(r["success"] for r in sel)
                grp = "D=-3" if D == -3 else "D!=-3"
                for kk in (f"{sec}|{grp}|{cls}", f"{sec}|{grp}", f"{sec}|ALL", "ALL", f"p<=61|{sec}", f"p>61|{sec}"):
                    if kk.startswith("p<=61") and p > 61: continue
                    if kk.startswith("p>61") and p <= 61: continue
                    a = acc.setdefault(kk, {"n": 0, "success": 0, "exp_exact": 0.0, "var": 0.0, "exp_1/(p+1)": 0.0, "exp_1/p": 0.0})
                    a["n"] += len(sel); a["success"] += k
                    a["exp_exact"] += len(sel) * rate; a["var"] += len(sel) * rate * (1 - rate)
                    a["exp_1/(p+1)"] += len(sel) / (p + 1); a["exp_1/p"] += len(sel) / p
    for a in acc.values():
        a["z_exact"] = round((a["success"] - a["exp_exact"]) / math.sqrt(a["var"]), 3) if a["var"] > 0 else None
        for f in ("exp_exact", "exp_1/(p+1)", "exp_1/p"):
            a[f] = round(a[f], 2)
        del a["var"]
    obs[seed] = dict(sorted(acc.items()))
# hensel_random exact rate vs 1/(p+1) for small p
hr = {f"p={k[0]}": round(v * (k[0] + 1), 4) for k, v in rate_cache.items() if k[3] == "hensel_random" and k[0] <= 43}
out = {"validation": validation, "hensel_random_exact_rate_times_(p+1)_small_p": hr, "observed_vs_exact_null": obs}
print(json.dumps(validation))
print(json.dumps(hr))
for seed in obs:
    print(seed)
    for k, v in obs[seed].items():
        if k.count("|") <= 1 or "teichmuller|D=-3" in k or "naive|D=-3" in k:
            print("  ", k, v)
json.dump(out, open("rt_r2_actual_lifts_output.json", "w"), indent=1)
