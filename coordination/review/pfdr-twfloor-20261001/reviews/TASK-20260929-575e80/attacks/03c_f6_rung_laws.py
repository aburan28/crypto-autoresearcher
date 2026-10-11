"""03c -- POST HOC sensitivity of NULL-P / NULL-B to the bundle law (labelled post hoc:
choices F6-2 pre-registered the law pooled over rungs; this variant was added after 03 showed
random m = 5 on-mode at 9 observed against 3.94 expected).

Jump law per (m, class, bits) from complete random-arm 02_bundles records of that rung (both
modes), falling back to the pooled (m, class) law when the rung holds fewer than 50 distinct
relations of the class. Everything else exactly as 03. Exact (FFT); no randomness.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402
from numlib import cp_pmf, poisson_binomial_tail  # noqa: E402
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("n3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_f6_nulls.py"))
n3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n3)
CLS = ("TT", "TB", "SS")


def rung_laws():
    agg = defaultdict(Counter)
    for line in open(n3.BUNDLES):
        r = json.loads(line)
        if r["scope"] != "stop" or not r["complete"] or not r["arm"].startswith("random"):
            continue
        for k, v in r["mult_hist"].items():
            agg[(r["m"], r["class"], r["bits"])][int(k)] += v
    out = {}
    for key, cnt in agg.items():
        tot = sum(cnt.values())
        if tot < 50:
            continue
        pmf = np.zeros(max(cnt) + 1)
        for k, v in cnt.items():
            pmf[k] = v / tot
        EJ = float(np.dot(np.arange(len(pmf)), pmf))
        out[key] = {"pmf": pmf, "EJ": EJ, "D": float(np.dot(np.arange(len(pmf)) ** 2, pmf)) / EJ,
                    "kmax": len(pmf) - 1, "relations": tot}
    return out


def tail(rel, mus, laws_for, thr):
    parts, lam = [], 0.0
    for c in CLS:
        mu = mus.get(c, 0.0)
        if mu <= 0:
            continue
        L = laws_for[c]
        parts.append((mu / L["EJ"], L["pmf"]))
        lam += mu / L["EJ"]
    need = thr - rel
    if need < 0:
        return 1.0
    if lam <= 0:
        return 0.0
    mix = np.zeros(max(len(p) for _, p in parts))
    for lc, p in parts:
        mix[:len(p)] += (lc / lam) * p
    f = cp_pmf(lam, mix)
    k = int(math.floor(need))
    return float(f[k + 1:].sum()) if k + 1 < len(f) else 0.0


def main():
    pooled = n3.jump_laws()
    rl = rung_laws()
    xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
    ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r" and x["mode"] == "on"]
    recs = []
    used = Counter()
    for x in ev:
        lf = {}
        for c in CLS:
            k = (x["m"], c, x["bits"])
            if k in rl:
                lf[c] = rl[k]
                used[f"rung|m{x['m']}|{c}"] += 1
            else:
                lf[c] = pooled[(x["m"], c)]
                used[f"pooled|m{x['m']}|{c}"] += 1
        u = 4 * x["S"] ** 2 / x["N"]
        thr = u / 0.81
        mus = {c: x[f"mu_{c}"] for c in CLS}
        ms = sum(mus.values())
        pP = tail(x["relations"], mus, lf, thr)
        phi = (u - x["relations"]) / ms if ms > 0 else 0.0
        pB = tail(x["relations"], {c: phi * v for c, v in mus.items()}, lf, thr) if phi > 0 else 1.0
        recs.append({"key": [x["panel"], x["bits"], x["curve"], x["m"], x["arm"], "on"], "cls": x["cls"],
                     "m": x["m"], "fire": x["ratio"] < 0.9, "p_P_rung": pP, "p_B_rung": pB})
    fams = {}
    for cl in ("random", "structured", "j0_random", "known_log", "j0_coset"):
        for m in (3, 4, 5):
            rs = [r for r in recs if r["cls"] == cl and r["m"] == m]
            if not rs:
                continue
            obs = sum(r["fire"] for r in rs)
            fams[f"on|{cl}|m{m}"] = {
                "n": len(rs), "observed": obs,
                "E_P_rung": sum(r["p_P_rung"] for r in rs),
                "P_ge_obs_P_rung": poisson_binomial_tail([r["p_P_rung"] for r in rs], obs),
                "E_B_rung": sum(r["p_B_rung"] for r in rs),
                "P_ge_obs_B_rung": poisson_binomial_tail([r["p_B_rung"] for r in rs], obs)}
    for name, sel in (("generic_all", lambda r: r["cls"] in ("random", "structured", "j0_random")),
                      ("random", lambda r: r["cls"] == "random"), ("structured", lambda r: r["cls"] == "structured")):
        rs = [r for r in recs if sel(r)]
        obs = sum(r["fire"] for r in rs)
        fams[f"on|POOLED|{name}"] = {"n": len(rs), "observed": obs,
                                     "E_P_rung": sum(r["p_P_rung"] for r in rs),
                                     "P_ge_obs_P_rung": poisson_binomial_tail([r["p_P_rung"] for r in rs], obs),
                                     "E_B_rung": sum(r["p_B_rung"] for r in rs)}
    dump("03c_f6_rung_laws.json", {"label": "POST HOC sensitivity (rung-specific bundle laws)",
                                   "laws_used": dict(used),
                                   "rung_laws": {f"m{m}|{c}|b{b}": {"EJ": L["EJ"], "D": L["D"], "kmax": L["kmax"],
                                                                     "relations": L["relations"]}
                                                 for (m, c, b), L in sorted(rl.items())},
                                   "families": fams})
    print(json.dumps(fams, indent=0))


if __name__ == "__main__":
    main()
