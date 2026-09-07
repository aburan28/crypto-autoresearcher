#!/usr/bin/env python3
"""Blind floor(Mx/p) exact fields on S2-P8219 at M=9.

Parameters only: p=8219, a=1, b=1, N=8117, M=9.
Labels (x*M)//p on dlog-table x-coordinates, identity at 0.
Does not read stage2_floor_miss.py, stage2_exact.py,
stage2_cs_audit.py, stage2.py, or RUN-ECDLP-5cad48-S2FL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO / "analysis" / "o2-sum-compatible-filters"))
from fourier_obstruction import dlog_table  # noqa: E402

P = 8219
A = 1
B = 1
N = 8117
M = 9


def remap_labels(hv: np.ndarray, m: int) -> tuple[np.ndarray, int]:
    used = np.flatnonzero(np.bincount(hv, minlength=m) > 0)
    if len(used) < m:
        remap = -np.ones(m, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv = remap[hv]
        m = int(len(used))
    if m < 2:
        raise RuntimeError("M_eff < 2")
    return hv.astype(np.int64, copy=False), m


def bucket_stats(hv: np.ndarray, m: int, n: int) -> dict:
    hv, m = remap_labels(hv, m)
    ind = np.zeros((m, n))
    for a in range(m):
        ind[a] = hv == a
    counts = ind.sum(axis=1)
    fourier = np.fft.rfft(ind, axis=1)
    fourier_s = np.fft.fft(fourier, axis=0)
    w_s = np.fft.ifft(fourier_s * fourier_s, axis=0)
    w = np.fft.irfft(w_s, n=n, axis=1).real
    num = np.stack([w[:, hv == c].sum(axis=1) for c in range(m)], axis=1)
    den = np.real(np.fft.ifft(np.fft.fft(counts) ** 2))
    pi = num / np.maximum(den[:, None], 1e-12)
    g = m * float(pi.max())
    tot = float(n) ** 2
    deltas = [sum(num[(c - d) % m, c] for c in range(m)) / tot for d in range(m)]
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    q = counts / n
    pi_c = pi[(np.arange(m) - dstar) % m, np.arange(m)]
    w_rel = float(np.sum(q * (pi_c / delta - 1.0) ** 2))
    min_q = float(q.min())
    return {
        "G_exact": g,
        "M_delta_exact": m * delta,
        "W_exact": w_rel,
        "min_q": min_q,
        "cs_bound_exact": 1.0 + (w_rel / max(min_q, 1e-18)) ** 0.5,
        "dstar_exact": dstar,
    }


def main() -> int:
    _g0, pts = dlog_table(P, A, B, N)
    if len(pts) != N:
        raise SystemExit(f"dlog table length {len(pts)} != {N}")
    xs = np.array([0 if pt is None else pt[0] for pt in pts], dtype=np.int64)
    hv = (xs * M) // P
    out = bucket_stats(hv, M, N)
    out["p"] = P
    out["a"] = A
    out["b"] = B
    out["N"] = N
    out["M"] = M
    out["arm"] = "floor(Mx/p)"
    out["cell"] = "S2-P8219"
    out["aligned_ratio"] = out["G_exact"] / out["M_delta_exact"]
    out["aligned_holds"] = out["aligned_ratio"] <= out["cs_bound_exact"]
    path = Path(__file__).resolve().parent / "blind_raw.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
