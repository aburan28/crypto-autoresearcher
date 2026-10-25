"""Out-of-window check of the rank reading (red team, TASK-20261023-7b5dc6).

PREDICTION written before this script ran (from the 1e5 -> 3e5 local growth exponents in
rt_ew_output.json: r7 6.6, EW-r8 8.4, EW-r9 8.8 in units of 2 dlog N / dlog log H):
  N(1e6) ~ 2.1e3 for the rank-7 curve, ~ 2.2e3 for EW-r8 and ~ 2.3e3 for EW-r9, i.e. both higher-rank
  curves overtake the rank-7 curve between H = 3e5 and H = 1e6.
If they do not, the reading 'rank buys points once the window clears the coefficient scale' is
weakened at this scale; either outcome is reported.
Output rt_ew_1e6_output.json.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rt_lib as L

H = 1000000
GRID = [100000, 300000, 1000000]
CURVES = [("EW-r7-N382623908456", [0, 0, 0, -10012, 346900]),
          ("EW-r8-N249649566346838", [1, -1, 0, -106384, 13075804]),
          ("EW-r9-N32107342006814614", [1, -1, 0, -135004, 97151644])]
out = {"H": H, "rows": []}
for lab, ai in CURVES:
    t0 = time.time()
    pts = L.enumerate_points(ai, H)
    cnt = L.counts_from_points(pts, GRID)
    out["rows"].append({"label": lab, "ainvs": ai, "counts": cnt, "seconds": round(time.time() - t0, 1)})
    print(lab, cnt, round(time.time() - t0, 1), "s", flush=True)
json.dump(out, open(os.path.join(HERE, "rt_ew_1e6_output.json"), "w"), indent=1)
