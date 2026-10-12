#!/usr/bin/env python3
"""TASK-20261001-b2c916 / JV-2 side measurement: what the 0.1-bit E-2
disagreement rule can resolve on the protocol's own d grid.

Uses the COMMITTED, hash-checked model_v2.evaluate unchanged. For each degree,
the store-free MITM minimum (C-2 guard applied) is taken over m in 2..16 on
  (i)  the protocol grid  d = 1.0 + 0.25 k   (what RUN-SEMBIN-be48b7 did), and
  (ii) a fine grid        d = 1.0 + 0.001 k  (a continuous-d proxy),
and the two margins against VOW are compared. Also checks the identity
CALLS == PROBE - FILL at even m (store-free MITM), which places every even-m
optimum within log2(s/(s-1)) bits of the C-2 edge.

This is not a re-derivation of E-2 (JV-1 and the blind re-deriver own that); it
measures only how far the committed driver's own figure moves when nothing but
the grid step changes.
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # never write __pycache__ into committed code dirs

import hashlib
import importlib.util
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
EXP = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c")
DRV = os.path.join(EXP, "code", "v2", "model_v2.py")
DIG = json.load(open(os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7", "artifact-digests.json")))
E2 = {97: 16.54, 109: 17.69, 131: 19.12, 163: 21.55, 191: 23.55, 233: 26.22, 239: 26.55,
      283: 29.00, 409: 35.49, 571: 42.70}


def load():
    if hashlib.sha256(open(DRV, "rb").read()).hexdigest() != DIG["code_v2"][os.path.relpath(DRV, REPO)]:
        raise SystemExit("driver hash mismatch")
    spec = importlib.util.spec_from_file_location("model_v2_committed", DRV)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    raw = json.load(open(os.path.join(EXP, "runs", "RUN-SEMBIN-be48b7", "raw-result.json")))
    mod.set_subgroup_order_log2(raw["inputs"]["subgroup_order_131"]["log2_r"])
    return mod


def best(mod, n, step, d_hi=None):
    top = d_hi if d_hi is not None else 120.0
    b = None
    for m in range(2, 17):
        k = 0
        while True:
            d = 1.0 + k * step
            k += 1
            if d > min(top, n) + 1e-9:
                break
            c = mod.evaluate(n, "MITM", m, d, None)
            if c[2] < 0.0:
                continue
            if b is None or c[6] < b[0]:
                b = (c[6], m, round(d, 4), c[0], c[2])
    return b


def main():
    mod = load()
    out = {"rows": {}, "identity_check": {}}
    # identity: at even m, store-free MITM, CALLS == PROBE - FILL exactly (algebraically)
    worst = 0.0
    for n in mod.DEGREES:
        for m in range(2, 17, 2):
            for d in (5.0, 16.25, 20.5, 33.75, 54.5):
                c = mod.evaluate(n, "MITM", m, d, None)
                worst = max(worst, abs(c[2] - (c[3] - c[4])))
    out["identity_check"] = {"claim": "even m, MITM: CALLS == PROBE - FILL",
                             "max_abs_residual_bits": worst,
                             "consequence": "in-domain (CALLS >= 0) <=> PROBE >= FILL; the unconstrained optimum of "
                                            "log2(2^PROBE + 2^FILL) sits at PROBE - FILL = log2(s/(s-1)), i.e. "
                                            "CALLS = log2(s/(s-1)) bits inside the C-2 edge"}
    for n in mod.DEGREES:
        vow = mod.vow_column(n)
        g = best(mod, n, 0.25)
        f = best(mod, n, 0.001)
        out["rows"][n] = {
            "grid_0.25": {"margin_vs_VOW": round(g[0] - vow, 4), "m": g[1], "d": g[2], "s": g[3], "CALLS": round(g[4], 4)},
            "grid_0.001": {"margin_vs_VOW": round(f[0] - vow, 4), "m": f[1], "d": f[2], "s": f[3], "CALLS": round(f[4], 4)},
            "grid_effect_bits": round(g[0] - f[0], 4),
            "E2": E2[n],
            "v2_minus_E2": round(g[0] - vow - E2[n], 4),
            "fine_minus_E2": round(f[0] - vow - E2[n], 4),
        }
    out["max_grid_effect_bits"] = max(r["grid_effect_bits"] for r in out["rows"].values())
    with open(os.path.join(HERE, "jv2_out", "jv2_grid_resolution.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["identity_check"], indent=1))
    for n, r in out["rows"].items():
        print(n, r)
    print("max grid effect", out["max_grid_effect_bits"])


if __name__ == "__main__":
    main()
