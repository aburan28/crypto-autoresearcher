#!/usr/bin/env python3
"""cost_table.py -- derivation aid for EXP-PFDR-c04716 (zero-run static derivation).

This is NOT a solver, NOT an experiment and NOT a run.  It performs exact
integer arithmetic on binomial coefficients and a real-valued balance solver,
and emits the conditional cost table of IDEA-20260903-dcf857 / H-PFDR-06fd60
so that every hand value in those records can be checked mechanically.
Nothing here touches a curve, a Macaulay matrix, a Groebner basis or a
sampled point.  Every number it emits is DERIVED (estimate), never measured,
and every bounded-slice number is CONDITIONAL on HEUR-001 of H-PFDR-06fd60.

Standard library only.  Deterministic (no randomness of any kind).

COST MODEL (IDEA-20260903-dcf857 claim (A), frozen in the contract inputs)
  n = m s digit variables (d = 2), B = 2^s.
  Ncols(n', D) = sum_{i <= D} binom(n', i)            (multilinear monomials)
  C(k)         = 2^k * Ncols(n - k, D(k))^omega        (k digits guessed)
  null slice    D(k) = d_reg(k) = ceil(((n - k) + 2m) / 2)
  bounded slice D(k) = min(D_0, d_reg(k))               (HEUR-001)
  balance       B = (m! 2^m C N)^{1/(m+1)},  T = 2 (m! 2^m C N)^{2/(m+1)} = 2 B^2,
                memory B = 2^s, with C = C(0) (k* = 0) and n = round(m s)
                iterated to a fixed point.
  rho           0.886 * 2^{(log2 N)/2}, O(1) memory.

The enumerative leaf k = n - s is ALSO charged the da1428 way (root-finding
plus O(1) lookup, 2^{m-1} roots per specialisation by KN-FIND-a8990a Thm C):
leaf = 2^{n-s} * 2^{m-1}.  Both the formula value at k = n - s and the
root-finding value are emitted; argmin is reported under both charges.

Usage:  python3 cost_table.py [--out DIR]
Writes ck-curves.yaml, cost-table.yaml, thresholds.yaml, fixtures.yaml,
concrete-cost.yaml into DIR (default: the script's own directory) and prints
a short summary to stdout.
"""
import argparse
import json
import math
import os
import sys
from math import comb, factorial, log2

SCRIPT_ID = "EXP-PFDR-c04716 / runs/STATIC-001 / cost_table.py"
QUALIFIER = "assuming HEUR-001 (H-PFDR-06fd60); estimate, not measured"

OMEGAS = (2.0, 2.807)
MS = (3, 4, 5)
D0S = (4, 6, 8)
LOG2NS = (64, 128, 256)
FIXTURE_MS = ((3, 6), (4, 8), (5, 8))
RHO_CONST = 0.886
SMALL_N_MARGIN_LOG2 = 9.0
HAND_TOLERANCE_LOG2 = 1.0

# ----------------------------------------------------------------------------
# Frozen hand values (preregistered; copied verbatim, never adjusted here).
# key: (log2N, m, D0, omega) -> dict(T=..., mem=..., source=...)
# ----------------------------------------------------------------------------
HAND = {
    # specification.yaml inputs.hand_values_to_reproduce (primary)
    (256, 5, 4, 2.0):   {"T": 108.7, "mem": 53.8, "source": "spec inputs.hand_values_to_reproduce"},
    (256, 5, 6, 2.0):   {"T": 116.6, "mem": 57.8, "source": "spec inputs.hand_values_to_reproduce (T); dcf857 (D) (mem)"},
    (256, 5, 8, 2.0):   {"T": 124.1, "mem": 61.5, "source": "spec inputs.hand_values_to_reproduce (T); dcf857 (D) (mem)"},
    (256, 5, 6, 2.807): {"T": 127.9, "mem": 63.5, "source": "spec inputs.hand_values_to_reproduce (T); dcf857 (D) (mem)"},
    (256, 4, 4, 2.0):   {"T": 128.6, "mem": 63.8, "source": "spec inputs.hand_values_to_reproduce (T); H-PFDR-06fd60 (D) (mem)"},
    (256, 4, 8, 2.0):   {"T": 146.8, "mem": 72.9, "source": "spec inputs.hand_values_to_reproduce (T); dcf857 (D) (mem)"},
    (128, 5, 4, 2.0):   {"T": 64.0,  "mem": 31.5, "source": "spec inputs.hand_values_to_reproduce (T); dcf857 (D) (mem)"},
    (64, 5, 4, 2.0):    {"T": 40.9,  "mem": 19.9, "source": "spec inputs.hand_values_to_reproduce (T); dcf857 (D) (mem)"},
    # H-PFDR-06fd60 statement (D) / IDEA-20260903-dcf857 claim (D) (secondary)
    (256, 4, 4, 2.807): {"T": 138.0, "mem": 68.5, "source": "H-PFDR-06fd60 (D); dcf857 (D)"},
    (256, 4, 6, 2.0):   {"T": 138.0, "mem": 68.5, "source": "dcf857 (D)"},
    (256, 4, 6, 2.807): {"T": 150.0, "mem": None, "source": "dcf857 (D) ('about 2^150')"},
    (256, 4, 8, 2.807): {"T": 164.4, "mem": 81.7, "source": "H-PFDR-06fd60 (D); dcf857 (D)"},
    (256, 5, 4, 2.807): {"T": 116.6, "mem": 57.8, "source": "H-PFDR-06fd60 (D); dcf857 (D)"},
    (256, 5, 8, 2.807): {"T": 139.0, "mem": 69.0, "source": "H-PFDR-06fd60 (D); dcf857 (D)"},
    (128, 4, 4, 2.0):   {"T": 75.0,  "mem": 36.9, "source": "dcf857 (D)"},
    (128, 5, 4, 2.807): {"T": 71.1,  "mem": None, "source": "H-PFDR-06fd60 (D); dcf857 (D)"},
    (128, 5, 8, 2.0):   {"T": 77.7,  "mem": 38.3, "source": "dcf857 (D)"},
}

