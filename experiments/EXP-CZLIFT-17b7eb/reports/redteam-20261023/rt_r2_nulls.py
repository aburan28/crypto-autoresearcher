"""R2: right null per definition, and per-section / per-D breakdown, from the admissible raw rows.

Random-section model on a split lift: tau(P) = P^ - P~ in E_1 with v(tau) - 1 ~ Geom(1/p),
leading digits uniform and independent for P and Q.  Then for the ratio read at the first
nonzero digit of z([p]P^):
   P(vQ = vP) = (p-1)/(p+1), P(vQ > vP) = P(vQ < vP) = 1/(p+1), P(success) = 1/(p+1)
   producer definition (rows with vQ >= vP):  null 1/p
   frozen/CORR definition (all v>=2 rows):    null 1/(p+1)
   symmetric (vQ = vP):                        null 1/(p-1)
   literal 'read at precision p^3' (vP = vQ = 2 only counts): null (p-1)/p^2
"""
import json, math, sys
RUNS = {"RUN-CZLIFT-041d05": "../../runs/RUN-CZLIFT-041d05/raw-result.json",
        "RUN-CZLIFT-6709c9": "../../runs/RUN-CZLIFT-6709c9/raw-result.json"}
out = {}
for rid, path in RUNS.items():
    raw = json.load(open(path))
    rows = []
    for c in raw["raw"]["curves"]:
        for r in c["rows"]:
            if r["vP"] >= 2:
                rows.append(dict(r, p=c["p"], D=c["D"]))
    n = len(rows)
    lt = sum(r["vQ"] < r["vP"] for r in rows)
    gt = sum(r["vQ"] > r["vP"] for r in rows)
    eq = sum(r["vQ"] == r["vP"] for r in rows)
    exp_lt = sum(1 / (r["p"] + 1) for r in rows)
    succ = sum(r["success"] for r in rows)
    vp3 = sum(r["vP"] >= 3 for r in rows)
    exp_vp3 = sum(1 / r["p"] for r in rows)

    def z(sel, null):
        S = [r for r in rows if sel(r)]
        k = sum(r["success"] for r in S)
        mu = sum(null(r["p"]) for r in S)
        var = sum(null(r["p"]) * (1 - null(r["p"])) for r in S)
        return {"n": len(S), "success": k, "expected": round(mu, 3), "z": round((k - mu) / math.sqrt(var), 3)}

    defs = {
        "frozen_all_v2_null_1/p (as in CORR)": z(lambda r: True, lambda p: 1 / p),
        "frozen_all_v2_null_1/(p+1) (matching null)": z(lambda r: True, lambda p: 1 / (p + 1)),
        "producer_vQ>=vP_null_1/p (matching null)": z(lambda r: r["vQ"] >= r["vP"] and r["vP"] < 8, lambda p: 1 / p),
        "symmetric_vQ=vP_null_1/(p-1) (matching null)": z(lambda r: r["vQ"] == r["vP"] and r["vP"] < 8, lambda p: 1 / (p - 1)),
        "literal_precision_p3_null_(p-1)/p^2": z(lambda r: True, lambda p: (p - 1) / p ** 2),
    }
    # literal p^3 reading counts success only when vP = vQ = 2
    S = rows
    k_lit = sum(r["success"] and r["vP"] == 2 and r["vQ"] == 2 for r in S)
    mu = sum((r["p"] - 1) / r["p"] ** 2 for r in S)
    var = sum((r["p"] - 1) / r["p"] ** 2 * (1 - (r["p"] - 1) / r["p"] ** 2) for r in S)
    defs["literal_precision_p3_null_(p-1)/p^2"] = {"n": n, "success": k_lit, "expected": round(mu, 3), "z": round((k_lit - mu) / math.sqrt(var), 3)}

    # per section x (D=-3 vs other) x class, producer def with 1/p, and frozen def with 1/(p+1)
    cells = {}
    for sec in ("hensel_random", "naive", "teichmuller"):
        for grp, gsel in (("D=-3", lambda r: r["D"] == -3), ("D!=-3", lambda r: r["D"] != -3)):
            for cls in ("canonical", "isomorphic", "pert_p2", "pert_p"):
                sel = lambda r, sec=sec, gsel=gsel, cls=cls: r["section"] == sec and gsel(r) and r["class"] == cls
                if not any(sel(r) for r in rows):
                    continue
                cells[f"{sec}|{grp}|{cls}"] = z(sel, lambda p: 1 / (p + 1))
        cells[f"{sec}|ALL"] = z(lambda r, sec=sec: r["section"] == sec, lambda p: 1 / (p + 1))
    out[rid] = {"n_degenerate": n, "vQ<vP": lt, "vQ>vP": gt, "vQ=vP": eq,
                "expected_each_side_n/(p+1)": round(exp_lt, 2),
                "vP>=3": vp3, "expected_vP>=3_sum_1/p": round(exp_vp3, 2),
                "successes": succ, "definitions": defs, "cells_frozen_def_null_1/(p+1)": cells}
print(json.dumps(out, indent=1))
json.dump(out, open("rt_r2_nulls_output.json", "w"), indent=1)
