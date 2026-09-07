#!/usr/bin/env python3
"""Blind P2 exact fields on S2-P523 at M=5.

Parameters only: N=523, M=5, labels (i*M)//N.
Does not read stage2_exact.py or RUN-ECDLP-5cad48-S2G.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

N = 523
M = 5


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
    hv = (np.arange(N, dtype=np.int64) * M) // N
    out = bucket_stats(hv, M, N)
    out["N"] = N
    out["M"] = M
    out["arm"] = "P2"
    out["cell"] = "S2-P523"
    path = Path(__file__).resolve().parent / "blind_raw.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
