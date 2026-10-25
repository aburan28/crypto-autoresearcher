"""R2: exact success rates of the deterministic sections (naive, teichmuller), exhaustive over
P in E(F_p)\\{O} and d in [2, p-2], on the canonical lift and on random lifts of the isomorphic
and pert_p2 classes (drawn with the producer's class definitions, run.py lift_classes);
then the expected success count of the admissible rows under these exact nulls.

Also tests the CM-automorphism prediction: on j = 0 lifts with A == 0 mod p^2 the Teichmuller
section is mu_6-equivariant mod p^2, and [zeta] acts on E_1/E_2 by the conjugate of its
eigenvalue on E(F_p), so every d in mu_6 \\ {+-1} must FAIL (forced failure, not rate 1/p).
"""
import json, math, random, sys
import numpy as np
sys.path.insert(0, '.')
from rt_padic import *

K = 8
rng = random.Random(856638)
curves = json.load(open('curves_from_raw.json'))


def lift_rate(p, A2, B2, L, section):
    E = ZpK(p, K, A2, B2)
    v = np.zeros(p, dtype=np.int64)
    u = np.zeros(p, dtype=np.int64)
    for k in range(1, p):
        Ph = E.lift(L[k], section)
        z = E.z_mult(p, Ph)
        vv = vp(z, p, K)
        v[k] = vv
        u[k] = (z // p ** vv) % p if vv < K else 0
    ks = np.arange(1, p)
    succ = n_ge = n_eq = 0
    mu6 = {d for d in range(2, p - 1) if pow(d, 6, p) == 1}
    succ_mu6 = n_mu6 = 0
    for d in range(2, p - 1):
        q = (d * ks) % p
        vP, vQ, uP, uQ = v[ks], v[q], u[ks], u[q]
        ok = (vP < K) & (vQ == vP) & (uQ == (d * uP) % p)
        succ += int(ok.sum())
        n_ge += int(((vQ >= vP) & (vP < K)).sum())
        n_eq += int(((vQ == vP) & (vP < K)).sum())
        if d in mu6:
            succ_mu6 += int(ok.sum())
            n_mu6 += p - 1
    n_all = (p - 1) * (p - 3)
    return {"rate_all": succ / n_all, "rate_ge": succ / n_ge if n_ge else 0.0, "rate_eq": succ / n_eq if n_eq else 0.0,
            "deg": bool((v[1:] >= 2).all()), "mu6_d": sorted(mu6), "mu6_success": succ_mu6, "mu6_pairs": n_mu6}


def draw(cls, p, A, B, jcm):
    if cls == "isomorphic":
        s = 1 + p * rng.randrange(1, p)
        return A * s * s, B * s ** 3
    if cls == "pert_p2":
        if jcm == 0:
            return p * p * rng.randrange(1, p), B + p * rng.randrange(0, p)
        return A + p * p * rng.randrange(1, p), B + p * p * rng.randrange(1, p)


table = {}
mu6_forced = []
for c in curves:
    p, A, B, jcm, D = c["p"], c["A"], c["B"], c["j_cm"], c["D"]
    L, N = cyclic_enumeration(p, A % p, B % p)
    assert N == p
    nl = 12 if p <= 61 else 4
    for sec in ("naive", "teichmuller"):
        res = {"canonical": [lift_rate(p, A, B, L, sec)]}
        for cls in ("isomorphic", "pert_p2"):
            res[cls] = [lift_rate(p, *draw(cls, p, A, B, jcm), L, sec) for _ in range(nl)]
        summ = {}
        for cls, lst in res.items():
            assert all(r["deg"] for r in lst)
            summ[cls] = {"rate_all_mean": float(np.mean([r["rate_all"] for r in lst])),
                         "rate_all_min": min(r["rate_all"] for r in lst), "rate_all_max": max(r["rate_all"] for r in lst),
                         "rate_ge_mean": float(np.mean([r["rate_ge"] for r in lst])), "n_lifts": len(lst)}
            if jcm == 0 and sec == "teichmuller":
                mu6_forced.append({"p": p, "class": cls, "mu6_d": lst[0]["mu6_d"],
                                   "mu6_success": sum(r["mu6_success"] for r in lst), "mu6_pairs": sum(r["mu6_pairs"] for r in lst)})
        table[f"{D}|{p}|{sec}"] = summ
    print(D, p, {s: {k: round(v["rate_all_mean"] * (p + 1), 3) for k, v in table[f'{D}|{p}|{s}'].items()} for s in ("naive", "teichmuller")}, flush=True)

# expected successes of the admissible rows under the exact nulls (frozen/CORR definition: all v>=2 rows)
RUNS = {"RUN-CZLIFT-041d05": "../../runs/RUN-CZLIFT-041d05/raw-result.json",
        "RUN-CZLIFT-6709c9": "../../runs/RUN-CZLIFT-6709c9/raw-result.json"}
cmp = {}
for rid, path in RUNS.items():
    raw = json.load(open(path))
    acc = {}
    for c in raw["raw"]["curves"]:
        p, D = c["p"], c["D"]
        for r in c["rows"]:
            if r["vP"] < 2 or r["class"] == "pert_p":
                continue
            sec = r["section"]
            if sec == "hensel_random":
                rate = 1 / (p + 1)
            else:
                rate = table[f"{D}|{p}|{sec}"][r["class"]]["rate_all_mean"]
            for key in (f"{sec}|{'D=-3' if D == -3 else 'D!=-3'}", f"{sec}|ALL", "ALL"):
                a = acc.setdefault(key, {"n": 0, "success": 0, "exp_exact": 0.0, "var_exact": 0.0, "exp_1/(p+1)": 0.0})
                a["n"] += 1
                a["success"] += int(r["success"])
                a["exp_exact"] += rate
                a["var_exact"] += rate * (1 - rate)
                a["exp_1/(p+1)"] += 1 / (p + 1)
    for a in acc.values():
        a["z_exact"] = round((a["success"] - a["exp_exact"]) / math.sqrt(a["var_exact"]), 3) if a["var_exact"] else None
        a["exp_exact"] = round(a["exp_exact"], 2)
        a["exp_1/(p+1)"] = round(a["exp_1/(p+1)"], 2)
        del a["var_exact"]
    cmp[rid] = acc
print(json.dumps(mu6_forced, indent=0))
print(json.dumps(cmp, indent=1))
json.dump({"exact_rates": table, "mu6_forced_failure": mu6_forced, "observed_vs_exact_null_excluding_pert_p_label": cmp},
          open("rt_r2_exact_output.json", "w"), indent=1)
