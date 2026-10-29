"""J2a(6) seeds and J2b(3) breadth: regenerate every main-block curve (bits, seed 8,100,000 + c) of the
recorded census with reviewer-written code (ownec.py) and compare (p, a, b_coef, N) with every record that
carries that (bits, c), and certify every recorded N with PARI/GP ellcard (an independent point-counting
implementation). Only main-block curves of recorded jobs are regenerated; no new block is touched.

usage: python3 -I -B regen_curves.py <toy-main-jobs.jsonl> <scratch-dir> <out.json>
"""
import hashlib
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownec  # noqa: E402

jobs_path, scratch, out_path = sys.argv[1:4]
os.makedirs(scratch, exist_ok=True)
by_curve = {}
n_records = 0
for ln in open(jobs_path):
    if not ln.strip():
        continue
    r = json.loads(ln)
    n_records += 1
    by_curve.setdefault((r["bits"], r["c"]), []).append((r["cell"], r["p"], r["a"], r["b_coef"], r["N"]))

t0 = time.time()
fails, rows = [], []
tried_hist = {}
for (bits, c) in sorted(by_curve):
    p, a, b, N, tried = ownec.regenerate_curve(bits, ownec.SEED_BLOCK["main"] + c)
    tried_hist[tried] = tried_hist.get(tried, 0) + 1
    rows.append((bits, c, p, a, b, N))
    for cell, rp, ra, rb, rN in by_curve[(bits, c)]:
        if (rp, ra, rb, rN) != (p, a, b, N):
            fails.append({"bits": bits, "c": c, "cell": cell, "recorded": [rp, ra, rb, rN], "regenerated": [p, a, b, N]})
    inv = {
        "p_prime": ownec.is_prime(p), "p_bits": p.bit_length() == bits, "N_prime": ownec.is_prime(N),
        "N_ne_p": N != p, "hasse": (N - p - 1) ** 2 <= 4 * p, "nonsingular": (4 * a ** 3 + 27 * b ** 2) % p != 0,
        "a_b_nonzero": a % p != 0 and b % p != 0, "N_gt_4sqrtp": N > 4 * math.isqrt(p) + 4,
        "universe_ge_4096": (N - 1) // 2 >= 4096,
    }
    if not all(inv.values()):
        fails.append({"bits": bits, "c": c, "invariants": inv})
regen_seconds = time.time() - t0

# PARI/GP ellcard on every distinct curve (batch)
gp_in = os.path.join(scratch, "ellcard.gp")
with open(gp_in, "w") as f:
    f.write("default(parisize, 256000000);\n")
    for bits, c, p, a, b, N in rows:
        f.write(f"print({bits},\" \",{c},\" \",ellcard(ellinit([{a},{b}],{p})) == {N}, \" \", isprime({N}));\n")
    bits, c, p, a, b, N = rows[0]          # negative control: a wrong order must print 0
    f.write(f"print(\"neg\",\" \",{c},\" \",ellcard(ellinit([{a},{b}],{p})) == {N + 2}, \" \", isprime({N + 2}));\n")
    f.write("quit;\n")
t1 = time.time()
gp = subprocess.run(["gp", "-q", "-f", gp_in], capture_output=True, text=True, timeout=3600)
gp_seconds = time.time() - t1
gp_all = [ln.split() for ln in gp.stdout.strip().splitlines()]
gp_neg = [ln for ln in gp_all if ln[0] == "neg"]
gp_lines = [ln for ln in gp_all if ln[0] != "neg"]
gp_bad = [ln for ln in gp_lines if ln[2] != "1" or ln[3] != "1"]
gp_ver = subprocess.run(["gp", "--version-short"], capture_output=True, text=True).stdout.strip()

table = "\n".join(",".join(map(str, r)) for r in rows) + "\n"
with open(os.path.join(scratch, "curves-main.csv"), "w") as f:
    f.write("bits,c,p,a,b,N\n" + table)
out = {
    "script": "scripts/regen_curves.py (own arithmetic: scripts/ownec.py)",
    "python": sys.version, "executable": sys.executable,
    "records_read": n_records,
    "distinct_curves": len(rows),
    "distinct_curves_per_bits": {str(b): sum(1 for r in rows if r[0] == b) for b in (20, 24, 28)},
    "records_compared": sum(len(v) for v in by_curve.values()),
    "regenerated_from_seed_8100000_plus_c_mismatches_or_invariant_failures": fails,
    "candidates_tried_histogram": dict(sorted(tried_hist.items())),
    "regeneration_seconds": round(regen_seconds, 1),
    "pari": {"version": gp_ver, "method": "ellcard(ellinit([a,b],p)) == N and isprime(N) for every distinct curve",
             "curves": len(gp_lines), "failures": gp_bad,
             "negative_control_wrong_order_N_plus_2": {"line": gp_neg, "rejected": bool(gp_neg) and gp_neg[0][2] == "0"}, "returncode": gp.returncode,
             "stderr": gp.stderr[-500:], "seconds": round(gp_seconds, 1)},
    "curve_table_sha256": hashlib.sha256(("bits,c,p,a,b,N\n" + table).encode()).hexdigest(),
    "curve_table_note": "bits,c,p,a,b,N rows of the regenerated curves (scratch file, not staged; it equals the recorded values when no mismatch is listed)",
}
with open(out_path, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print("curves", len(rows), "records", out["records_compared"], "fails", len(fails), "pari curves", len(gp_lines),
      "pari bad", len(gp_bad), "regen s", round(regen_seconds, 1), "gp s", round(gp_seconds, 1))
