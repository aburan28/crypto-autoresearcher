"""Null-object control with an independent implementation: R fresh uniform n-subsets of L per curve (reviewer
generator and kernel), each measured exactly like the log-GAP arm against the RECORDED null arm of the cell
(kappa = S/M, z = (S - M)/sqrt(1.05 V)). If the recorded null is a correct reference for uniform label sets, the
R fresh z values per cell are ~ N(0, 1); a shifted mean localizes a reference defect, not a log-GAP effect.
Cells: those with the notable log-GAP deviations (largest |z|, CI excluding 1, the b20-r3 stratum) and one
quiet control cell. Usage: python3 -I -B j3a_nullobject.py <R>. Writes outputs/null-object-control.json.
"""
import hashlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import common as C  # noqa: E402

CELLS = ["b28-r1-n256", "b28-r2-n256", "b28-r3-n256", "b24-r1-n2048", "b20-r3-n256", "b20-r3-n512",
         "b28-r2-n512", "b24-r1-n256"]


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    recs = C.load_jobs()
    an = {c["cell"]: c for c in C.load_analysis()["cells"]}
    out = {}
    for cid in CELLS:
        rs = sorted([r for r in recs if r["cell"] == cid and r["status"] == "ok"], key=lambda r: r["c"])
        g, m, s2, _ = C.curve_arrays(rs)
        n = rs[0]["n"]
        zs, ks = [], []
        h = hashlib.sha256()
        for k in range(R):
            Cs = []
            for rec in rs:
                rng = C.review_np_rng("null-object", cid, rec["c"], k)
                X = C.uniform_labels(n, rec["p"], rec["a"], rec["b_coef"], rng)
                Cs.append(C.count_CD(X, rec["p"])[0])
            Cs = np.array(Cs, float)
            h.update(Cs.astype(np.int64).tobytes())
            st = C.cell_stats_np(Cs, m, s2)
            zs.append(st["z"])
            ks.append(st["kappa"])
        zs = np.array(zs)
        out[cid] = {"R": R, "fresh_uniform_z": [float(x) for x in zs], "fresh_uniform_kappa": [float(x) for x in ks],
                    "mean_z": float(zs.mean()), "se_mean_z": float(1 / math.sqrt(R)), "sd_z": float(zs.std(ddof=1)),
                    "mean_kappa": float(np.mean(ks)), "gap_kappa_recorded": an[cid]["kappa"], "gap_z_recorded": an[cid]["z"],
                    "gap_z_vs_fresh_mean": float((an[cid]["z"] - zs.mean()) / math.sqrt(1 + 1 / R)),
                    "counts_sha256": h.hexdigest()}
        print(cid, round(zs.mean(), 3), round(zs.std(ddof=1), 3), round(np.mean(ks), 4), "gap", round(an[cid]["kappa"], 4), round(an[cid]["z"], 2), flush=True)
    allz = np.concatenate([out[c]["fresh_uniform_z"] for c in CELLS])
    C.write_json("null-object-control.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a (null-object control, independent implementation)",
        "inputs": [C.rel(C.JOBS), C.rel(C.ANALYSIS)], "method": __doc__.strip(), "cells": out,
        "pooled": {"n": int(allz.size), "mean_z": float(allz.mean()), "sd_z": float(allz.std(ddof=1)),
                   "se_mean": float(1 / math.sqrt(allz.size))}}, sig=7)


if __name__ == "__main__":
    main()
