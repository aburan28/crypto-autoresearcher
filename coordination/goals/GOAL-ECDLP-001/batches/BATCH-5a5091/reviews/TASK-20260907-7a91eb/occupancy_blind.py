#!/usr/bin/env python3
"""Blind occupancy re-derivation from labels only.

Rebuilds floor(Mx/p) from dlog_table and (x*M)//p.
Must not import or read the S2OC producer or S2OC run artifacts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO / "analysis" / "o2-sum-compatible-filters"))
from fourier_obstruction import dlog_table  # noqa: E402

TARGETS = (
    {"id": "S2-P8219", "p": 8219, "a": 1, "b": 1, "N": 8117, "M": 9},
    {"id": "S2-P32779", "p": 32779, "a": 3, "b": 5, "N": 32909, "M": 13},
)


def occupancy(hv: np.ndarray, m: int) -> dict:
    counts_before = np.bincount(hv, minlength=m)
    n_empty = int(np.sum(counts_before == 0))
    used = np.flatnonzero(counts_before > 0)
    if len(used) < m:
        remap = -np.ones(m, dtype=np.int64)
        remap[used] = np.arange(len(used))
        hv = remap[hv]
        m = int(len(used))
    if m < 2:
        raise RuntimeError("M_eff < 2")
    n = int(hv.size)
    counts = np.bincount(hv, minlength=m).astype(np.float64)
    q = counts / n
    return {
        "q": [float(x) for x in q],
        "n_empty_before_remap": n_empty,
        "M_eff": int(m),
    }


def main() -> int:
    out = []
    for cell in TARGETS:
        p, a, b, n, m = cell["p"], cell["a"], cell["b"], cell["N"], cell["M"]
        _g0, pts = dlog_table(p, a, b, n)
        if len(pts) != n:
            raise SystemExit(f"dlog table length {len(pts)} != {n}")
        xs = np.array([0 if pt is None else pt[0] for pt in pts], dtype=np.int64)
        labels = (xs * m) // p
        rec = occupancy(labels, m)
        rec.update({"cell": cell["id"], "M": m, "arm": "floor(Mx/p)"})
        out.append(rec)
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({row["cell"]: {"M": row["M"], "M_eff": row["M_eff"], "n_empty_before_remap": row["n_empty_before_remap"]} for row in out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
