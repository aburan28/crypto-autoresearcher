#!/usr/bin/env python3
"""Blind re-derivation of unconstrained hat a for floor(Mx/p).

Reads only the recorded Stage 2 W table and the frozen protocol
formulas. Does not read stage2_fit.py or RUN-ECDLP-5cad48-S2FIT.
Does not classify W.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[7]
S2 = REPO / "experiments" / "EXP-ECDLP-5cad48" / "runs" / "RUN-ECDLP-5cad48-S2" / "raw-result.json"
ARM = "floor(Mx/p)"
H2_C0 = 0.25
OUT = Path(__file__).resolve().parent / "blind_raw.json"

CELLS = (
    ("S2-P523", 523, (5, 8, 12)),
    ("S2-P1033", 1033, (6, 10, 16)),
    ("S2-P2063", 2063, (7, 13, 21)),
    ("S2-P4111", 4111, (8, 16, 28)),
    ("S2-P8219", 8219, (9, 20, 37)),
    ("S2-P16417", 16417, (11, 25, 49)),
    ("S2-P32779", 32779, (13, 32, 64)),
    ("S2-P65539", 65539, (16, 40, 84)),
)


def arm_rec(cell: dict, m: int) -> dict:
    for block in cell["Ms"]:
        if int(block["M"]) == int(m):
            return block["arms"][ARM]
    raise KeyError(m)


def ols(rows: list[dict]) -> dict:
    log_m = np.log(np.array([r["M"] for r in rows], dtype=np.float64))
    log_p = np.log(np.array([r["p"] for r in rows], dtype=np.float64))
    y = np.log(np.array([r["W"] for r in rows], dtype=np.float64))
    x = np.column_stack([np.ones(len(rows)), log_m, log_p])
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return {"c": float(beta[0]), "a": float(beta[1]), "b": float(beta[2]), "n": len(rows)}


def main() -> int:
    s2 = json.loads(S2.read_text())
    cells = {c["id"]: c for c in s2["cells"]}
    rows = []
    excluded = []
    for cell_id, p, grid in CELLS:
        cell = cells[cell_id]
        for m in grid:
            rec = arm_rec(cell, m)
            w = float(rec["W_plugin"])
            min_q = float(rec["min_q"])
            if m * min_q < H2_C0:
                excluded.append({"cell": cell_id, "M": m, "reason": "H2"})
                continue
            if w <= 0:
                excluded.append({"cell": cell_id, "M": m, "reason": "nonpositive_W_plugin"})
                continue
            rows.append({"cell": cell_id, "p": p, "M": m, "W": w})
    full = ols(rows)
    primes = sorted({r["p"] for r in rows})
    left = []
    for p in primes:
        sub = [r for r in rows if r["p"] != p]
        left.append({"left_out_p": p, **ols(sub)})
    n = float(len(left))
    a_i = np.array([e["a"] for e in left], dtype=np.float64)
    se_a = math.sqrt(((n - 1.0) / n) * float(np.sum((a_i - a_i.mean()) ** 2)))
    out = {
        "quantity": "unconstrained hat a for floor(Mx/p) on W_plugin",
        "arm": ARM,
        "n_rows": len(rows),
        "n_primes": len(primes),
        "exclusions": excluded,
        "full": full,
        "leave_one_prime": left,
        "se_a": se_a,
        "interval_a": [full["a"] - 1.96 * se_a, full["a"] + 1.96 * se_a],
        "SMALL_W_or_LARGE_W": False,
        "fit_of_a": False,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"a": full["a"], "b": full["b"], "n": full["n"], "n_primes": len(primes)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
