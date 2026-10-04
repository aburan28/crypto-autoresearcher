"""J6 follow-up (declared after reading the per-rung cells): where does the small_x TT4 band excess sit?
Per-curve excess d_j = A_j - mean(randoms_j) at 30 and 32 bits for small_x, subgroup, dickson and the
known-null arms; the share of the band excess carried by the top-k curves; the count distribution of A
against the randoms (pooled). No simulation. Reads the extract only.
Command: nice -n 19 $PY attacks/j6/smallx_tt4_localise.py --out attacks/j6/out/smallx-tt4-localise.json"""
import argparse, json, os, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
design = L.load_design(); rows = L.load_extract()
groups, _, _ = L.build_groups(rows, design)
out = {}
for arm in ("small_x", "subgroup", "dickson", "known_null_sub", "known_null_dick"):
    fam = L.FAM_OF[arm]
    for b in (30, 32):
        g = groups[(fam, "TT", 4, b)]
        A = L.arm_counts(rows, g, arm, "TT", 4, b)
        R = g.randoms
        d = A - R.mean(axis=1)
        order = np.argsort(-d)
        tot = d.sum()
        out[f"{arm}|{b}"] = {
            "curves": int(len(A)), "C_A": float(A.sum()), "C_R": float(R.mean(axis=1).sum()), "excess": float(tot),
            "A_hist": {str(k): int(v) for k, v in sorted(Counter(A.astype(int).tolist()).items())},
            "randoms_hist_per_arm": {str(k): round(v / 3, 2) for k, v in sorted(Counter(R.astype(int).ravel().tolist()).items())},
            "top10_curves_excess_sum": float(d[order[:10]].sum()),
            "top10_curves": [[int(g.curves[i]), int(A[i]), [int(x) for x in R[i]]] for i in order[:10]],
            "curves_with_A_ge_4": int(np.sum(A >= 4)), "random_instances_with_count_ge_4_per_arm": round(float(np.sum(R >= 4)) / 3, 2)}
L.jdump(a.out, out)
for k, v in out.items():
    print(k, v["C_A"], round(v["C_R"], 1), round(v["excess"], 1), v["A_hist"], v["randoms_hist_per_arm"], "top10", round(v["top10_curves_excess_sum"], 1), v["curves_with_A_ge_4"], v["random_instances_with_count_ge_4_per_arm"])
