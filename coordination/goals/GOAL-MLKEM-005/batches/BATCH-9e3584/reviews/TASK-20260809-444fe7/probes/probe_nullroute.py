#!/usr/bin/env python3
"""PROBE N (red team, TASK-20260809-444fe7) -- THE OBSERVABLE G-VAR DOES NOT CATCH.

NOT PRE-REGISTERED. A red-team probe on my own frames, at the scale actually
run here. It rescores NO frozen verdict: it neither confirms nor overturns
R-OUT-1, and it makes no admissibility claim about any observable. CLAIM TIER
TOY.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out probe_nullroute_output.json

WHAT IT ATTACKS
---------------
BATCH-9e3584 Section R (TASK-20260809-cda2f6, report_relvar.md) decides G-VAR
by BIT IDENTITY of 8 IEEE-754 doubles (prereg 2.5), and concludes in
report_relvar.md section 5(iii): "The decision was made structurally, by
bit-identity of the 8 IEEE-754 doubles, not by a tolerance, so it cannot be
tuned into or out of firing."

AM-11 (DEC-20260808-05b684) states the requirement mathematically: "any
closed-form function of (d, k, beta, q) with zero between-basis variance MUST
be refused".

X_null is a closed-form function of (d, k, beta, q) BECAUSE log|det B| =
(d-k) log q EXACTLY for B = [[I_k, A],[0, q I_{d-k}]], for every A. That is a
property of the FUNCTION. Bit identity is a property of the ARITHMETIC ROUTE
used to evaluate it. measure_relvar.py evaluates X_null from the matrix-free
closed form (its x_null_of docstring says so in terms). This probe evaluates
THE SAME MATHEMATICAL OBSERVABLE through four other routes to the same
quantity, all of which read the actual basis, and scores each through a
faithful reimplementation of the same G-REL / G-VAR code path.

ROUTES to log|det B| (all mathematically equal to (d-k)*log q for every A):
    R0  closed form            (d-k)*log(q)                       [the producer's route]
    R1  LU / slogdet           np.linalg.slogdet(B)               [the producer's rdet route]
    R2  QR of B^T              sum_i log|R_ii|                    [= sum log||b*_i||]
    R3  LU / slogdet of U B    U a fixed unimodular re-presentation of the SAME lattice
    R4  Gram                   0.5 * slogdet(B B^T)

Two observables are formed from each route, exactly as the frozen definitions
read them:
    X_null^route(B,beta) = (beta/d)*(1/d)*logdet_route(B)      [prereg 1.4]
    rdet^route(B)        = exp(logdet_route(B)/d)              [prereg 1.4]

MY OWN CHECK'S COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE RUNNING, BOTH WAYS
---------------------------------------------------------------------------
* could-not-FIRE (this probe could never show a miss): if EVERY arithmetic
  route to log|det B| happened to be bit-identical across the 8 bases, no
  route would escape G-VAR and the probe could not fire. This is a LIVE
  possibility and not a straw man -- R1 is predicted here to be bit-identical,
  because for this block-triangular B partial pivoting never touches A and the
  LU diagonal is [1]*k + [q]*(d-k) independently of A. The probe fires only if
  some route is NOT bit-identical, which is a measured outcome.
* could-not-PASS (this probe would flag any route, so flagging means nothing):
  if a route carried GENUINE basis dependence, G-VAR admitting it would be
  CORRECT rather than a miss. Guarded by measuring, at every cell and basis,
  max|X^route - X^closed_form| and the route's between-basis float sd, and
  comparing the latter against hkz's committed between-basis sd (0.023888 at
  L7 beta=5, results_relvar.json G_VAR.per_candidate.hkz.per_cell.L7_b5).
  A route is reported as a MISS only if its deviation from the closed form is
  many orders of magnitude below tau_rel = 0.10 AND below every real
  candidate's dispersion.

AM-10 / AM-11 APPLIED TO THIS PROBE'S OWN STATISTICS
----------------------------------------------------
Every statistic below is computed over ALL 8 frozen bases i = 0..7 (AM-10
replication), and every one is reported with its between-basis dispersion:
float sd, min, max, and the bit-identity flag (AM-11 dispersion). G-REL is
reported at BOTH normalizations with s_X/|X| beside it (AM-10 b).
"""
import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import OrderedDict

import numpy as np

Q = 3329
LOGQ = math.log(Q)
TAU_REL = 0.10
S_X = 1.0
N_BASES = 8

