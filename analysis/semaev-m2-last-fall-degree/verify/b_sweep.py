#!/usr/bin/env python3
"""Re-check every exact last fall degree of results/instances.json with implementation B.

For each m = 2 instance with an exact refutation degree d and NMIN <= n <= NMAX, run
indep_verify.py at D = d-1 and D = d. It checks four things:
  - B's solution count equals A's;
  - 1 is not in W_{d-1}, according to B;
  - B's dims of W_{d-1} equal A's (both closures are complete there);
  - 1 is in W_d, according to B.
usage: b_sweep.py instances.json NMAX [NMIN]"""
import json, re, subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
recs, nmax = json.load(open(sys.argv[1])), int(sys.argv[2])
nmin = int(sys.argv[3]) if len(sys.argv) > 3 else 0
bad = 0
for r in sorted(recs, key=lambda r: (r["n"], r["name"])):
    d = r.get("d_ref_exact")
    if d is None or not nmin <= r["n"] <= nmax:
        continue
    out = {}
    for D in (d - 1, d):
        args = ["python3", os.path.join(here, "indep_verify.py"), str(r["n"]), r["modulus_hex"], str(r["a2"]),
                r["a6_hex"], r["z_hex"], str(D)] + r["V_basis_hex"]
        txt = subprocess.run(args, capture_output=True, text=True).stdout
        cnt = int(re.search(r"boolean solutions \(ordered pairs\): (\d+)", txt).group(1))
        m = re.search(r"W(\d+) dims \[([\d, ]+)\] contains_one (\d)", txt)
        out[D] = (cnt, [int(x) for x in m.group(2).split(",")], int(m.group(3)))
    a_low = r["closures"][str(d - 1)]
    ok = (out[d - 1][0] == r["boolean_solutions"] and out[d - 1][2] == 0 and out[d][2] == 1
          and out[d - 1][1] == a_low["W_dims"] and a_low["W_one"] == 0)
    bad += not ok
    print(f"{r['name']:6s} n={r['n']:2d} d={d} B_count={out[d-1][0]} B_W{d-1}={out[d-1][1]} A_W{d-1}={a_low['W_dims']} "
          f"B_one(W{d-1})={out[d-1][2]} B_one(W{d})={out[d][2]} {'AGREE' if ok else 'DISAGREE'}", flush=True)
print(f"done; disagreements: {bad}")
