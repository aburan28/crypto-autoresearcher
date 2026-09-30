#!/usr/bin/env python3
"""Bench the dense column pass vs the rank-only instrument, optionally on GPU.

Examples:
  python3 tools/gf2_bench_rank.py                  # CPU, small shapes
  python3 tools/gf2_bench_rank.py --large          # CERTBIN-shaped
  python3 tools/gf2_bench_rank.py --gpu            # also time CUDA tail if present
  python3 tools/gf2_bench_rank.py --out bench.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.gf2 import kernels, rank_only  # noqa: E402
from crypto_autoresearcher.gf2.closure import Closure  # noqa: E402


def _random_eqs(nv, neq, rng):
    eqs = []
    for _ in range(neq):
        terms = []
        for _ in range(int(rng.integers(3, 8))):
            # random degree-<=2 monomial as a bitmask
            d = int(rng.integers(0, 3))
            bits = rng.choice(nv, size=d, replace=False) if d else []
            m = 0
            for b in bits:
                m |= 1 << int(b)
            terms.append(m)
        eqs.append(sorted(set(terms)))
    return eqs


def _time(fn, repeats=1):
    best = None
    out = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        out = fn()
        dt = time.perf_counter() - t0
        best = dt if best is None else min(best, dt)
    return best, out


def bench_shape(nv, D, seed=0):
    neq = nv - 1
    rng = np.random.default_rng(seed)
    eqs = _random_eqs(nv, neq, rng)
    cl = Closure(nv, D, neq)
    M = cl.build_M(eqs)
    R, W = M.shape
    C = cl.C
    row = {
        "nv": nv, "D": D, "neq": neq, "R": R, "C": C, "W": W,
        "words": int(R * W), "backend_kernels": kernels.backend(),
    }

    def dense_rank():
        Mc = M.copy()
        return kernels.column_pass(Mc, C, keep_ops=False, algorithm="auto")

    def dense_ops():
        Mc = M.copy()
        return kernels.column_pass(Mc, C, keep_ops=True, algorithm="auto")

    def rank_inst(alg):
        return rank_only.rank_profile(M, C, want_cert=False, algorithm=alg)

    t, log = _time(dense_rank)
    row["dense_rank_s"] = t
    row["dense_rank"] = int(log.K)
    t, log = _time(dense_ops)
    row["dense_ops_s"] = t

    for alg in ("dense", "sparse", "auto"):
        try:
            t, res = _time(lambda a=alg: rank_inst(a))
        except Exception as exc:
            row[f"rank_only_{alg}_s"] = None
            row[f"rank_only_{alg}_err"] = str(exc)
            continue
        row[f"rank_only_{alg}_s"] = t
        row[f"rank_only_{alg}_rank"] = res.rank
        row[f"rank_only_{alg}_backend"] = res.backend
        row[f"rank_only_{alg}_match"] = res.pivcols == tuple(int(x) for x in
            kernels.column_pass(M.copy(), C, keep_ops=False).cs.tolist())
    return row


def bench_gpu_tail():
    from crypto_autoresearcher.gf2 import gpu as gf2gpu
    ok, reason = gf2gpu.available()
    if not ok:
        return {"gpu": False, "reason": reason}
    rng = np.random.default_rng(1)
    R, W, ch, npiv, nr = 4096, 1024, 128, 64, 2048
    M = rng.integers(0, 2**64, size=(R, W), dtype=np.uint64)
    rows = rng.choice(R, size=nr, replace=False).astype(np.int32)
    cw = (npiv + 63) // 64
    cfs = rng.integers(0, 2**64, size=(nr, cw), dtype=np.uint64)
    # keep only low npiv bits meaningful
    if npiv < 64:
        cfs[:, 0] &= (np.uint64(1) << npiv) - np.uint64(1)
    Bs = rng.integers(0, 2**64, size=(npiv, W), dtype=np.uint64)
    w0, x0, tail = 0, 0, W
    Mc = M.copy()
    t0 = time.perf_counter()
    gf2gpu.cpu_tail_chunk(Mc, W, w0, x0, ch, rows, cfs, cw, Bs, tail, npiv, True)
    t_cpu = time.perf_counter() - t0
    t0 = time.perf_counter()
    Mg = gf2gpu.gpu_tail_chunk(M, W, w0, x0, ch, rows, cfs, cw, Bs, tail, npiv, True)
    t_gpu = time.perf_counter() - t0
    return {
        "gpu": True,
        "cpu_s": t_cpu,
        "gpu_s": t_gpu,
        "speedup": t_cpu / t_gpu if t_gpu else None,
        "bit_identical": bool(np.array_equal(Mc, Mg)),
        "device": __import__("cupy").cuda.runtime.getDeviceProperties(0)["name"].decode(),
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--large", action="store_true",
                   help="include nv=20/24 D=5/6 CERTBIN-shaped systems")
    p.add_argument("--gpu", action="store_true")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)

    shapes = [(8, 3), (12, 4), (16, 4)]
    if args.large:
        shapes += [(20, 5), (24, 5), (20, 6)]
    rows = [bench_shape(nv, D) for nv, D in shapes]
    out = {
        "host": os.uname().nodename if hasattr(os, "uname") else "",
        "omp_threads": os.environ.get("CRYPTO_AR_GF2_INNER_THREADS"),
        "shapes": rows,
    }
    if args.gpu:
        out["gpu_tail"] = bench_gpu_tail()
    text = json.dumps(out, indent=2)
    print(text)
    if args.out:
        args.out.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
