#!/usr/bin/env python3
"""Blind exact-W re-derivation for S2-P2063 floor(Mx/p) M=7.

Does not import or read stage2.py, raw-result.json, or
execution-report-stage2.yaml.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO / "analysis" / "o2-sum-compatible-filters"))
from fourier_obstruction import dlog_table  # noqa: E402

P, A, B, N, M = 2063, 1, 5, 2129, 7


def exact_w(hv: np.ndarray, m: int, n: int) -> dict:
    used = np.flatnonzero(np.bincount(hv, minlength=m) > 0)
    if len(used) < m:
        remap = -np.ones(m, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv = remap[hv]
        m = int(len(used))
    if m < 2:
        raise RuntimeError("M_eff < 2")
    ind = np.zeros((m, n))
    for bucket in range(m):
        ind[bucket] = hv == bucket
    counts = ind.sum(axis=1)
    fourier = np.fft.rfft(ind, axis=1)
    fourier_s = np.fft.fft(fourier, axis=0)
    w_s = np.fft.ifft(fourier_s * fourier_s, axis=0)
    w = np.fft.irfft(w_s, n=n, axis=1).real
    num = np.stack([w[:, hv == c].sum(axis=1) for c in range(m)], axis=1)
    den = np.real(np.fft.ifft(np.fft.fft(counts) ** 2))
    pi = num / np.maximum(den[:, None], 1e-12)
    tot = float(n) ** 2
    deltas = [sum(num[(c - d) % m, c] for c in range(m)) / tot for d in range(m)]
    dstar = int(np.argmax(deltas))
    delta = float(deltas[dstar])
    q = counts / n
    pi_c = pi[(np.arange(m) - dstar) % m, np.arange(m)]
    w_rel = float(np.sum(q * (pi_c / delta - 1.0) ** 2))
    return {"M_eff": int(m), "W": w_rel, "G": m * float(pi.max()), "M_delta": m * delta, "dstar": dstar}


def main() -> int:
    _g0, pts = dlog_table(P, A, B, N)
    if len(pts) != N:
        raise RuntimeError(f"dlog table length {len(pts)} != {N}")
    xs = np.array([0 if pt is None else pt[0] for pt in pts], dtype=np.int64)
    hv = (xs * M) // P
    out = exact_w(hv, M, N)
    out.update({"p": P, "a": A, "b": B, "N": N, "M": M, "arm": "floor(Mx/p)"})
    Path(__file__).with_name("blind_raw.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
