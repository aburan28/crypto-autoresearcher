#!/usr/bin/env python3
"""End-to-end CPU vs GPU timing of the rank-profile solver on one machine.

For each workload (random quadratic systems, neq = nv - 1) runs
``rankprofile.macaulay_profile`` / ``w_profile`` end to end with ``gpu=False``
and ``gpu=True``, alternating, ``--reps`` times each, checks that the records
are identical, and prints one JSON document: machine, GPU, per-workload
times and the speedup of the best GPU run over the best CPU run.

    python3 tools/gf2_bench_gpu.py [--reps 3] [--out bench.json] [--quick]

Needs a CUDA device and CuPy for the GPU column (``.[gf2-gpu]``); without one
it reports why and times the CPU path only. It reads no run package and
writes no research record.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from crypto_autoresearcher.gf2 import gpu, kernels, rankprofile  # noqa: E402

WORKLOADS = [("M", 24, 5), ("M", 20, 6), ("M", 26, 5), ("W", 20, 5), ("W", 22, 5)]
QUICK = [("M", 20, 5), ("W", 18, 5)]


def system(nv, neq, seed=0):
    rng = np.random.default_rng(seed)
    mon = [0] + [1 << i for i in range(nv)] + [(1 << i) | (1 << j) for i, j in combinations(range(nv), 2)]
    return [[m for m in mon if rng.random() < 0.5] for _ in range(neq)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--out")
    ap.add_argument("--quick", action="store_true", help="two small workloads only")
    a = ap.parse_args()
    ok, why = gpu.available()
    info = {"host": platform.node(), "cpus": os.cpu_count(), "backend": kernels.backend(),
            "gpu_available": ok, "gpu_reason": why}
    if ok:
        import cupy as cp
        dev = cp.cuda.runtime.getDeviceProperties(0)
        info["gpu"] = dev["name"].decode() if isinstance(dev["name"], bytes) else dev["name"]
    results = []
    for kind, nv, D in (QUICK if a.quick else WORKLOADS):
        eqs = system(nv, nv - 1)
        fn = rankprofile.macaulay_profile if kind == "M" else rankprofile.w_profile
        times = {"cpu": [], "gpu": []}
        recs = {}
        for _ in range(a.reps):
            for mode in (("cpu", "gpu") if ok else ("cpu",)):
                t = time.perf_counter()
                rec, _, _ = fn(eqs, nv, D, gpu=(mode == "gpu"))
                times[mode].append(time.perf_counter() - t)
                recs.setdefault(mode, rec)
                if recs[mode] != rec:
                    raise SystemExit(f"{kind}{nv}/{D} {mode}: record changed between runs")
        same = ok and recs["cpu"] == recs["gpu"]
        row = {"workload": f"{kind}_{D} nv={nv}", "cpu_s": [round(x, 3) for x in times["cpu"]],
               "gpu_s": [round(x, 3) for x in times["gpu"]], "records_equal": same if ok else None}
        if ok:
            row["speedup_best"] = round(min(times["cpu"]) / min(times["gpu"]), 2)
        results.append(row)
        print(json.dumps(row), flush=True)
        if ok and not same:
            raise SystemExit(f"{kind}{nv}/{D}: GPU record differs from CPU record")
    doc = {"machine": info, "results": results}
    text = json.dumps(doc, indent=1)
    if a.out:
        Path(a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