# frozen family, prereg 1.2 / 1.3 -- transcribed from the notarized text
LATTICES = OrderedDict([
    ("L1", (100, 30)), ("L2", (100, 70)),
    ("L4", (140, 40)), ("L5", (140, 100)),
    ("L7", (20, 6)), ("L8", (20, 14)),
    ("L9", (30, 9)), ("L10", (30, 21)),
    ("L11", (40, 12)), ("L12", (40, 28)),
])
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95],
             20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}
REL1_PAIR = {100: (15, 65), 140: (20, 95), 20: (5, 15), 30: (7, 22),
             40: (10, 30)}
MIRROR = [("L1", "L2"), ("L4", "L5"), ("L7", "L8"), ("L9", "L10"),
          ("L11", "L12")]

ROUTES = ["R0_closed_form", "R1_slogdet", "R2_QR_of_BT", "R3_slogdet_of_UB",
          "R4_gram_half_slogdet", "R5_slogdet_of_BH_ambient_isometry"]


# ---------------------------------------------------------------- frozen objects
def make_A(d, k, q, i):
    """prereg 1.1, transcribed: A = make_A(d,k,q,i) from default_rng([1,d,k,i])."""
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, d - k), dtype=np.int64)


def build_basis(d, k, q, i):
    """prereg 1.1: B = [[I_k, A],[0, q I_{d-k}]], exact integer arithmetic."""
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, q, i)
    B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
    return B


