#!/usr/bin/env python3
"""Standalone blind re-derivation of floor(Mx/p) G and Md.

Uses RT-EXP-1 bucket_gain convolution and fourier_obstruction.dlog_table
at the frozen Stage 0 fixture. Does not import or read any producer
Stage 0 path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve()
for parent in REPO.parents:
    if (parent / "analysis" / "o2-sum-compatible-filters" / "rt_exp_1.py").is_file():
        sys.path.insert(0, str(parent / "analysis" / "o2-sum-compatible-filters"))
        break
else:
    raise SystemExit("could not locate analysis/o2-sum-compatible-filters")

from fourier_obstruction import dlog_table  # noqa: E402
from rt_exp_1 import bucket_gain  # noqa: E402

# Frozen parameters from the review-plan quantity statement.
P = 65539
A = 0
B = 11
N_ORDER = 65287
M = 40
FILTER_NAME = "floor(Mx/p)"


def h_floor(pt):
    if pt is None:
        return 0
    return (M * int(pt[0])) // P


def main() -> int:
    g0, pts = dlog_table(P, A, B, N_ORDER)
    if len(pts) != N_ORDER:
        raise SystemExit(f"dlog_table length {len(pts)} != N {N_ORDER}")
    hv = np.array([h_floor(pt) for pt in pts], dtype=np.int64)
    identity_indices = [i for i, pt in enumerate(pts) if pt is None]
    g, md, m_eff = bucket_gain(hv, M, N_ORDER)
    out = {
        "filter": FILTER_NAME,
        "p": P,
        "a": A,
        "b": B,
        "N": N_ORDER,
        "M": M,
        "G0": [int(g0[0]), int(g0[1])],
        "identity_indices": identity_indices,
        "walk_closed": identity_indices == [0],
        "h": "floor(M*x/p); h(O)=0",
        "method": "rt_exp_1.bucket_gain exact whole-group FFT convolution",
        "G": float(g),
        "M_delta": float(md),
        "M_eff": int(m_eff),
    }
    dest = Path(__file__).with_name("blind_raw.json")
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