# Frozen D_0-threshold brackets at 256 bits (preregistered_prediction.formula)
PREDICTED_THRESHOLDS_256 = {
    (5, 2.0):   {"lo": 8, "hi": 10, "text": "between 8 and 10"},
    (5, 2.807): {"lo": 4, "hi": 6,  "text": "between 4 and 6"},
    (4, 2.0):   {"lo": None, "hi": 4, "text": "below 4"},
}


# ----------------------------------------------------------------------------
# Minimal YAML emitter (standard library only; strings via JSON double quotes)
# ----------------------------------------------------------------------------
def _scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if math.isinf(v) or math.isnan(v):
            return "null"
        return repr(round(v, 4))
    return json.dumps(str(v))


def _is_flat_list(v):
    return isinstance(v, (list, tuple)) and all(
        not isinstance(x, (dict, list, tuple)) for x in v)


def emit_yaml(obj, indent=0, out=None):
    if out is None:
        out = []
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = str(k)
            if not key.replace("_", "").replace("-", "").isalnum():
                key = json.dumps(key)
            if isinstance(v, dict):
                if not v:
                    out.append(f"{pad}{key}: {{}}")
                else:
                    out.append(f"{pad}{key}:")
                    emit_yaml(v, indent + 1, out)
            elif isinstance(v, (list, tuple)):
                if not v:
                    out.append(f"{pad}{key}: []")
                elif _is_flat_list(v):
                    out.append(f"{pad}{key}: [{', '.join(_scalar(x) for x in v)}]")
                else:
                    out.append(f"{pad}{key}:")
                    emit_yaml(v, indent + 1, out)
            else:
                out.append(f"{pad}{key}: {_scalar(v)}")
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if isinstance(item, dict):
                lines = []
                emit_yaml(item, indent + 1, lines)
                if lines:
                    first = lines[0].lstrip()
                    out.append(f"{pad}- {first}")
                    out.extend(lines[1:])
            elif _is_flat_list(item):
                out.append(f"{pad}- [{', '.join(_scalar(x) for x in item)}]")
            else:
                out.append(f"{pad}- {_scalar(item)}")
    else:
        out.append(f"{pad}{_scalar(obj)}")
    return out


def write_yaml(path, obj, header_lines):
    lines = ["# " + h for h in header_lines] + emit_yaml(obj)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ----------------------------------------------------------------------------
# Cost model primitives
# ----------------------------------------------------------------------------
def ncols(nvars, D):
    """Number of multilinear monomials of degree <= D in nvars variables."""
    return sum(comb(nvars, i) for i in range(0, min(D, nvars) + 1))