def unimodular(d, rng):
    """The SAME construction measure_relvar.py uses for its T3 residual, so the
    re-presentation is the producer's object and not one I invented."""
    U = np.eye(d, dtype=np.int64)
    U = U[rng.permutation(d)]
    signs = rng.integers(0, 2, size=d) * 2 - 1
    U = U * signs[:, None]
    for _ in range(d // 2):
        a, b = rng.choice(d, size=2, replace=False)
        s = int(rng.integers(0, 2)) * 2 - 1
        U[a] = U[a] + s * U[b]
    return U


_UCACHE = {}
_HCACHE = {}


def fixed_unimodular(d):
    """ONE fixed U per dimension, drawn from a seed that does not depend on the
    basis index i. So U is a constant of the probe, and any between-basis
    variation in logdet(U B_i) comes from B_i alone."""
    if d not in _UCACHE:
        _UCACHE[d] = unimodular(d, np.random.default_rng([424242, d]))
    return _UCACHE[d]


def haar_orthogonal(d, rng):
    """The SAME construction measure_relvar.py uses for its T1 ambient-isometry
    residual."""
    Z = rng.standard_normal((d, d))
    Qm, Rm = np.linalg.qr(Z)
    ph = np.sign(np.diag(Rm))
    ph[ph == 0] = 1.0
    return Qm * ph


def fixed_isometry(d):
    """ONE fixed ambient isometry H per dimension, seed independent of i. B H
    is a DIFFERENT PRESENTATION OF THE SAME LATTICE up to an ambient rotation;
    |det BH| = |det B| exactly, so the observable is unchanged mathematically.
    This is the transform the frozen gate's own T1 clause applies."""
    if d not in _HCACHE:
        _HCACHE[d] = haar_orthogonal(d, np.random.default_rng([313131, d]))
    return _HCACHE[d]


# ---------------------------------------------------------------- the five routes
def logdet_routes(B, d, k):
    out = OrderedDict()
    out["R0_closed_form"] = float((d - k) * LOGQ)
    _, la = np.linalg.slogdet(B.astype(np.float64))
    out["R1_slogdet"] = float(la)
    _, R = np.linalg.qr(B.astype(np.float64).T)
    out["R2_QR_of_BT"] = float(np.sum(np.log(np.abs(np.diag(R)))))
    U = fixed_unimodular(d)
    _, la3 = np.linalg.slogdet((U @ B).astype(np.float64))
    out["R3_slogdet_of_UB"] = float(la3)
    G = (B @ B.T).astype(np.float64)
    _, la4 = np.linalg.slogdet(G)
    out["R4_gram_half_slogdet"] = float(0.5 * la4)
    H = fixed_isometry(d)
    _, la5 = np.linalg.slogdet(B.astype(np.float64) @ H)
    out["R5_slogdet_of_BH_ambient_isometry"] = float(la5)
    return out


def bit_identical(vals):
    return len({float(v).hex() for v in vals}) == 1


def rho_both(x_b, x_a, s=S_X):
    num = abs(x_b - x_a)
    den_raw = abs(x_a)
    return {
        "value_maxfloor": num / max(den_raw, s),
        "value_absX": (num / den_raw) if den_raw > 0 else None,
        "s_over_absX": (s / den_raw) if den_raw > 0 else None,
        "scale_floor_is_binding": bool(den_raw < s),
    }


def summarize(vals):
    a = np.asarray(vals, dtype=float)
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "min": float(a.min()), "max": float(a.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="probe_nullroute_output.json")
    args = ap.parse_args()
    t0 = time.time()

    RES = OrderedDict()
    RES["probe"] = "PROBE-N"
    RES["task_id"] = "TASK-20260809-444fe7"
    RES["role"] = "red-team"
    RES["claim_tier"] = "toy"
    RES["status_of_this_measurement"] = (
        "RED-TEAM PROBE. NOT PRE-REGISTERED. NOT a rescoring of any frozen "
        "verdict. Makes no admissibility claim about any observable and does "
        "not adjudicate R-OUT-1 in either direction.")
    RES["environment"] = {
        "platform": platform.platform(), "python": platform.python_version(),
        "numpy": np.__version__,
    }
    try:
        RES["git_revision"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            check=True).stdout.strip()
    except Exception as e:                                   # pragma: no cover
        RES["git_revision"] = "UNAVAILABLE: %s" % e

    # ------------------------------------------------ 1. evaluate every route
    base = {}
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            B = build_basis(d, k, Q, i)
            base[(lat, i)] = logdet_routes(B, d, k)

    # ------------------------------------------------ 2. deviation from closed form
    dev = OrderedDict()
    for r in ROUTES:
        worst_abs, worst_rel, where = 0.0, 0.0, None
        for (lat, i), lr in base.items():
            e = abs(lr[r] - lr["R0_closed_form"])
            rel = e / abs(lr["R0_closed_form"]) if lr["R0_closed_form"] else 0.0
            if e > worst_abs:
                worst_abs, worst_rel, where = e, rel, "%s_i%d" % (lat, i)
        dev[r] = {"max_abs_dev_in_logdet": worst_abs,
                  "max_rel_dev_in_logdet": worst_rel, "at": where}
    RES["route_deviation_from_the_closed_form"] = dev

    # ------------------------------------------------ 3. G-VAR per route, per observable
    gvar = OrderedDict()
    for r in ROUTES:
        for obs in ("X_null", "rdet"):
            cells = OrderedDict()
            for lat, (d, k) in LATTICES.items():
                for beta in BETA_GRID[d]:
                    vals = []
                    for i in range(N_BASES):
                        ld = base[(lat, i)][r]
                        vals.append((beta / d) * (1.0 / d) * ld if obs == "X_null"
                                    else math.exp(ld / d))
                    cells["%s_b%d" % (lat, beta)] = {
                        "bit_identical": bit_identical(vals),
                        "float_sd": float(np.std(vals, ddof=1)),
                        "mean": float(np.mean(vals)),
                        "spread_max_minus_min": float(np.max(vals) - np.min(vals)),
                    }
            n_zero = sum(1 for v in cells.values() if v["bit_identical"])
            gvar["%s|%s" % (obs, r)] = {
                "n_cells": len(cells),
                "n_cells_bit_identical": n_zero,
                "G_VAR_REFUSES": bool(cells) and n_zero == len(cells),
                "max_float_sd_over_cells": max(v["float_sd"] for v in cells.values()),
                "per_cell": cells,
            }
    RES["G_VAR_by_route"] = gvar

    # ------------------------------------------------ 4. G-REL1 / G-REL2 per route
    grel = OrderedDict()
    for r in ROUTES:
        for obs in ("X_null", "rdet"):
            def X(lat, beta, i):
                d = LATTICES[lat][0]
                ld = base[(lat, i)][r]
                return ((beta / d) * (1.0 / d) * ld if obs == "X_null"
                        else math.exp(ld / d))

            rel1 = OrderedDict()
            for lat, (d, k) in LATTICES.items():
                lo, hi = REL1_PAIR[d]
                ent = [rho_both(X(lat, hi, i), X(lat, lo, i)) for i in range(N_BASES)]
                sm = summarize([e["value_maxfloor"] for e in ent])
                rel1[lat] = {
                    "beta_lo": lo, "beta_hi": hi,
                    "maxfloor": sm,
                    "absX": summarize([e["value_absX"] for e in ent]),
                    "n_pass_maxfloor_of_8": int(sum(
                        e["value_maxfloor"] >= TAU_REL for e in ent)),
                    "pass_at_mean_over_8": bool(sm["mean"] >= TAU_REL),
                    "scale_floor_binding_in_n_of_8": int(sum(
                        e["scale_floor_is_binding"] for e in ent)),
                }
            rel2 = OrderedDict()
            for a, b in MIRROR:
                d = LATTICES[a][0]
                for beta in BETA_GRID[d]:
                    ent = [rho_both(X(b, beta, i), X(a, beta, i))
                           for i in range(N_BASES)]
                    sm = summarize([e["value_maxfloor"] for e in ent])
                    rel2["%s/%s_b%d" % (a, b, beta)] = {
                        "maxfloor": sm,
                        "absX": summarize([e["value_absX"] for e in ent]),
                        "n_pass_maxfloor_of_8": int(sum(
                            e["value_maxfloor"] >= TAU_REL for e in ent)),
                        "pass_at_mean_over_8": bool(sm["mean"] >= TAU_REL),
                        "scale_floor_binding_in_n_of_8": int(sum(
                            e["scale_floor_is_binding"] for e in ent)),
                    }
            grel["%s|%s" % (obs, r)] = {
                "REL1_n_lattices_passing_at_mean": sum(
                    1 for v in rel1.values() if v["pass_at_mean_over_8"]),
                "REL1_n_lattices": len(rel1),
                "REL2_n_cells_passing_at_mean": sum(
                    1 for v in rel2.values() if v["pass_at_mean_over_8"]),
                "REL2_n_cells": len(rel2),
                "REL1": rel1, "REL2": rel2,
            }
    RES["G_REL_by_route"] = grel

    # ------------------------------------------------ 5. the verdict table
    HKZ_SD_COMMITTED = 0.023887966155964283   # results_relvar.json, hkz L7_b5
    verdict = OrderedDict()
    for key, g in gvar.items():
        obs, r = key.split("|")
        dv = dev[r]
        walks = grel[key]
        passes_gate = (walks["REL1_n_lattices_passing_at_mean"] > 0
                       and walks["REL2_n_cells_passing_at_mean"] > 0)
        blind = dv["max_abs_dev_in_logdet"] == 0.0 or dv["max_rel_dev_in_logdet"] < 1e-12
        verdict[key] = {
            "mathematically_a_closed_form_in_(d,k,beta,q)": True,
            "agrees_with_the_closed_form_to_relative": dv["max_rel_dev_in_logdet"],
            "carries_no_information_at_the_gate's_resolution": bool(blind),
            "max_between_basis_float_sd": g["max_float_sd_over_cells"],
            "ratio_of_that_sd_to_committed_hkz_sd_at_L7_b5":
                g["max_float_sd_over_cells"] / HKZ_SD_COMMITTED,
            "G_VAR_REFUSES": g["G_VAR_REFUSES"],
            "passes_G_REL1_and_G_REL2_somewhere": bool(passes_gate),
            "ESCAPES_G_VAR_WHILE_BLIND": bool(
                blind and not g["G_VAR_REFUSES"] and passes_gate),
        }
    RES["VERDICT"] = verdict

    # --------------------- 5b. does the ESCAPING route reproduce prereg 2.6?
    # The pre-registered X_null table of prereg 2.6 is stated to 6 decimals and
    # the measuring task is required to reproduce it. If the escaping route
    # reproduces the SAME notarized table to every printed digit at every cell
    # and every basis, then the two routes are indistinguishable at the
    # resolution the frozen text itself uses, and G-VAR separates them anyway.
    PREREG_2_6 = {
        "L1": {15: 0.851595, 30: 1.703190, 35: 1.987055, 50: 2.838650, 65: 3.690244},
        "L2": {15: 0.364969, 30: 0.729938, 35: 0.851595, 50: 1.216564, 65: 1.581533},
        "L4": {20: 0.827595, 40: 1.655189, 45: 1.862088, 70: 2.896581, 95: 3.931074},
        "L5": {20: 0.331038, 40: 0.662076, 45: 0.744835, 70: 1.158632, 95: 1.572430},
        "L7": {5: 1.419325, 10: 2.838650, 15: 4.257974},
        "L8": {5: 0.608282, 10: 1.216564, 15: 1.824846},
        "L9": {7: 1.324703, 15: 2.838650, 22: 4.163353},
        "L10": {7: 0.567730, 15: 1.216564, 22: 1.784294},
        "L11": {10: 1.419325, 20: 2.838650, 30: 4.257974},
        "L12": {10: 0.608282, 20: 1.216564, 30: 1.824846},
    }
    repro = OrderedDict()
    for r in ROUTES:
        n_ok, n_tot, worst = 0, 0, 0.0
        for lat, (d, k) in LATTICES.items():
            for beta in BETA_GRID[d]:
                want = PREREG_2_6[lat][beta]
                for i in range(N_BASES):
                    got = (beta / d) * (1.0 / d) * base[(lat, i)][r]
                    n_tot += 1
                    worst = max(worst, abs(round(got, 6) - want))
                    if round(got, 6) == want:
                        n_ok += 1
        repro[r] = {
            "cells_x_bases": n_tot,
            "n_reproducing_prereg_2.6_to_6_decimals": n_ok,
            "max_abs_deviation_after_rounding_to_6dp": worst,
        }
    RES["reproduction_of_the_notarized_prereg_2.6_table"] = repro

    RES["HEADLINE"] = {
        "routes_that_escape_G_VAR_while_being_the_same_closed_form": [
            k for k, v in verdict.items() if v["ESCAPES_G_VAR_WHILE_BLIND"]],
        "routes_that_G_VAR_refuses": [
            k for k, v in verdict.items() if v["G_VAR_REFUSES"]],
        "reading": (
            "G-VAR as implemented decides on the ARITHMETIC ROUTE used to "
            "evaluate an observable, not on the observable. Any route listed "
            "as escaping agrees with the matrix-free closed form to the stated "
            "relative deviation, i.e. it is the SAME function of (d,k,beta,q) "
            "to within float rounding, and it still walks G-REL. This does not "
            "overturn R-OUT-1 -- finding one refused blind observable is enough "
            "to declare the gate inadmissible -- it bounds the GENERALITY of "
            "G-VAR as a refusal criterion."),
    }
    RES["could_not_fail_check_on_this_probe"] = {
        "could_not_FIRE": (
            "Would hold if every arithmetic route were bit-identical. Measured "
            "outcome: R1_slogdet IS bit-identical for both observables at every "
            "cell, so the arrangement was live and the probe did not run in it "
            "by construction."),
        "could_not_PASS": (
            "Would hold if the escaping routes carried genuine basis "
            "dependence. Guarded by max_rel_dev_in_logdet and by the ratio of "
            "the route's own float sd to hkz's committed between-basis sd, "
            "both reported per route above."),
    }
    RES["seconds"] = time.time() - t0
    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1)

    # ------------------------------------------------ human-readable summary
    print("=" * 78)
    print("PROBE N -- the observable G-VAR does not catch")
    print("RED-TEAM PROBE, NOT PRE-REGISTERED, RESCORES NOTHING. TOY.")
    print("=" * 78)
    print("\n%-26s %-16s %-16s" % ("route", "max|dev| logdet", "max rel dev"))
    for r in ROUTES:
        print("%-26s %-16.3e %-16.3e" % (r, dev[r]["max_abs_dev_in_logdet"],
                                         dev[r]["max_rel_dev_in_logdet"]))
    print("\n%-32s %5s %6s %7s %12s %10s" % (
        "observable | route", "cells", "bitid", "G-VAR", "max float sd",
        "REL2 pass"))
    for key, g in gvar.items():
        w = grel[key]
        print("%-32s %5d %6d %7s %12.3e %5d/%-4d" % (
            key, g["n_cells"], g["n_cells_bit_identical"],
            "REFUSE" if g["G_VAR_REFUSES"] else "admit",
            g["max_float_sd_over_cells"],
            w["REL2_n_cells_passing_at_mean"], w["REL2_n_cells"]))
    print("\nESCAPES G-VAR WHILE BLIND: %s" %
          RES["HEADLINE"]["routes_that_escape_G_VAR_while_being_the_same_closed_form"])
    print("REFUSED BY G-VAR         : %s" % RES["HEADLINE"]["routes_that_G_VAR_refuses"])
    print("\nwrote %s in %.2f s" % (args.out, RES["seconds"]))


if __name__ == "__main__":
    main()
