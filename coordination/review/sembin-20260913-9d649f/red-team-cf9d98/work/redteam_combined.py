#!/usr/bin/env python3
"""Combined-correction crossover for TASK-20260913-cf9d98.

Applies every asymmetry located in J2 at once, in BOTH directions, so the net
is a computed number rather than an addition of separately-quoted shifts.

Charged against the record:                    direction
  coherent vOW operating point (store 2^1)     up   (record over-credits Semaev)
  FIPS cofactor h on the baseline's group      up
  negation / Frobenius automorphism speedup    up
Charged for the record:
  ceiled k, the reading Section 3 defines      down (record under-credits Semaev)
  unit conversion: a group op is 2^u field ops down
  m re-optimised under the metric              down
"""

from __future__ import annotations

import json
import math

from redteam_recompute import (semaev_memory_log2, semaev_time_log2,
                               log2_add, log2_factorial, vow_time_log2)

M_RANGE = range(2, 31)


def s_time(n, m, ceiled):
    if not ceiled:
        return semaev_time_log2(n, m)
    k = float(-(-n // m))
    return log2_add(log2_factorial(m) + k + (n - m * k) + 12.0 * math.log2(n),
                    2.0 * k)


def semaev_product(n, storage, ceiled, reopt):
    ms = M_RANGE if reopt else [min(M_RANGE, key=lambda mm: s_time(n, mm, ceiled))]
    return min(s_time(n, m, ceiled) + semaev_memory_log2(n, m, storage)
               for m in ms)


def vow_product(n, store_log2, h, u, auto):
    return (vow_time_log2(n, 0.0, h, 0.886, auto) + u
            + store_log2 + math.log2(3.0 * n))


def crossover(storage, **kw):
    for n in range(250, 1201):
        if semaev_product(n, storage, kw["ceiled"], kw["reopt"]) < vow_product(
                n, kw["store"], kw["h"], kw["u"], kw["auto"]):
            return n
    return None


def margin(n, storage, **kw):
    return round(vow_product(n, kw["store"], kw["h"], kw["u"], kw["auto"])
                 - semaev_product(n, storage, kw["ceiled"], kw["reopt"]), 4)


SCENARIOS = {
    "S0 record as published":
        dict(store=30.0, h=1, u=0.0, auto=0.0, ceiled=False, reopt=False),
    "S1 + coherent vOW operating point only":
        dict(store=1.0, h=1, u=0.0, auto=0.0, ceiled=False, reopt=False),
    "S2 + ceiled k only (favours Semaev)":
        dict(store=30.0, h=1, u=0.0, auto=0.0, ceiled=True, reopt=True),
    "S3 + unit conversion 2^5 only (favours Semaev)":
        dict(store=30.0, h=1, u=5.0, auto=0.0, ceiled=False, reopt=False),
    "S4 ALL corrections, B-409 (h=2, negation only)":
        dict(store=1.0, h=2, u=5.0, auto=0.5, ceiled=True, reopt=True),
    "S5 ALL corrections, K-409 (h=4, Frobenius sqrt(2n))":
        dict(store=1.0, h=4, u=5.0, auto=4.84, ceiled=True, reopt=True),
    "S6 ALL corrections but NO unit conversion (u=0), B-409":
        dict(store=1.0, h=2, u=0.0, auto=0.5, ceiled=True, reopt=True),
    "S7 ALL pro-Semaev corrections only, record baseline":
        dict(store=30.0, h=1, u=5.0, auto=0.0, ceiled=True, reopt=True),
}

out = {}
for name, kw in SCENARIOS.items():
    out[name] = {
        s: {"crossover": crossover(s, **kw),
            "margin_409": margin(409, s, **kw),
            "margin_571": margin(571, s, **kw),
            "verdict_409": "semaev" if margin(409, s, **kw) > 0 else "vow",
            "verdict_571": "semaev" if margin(571, s, **kw) > 0 else "vow"}
        for s in ("dense", "semaev_sparse")}

out["_readings_agree_at_409"] = {
    name: (v["dense"]["verdict_409"] == v["semaev_sparse"]["verdict_409"])
    for name, v in out.items() if not name.startswith("_")}

print(json.dumps(out, indent=2))
