#!/usr/bin/env python3
"""Cost model for the degree-D closure W_D (lfdclose2.c, dense M4RI) on Semaev t-chain systems.
Columns = sum_{d<=D} C(N,d), N = n + t*k.  Dense bytes of one matrix = rows*ncols/8.
Calibration points are MEASURED (calib.json, written by calibrate.sh); everything else is DERIVED."""
import json, math, sys
from math import comb
def ncols(N, D): return sum(comb(N, d) for d in range(D + 1))
def dense_gb(rows, cols): return rows * cols / 8 / 1e9
if __name__ == "__main__":
    cal = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []
    # log-log fit: time = a * ncols^b  (single thread), rss = c * ncols^e
    xs = [math.log(p["ncols"]) for p in cal]
    def fit(key):
        ys = [math.log(p[key]) for p in cal]; n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
        b = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
        return b, math.exp(my - b*mx)
    bt, at = fit("wall_s"); br, ar = fit("maxrss_mb")
    print(f"fit: wall_s = {at:.3e} * ncols^{bt:.2f};  rss_mb = {ar:.3e} * ncols^{br:.2f}  (points: {len(cal)})")
    for name, N, D in [("C19 D=4", 40, 4), ("C19 D=5", 40, 5), ("C21 D=5", 42, 5), ("m4 l5 N=46 D=4", 46, 4), ("m4 l5 N=46 D=5", 46, 5)]:
        c = ncols(N, D)
        print(f"{name:16s} N={N} ncols={c:>10,d} dense1={dense_gb(c, c):8.1f} GB  est_rss={ar*c**br/1e3:9.1f} GB  est_wall(1 core)={at*c**bt/86400:9.1f} d")
