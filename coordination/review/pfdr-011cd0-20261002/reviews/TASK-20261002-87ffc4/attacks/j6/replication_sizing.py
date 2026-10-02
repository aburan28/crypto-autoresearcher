"""J6: Gaussian planning approximation (labelled as such; not a power simulation) of the curves
an independent replication needs, per FAM-1 cell, so that (a) a one-sided 95% upper bound at
kappa_hat = 1 falls at or below the cell's target, and (b) a single pre-registered confirmatory
test at one-sided alpha in {0.01, the family t*} has power 0.8 / 0.9 at kappa = 1.10 (and at the
small_x TT4 point estimate). SE scales as 1/sqrt(n) from the archived band SE at the realised n.
Command: nice -n 19 $PY attacks/j6/replication_sizing.py --out attacks/j6/out/replication-sizing.json
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L  # noqa: E402

Z = {0.01: 2.3263478740, 0.8: 0.8416212336, 0.9: 1.2815515655}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    an = json.load(open(os.path.join(L.EXP, "runs", "RUN-PFDR-011cd0-analysis", "analysis.json")))
    cells = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(L.EXP, "runs", "RUN-PFDR-011cd0-analysis", "cells.jsonl"))}
    t = an["t_star"]
    out = {"method": "Gaussian approximation, SE proportional to 1/sqrt(curves); planning only", "t_star": t, "cells": {}}
    for cid, ai in an["A_INT"].items():
        if cid.startswith("CARRY"):
            continue
        n = cells[cid]["curves_used"]
        se = ai["SE"]
        cls_m = cid.split("|")[1]
        tgt = L.TARGET[(cls_m[:2], int(cls_m[2]))]
        q1 = ai["q"]["q_one_sided_095"]
        need_ub = n * (q1 * se / (tgt - 1.0)) ** 2
        ent = {"curves_realised": n, "SE": se, "target": tgt,
               "curves_for_upper_bound_at_target_if_kappa_hat_1": math.ceil(need_ub)}
        for kap_alt in (1.10, ai["kappa_rel"]):
            if kap_alt <= 1.0:
                continue
            for pw in (0.8, 0.9):
                for lab, thr in (("alpha_0.01_single_test", Z[0.01]), ("family_t_star", t)):
                    se_need = (kap_alt - 1.0) / (thr + Z[pw])
                    ent[f"curves_power{pw}_at_{kap_alt:.3f}_{lab}"] = math.ceil(n * (se / se_need) ** 2)
        out["cells"][cid] = ent
    L.jdump(a.out, out)
    print(json.dumps(out["cells"]["small_x|TT4|band"], indent=1))


if __name__ == "__main__":
    main()
