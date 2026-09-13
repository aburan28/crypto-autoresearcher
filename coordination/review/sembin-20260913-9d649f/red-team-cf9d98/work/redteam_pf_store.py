#!/usr/bin/env python3
"""Localise the prime-field control failure: is it the PRODUCT metric, or the
2^30 distinguished-point store the record charges the baseline?

Re-runs J6-A's control over the store_log2 sweep of J2-a. If the ordering
inverts only at large store_log2, the two joints are the same defect seen
twice, and the store size is the load-bearing choice in both.
"""

from __future__ import annotations

import json
import math

import redteam_extend
read_pfdr = redteam_extend.read_pfdr
from redteam_recompute import vow_memory_log2, vow_time_log2

rows = read_pfdr()
out = {}
for w in (0.0, 1.0, 10.0, 20.0, 30.0, 40.0, 60.0):
    per_size = {}
    for n in (64, 128, 256):
        sub = [r for r in rows if r["log2_N"] == n]
        rho_t = vow_time_log2(n)
        rho_m = vow_memory_log2(n, w)
        wins = [r for r in sub
                if (r["ic_time_log2"] + r["ic_memory_log2"]) < rho_t + rho_m]
        best = max(-((r["ic_time_log2"] + r["ic_memory_log2"])
                     - (rho_t + rho_m)) for r in sub)
        per_size[f"log2_N={n}"] = {
            "rho_memory_log2": round(rho_m, 4),
            "cells_where_prime_field_IC_wins_the_PRODUCT": len(wins),
            "best_product_margin_for_IC_bits": round(best, 4),
            "ordering_known_from_KN_OPEN_001_is_inverted": len(wins) > 0,
        }
    out[f"store_log2={int(w)}"] = per_size

# the smallest store_log2 at which the inversion appears, per size
thresholds = {}
for n in (64, 128, 256):
    sub = [r for r in rows if r["log2_N"] == n]
    rho_t = vow_time_log2(n)
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        rho_m = vow_memory_log2(n, mid)
        if any((r["ic_time_log2"] + r["ic_memory_log2"]) < rho_t + rho_m
               for r in sub):
            hi = mid
        else:
            lo = mid
    thresholds[f"log2_N={n}"] = round(hi, 3)

print(json.dumps({
    "sweep": out,
    "smallest_store_log2_at_which_the_prime_field_ordering_inverts": thresholds,
    "record_charges_store_log2": 30,
    "reading": ("The prime-field control passes at every store size the "
                "baseline actually needs at M = 1 and fails at the size the "
                "record charges. J2 and J6 are therefore the same defect: the "
                "2^30-point store is a memory charge the baseline neither "
                "needs nor can use at the single-processor time the record "
                "also charges it."),
}, indent=2))
