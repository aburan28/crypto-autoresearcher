"""Red-team unbounded-independence control for EXP-CZLIFT-ed8113 (TASK-20261023-62eb31).

For every replayed producer trial (rt_replay_inputs.json) compute, with PARI/GP
at realprecision 77 (cypari2 2.2.4 / PARI 2.17.2, installed outside the repo):
  - canonical heights h(P_i) (PARI/BSD normalization = 2 x the JKSST/Silverman
    normalization used in JKSST 2000 section 2.4),
  - the Neron-Tate height-pairing determinant det<P_i,P_j> of the lifted tuple
    and its normalized form det / prod h(P_i) in [0, 1]; the tuple is
    Z-independent modulo torsion iff det > 0 (any coefficient size),
  - torsion orders (ellorder, 0 = infinite order),
  - log |Delta_min| of the minimal model,
  - JKSST 2000 section 5.1.2 empirical dependence bounds 5|D|^-1/4 (r=2) and
    66|D|^-1/4 (r=3), summed per cell as a predicted count,
  - the JKSST Lemma 4.1 ratio log|D| / max hhat_S(P_i) (their constant C1).
Tuples with normalized det < 1e-40 are flagged dependent and their relation is
recovered with lindep and verified exactly with ellmul/elladd.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PYENV = os.environ.get("RT_PYENV")
if PYENV:
    sys.path.insert(0, PYENV)
import cypari2  # noqa: E402

pari = cypari2.Pari()
pari.allocatemem(256 * 10**6, silent=True)
pari("default(realprecision, 77)")
pari("""rtrow(A2,A4,A6,pts) = {
  my(E = ellinit([0,A2,0,A4,A6]), n = #pts, h, H, d, Em, o);
  h = vector(n, i, ellheight(E, pts[i]));
  H = ellheightmatrix(E, pts);
  d = matdet(H);
  Em = ellminimalmodel(E);
  o = vector(n, i, ellorder(E, pts[i]));
  [h, d, d / prod(i = 1, n, h[i]), log(abs(Em.disc)), o]
}""")
pari("""rtrel(A2,A4,A6,pts) = {
  my(E = ellinit([0,A2,0,A4,A6]), H = ellheightmatrix(E, pts), K = matker(H), v, S);
  if (#K == 0, return(0));
  v = lindep(K[,1]~);
  v = lindep(H[1,]);
  S = [0];
  for (i = 1, #pts, S = elladd(E, S, ellmul(E, pts[i], v[i])));
  [v~, S == [0]]
}""")


def main():
    d = json.load(open(os.path.join(HERE, "rt_replay_inputs.json")))
    out = {"tool": "PARI " + ".".join(map(str, pari.version())), "realprecision": 77,
           "height_normalization": "PARI/BSD (2 x JKSST)", "cells": [], "dependent_trials": [],
           "summary": {}}
    all_norm = {2: [], 3: []}
    for seed in ("20261009", "20261010"):
        cells = {}
        for row in d[seed]["rows"]:
            p, r = row["p"], row["r"]
            pts = "[" + ",".join(f"[{x},{y}]" for x, y in row["pts"]) + "]"
            res = pari(f"rtrow({row['A2']},{row['A4']},{row['A6']},{pts})")
            h = [float(x) for x in res[0]]
            det = res[1]
            norm = float(res[2])
            logD = float(res[3])
            orders = [int(x) for x in res[4]]
            dep = bool(pari(f"{res[2]} < 1e-40"))
            c = cells.setdefault((p, r), {"n": 0, "dep": 0, "min_norm": 1.0, "norms": [], "logD": [],
                                          "jksst_pred": 0.0, "C1": [], "h_over_logp": [], "torsion_pts": 0})
            c["n"] += 1
            c["norms"].append(norm)
            c["logD"].append(logD)
            c["torsion_pts"] += sum(1 for o in orders if o)
            k = 5.0 if r == 2 else 66.0
            c["jksst_pred"] += min(1.0, k * math.exp(-logD / 4))
            hS = [x / 2 for x in h]
            c["C1"].append(logD / max(hS))
            c["h_over_logp"].extend(x / math.log(p) for x in hS)
            if not dep:
                c["min_norm"] = min(c["min_norm"], norm)
                all_norm[r].append(norm)
            else:
                c["dep"] += 1
                rel = pari(f"rtrel({row['A2']},{row['A4']},{row['A6']},{pts})")
                out["dependent_trials"].append({"seed": int(seed), "p": p, "r": r, "i": row["i"], "pts": row["pts"],
                                                "normalized_det": norm, "heights_pari": h, "orders": orders,
                                                "relation": [int(x) for x in rel[0]], "relation_verified_exactly": bool(rel[1])})
        for (p, r), c in sorted(cells.items()):
            ln = sorted(c["norms"])
            out["cells"].append({
                "seed": int(seed), "p": p, "r": r, "trials": c["n"], "dependent_unbounded": c["dep"],
                "min_normalized_det_independent": c["min_norm"],
                "q05_normalized_det": ln[len(ln) // 20],
                "median_log_abs_Dmin": sorted(c["logD"])[len(c["logD"]) // 2],
                "median_log2_abs_Dmin_bits": round(sorted(c["logD"])[len(c["logD"]) // 2] / math.log(2), 1),
                "jksst_empirical_predicted_dependent": round(c["jksst_pred"], 4),
                "median_C1_logD_over_max_hhatS": round(sorted(c["C1"])[len(c["C1"]) // 2], 2),
                "min_C1": round(min(c["C1"]), 2),
                "median_hhatS_over_logp": round(sorted(c["h_over_logp"])[len(c["h_over_logp"]) // 2], 3),
                "torsion_points": c["torsion_pts"],
            })
            print(json.dumps(out["cells"][-1]))
    out["summary"] = {
        "dependent_unbounded_total": len(out["dependent_trials"]),
        "min_normalized_det_independent_r2": min(all_norm[2]),
        "min_normalized_det_independent_r3": min(all_norm[3]),
        "jksst_predicted_total": round(sum(c["jksst_empirical_predicted_dependent"] for c in out["cells"]), 3),
    }
    print(json.dumps(out["summary"]))
    print(json.dumps(out["dependent_trials"]))
    json.dump(out, open(os.path.join(HERE, "rt_regulator_control.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
