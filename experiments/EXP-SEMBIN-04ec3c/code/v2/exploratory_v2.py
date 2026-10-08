#!/usr/bin/env python3
"""Exploratory sensitivity columns X-1 .. X-8 (AMD-20261001-e61f2b change C-7).

NON-GATING AND NEVER CONFIRMATORY. None of these may enter a primary sub-rho
count or a scoring line, or be quoted without its label. Each is computed under
C-1's construction charge unless its own text says otherwise, over m in 2..16
and the v1 d grid (1.0 .. n, step 0.25), with the C-2 domain guard
(CALLS >= 0, using the column's own K and TPR) applied to every minimum.

Interpretations of the one-line amendment texts are stated per column in the
`interpretation` field and repeated in the manifest.
"""
from __future__ import annotations

import math

LOG2_7 = math.log2(7.0)


def _lsum(xs):
    top = max(xs)
    return top + math.log2(sum(2.0 ** (x - top) for x in xs))


def _grid(bound):
    k = 0
    while True:
        d = 1.0 + 0.25 * k
        if d > bound + 1e-9:
            return
        yield d
        k += 1


def _better(best, cand):
    return best is None or cand["TOTAL"] < best["TOTAL"]


def _row(best, vow, extra_cols=None):
    if best is None:
        return {"in_domain_cells": 0, "note": "no in-domain cell"}
    r = dict(best)
    r["margin_vs_VOW_bits"] = r["TOTAL"] - vow
    for name, val in (extra_cols or {}).items():
        r[f"margin_vs_{name}_bits"] = None if val is None else r["TOTAL"] - val
    return r


def x1_truncated_s_factorial(drv, degrees, budgets):
    """X-1 truncated-MITM relation cost: s! in place of m! (blind V4)."""
    out = []
    for n in degrees:
        N = drv.log2_N(n)
        vow = drv.vow_column(n)
        for b in budgets:
            best = None
            for m in range(2, 17):
                S = m // 2
                for d in _grid(float(n)):
                    s = S if b is None else min(S, math.floor(b / d))
                    if s < 1:
                        continue
                    L = math.log2(math.factorial(s))
                    TPR = N + L - m * d
                    CALLS = d + TPR
                    if CALLS < 0:
                        continue
                    PROBE = d + TPR + (m - s) * d
                    T = _lsum((PROBE, s * d, 2.0 * d))
                    c = {"TOTAL": T, "m": m, "d": d, "s": s, "log2_table_entries": s * d}
                    if _better(best, c):
                        best = c
            out.append({"n": n, "B": "unlimited" if b is None else b,
                        **_row(best, vow)})
    return {"label": "X-1 (blind V4): truncated-MITM relation cost with s! in place of m!",
            "interpretation": "MITM_CAPPED law s = min(S, floor(log2 B / d)), cells with s >= 1 only; L = log2(s!); construction charged; LA = 2d",
            "rows": out}


def _mitm_family_min(drv, n, N, *, K_shift=0.0, la_extra=None, fill_shift=0.0,
                     la_shift=0.0, probe_only=False):
    best = None
    for m in range(2, 17):
        S = m // 2
        L = math.log2(math.factorial(m))
        for d in _grid(float(n)):
            s = S
            K = d + K_shift
            TPR = N + L - m * d
            CALLS = K + TPR
            if CALLS < 0:
                continue
            PROBE = K + TPR + (m - s) * d
            LA = 2.0 * d + la_shift + (0.0 if la_extra is None else la_extra(m))
            if probe_only:
                T = _lsum((PROBE, LA))
            else:
                FILL = s * d + fill_shift if s >= 1 else 0.0
                T = _lsum((PROBE, FILL, LA))
            c = {"TOTAL": T, "m": m, "d": d, "s": s,
                 "log2_table_entries": s * d + fill_shift}
            if _better(best, c):
                best = c
    return best


def x2_K_d_minus_1(drv, degrees):
    rows = []
    for n in degrees:
        best = _mitm_family_min(drv, n, drv.log2_N(n), K_shift=-1.0)
        rows.append({"n": n, **_row(best, drv.vow_column(n))})
    return {"label": "X-2 (blind D1): K = d - 1 (negation-closed F)",
            "interpretation": "store-free MITM law (s = S), construction charged, K = d - 1 in PROBE and CALLS",
            "rows": rows}


def x3_la_weight(drv, degrees):
    rows = []
    for n in degrees:
        a = _mitm_family_min(drv, n, drv.log2_N(n), la_extra=lambda m: math.log2(m))
        b = _mitm_family_min(drv, n, drv.log2_N(n),
                             la_extra=lambda m: math.log2(m) + math.log2(3.0))
        rows.append({"n": n,
                     "LA_log2m_plus_2d": _row(a, drv.vow_column(n)),
                     "LA_log2m_plus_2d_plus_log2_3": _row(b, drv.vow_column(n))})
    return {"label": "X-3 (blind D2, V6): LA = log2 m + 2d, and the same plus log2 3",
            "interpretation": "store-free MITM law (s = S), construction charged",
            "rows": rows}


