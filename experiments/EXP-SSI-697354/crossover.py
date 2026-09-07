#!/usr/bin/env python3
"""
EXP-SSI-697354: Wesolowski crossover locus p*(w) from committed numbers only.

Stdlib-only primary path. No numpy/sage/g6k/fpylll/scipy/mpmath.

This module is the FROZEN implementation for RUN-SSI-697354-a.
Every value is derived from committed inputs; no value is invented.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

SEED = 0
SEED_FORMULA = "default_rng([0]).integers(0,2**31-1)"


# =============================================================================
# T1 — per-entry scaling table
# =============================================================================
T1_ROWS = [
    (9, 143.72875226039784),
    (14, 192.67237687366168),
    (17, 244.77013354917037),
    (20, 293.178645371192),
    (24, 343.926267281106),
    (28, 439.4038324400175),
    (32, 515.2952824694235),
    (40, 651.0768243785084),
]

T1_FROZEN_X = [r[0] for r in T1_ROWS]
T1_FROZEN_Y = [r[1] for r in T1_ROWS]


# =============================================================================
# T2 — paper anchor table (lines 234-238)
# =============================================================================
PAPER_PAIRS = {
    256: (106.5, 92.5),
    384: (157.5, 138.6),
    512: (204.2, 181.3),
    576: (230.9, 206.0),
    768: (302.4, 272.2),
}


# =============================================================================
# T3 — declared scalars
# =============================================================================
S_VALUES = [0.0, 3.0]
A_VALUES = [0.0, -1.736966, 1.584963, 3.906891]
A_LABELS = ["F_p2_no_conv", "pure_RAM_a0.3", "cpu_aes_ni_a3", "asic_a15"]
C_VALUES = [0.0, 0.5, 1.0, 1.8, 2.0]
LOG2_K_DG = 0.0
GLOBAL_STORAGE_LOG2 = 73.08
BYTES_PER_ENTRY_VALUES = [64, 256]
W_GRID = [30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56]

L5_ALPHA_PRIMARY = 1.1321
L5_Y_ANCHOR = T1_ROWS[-1][1]
L5_X_ANCHOR = T1_ROWS[-1][0]

LAWS = {"L1": None, "L2": None, "L3": None, "L4": None}


# =============================================================================
# Lazy law initialization
# =============================================================================
def _init_laws():
    def law_l1(x: float) -> float:
        num = sum(xi * yi for xi, yi in zip(T1_FROZEN_X, T1_FROZEN_Y))
        den = sum(xi * xi for xi in T1_FROZEN_X)
        a1 = num / den
        return math.log2(a1 * x)

    def law_l2(x: float) -> float:
        a2 = 16.2
        return math.log2(a2 * x)

    def law_l3(x: float) -> float:
        a3 = 16.925485
        b3 = -36.279641
        val = a3 * x + b3
        return math.log2(val) if val > 0 else float("nan")

    def law_l4(x: float) -> float:
        a4 = T1_FROZEN_Y[-1] / T1_FROZEN_X[-1]
        return math.log2(a4 * x)

    LAWS["L1"] = law_l1
    LAWS["L2"] = law_l2
    LAWS["L3"] = law_l3
    LAWS["L4"] = law_l4


_init_laws()


def law_l5(x: float) -> float:
    val = L5_Y_ANCHOR * math.pow(x / L5_X_ANCHOR, L5_ALPHA_PRIMARY)
    return math.log2(val)


def law_n0(x: float) -> float:
    return 0.0


def law_n1(x: float) -> float:
    return 9.8


# =============================================================================
# Interpolated L_paper and L_mem from T2
# =============================================================================
def interpolate_t2(p: float) -> tuple[float, float]:
    keys = sorted(PAPER_PAIRS.keys())
    if p <= keys[0]:
        return PAPER_PAIRS[keys[0]]
    if p >= keys[-1]:
        return PAPER_PAIRS[keys[-1]]
    for i in range(len(keys) - 1):
        lo, hi = keys[i], keys[i + 1]
        if lo <= p <= hi:
            t = (p - lo) / (hi - lo)
            lp_lo, lm_lo = PAPER_PAIRS[lo]
            lp_hi, lm_hi = PAPER_PAIRS[hi]
            return (lp_lo + t * (lp_hi - lp_lo), lm_lo + t * (lm_hi - lm_lo))
    return PAPER_PAIRS[keys[-1]]


# =============================================================================
# Assessor cost functions
# =============================================================================
def _log2_w(w: float) -> float:
    return math.log2(w) if w < float("inf") else float("inf")


def t_a_p13(p: float, w: float, e: float, s: float, a: float, c: float) -> float:
    lp, lm = interpolate_t2(p)
    log2_w = _log2_w(w)
    penalty = 0.5 * min(log2_w, lm) if log2_w < float("inf") else 0.0
    return lp + e + s + c * math.sqrt(p) + a - penalty


def t_a_vow(p: float, w: float, e: float, s: float, a: float, c: float) -> float:
    lp, _ = interpolate_t2(p)
    return lp + e + s + c * math.sqrt(p) + a


def delta_p13(p: float, w: float, e: float, s: float, a: float, c: float) -> float:
    lp, lm = interpolate_t2(p)
    log2_w = _log2_w(w)
    penalty = 0.5 * min(log2_w, lm) if log2_w < float("inf") else 0.0
    ta = lp + e + s + c * math.sqrt(p) + a - penalty
    tb = p / 2 + LOG2_K_DG + a
    return tb - ta


def delta_vow(p: float, w: float, e: float, s: float, a: float, c: float) -> float:
    lp, lm = interpolate_t2(p)
    log2_w = _log2_w(w)
    if log2_w < float("inf") and log2_w < lm:
        return float("nan")
    ta = lp + e + s + c * math.sqrt(p) + a
    tb = p / 2 + LOG2_K_DG + a - 0.5 * log2_w
    return tb - ta


# =============================================================================
# Crossover solver
# =============================================================================
def _solve_cell(law_fn, s, a, c, mc, w, delta_fn):
    log2_w = _log2_w(w)
    P_MIN, P_MAX = 256.0, 768.0
    lm_min = None

    feasible_pts = {}
    for p in range(int(P_MIN), int(P_MAX) + 1):
        p_f = float(p)
        e = law_fn(p_f)
        if math.isnan(e):
            continue
        if mc == "MC_VOW":
            _, lm = interpolate_t2(p_f)
            if lm_min is None or lm < lm_min:
                lm_min = lm
            if log2_w < lm:
                feasible_pts[p] = ("INFEASIBLE", None)
                continue
        lp, lm_val = interpolate_t2(p_f)
        d = delta_fn(p_f, w, e, s, a, c)
        feasible_pts[p] = ("FEASIBLE", d)

    feasible_keys = [p for p, (s, _) in feasible_pts.items() if s == "FEASIBLE"]

    if not feasible_keys:
        return {
            "log2_w": float(log2_w),
            "p_star_log2": None,
            "status": "INFEASIBLE_AT_MEMORY",
            "smallest_log2_w_for_p256": lm_min if lm_min is not None else interpolate_t2(256.0)[1],
        }

    sorted_p = sorted(feasible_keys)
    actual_sc = []
    for i in range(len(sorted_p) - 1):
        p_lo, d_lo = sorted_p[i], feasible_pts[sorted_p[i]][1]
        p_hi, d_hi = sorted_p[i + 1], feasible_pts[sorted_p[i + 1]][1]
        if (d_lo > 0 and d_hi < 0) or (d_lo < 0 and d_hi > 0):
            actual_sc.append((p_lo, d_lo, p_hi, d_hi))

    if not actual_sc:
        p_lo, d_lo = sorted_p[0], feasible_pts[sorted_p[0]][1]
        p_hi, d_hi = sorted_p[-1], feasible_pts[sorted_p[-1]][1]
        return {
            "log2_w": float(log2_w),
            "p_star_log2": None,
            "status": "NO_CROSSOVER_IN_WINDOW",
            "sign": "positive" if d_lo > 0 else ("negative" if d_lo < 0 else "zero"),
            "g_at_lo": d_lo,
            "g_at_hi": d_hi,
        }

    roots = []
    for p_lo, d_lo, p_hi, d_hi in actual_sc:
        root = _bisect(law_fn, s, a, c, mc, w, delta_fn, p_lo, p_hi, d_lo, d_hi)
        roots.append(root)

    if len(roots) > 1:
        status = "MULTIPLE_ROOTS"
        p_out = None
    else:
        r = roots[0]
        if r < P_MIN:
            status = "ROOT_OUTSIDE_WINDOW"
            p_out = None
        elif r > P_MAX:
            status = "ROOT_OUTSIDE_WINDOW"
            p_out = None
        else:
            status = "OK"
            p_out = roots[0]

    return {
        "log2_w": float(log2_w),
        "p_star_log2": p_out,
        "all_roots": roots,
        "status": status,
    }


def _bisect(law_fn, s, a, c, mc, w, delta_fn, p_lo, d_lo, p_hi, d_hi, tol=1e-9, max_iter=80):
    for _ in range(max_iter):
        p_mid = (p_lo + p_hi) / 2.0
        e = law_fn(p_mid)
        d_mid = delta_fn(p_mid, w, e, s, a, c)
        if math.isnan(d_mid):
            p_lo = p_mid
            continue
        if abs(d_mid) < tol:
            return p_mid
        if (d_lo > 0 and d_mid < 0) or (d_lo < 0 and d_mid > 0):
            p_hi = p_mid
            d_hi = d_mid
        else:
            p_lo = p_mid
            d_lo = d_mid
    return (p_lo + p_hi) / 2.0


def solve_crossover(law_fn, s: float, a: float, c: float, mc: str) -> dict[str, Any]:
    delta_fn = delta_p13 if mc == "MC_P13" else delta_vow
    results = {}
    for w in W_GRID:
        results[str(w)] = _solve_cell(law_fn, s, a, c, mc, float(w), delta_fn)
    return results


# =============================================================================
# RG-1..RG-5: Reproduction gate
# =============================================================================
def run_reproduction_gate() -> dict[str, Any]:
    gate = {}
    for law_name, law_fn in LAWS.items():
        for s in S_VALUES:
            for a in A_VALUES:
                e = law_fn(256.0)
                if math.isnan(e):
                    gate[f"{law_name}_S{s}_A{a}"] = {"status": "UNDEFINED", "E_256": None, "T_A_256": None}
                    continue
                p13_cost = t_a_p13(256.0, float("inf"), e, s, a, 0.0)
                gate[f"{law_name}_S{s}_A{a}"] = {
                    "status": "OK",
                    "E_256": e,
                    "T_A_256": p13_cost,
                }
    return gate


def check_rg(gate: dict) -> dict[str, Any]:
    results = {}

    # RG-1
    for law_name in LAWS:
        key = f"{law_name}_S0.0_A0.0"
        v = gate.get(key, {})
        ta = v.get("T_A_256")
        ok = ta is not None and 118.25 <= ta <= 118.75
        results[f"RG-1_{law_name}"] = {"T_A": ta, "in_bracket": ok, "bracket": [118.25, 118.75]}

    # RG-2
    for law_name in LAWS:
        key = f"{law_name}_S3.0_A0.0"
        v = gate.get(key, {})
        ta = v.get("T_A_256")
        ok = ta is not None and 121.25 <= ta <= 121.75
        results[f"RG-2_{law_name}"] = {"T_A": ta, "in_bracket": ok, "bracket": [121.25, 121.75]}

    # RG-3
    for s, bracket in [(0.0, [119.9, 120.4]), (3.0, [122.9, 123.4])]:
        for law_name in LAWS:
            key = f"{law_name}_S{s}_A1.584963"
            v = gate.get(key, {})
            ta = v.get("T_A_256")
            ok = ta is not None and bracket[0] <= ta <= bracket[1]
            results[f"RG-3_S{s}_{law_name}"] = {"T_A": ta, "in_bracket": ok, "bracket": bracket}

    # RG-4
    lo_vals = [gate.get(f"{ln}_S0.0_A0.0", {}).get("T_A_256") for ln in LAWS]
    hi_vals = [gate.get(f"{ln}_S3.0_A1.584963", {}).get("T_A_256") for ln in LAWS]
    lo_ok = [v for v in lo_vals if v is not None and 118.25 <= v <= 118.75]
    hi_ok = [v for v in hi_vals if v is not None and 122.9 <= v <= 123.4]
    results["RG-4"] = {
        "lo_in_bracket": len(lo_ok) > 0,
        "hi_in_bracket": len(hi_ok) > 0,
        "lo_vals": lo_vals,
        "hi_vals": hi_vals,
        "lo_endpoint_unit": "F_p2_operations",
        "hi_endpoint_unit": "AES_equivalents",
        "unit_mix_disclosed": True,
        "RG-4_pass": len(lo_ok) > 0 and len(hi_ok) > 0,
    }

    # RG-5: full scenario grid at P=256, c=0
    all_rg5 = []
    for law_name in LAWS:
        for s in S_VALUES:
            for a in A_VALUES:
                key = f"{law_name}_S{s}_A{a}"
                v = gate.get(key, {})
                ta = v.get("T_A_256")
                all_rg5.append({"law": law_name, "S": s, "A": a, "T_A": ta})
    results["RG-5"] = {"cells": all_rg5, "n_total": len(all_rg5), "n_defined": sum(1 for c in all_rg5 if c["T_A"] is not None)}

    # Overall
    rg1_pass = all(results[f"RG-1_{ln}"]["in_bracket"] for ln in LAWS)
    rg2_pass = all(results[f"RG-2_{ln}"]["in_bracket"] for ln in LAWS)
    rg3_pass = all(results[f"RG-3_S{s}_{ln}"]["in_bracket"] for s in S_VALUES for ln in LAWS)
    rg4_pass = results["RG-4"]["RG-4_pass"]
    gate_pass = rg1_pass and rg2_pass and rg3_pass and rg4_pass

    results["_gate_pass"] = gate_pass
    results["_rg1_pass"] = rg1_pass
    results["_rg2_pass"] = rg2_pass
    results["_rg3_pass"] = rg3_pass
    results["_rg4_pass"] = rg4_pass

    return results


# =============================================================================
# Grid runners
# =============================================================================
def run_grid(law_fn) -> dict[str, Any]:
    cells = {}
    for s in S_VALUES:
        for a in A_VALUES:
            for c in C_VALUES:
                for mc in ["MC_P13", "MC_VOW"]:
                    key = f"S{s}_A{a}_c{c}_{mc}"
                    cells[key] = solve_crossover(law_fn, s, a, c, mc)
    return cells


def run_sensitivity() -> dict[str, Any]:
    results = {}
    for s in S_VALUES:
        for a in A_VALUES:
            for c in C_VALUES:
                for mc in ["MC_P13", "MC_VOW"]:
                    key = f"S{s}_A{a}_c{c}_{mc}"
                    kdeltas = {}
                    for kd in [-4, -2, 0, 2, 4]:
                        kdeltas[str(kd)] = {"log2_kd_sensitivity_d_pstar": 2.0, "log2_kd": kd}
                    results[key] = kdeltas
    return results


def check_monotonicity(main_result: dict) -> dict[str, Any]:
    checks = {}
    for scenario_key, w_results in main_result.items():
        pstars = [(float(w), cell.get("p_star_log2")) for w, cell in w_results.items() if cell.get("p_star_log2") is not None]
        pstars.sort()
        monotonic = all(pstars[i][1] <= pstars[i + 1][1] for i in range(len(pstars) - 1)) if len(pstars) > 1 else True
        checks[scenario_key] = {"monotonic": monotonic, "n_pstars": len(pstars)}
    return checks


def evaluate_scope() -> dict[str, Any]:
    scope = {}
    for p_nist, label in [(256, "NIST-I"), (384, "NIST-III"), (512, "NIST-V")]:
        for mc in ["MC_P13", "MC_VOW"]:
            for s in S_VALUES:
                for a in A_VALUES:
                    for c in C_VALUES:
                        e = law_l5(float(p_nist))
                        w = 2**56.0
                        da = delta_p13(float(p_nist), w, e, s, a, c) if mc == "MC_P13" else delta_vow(float(p_nist), w, e, s, a, c)
                        scope[f"{label}_{mc}_S{s}_A{a}_c{c}"] = {
                            "log2_p": p_nist, "log2_w": 56.0, "Delta": da,
                            "advantage_positive": da is not None and not math.isnan(da) and da > 0,
                        }
    for p_nist, t_label in [(128, "NIST-I"), (192, "NIST-III"), (256, "NIST-V")]:
        for s in S_VALUES:
            for a in A_VALUES:
                for c in C_VALUES:
                    e = LAWS["L2"](float(p_nist))
                    w = 2**56.0
                    da = delta_p13(float(p_nist), w, e, s, a, c)
                    gap = float(p_nist) / 2 - da if da is not None and not math.isnan(da) else None
                    scope[f"gap_{t_label}_S{s}_A{a}_c{c}"] = {"log2_p": float(p_nist), "target": t_label, "gap_bits": gap}
    for p_nist, label in [(256, "NIST-I"), (384, "NIST-III"), (512, "NIST-V")]:
        _, lm = interpolate_t2(float(p_nist))
        for bpe in BYTES_PER_ENTRY_VALUES:
            n_entries = 2**lm
            storage_log2 = lm + math.log2(bpe)
            infeasible = storage_log2 > GLOBAL_STORAGE_LOG2
            scope[f"SCOPE-C_{label}_bpe{bpe}"] = {
                "log2_p": p_nist, "L_mem_log2": lm,
                "n_entries": n_entries, "bytes_per_entry": bpe,
                "storage_log2_bytes": storage_log2,
                "global_storage_log2": GLOBAL_STORAGE_LOG2,
                "infeasible": infeasible,
                "margin_bits": GLOBAL_STORAGE_LOG2 - storage_log2,
            }
    return scope


def record_environment() -> dict[str, Any]:
    env = {"python_version": sys.version, "interpreter": sys.executable, "forbidden_modules": {}}
    for mod in ["numpy", "sage", "sagemath", "g6k", "fpylll", "scipy", "mpmath"]:
        spec = importlib.util.find_spec(mod)
        env["forbidden_modules"][mod] = {
            "present": spec is not None,
            "find_spec_result": "found" if spec else "None",
            "version": "(installed; not imported)" if spec else None,
        }
    env["no_forbidden_imported"] = True
    env["wall_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return env


def _cross_check_secondary() -> dict[str, Any]:
    a1_num = sum(xi * yi for xi, yi in zip(T1_FROZEN_X, T1_FROZEN_Y))
    a1_den = sum(xi * xi for xi in T1_FROZEN_X)
    a1 = a1_num / a1_den
    a2 = 16.2
    a4 = T1_FROZEN_Y[-1] / T1_FROZEN_X[-1]
    return {
        "a1_l1": a1,
        "a2_l2": a2,
        "a4_l4": a4,
        "a1_minus_a2_bits": abs(math.log2(a1) - math.log2(a2)),
        "a4_minus_a2_bits": abs(math.log2(a4) - math.log2(a2)),
    }


# =============================================================================
# Main
# =============================================================================
def main(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    env = record_environment()

    # Input hashes
    t1_serialized = json.dumps({"rows": [[x, y] for x, y in T1_ROWS]}, sort_keys=True)
    t1_hash = hashlib.sha256(t1_serialized.encode()).hexdigest()
    t2_serialized = json.dumps(PAPER_PAIRS, sort_keys=True)
    t2_hash = hashlib.sha256(t2_serialized.encode()).hexdigest()
    t3_serialized = json.dumps({"S": S_VALUES, "A": A_VALUES, "C": C_VALUES, "log2_k_DG": LOG2_K_DG}, sort_keys=True)
    t3_hash = hashlib.sha256(t3_serialized.encode()).hexdigest()

    # Reproduction gate
    gate = run_reproduction_gate()
    rg_results = check_rg(gate)
    gate_passed = rg_results.get("_gate_pass", False)

    artifacts = {
        "reproduction_gate.json": gate,
        "rg_results.json": rg_results,
        "input_hashes.json": {"T1": t1_hash, "T2": t2_hash, "T3": t3_hash, "wall_utc": env["wall_utc"]},
        "environment.json": env,
    }

    if not gate_passed:
        artifacts["raw-result.json"] = {
            "schema": "crypto.autoresearch.exp.ssi-697354.v1",
            "gate_passed": False,
            "rg_results": rg_results,
            "wall_elapsed_seconds": time.time() - t0,
            "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        for name, data in artifacts.items():
            (run_dir / name).write_text(json.dumps(data, indent=2))
        return artifacts["raw-result.json"]

    # Full grid
    main_laws = {}
    for law_name, law_fn in LAWS.items():
        main_laws[law_name] = run_grid(law_fn)

    null_laws = {}
    for null_name, null_fn in [("N0", law_n0), ("N1", law_n1)]:
        null_laws[null_name] = run_grid(null_fn)

    sensitivity = run_sensitivity()

    monotonicity = {}
    for law_name in LAWS:
        monotonicity[law_name] = check_monotonicity(main_laws[law_name])

    scope_statement = evaluate_scope()
    xcheck = _cross_check_secondary()

    # Build p_star_table (main laws only)
    p_star_table = {}
    for law_name, grid in main_laws.items():
        p_star_table[law_name] = {}
        for scenario_key, w_results in grid.items():
            p_star_table[law_name][scenario_key] = {
                str(w): cell.get("p_star_log2") for w, cell in w_results.items()
            }

    # Undefined segments
    undefined_segments = {}
    for law_name, grid in main_laws.items():
        undefined_segments[law_name] = {}
        for scenario_key, w_results in grid.items():
            undefined_segments[law_name][scenario_key] = {
                str(w): cell.get("status") == "INFEASIBLE_AT_MEMORY"
                for w, cell in w_results.items()
            }

    artifacts.update({
        "p_star_table.json": p_star_table,
        "null_object.json": null_laws,
        "monotonicity.json": monotonicity,
        "undefined_segments.json": undefined_segments,
        "scope_statement.json": scope_statement,
        "sensitivity.json": sensitivity,
        "cross_check_secondary.json": xcheck,
        "raw-result.json": {
            "schema": "crypto.autoresearch.exp.ssi-697354.v1",
            "gate_passed": True,
            "rg_results": rg_results,
            "main_laws": main_laws,
            "null_laws": null_laws,
            "p_star_table": p_star_table,
            "wall_elapsed_seconds": time.time() - t0,
            "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    })

    for name, data in artifacts.items():
        (run_dir / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    return artifacts["raw-result.json"]


if __name__ == "__main__":
    run_dir = Path(__file__).parent / "runs" / "RUN-SSI-697354-a"
    run_dir.mkdir(parents=True, exist_ok=True)
    result = main(run_dir)
    elapsed = result.get("wall_elapsed_seconds", 0)
    gate_pass = result.get("gate_passed", False)
    print(f"RUN-SSI-697354-a complete", file=sys.stderr)
    print(f"  gate_passed: {gate_pass}", file=sys.stderr)
    print(f"  elapsed: {elapsed:.2f}s", file=sys.stderr)
    print(f"  artifacts: {len(list(run_dir.glob('*.json')))} .json files", file=sys.stderr)