def d_reg(nvars, m):
    """Semi-regular null degree, 84cdb7 at d = 2 with nvars variables."""
    return -(-(nvars + 2 * m) // 2)  # ceil((nvars + 2m)/2)


def D_of(slice_name, nvars, m, D0):
    if slice_name == "null":
        return d_reg(nvars, m)
    if slice_name == "bounded":
        return min(D0, d_reg(nvars, m))
    raise ValueError(slice_name)


def log2_rho(log2N):
    return log2(RHO_CONST) + log2N / 2.0


def crossing_residual(D0, omega):
    """n - k below which 2 (1 - D0/(n-k))^omega < 1: D0 / (1 - 2^{-1/omega})."""
    return D0 / (1.0 - 2.0 ** (-1.0 / omega))


# ----------------------------------------------------------------------------
# C(k) curves
# ----------------------------------------------------------------------------
def curve(m, s, D0, omega, slice_name):
    n = m * s
    kmax = n - s
    entries = []
    for k in range(0, kmax + 1):
        nres = n - k
        D = D_of(slice_name, nres, m, D0)
        lc = k + omega * log2(ncols(nres, D))
        entries.append((k, D, lc))
    leaf_rootfind = (n - s) + (m - 1)  # log2(2^{n-s} * 2^{m-1})
    vals = [e[2] for e in entries]
    argmin_formula = min(range(len(vals)), key=lambda i: vals[i])
    vals_leaf = vals[:-1] + [leaf_rootfind]
    argmin_leaf = min(range(len(vals_leaf)), key=lambda i: vals_leaf[i])
    ratios = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    strictly_decreasing = all(r < 0 for r in ratios)
    # first k at which the ratio C(k+1)/C(k) drops below 1 (bounded slice)
    first_drop = next((i for i, r in enumerate(ratios) if r < 0), None)
    argmax = max(range(len(vals)), key=lambda i: vals[i])
    return {
        "m": m, "s": s, "n": n, "D0": (D0 if slice_name == "bounded" else None),
        "omega": omega, "slice": slice_name,
        "k_range": [0, kmax],
        "argmin_k_formula_leaf": argmin_formula,
        "argmin_k_rootfinding_leaf": argmin_leaf,
        "log2C_at_argmin_formula_leaf": vals[argmin_formula],
        "log2C_at_k0": vals[0],
        "log2C_formula_at_leaf": vals[-1],
        "log2C_rootfinding_leaf": leaf_rootfind,
        "argmax_k": argmax,
        "log2C_at_argmax": vals[argmax],
        "strictly_decreasing_in_k": strictly_decreasing,
        "first_k_with_ratio_below_1": first_drop,
        "residual_vars_at_first_drop": (n - first_drop if first_drop is not None else None),
        "predicted_crossing_residual_vars": (crossing_residual(D0, omega) if slice_name == "bounded" else None),
        "min_log2_ratio": min(ratios) if ratios else None,
        "max_log2_ratio": max(ratios) if ratios else None,
        "entries_format": "[k, D(k), log2 C(k)]  (2^m filtering NOT included; it is a k-independent factor charged in the balance)",
        "entries": [[k, D, round(lc, 4)] for (k, D, lc) in entries],
    }


# ----------------------------------------------------------------------------
# Balance solver
# ----------------------------------------------------------------------------
def log2_oracle(n, m, D0, omega):
    """log2 of 2^m * Ncols(n, min(D0, d_reg(n)))^omega, i.e. C(0) with filtering."""
    D = min(D0, d_reg(n, m))
    return m + omega * log2(ncols(n, D)), D


def balance(m, D0, omega, log2N, maxit=500):
    """Fixed point of s = (log2 m! + log2 C(0)(n = round(m s)) + log2 N)/(m+1)."""
    lm = log2(factorial(m))

    def s_of_n(n):
        lc, D = log2_oracle(n, m, D0, omega)
        return (lm + lc + log2N) / (m + 1), lc, D

    s = log2N / (m + 1)
    seen = {}
    iterations = 0
    cycle = None
    while iterations < maxit:
        iterations += 1
        n = int(round(m * s))
        if n in seen:
            # revisited n: either converged (round(m s_of_n(n)) == n) or a cycle
            s_new, lc, D = s_of_n(n)
            if int(round(m * s_new)) == n:
                s = s_new
                break
            cycle = sorted(seen.keys())
            break
        s_new, lc, D = s_of_n(n)
        seen[n] = s_new
        if int(round(m * s_new)) == n:
            s = s_new
            break
        s = s_new
    resolved_by = "self_consistent_fixed_point"
    if cycle is not None:
        # choose the candidate n with the smallest rounding residual |m s(n) - n|
        best = min(cycle, key=lambda nn: abs(m * s_of_n(nn)[0] - nn))
        s, lc, D = s_of_n(best)
        n = best
        resolved_by = f"rounding_cycle_over_n={cycle}_resolved_by_min_residual"
    else:
        n = int(round(m * s))
        s, lc, D = s_of_n(n)
    log2T = 1.0 + 2.0 * s
    # rounding sensitivity: re-solve s at n-1 and n+1 (no re-rounding)
    s_lo, _, _ = s_of_n(max(n - 1, 1))
    s_hi, _, _ = s_of_n(n + 1)
    return {
        "s": s, "n": n, "D_used": D, "log2C0_with_filter": lc,
        "log2T": log2T, "log2_memory": s,
        "iterations": iterations, "resolved_by": resolved_by,
        "log2T_if_n_minus_1": 1.0 + 2.0 * s_lo,
        "log2T_if_n_plus_1": 1.0 + 2.0 * s_hi,
        "ncols_n_D_exact": ncols(n, D),
    }


def balance_closed_form_C1(m, log2N):
    """C = 1: log2 T = 1 + (2/(m+1)) (log2 m! + m + log2 N)."""
    return 1.0 + (2.0 / (m + 1)) * (log2(factorial(m)) + m + log2N)


def balance_closed_form_C1_no_filter(m, log2N):
    """84cdb7's own form without the 2^m filter: 1 + (2/(m+1))(log2 m! + log2 N)."""
    return 1.0 + (2.0 / (m + 1)) * (log2(factorial(m)) + log2N)


def balance_enumerative(m, log2N):
    """C = B^{m-1} 2^{m-1}: (m+1) s = log2 m! + m + (m-1) s + (m-1) + log2 N."""
    s = (log2(factorial(m)) + 2 * m - 1 + log2N) / 2.0
    return 1.0 + 2.0 * s, s


def balance_enumerative_iterated(m, log2N, iters=200):
    """Same limit obtained by iterating the balance with C = B^{m-1} 2^{m-1}."""
    s = log2N / (m + 1)
    for _ in range(iters):
        lc = (m - 1) * s + (m - 1) + m  # log2(2^m * B^{m-1} * 2^{m-1})
        s = (log2(factorial(m)) + lc + log2N) / (m + 1)
    return 1.0 + 2.0 * s, s


# ----------------------------------------------------------------------------
# Direct-presentation fixture (IDEA-20260808-da1428)
# ----------------------------------------------------------------------------
def direct_presentation(m, omega, B, D_S):
    """da1428: k of m coordinates fixed to factor-base values (B^k),
    residual m-k variables solved at semi-regular degree
    ceil(((m-k)(B-1) + D_S)/2) with dense column count binom(D + (m-k), m-k);
    leaf k = m-1 charged by root-finding: B^{m-1} * 2^{m-1}."""
    costs = []
    for k in range(0, m):
        if k == m - 1:
            lc = (m - 1) * log2(B) + (m - 1)
            costs.append((k, None, lc))
        else:
            r = m - k
            D = -(-((r * (B - 1)) + D_S) // 2)
            lc = k * log2(B) + omega * log2(comb(D + r, r))
            costs.append((k, D, lc))
    vals = [c[2] for c in costs]
    argmin = min(range(len(vals)), key=lambda i: vals[i])
    ratio_log2 = vals[m - 2] - vals[m - 1]
    return costs, argmin, ratio_log2


# ----------------------------------------------------------------------------
# Main derivation
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)
    header = [
        f"Emitted by {SCRIPT_ID}",
        "ZERO-RUN STATIC DERIVATION. Every number is DERIVED (estimate), never measured.",
        "Every bounded-slice / table number is CONDITIONAL on HEUR-001 of H-PFDR-06fd60.",
        "Cost model: IDEA-20260903-dcf857 claim (A). Cost unit: F_p field operations (log2).",
    ]
    summary = {}

    # ---------------- self-check of primitives ----------------
    assert ncols(10, 10) == 2 ** 10 and ncols(10, 0) == 1 and ncols(5, 2) == 16
    assert d_reg(18, 3) == 12 and d_reg(40, 5) == 25 and d_reg(17, 3) == 12
    assert abs(crossing_residual(4, 2.0) - 4 / (1 - 2 ** -0.5)) < 1e-12

    # ================= ck-curves.yaml =================
    curves = {"fixture_ms": [], "table_cells": []}
    null_fixture_ok = True
    null_details = []
    for (m, s) in FIXTURE_MS:
        for omega in OMEGAS:
            c_null = curve(m, s, None, omega, "null")
            c_null["D0"] = None
            curves["fixture_ms"].append(c_null)
            leaf = c_null["k_range"][1]
            ok = (c_null["strictly_decreasing_in_k"]
                  and c_null["argmin_k_formula_leaf"] == leaf
                  and c_null["argmin_k_rootfinding_leaf"] == leaf)
            null_fixture_ok = null_fixture_ok and ok
            null_details.append({
                "m": m, "s": s, "n": m * s, "omega": omega, "leaf_k": leaf,
                "strictly_decreasing": c_null["strictly_decreasing_in_k"],
                "argmin_k_formula_leaf": c_null["argmin_k_formula_leaf"],
                "argmin_k_rootfinding_leaf": c_null["argmin_k_rootfinding_leaf"],
                "max_log2_ratio_C(k+1)/C(k)": c_null["max_log2_ratio"],
                "min_log2_ratio_C(k+1)/C(k)": c_null["min_log2_ratio"],
                "asymptotic_log2_ratio_1_minus_omega": 1 - omega,
                "log2C_k0": c_null["log2C_at_k0"],
                "log2C_rootfinding_leaf": c_null["log2C_rootfinding_leaf"],
                "pass": ok,
            })
            for D0 in D0S:
                curves["fixture_ms"].append(curve(m, s, D0, omega, "bounded"))

    # ================= cost-table.yaml =================
    table = []
    cell_index = {}
    for log2N in LOG2NS:
        rho = log2_rho(log2N)
        for m in MS:
            for D0 in D0S:
                for omega in OMEGAS:
                    b = balance(m, D0, omega, log2N)
                    hand = HAND.get((log2N, m, D0, omega))
                    disc_T = (b["log2T"] - hand["T"]) if hand else None
                    disc_mem = (b["log2_memory"] - hand["mem"]) if (hand and hand["mem"] is not None) else None
                    # curve at the balanced (rounded) s
                    s_int = int(round(b["s"]))
                    cb = curve(m, s_int, D0, omega, "bounded")
                    cn = curve(m, s_int, None, omega, "null")
                    cn["D0"] = None
                    curves["table_cells"].append({"cell": f"log2N={log2N} m={m} D0={D0} omega={omega}", **cb})
                    curves["table_cells"].append({"cell": f"log2N={log2N} m={m} D0={D0} omega={omega}", **cn})
                    kc = m * s_int - 2 * (D0 - m)
                    cell = {
                        "log2N": log2N, "m": m, "D0": D0, "omega": omega,
                        "tags": f"(D_0 = {D0}, omega = {omega})",
                        "qualifier": QUALIFIER,
                        "value_kind": "estimate (derived); never measured",
                        "s_balanced": b["s"], "n_rounded": b["n"], "D_used_at_k0": b["D_used"],
                        "ncols_n_D_exact": b["ncols_n_D_exact"],
                        "log2_C0_with_2m_filter": b["log2C0_with_filter"],
                        "log2_T": b["log2T"], "log2_memory": b["log2_memory"],
                        "prior_rho_log2_T": rho, "prior_rho_log2_memory": 0,
                        "log2_T_minus_rho": b["log2T"] - rho,
                        "beats_rho_on_time_conditionally": b["log2T"] < rho,
                        "beats_rho_on_memory": False,
                        "balance_iterations": b["iterations"], "balance_resolved_by": b["resolved_by"],
                        "rounding_sensitivity_log2T_n_minus_1": b["log2T_if_n_minus_1"],
                        "rounding_sensitivity_log2T_n_plus_1": b["log2T_if_n_plus_1"],
                        "hand_T_log2": hand["T"] if hand else None,
                        "hand_memory_log2": (hand["mem"] if hand else None),
                        "hand_source": hand["source"] if hand else None,
                        "discrepancy_T_script_minus_hand": disc_T,
                        "discrepancy_memory_script_minus_hand": disc_mem,
                        "within_1_log2_of_hand": (abs(disc_T) <= HAND_TOLERANCE_LOG2) if hand else None,
                        "curve_at_balanced_s": {
                            "s_int": s_int, "n": m * s_int,
                            "bounded_argmin_k_rootfinding_leaf": cb["argmin_k_rootfinding_leaf"],
                            "bounded_argmin_k_formula_leaf": cb["argmin_k_formula_leaf"],
                            "bounded_argmax_k": cb["argmax_k"],
                            "bounded_first_k_with_ratio_below_1": cb["first_k_with_ratio_below_1"],
                            "bounded_residual_vars_at_first_drop": cb["residual_vars_at_first_drop"],
                            "predicted_crossing_residual_vars": cb["predicted_crossing_residual_vars"],
                            "bounded_log2C_k0": cb["log2C_at_k0"],
                            "bounded_log2C_rootfinding_leaf": cb["log2C_rootfinding_leaf"],
                            "null_argmin_k_rootfinding_leaf": cn["argmin_k_rootfinding_leaf"],
                            "null_strictly_decreasing": cn["strictly_decreasing_in_k"],
                        },
                        "interior_band_HEUR002_only": {
                            "k_c": kc,
                            "k_c_within_guessing_range": (0 <= kc <= m * s_int - s_int),
                            "binom_2(D0-m)_D0": comb(2 * (D0 - m), D0) if D0 - m >= 0 else 0,
                            "P5_formula_log2": (kc + omega * log2(comb(2 * (D0 - m), D0))) if (D0 - m >= 0 and comb(2 * (D0 - m), D0) > 0) else None,
                            "P5_formula_note": "2^{k_c} binom(2(D_0 - m), D_0)^omega as frozen; null when the binomial is zero (2(D_0 - m) < D_0)",
                            "script_log2C_at_k_c": (cb["entries"][kc][2] if 0 <= kc <= m * s_int - s_int else None),
                        },
                    }
                    table.append(cell)
                    cell_index[(log2N, m, D0, omega)] = cell

    # ================= thresholds.yaml =================
    thresholds = []
    for log2N in LOG2NS:
        rho = log2_rho(log2N)
        for m in MS:
            for omega in OMEGAS:
                scan = []
                lo = None
                hi = None
                for D0 in range(2, 41, 2):
                    b = balance(m, D0, omega, log2N)
                    below = b["log2T"] < rho
                    scan.append({"D0": D0, "log2_T": b["log2T"], "log2_memory": b["s"],
                                 "log2_T_minus_rho": b["log2T"] - rho, "T_below_rho": below})
                    if below:
                        lo = D0
                    elif hi is None:
                        hi = D0
                        break
                if lo is None:
                    bracket_text = f"below {hi} (T >= rho already at D_0 = {hi})"
                elif hi is None:
                    bracket_text = f"above {lo} (T < rho at every even D_0 up to {lo})"
                else:
                    bracket_text = f"between {lo} and {hi}"
                pred = PREDICTED_THRESHOLDS_256.get((m, omega)) if log2N == 256 else None
                matches = None
                if pred is not None:
                    if pred["lo"] is None:
                        matches = (hi is not None and hi <= pred["hi"])
                    else:
                        matches = (lo == pred["lo"] and hi == pred["hi"])
                thresholds.append({
                    "log2N": log2N, "m": m, "omega": omega,
                    "prior_rho_log2_T": rho,
                    "largest_even_D0_with_T_below_rho": lo,
                    "smallest_even_D0_with_T_at_or_above_rho": hi,
                    "bracket": bracket_text,
                    "qualifier": QUALIFIER,
                    "predicted_bracket_256": (pred["text"] if pred else None),
                    "matches_prediction": matches,
                    "scan": scan,
                })

    # interior band cells at the fixture (m, s) pairs
    interior = []
    for (m, s) in FIXTURE_MS:
        for D0 in D0S:
            for omega in OMEGAS:
                n = m * s
                kc = n - 2 * (D0 - m)
                cb = curve(m, s, D0, omega, "bounded")
                bn = comb(2 * (D0 - m), D0) if D0 - m >= 0 else 0
                interior.append({
                    "m": m, "s": s, "n": n, "D0": D0, "omega": omega,
                    "k_c": kc, "k_c_within_guessing_range": (0 <= kc <= n - s),
                    "binom_2(D0-m)_D0": bn,
                    "P5_formula_log2": (kc + omega * log2(bn)) if bn > 0 else None,
                    "script_log2C_at_k_c": (cb["entries"][kc][2] if 0 <= kc <= n - s else None),
                    "bounded_argmin_k_rootfinding_leaf": cb["argmin_k_rootfinding_leaf"],
                    "qualifier": "HEUR-002 only; " + QUALIFIER,
                })

    # ================= fixtures.yaml =================
    # F2: direct presentation
    direct = []
    direct_ok = True
    for m in MS:
        D_S = m * 2 ** (m - 1)  # total degree of S_{m+1} (2^{m-1} per variable); ratio exponent independent of D_S
        for omega in OMEGAS:
            rows = []
            prev = None
            B0 = None
            all_leaf_from = True
            for j in range(4, 21):
                B = 2 ** j
                costs, argmin, rl = direct_presentation(m, omega, B, D_S)
                slope = (rl - prev) if prev is not None else None  # per doubling of B == d log2 ratio / d log2 B
                rows.append({"log2B": j, "B": B, "argmin_k": argmin,
                             "log2_costs_k0_to_km1": [round(c[2], 4) for c in costs],
                             "log2_ratio_k_m2_over_k_m1": rl,
                             "local_slope_dlog2ratio_dlog2B": slope})
                if argmin == m - 1 and B0 is None:
                    B0 = B
                if argmin != m - 1:
                    B0 = None
                prev = rl
            final_slope = rows[-1]["local_slope_dlog2ratio_dlog2B"]
            target = 2 * omega - 1
            ok = (rows[-1]["argmin_k"] == m - 1 and abs(final_slope - target) < 0.05)
            direct_ok = direct_ok and ok
            direct.append({"m": m, "omega": omega, "D_S_used": D_S,
                           "target_exponent_2omega_minus_1": target,
                           "slope_at_largest_B": final_slope,
                           "argmin_at_largest_B": rows[-1]["argmin_k"],
                           "leaf_k": m - 1,
                           "B_0_smallest_grid_B_from_which_argmin_is_leaf": B0,
                           "pass": ok, "rows": rows})

    # F3: balance limits
    bal = []
    bal_ok = True
    for m in MS:
        e = {"m": m, "target_exponent_C1": 2.0 / (m + 1), "target_exponent_enumerative": 1.0}
        pts = []
        for log2N in LOG2NS:
            c1 = balance_closed_form_C1(m, log2N)
            c1n = balance_closed_form_C1_no_filter(m, log2N)
            en, s_en = balance_enumerative(m, log2N)
            en_it, s_it = balance_enumerative_iterated(m, log2N)
            pts.append({"log2N": log2N, "C1_log2T_with_2m_filter": c1, "C1_log2T_84cdb7_form_no_filter": c1n,
                        "C1_log2T_over_log2N": c1 / log2N,
                        "enumerative_log2T_closed": en, "enumerative_log2T_iterated": en_it,
                        "enumerative_log2_memory": s_en,
                        "enumerative_log2T_over_log2N": en / log2N})
        slope_c1 = (balance_closed_form_C1(m, 256) - balance_closed_form_C1(m, 128)) / 128.0
        slope_en = (balance_enumerative(m, 256)[0] - balance_enumerative(m, 128)[0]) / 128.0
        ok = abs(slope_c1 - 2.0 / (m + 1)) < 1e-9 and abs(slope_en - 1.0) < 1e-9 \
            and all(abs(p["enumerative_log2T_closed"] - p["enumerative_log2T_iterated"]) < 1e-6 for p in pts)
        bal_ok = bal_ok and ok
        e.update({"slope_dlog2T_dlog2N_C1": slope_c1, "slope_dlog2T_dlog2N_enumerative": slope_en,
                  "C1_constant_offset_log2": 1.0 + (2.0 / (m + 1)) * (log2(factorial(m)) + m),
                  "enumerative_constant_offset_log2": log2(factorial(m)) + 2 * m,
                  "points": pts, "pass": ok})
        bal.append(e)

    # small-N tell
    small = []
    small_ok = True
    for m in MS:
        for D0 in D0S:
            for omega in OMEGAS:
                c = cell_index[(64, m, D0, omega)]
                gap = c["log2_T_minus_rho"]
                ok = gap >= SMALL_N_MARGIN_LOG2
                small_ok = small_ok and ok
                small.append({"m": m, "D0": D0, "omega": omega, "log2_T": c["log2_T"],
                              "prior_rho_log2_T": c["prior_rho_log2_T"], "log2_T_minus_rho": gap,
                              "loses_by_at_least_2^9": ok})
    min_gap_cell = min(small, key=lambda x: x["log2_T_minus_rho"])

    # hand comparison summary
    comps = [c for c in table if c["hand_T_log2"] is not None]
    worst = max(comps, key=lambda c: abs(c["discrepancy_T_script_minus_hand"]))
    all_within = all(c["within_1_log2_of_hand"] for c in comps)
    primary = [c for c in comps if c["hand_source"].startswith("spec inputs")]
    primary_within = all(c["within_1_log2_of_hand"] for c in primary)

    fixtures = {
        "F1_null_slice_reproduces_da1428": {
            "forced_disposition": "C(k) strictly decreasing to the enumerative leaf; argmin at the leaf; assembled total N^1",
            "pass": null_fixture_ok, "cells": null_details,
            "assembled_total_with_enumerative_oracle": [
                {"m": m, "log2N": L, "log2T": balance_enumerative(m, L)[0], "log2T_over_log2N": balance_enumerative(m, L)[0] / L}
                for m in MS for L in LOG2NS],
        },
        "F2_direct_presentation_ratio": {
            "forced_disposition": "argmin at k = m-1 (no flip) and k=m-2 / k=m-1 ratio Theta(B^{2 omega - 1})",
            "pass": direct_ok, "per_m_omega": direct,
        },
        "F3_balance_limits": {
            "forced_disposition": "C = 1 gives exponent 2/(m+1); C = B^{m-1} (enumerative) gives exponent 1",
            "pass": bal_ok, "per_m": bal,
        },
        "SMALL_N_TELL_64_bits": {
            "forced_disposition": "every bounded-slice cell at log2 N = 64 loses to rho by at least 2^9",
            "pass": small_ok, "min_gap_cell": min_gap_cell, "cells": small,
        },
        "HAND_VALUE_COMPARISON": {
            "tolerance_log2": HAND_TOLERANCE_LOG2,
            "primary_cells_all_within_tolerance": primary_within,
            "all_listed_cells_within_tolerance": all_within,
            "largest_abs_discrepancy_cell": {k: worst[k] for k in ("log2N", "m", "D0", "omega", "log2_T", "hand_T_log2", "discrepancy_T_script_minus_hand", "hand_source")},
            "cells": [{k: c[k] for k in ("log2N", "m", "D0", "omega", "log2_T", "hand_T_log2", "discrepancy_T_script_minus_hand",
                                          "log2_memory", "hand_memory_log2", "discrepancy_memory_script_minus_hand", "within_1_log2_of_hand", "hand_source")} for c in comps],
        },
        "BOTH_OMEGA_CONTROL": {"omegas_emitted": list(OMEGAS), "pass": True},
        "m3_arithmetic_row": {
            "statement_in_hand_table": "m = 3, any D_0: T = 2 (6 x 8 x C N)^{1/2} >= N^{1/2} x 2^{2.8} for C >= 1",
            "script_constant_log2_2_sqrt_48": 1.0 + 0.5 * log2(48),
            "note": "the script's constant is log2(2 sqrt(48)); reported for comparison with the hand value 2.8",
        },
    }

    # ================= concrete-cost.yaml =================
    def cellname(c):
        return f"log2 N = {c['log2N']}, m = {c['m']}, D_0 = {c['D0']}, omega = {c['omega']}"

    psets = []
    for c in table:
        psets.append({
            "name": cellname(c) + " [" + QUALIFIER + "]",
            "security_parameter": c["log2N"],
            "tags": c["tags"],
            "time_log2": c["log2_T"],
            "memory_log2": c["log2_memory"],
            "prior_time_log2": c["prior_rho_log2_T"],
            "prior_memory_log2": 0,
            "time_minus_prior_log2": c["log2_T_minus_rho"],
            "value_kind": "estimate (derived)",
        })
    cond_affected = [cellname(c) for c in table if c["log2_T"] < c["prior_rho_log2_T"]]
    cond_safe = [cellname(c) + f" (T - rho = 2^{c['log2_T_minus_rho']:.1f})" for c in table if c["log2_T"] >= c["prior_rho_log2_T"]]

    concrete = {"concrete_cost": {
        "id": None,
        "id_note": "draft inside a zero-run package; no COST identifier minted (a ledger record, if ever promoted, is minted by the Coordinator with tools/allocate_id.py)",
        "hypothesis_id": "H-PFDR-06fd60",
        "experiment_id": "EXP-PFDR-c04716",
        "algorithm_ref": "Digit-presentation index calculus (IDEA-20260830-84cdb7) with the decomposition oracle solved by Macaulay linear algebra at degree D_0 with k* = 0 (no guessing); CONDITIONAL on HEUR-001 of H-PFDR-06fd60",
        "cost_unit": "F_p field operations (log2)",
        "bound_kind": "heuristic_estimate",
        "qualifier_on_every_cell": QUALIFIER,
        "conditionality": "EVERY cell is conditional on HEUR-001 (bounded last fall degree AND bounded solve at D_0). Unconditionally this block claims NOTHING: the semi-regular null gives T = N^1 (fixture F1). No cell is quoted without its (D_0, omega) tags.",
        "how_produced": "derived by cost_table.py (exact integer binomials, real-valued balance iterated to a fixed point); no measurement of any kind",
        "parameter_sets": psets,
        "optimistic_assumptions": [
            "[UNDER-estimates cost] HEUR-001: last fall degree bounded by D_0 uniformly in s, p, curve and target (unmeasured; EXP-PFDR-cbdefb measures it; the honest prior is 0.05 against it per H-PFDR-06fd60)",
            "[UNDER-estimates cost] bounded last fall implies bounded SOLVE: the degree-D_0 Macaulay matrix is assumed to determine the solutions (Huang-Kosters-Yeo relation RECALLED, pointer only, not opened)",
            "[UNDER-estimates cost] omega = 2 in the omega-2 column is not achievable for structured sparse Macaulay matrices; the omega = 2.807 column is the conservative one and is emitted for every cell",
            "[UNDER-estimates cost] yield at the KN-FIND-007 forced mean B^m/(m! N) with 2^m filtering (HEUR-003); no accidental-decomposition or coverage losses beyond that",
            "[UNDER-estimates cost] sparse linear algebra at B^2 with unit constant",
            "[UNDER-estimates cost] no cost charged for recognising digit solutions, for certificate checks, for building the Macaulay matrix, or for constructing the summation polynomial S_{m+1} (S_6 at m = 5 is charged nowhere; KN-OPEN-5b3a08 instrument defect at S_4 noted)",
            "[UNDER-estimates cost] balance solved with s real-valued and n = round(m s); rounding s to an integer costs up to a factor 2 in B (up to +2 in log2 T); the per-cell sensitivity to n +/- 1 is recorded in cost-table.yaml",
            "[UNDER-estimates cost] the k* = 0 point is used for every cell; the C(k) curve at the balanced s is emitted in ck-curves.yaml so a reader can check no k gives a lower C(0)-charged balance under the same model",
        ],
        "overestimating_factors": [
            "[OVER-estimates cost] Ncols counted as the full sum of binomials up to D_0 and the solve charged Ncols^omega; a sparse XL/Wiedemann charge nnz x Ncols would be lower than Ncols^2",
            "[OVER-estimates cost] filtering 2^m charged in full although the y^2 = f(x) variant of 84cdb7 removes it at the price of m extra variables",
        ],
        "hidden_overhead_disclosure": "the o(1) of N^{2/(m+1)+o(1)} is the factor 2 (m! 2^m Ncols(ms, D_0)^omega)^{2/(m+1)} in T; log2 of the per-target oracle cost 2^m Ncols(n, D_0)^omega at 256 bits is given per cell as log2_C0_with_2m_filter in cost-table.yaml",
        "parallelism": "Relation collection is embarrassingly parallel over targets (time T/P with P processors, memory unchanged); the B^2 sparse linear algebra is the serial bottleneck and parallelises only with block-Wiedemann at communication cost. Pollard rho parallelises linearly with van Oorschot-Wiener distinguished points at O(1) memory per processor.",
        "time_memory_tradeoff": "Arity m is the only knob: larger m lowers the exponent 2/(m+1) and raises both the per-target polynomial 2^m Ncols(ms, D_0)^omega and the memory 2^s = N^{1/(m+1)} x constants. No van Oorschot-Wiener style interpolation down to rho's O(1) memory exists for this family; the memory floor is the factor base, 2^s as tabulated per cell. Full-guessing (the null-slice optimum) has memory O(B) and time N^1 and is the low-memory endpoint of the hybrid family.",
        "affected_scope": [
            "NONE unconditionally.",
            "Conditionally on HEUR-001 with the stated (D_0, omega), the following cells have T < rho on TIME ONLY (memory 2^s against rho's O(1); no cell dominates rho on memory): " + ("; ".join(cond_affected) if cond_affected else "none"),
            "This is a parameter-re-evaluation signal under HEUR-001 and not a break; it is worthless until EXP-PFDR-cbdefb reports (PARETO-RHO control of the contract).",
        ],
        "safe_scope": [
            "all curves if HEUR-001 fails (the pre-registered expectation of 84cdb7, d52480 and H-PFDR-06fd60)",
            "all cells with T >= rho even assuming HEUR-001: " + ("; ".join(cond_safe) if cond_safe else "none"),
            "m = 3 at every N: T = 2 (6 x 8 x C N)^{1/2} >= 2^{" + f"{1.0 + 0.5 * log2(48):.2f}" + "} N^{1/2} for C >= 1, by arithmetic",
            "every cell on memory: 2^s memory against rho's O(1)",
        ],
        "dominated_by": "Pollard rho dominates every cell unconditionally (the null slice gives T = N^1); conditionally on HEUR-001 rho still dominates every cell on memory and dominates on time every cell listed under safe_scope",
        "sota_delta": "unconditionally +0 on every axis; conditional (HEUR-001) time deltas per cell are the time_minus_prior_log2 fields above, each tagged with (D_0, omega)",
        "implementation_ref": None,
        "status": "draft",
    }}

    # ================= write files =================
    write_yaml(os.path.join(out, "ck-curves.yaml"), {
        "model": "C(k) = 2^k Ncols(n - k, D(k))^omega; null D(k) = ceil(((n-k)+2m)/2); bounded D(k) = min(D_0, d_reg(k)); k = 0..n-s; leaf also charged by root-finding 2^{n-s} 2^{m-1}",
        "qualifier": "bounded-slice curves " + QUALIFIER,
        "curves": curves}, header)
    write_yaml(os.path.join(out, "cost-table.yaml"), {
        "model": "T = 2 (m! 2^m C(0) N)^{2/(m+1)} = 2 B^2, memory B = 2^s, C(0) = Ncols(n, min(D_0, d_reg(n)))^omega, n = round(m s), iterated to a fixed point; rho = 0.886 sqrt(N)",
        "qualifier": QUALIFIER,
        "hand_value_tolerance_log2": HAND_TOLERANCE_LOG2,
        "cells": table}, header)
    write_yaml(os.path.join(out, "thresholds.yaml"), {
        "definition": "for each (log2 N, m, omega) the even D_0 grid 2..40 is scanned; the bracket is (largest even D_0 with T < rho, smallest even D_0 with T >= rho)",
        "qualifier": QUALIFIER,
        "thresholds": thresholds,
        "interior_band_HEUR002_only_fixture_ms": interior}, header)
    write_yaml(os.path.join(out, "fixtures.yaml"), fixtures, header)
    write_yaml(os.path.join(out, "concrete-cost.yaml"), concrete, header)

    # ================= stdout summary =================
    summary = {
        "F1_null_slice_pass": null_fixture_ok,
        "F2_direct_presentation_pass": direct_ok,
        "F3_balance_limits_pass": bal_ok,
        "small_N_tell_pass": small_ok,
        "small_N_min_gap": {k: min_gap_cell[k] for k in ("m", "D0", "omega", "log2_T_minus_rho")},
        "hand_primary_all_within_1": primary_within,
        "hand_all_listed_within_1": all_within,
        "largest_discrepancy": fixtures["HAND_VALUE_COMPARISON"]["largest_abs_discrepancy_cell"],
        "thresholds_256": [{k: t[k] for k in ("m", "omega", "bracket", "predicted_bracket_256", "matches_prediction")} for t in thresholds if t["log2N"] == 256],
        "bounded_slice_argmin_not_0_cells": [c["tags"] + f" log2N={c['log2N']} m={c['m']}" for c in table if c["curve_at_balanced_s"]["bounded_argmin_k_rootfinding_leaf"] != 0],
        "cells_conditionally_below_rho": cond_affected,
    }
    print(json.dumps(summary, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