def x4_cofactor_131(drv):
    N4 = drv.log2_N(131) + 2.0
    best = _mitm_family_min(drv, 131, N4)
    vow4 = drv.LOG2_VOW_CONST + N4 / 2.0
    return {"label": "X-4 (blind V5): N = log2(4r) at n = 131",
            "interpretation": "store-free MITM law (s = S), construction charged; margins against the primary VOW (from r), against VOW recomputed from 4r, and PUB",
            "N_used": N4,
            "row": _row(best, drv.vow_column(131),
                        {"VOW_recomputed_from_4r": vow4, "PUB": drv.PUB_131}),
            "VOW_recomputed_from_4r": vow4}


def x5_vow_golden_collision(drv, degrees, budgets):
    rows = []
    for n in degrees:
        N = drv.log2_N(n)
        vow = drv.vow_column(n)
        for b in budgets:
            best = None
            for m in range(4, 17):
                S = m // 2
                L = math.log2(math.factorial(m))
                for d in _grid(float(n)):
                    TPR = N + L - m * d
                    CALLS = d + TPR
                    if CALLS < 0:
                        continue
                    for s in range(1, S):
                        if s * d < 10.0:
                            continue
                        if b is not None and s * d > b:
                            continue
                        o = LOG2_7 + (m - S) * d + (S - s) * d / 2.0
                        PROBE = d + TPR + o
                        T = _lsum((PROBE, 2.0 * d))
                        c = {"TOTAL": T, "m": m, "d": d, "s": s,
                             "log2_memory_per_target_entries": s * d}
                        if _better(best, c):
                            best = c
            rows.append({"n": n, "B": "unlimited" if b is None else b, **_row(best, vow)})
    return {"label": "X-5 (J3 RC3): oracle VOW_GC, o = log2 7 + (m-S)d + (S-s)d/2 for s < S",
            "interpretation": "integer s in 1..S-1 with per-target memory s*d >= 10 (and s*d <= log2 B for a finite budget); no shared-table fill term; TOTAL = log2(2^PROBE + 2^LA); m >= 4 so that s < S admits s >= 1",
            "rows": rows}


def x6_pcs_batch(drv, degrees):
    rows = []
    for n in degrees:
        N = drv.log2_N(n)
        vow = drv.vow_column(n)
        best_rel, best_la = None, None
        for d in _grid(float(n)):
            w = d
            rel = 2.0 + d + (N - w) / 2.0
            c1 = {"TOTAL": rel, "d": d, "w": w}
            c2 = {"TOTAL": _lsum((rel, 2.0 * d)), "d": d, "w": w}
            if _better(best_rel, c1):
                best_rel = c1
            if _better(best_la, c2):
                best_la = c2
        r1, r2 = _row(best_rel, vow), _row(best_la, vow)
        for r in (r1, r2):
            r["argmin_at_lower_d_bound"] = (r["d"] == 1.0)
        rows.append({"n": n, "relation_formula_alone": r1, "relation_plus_LA_2d": r2})
    return {"label": "X-6 (J3 RC3): relation model PCS_BATCH, total = 2 + d + (N - w)/2 for w <= d",
            "interpretation": "w = d (the formula decreases in w, so w = d minimises it under w <= d); reported as written and with LA = 2d added; no m dependence; the argmin sits at the lower d bound and is bound-tracking",
            "rows": rows}


def x7_orbit_quotient(drv):
    rows = []
    for n in (131, 163):
        q = math.log2(2.0 * n)
        best = _mitm_family_min(drv, n, drv.log2_N(n), K_shift=-q,
                                fill_shift=-q, la_shift=-2.0 * q)
        vow = drv.vow_column(n)
        rows.append({"n": n, "log2_2n": q,
                     **_row(best, vow, {"VOW_minus_log2_sqrt_2n": vow - q / 2.0,
                                        "PUB": drv.pub_column(n)})})
    return {"label": "X-7 (J3 section 4; TASK-20260929-c05f6e DESIGN.md section 7): Frobenius x negation orbit quotient",
            "interpretation": "store-free MITM law (s = S); K, FILL and store reduced by log2(2n), LA by 2 log2(2n); domain guard on CALLS = K' + TPR",
            "rows": rows}


def x8_cofactor_two_degrees(drv):
    rows = []
    for n in (79, 89):
        N = float(n - 1)
        vow = drv.LOG2_VOW_CONST + N / 2.0
        cc = _mitm_family_min(drv, n, N)
        po = _mitm_family_min(drv, n, N, probe_only=True)
        rows.append({"n": n, "N_used": N, "VOW": vow,
                     "construction_charged": _row(cc, vow),
                     "probe_only_NOT_A_COST": _row(po, vow)})
    return {"label": "X-8 (J4-6): rows at n = 79 and n = 89 with N = n - 1 (cofactor 2)",
            "interpretation": "store-free MITM law (s = S); probe-only = log2(2^PROBE + 2^LA), not a cost; domain guard applied to both",
            "rows": rows}


def all_columns(drv):
    degs = drv.DEGREES
    return {
        "X-1": x1_truncated_s_factorial(drv, degs, drv.BUDGETS),
        "X-2": x2_K_d_minus_1(drv, degs),
        "X-3": x3_la_weight(drv, degs),
        "X-4": x4_cofactor_131(drv),
        "X-5": x5_vow_golden_collision(drv, degs, drv.BUDGETS),
        "X-6": x6_pcs_batch(drv, degs),
        "X-7": x7_orbit_quotient(drv),
        "X-8": x8_cofactor_two_degrees(drv),
    }
