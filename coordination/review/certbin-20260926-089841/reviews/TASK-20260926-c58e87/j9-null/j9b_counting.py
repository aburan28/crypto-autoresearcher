"""J9 (b) counting (TASK-20260926-c58e87). Own code (j10-ptm/rtlib.py) only.
Computes P = rank pi_4(M_4) from the quadratic part alone (L-TOP) for:
  * S_3's quadratic part phi_{x_R}(Q) at every one of the 144 RC-1 x_R (U62, S62, C20);
  * N-CONV17's Q_k (T = identity);
and the saturation arithmetic dim Z_top - 153 against dim B_{<=3} = 988.
Reads only EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json (x_R values).
Does NOT read any RUN-CERTBIN-6ebb0e record.
Usage: python3 j9b_counting.py <worktree> <out.json>
"""
import json
import sys
import time
from math import comb

sys.path.insert(0, __file__.rsplit("/", 2)[0] + "/j10-ptm")
import rtlib as R  # noqa: E402

wt, out = sys.argv[1], sys.argv[2]
t0 = time.time()
d = json.load(open(f"{wt}/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"))
rows_M4 = 17 * (1 + 18 + comb(18, 2))
dimB3 = 1 + 18 + comb(18, 2) + comb(18, 3)
triv = comb(17, 2) + 17
res = {"rows_M4": rows_M4, "dim_B_le3": dimB3, "trivial_syzygies": triv, "per_xR": [], "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
for setname in ("U62", "S62", "C20"):
    for rec in d["sets"][setname]:
        xr = rec["archived"]["x_R"]
        E = R.descent(xr, R.poly_basis())
        P = R.P_rank(E)
        res["per_xR"].append({"set": setname, "idx": rec["idx"], "x_R": xr, "P": P})
Ps = sorted({r["P"] for r in res["per_xR"]})
res["S3_P_values"] = Ps
E17 = R.conv17()
P17 = R.P_rank(E17)
res["NCONV17_P"] = P17
def sat(P):
    z = rows_M4 - P
    return {"P": P, "dim_Z_top": z, "Z_top_minus_trivial": z - triv,
            "excess_over_B3": z - triv - dimB3,
            "forced_nontrivial_syzygies_min": max(0, z - triv - dimB3),
            "forced_dimK_min": max(0, z - dimB3)}
res["saturation_arithmetic"] = {"S3": [sat(p) for p in Ps], "NCONV17": sat(P17),
                                "null_reference_P_2448": sat(2448)}
res["seconds"] = round(time.time() - t0, 1)
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "per_xR"}, indent=1))
