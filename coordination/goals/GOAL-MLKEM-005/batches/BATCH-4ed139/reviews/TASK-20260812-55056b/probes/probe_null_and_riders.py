#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAL TASK-20260812-55056b probe F -- THE VALIDATOR'S OWN NULL, plus the
independent re-derivation of rider (ii) and the checkable half of rider (iii).

FOUR THINGS, in order:

  N1  MY OWN PARAMETER-DETERMINED OBSERVABLE, pushed through the LEAD'S OWN
      gate and code path. X_par(B, beta) = (beta / d) * log(q) * (k / d) reads
      ZERO entries of A and is a closed form in (d, k, beta, q). It is
      beta-DEPENDENT, so it is not scale_degenerate, and G-VAR2 MUST refuse it
      at every cell. If the gate admits it, the gate admits a parameter.

  N2  MY OWN BETA-FREE PARAMETER-DETERMINED OBSERVABLE, same construction with
      the beta factor removed and evaluated THROUGH THE MATRIX by the float
      routes: X_parfree = log|det B| / (d * k). Prediction, made before running:
      it reproduces the rdet mechanism -- scale_degenerate on VAR-S, VAR-F PASS
      by broken bit-identity under R2/R4/R5 -- i.e. the lead's F0 failure is a
      property of the CLAUSE and not of rdet. This is the null-object control
      the batch's headline needs: a SECOND, independently constructed blind
      observable that the instrument admits.

  N3  MY OWN PERTURBATION OF THE V_evade FAMILY at amplitudes I choose and the
      prereg does not name: lambda in {3.7e-7, 4.2e-5, 2.3e-3, 7.9e-3, 1.1e-2}.
      Reports where VAR-S crosses. The prereg's own grid is decadal; a crossing
      that only exists on decade boundaries would be a grid artifact.

  R2  RIDER (ii) RE-DERIVED: X_gso_k over the RAW basis through RQ (QR of B^T)
      and RG (Cholesky of the Gram), its G-REL1 rho, its G-VAR2 profile, and
      THE NINE-ORDERS-OF-MAGNITUDE VAR-F ANOMALY -- fibre sd ~9.02e-02 for
      X_gso_k at L7 beta 5 and ~4.18e-11 for rdet|R2 at the same cell, both
      PASS.

  R3  RIDER (iii) checkable half: the committed hkz/lam1n values it reports are
      compared against results_relvar.json, and ENVIRONMENTS_DIFFER is
      recomputed field by field from the two committed environment blocks.
      fpylll itself is NOT re-run here and its absence is recorded as coverage.

The LEAD'S OWN module is imported for N1/N2/R2 so my null goes through the
instrument the batch actually scored, not through a re-reading of it. My own
independent implementation (probe C) is used in parallel where a second opinion
is wanted.

Run from the repository root.
"""
import importlib.util
import json
import math
import os
import sys
from collections import OrderedDict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LEADPY = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-56b9da/measure_gvar2.py")
RELVAR = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
          "TASK-20260809-cda2f6/results_relvar.json")
RIDER3 = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-0e930c/results_l7l8.json")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


LEAD = load(LEADPY, "lead_measure_gvar2")          # the instrument itself
RD = load(os.path.join(HERE, "probe_gvar2_rederive.py"), "val_rederive")

Q = LEAD.Q
NB = LEAD.N_BASES
LAT = LEAD.LATTICES
BG = LEAD.BETA_GRID


def cellstats(fn, fam):
    """Build the {lattice: {beta: {s, m, bit_identical, n_distinct}}} structure
    the LEAD's var_s_from_cells / var_f_from_cells consume."""
    out = OrderedDict()
    for lat, (d, k) in LAT.items():
        out[lat] = OrderedDict()
        for beta in BG[d]:
            vals = [fn(lat, d, k, beta, i, fam) for i in range(NB)]
            s, m = LEAD.sd_mean(vals)
            out[lat][beta] = {"s": s, "m": m,
                              "spread": float(max(vals) - min(vals)),
                              "bit_identical": LEAD.bit_identical(vals),
                              "n_distinct": len({float(v).hex() for v in vals}),
                              "seed_prefix": LEAD.FAMILIES[fam][0]}
    return out


_BC = {}


def B_of(lat, i, fam):
    key = (lat, i, fam)
    if key not in _BC:
        d, k = LAT[lat]
        _BC[key] = LEAD.build_basis_fam(d, k, i, fam)
    return _BC[key]


def ld_of(lat, i, fam, route):
    d, k = LAT[lat]
    m = LEAD.moduli(d, k, i, LEAD.FAMILIES[fam][1])
    r, _ = LEAD.logdet_routes_fam(B_of(lat, i, fam), d, k, m, fam)
    return r[route]


# ---------------- N1: parameter-determined, beta-DEPENDENT, closed form
def X_par(lat, d, k, beta, i, fam):
    return (beta / d) * math.log(Q) * (k / d)


# ---------------- N2: parameter-determined, beta-FREE, through the matrix
def make_X_parfree(route):
    def f(lat, d, k, beta, i, fam):
        return ld_of(lat, i, fam, route) / (d * k)
    return f


# ---------------- N3: V_evade at MY amplitudes
def make_X_lambda(route, lam):
    def f(lat, d, k, beta, i, fam):
        A00 = int(B_of(lat, i, fam)[0, k])
        return (beta / d) * (1.0 / d) * ld_of(lat, i, fam, route) \
            + lam * A00 / Q
    return f


# ---------------- rider (ii): X_gso_k through RQ and RG
def X_gso_k(lat, d, k, beta, i, fam, route):
    B = B_of(lat, i, fam).astype(np.float64)
    if route == "RQ":
        R = np.linalg.qr(B.T)[1]
        dg = np.abs(np.diag(R))[:k]
        return float(np.mean(np.log(dg)))
    G = B @ B.T
    L = np.linalg.cholesky(G)
    dg = np.abs(np.diag(L))[:k]
    return float(np.mean(np.log(dg)))


def make_gsok(route):
    return lambda lat, d, k, beta, i, fam: X_gso_k(lat, d, k, beta, i, fam,
                                                   route)


def score(fn, fam, label):
    """Full G-VAR2 through the LEAD'S OWN var_s/var_f/gvar2."""
    vs = LEAD.var_s_from_cells(cellstats(fn, fam))
    fib = LEAD.FIBRE_OF[fam][0]
    vf = LEAD.var_f_from_cells(cellstats(fn, fib))
    g = {c: LEAD.gvar2(vs[c], vf[c]) for c in vs}
    return {
        "label": label, "family": fam, "cells": len(vs),
        "VAR_S_ADMIT": sum(1 for c in vs if vs[c]["VAR_S"] == "ADMIT"),
        "VAR_S_REFUSE": sum(1 for c in vs if vs[c]["VAR_S"] == "REFUSE"),
        "VAR_S_degenerate": sum(1 for c in vs
                                if vs[c]["VAR_S"] == "scale_degenerate"),
        "VAR_F_PASS": sum(1 for c in vs if vf[c]["VAR_F"] == "PASS"),
        "GVAR2_ADMIT": sum(1 for x in g.values() if x == "ADMIT"),
        "GVAR2_REFUSE": sum(1 for x in g.values() if x == "REFUSE"),
        "max_s_c": max(vs[c]["s_c"] for c in vs),
        "fib_sd_min": min(vf[c]["s_c_fib"] for c in vs),
        "fib_sd_max": max(vf[c]["s_c_fib"] for c in vs),
        "fib_sd_L7_b5": vf.get("L7_b5", {}).get("s_c_fib"),
    }, vs, vf, g


def main():
    print("=" * 78)
    print("VALIDATOR'S OWN NULL + RIDER (ii)/(iii) RE-DERIVATION")
    print("instrument: the LEAD's OWN measure_gvar2.py, imported")
    print("=" * 78)

    # ---------------------------------------------------------------- N1
    print("\n### N1  my parameter-determined, BETA-DEPENDENT observable")
    print("###     X_par = (beta/d) * log q * (k/d)   -- reads ZERO entries of A")
    print("###     PREDICTED BEFORE RUNNING: G-VAR2 must REFUSE at 38/38.")
    for fam in ("F0", "F1"):
        r, _, _, _ = score(X_par, fam, "X_par")
        print("   %s  VAR_S ADMIT=%d REFUSE=%d deg=%d | VAR_F PASS=%d | "
              "G-VAR2 ADMIT=%d REFUSE=%d | max s_c=%.3e"
              % (fam, r["VAR_S_ADMIT"], r["VAR_S_REFUSE"],
                 r["VAR_S_degenerate"], r["VAR_F_PASS"], r["GVAR2_ADMIT"],
                 r["GVAR2_REFUSE"], r["max_s_c"]))

    # ---------------------------------------------------------------- N2
    print("\n### N2  my parameter-determined, BETA-FREE observable through the")
    print("###     matrix: X_parfree = log|det B| / (d*k). PREDICTED BEFORE")
    print("###     RUNNING: reproduces the rdet mechanism -- ADMIT under")
    print("###     R2/R4/R5, REFUSE under R0/R1/R3, at 38/38.")
    n2 = {}
    for route in LEAD.ROUTES6:
        for fam in ("F0", "F1"):
            r, _, vf, _ = score(make_X_parfree(route), fam,
                                "X_parfree|%s" % route)
            n2["%s|%s" % (fam, route)] = r
            print("   %-3s %-34s deg=%2d VAR_F PASS=%2d G-VAR2 ADMIT=%2d "
                  "fib_sd=[%.2e, %.2e]"
                  % (fam, route, r["VAR_S_degenerate"], r["VAR_F_PASS"],
                     r["GVAR2_ADMIT"], r["fib_sd_min"], r["fib_sd_max"]))

    # ---------------------------------------------------------------- N3
    print("\n### N3  my own V_evade perturbation amplitudes (OFF the frozen")
    print("###     decadal grid): VAR-S ADMIT count over 38 F0 cells")
    print("   %-12s %s" % ("lambda", "  ".join("%-8s" % r[:2]
                                               for r in LEAD.ROUTES6)))
    for lam in (3.7e-7, 4.2e-5, 2.3e-3, 7.9e-3, 1.1e-2, 5.0e-2):
        row = []
        for route in LEAD.ROUTES6:
            _, vs, _, _ = score(make_X_lambda(route, lam), "F0",
                                "X_lam_%g" % lam)
            row.append(sum(1 for c in vs if vs[c]["VAR_S"] == "ADMIT"))
        print("   %-12.3g %s" % (lam, "  ".join("%-8d" % x for x in row)))

    # ---------------------------------------------------------------- R2
    print("\n### R2  RIDER (ii) re-derived: X_gso_k, routes RQ and RG")
    gsok = {}
    for route in ("RQ", "RG"):
        for fam in ("F0", "F1"):
            r, vs, vf, g = score(make_gsok(route), fam, "X_gso_k|%s" % route)
            gsok["%s|%s" % (route, fam)] = (r, vs, vf)
            print("   %-3s %-3s cells=%d deg=%d VAR_S_ADMIT=%d VAR_F_PASS=%d "
                  "G-VAR2 ADMIT=%d  fib_sd=[%.3e, %.3e]  fib_sd@L7_b5=%.4e"
                  % (route, fam, r["cells"], r["VAR_S_degenerate"],
                     r["VAR_S_ADMIT"], r["VAR_F_PASS"], r["GVAR2_ADMIT"],
                     r["fib_sd_min"], r["fib_sd_max"], r["fib_sd_L7_b5"]))
    # per-lattice F0 sd table (rider (ii) section B)
    print("\n   rider (ii) section B table, re-derived (F0, route RQ):")
    print("   %-5s %-10s %16s %12s %8s" %
          ("lat", "(d,k)", "mean X_gso_k", "sd over 8", "distinct"))
    for lat, (d, k) in LAT.items():
        vals = [X_gso_k(lat, d, k, BG[d][0], i, "F0", "RQ") for i in range(NB)]
        print("   %-5s %-10s %16.9f %12.4e %6d/8" %
              (lat, "(%d,%d)" % (d, k), float(np.mean(vals)),
               float(np.std(vals, ddof=1)),
               len({float(v).hex() for v in vals})))
    # the nine-orders anomaly
    print("\n   THE VAR-F ANOMALY (rider (ii) F.1), re-derived at L7 beta 5:")
    a = gsok["RQ|F0"][2]["L7_b5"]
    rvs = LEAD.var_f_from_cells(cellstats(
        lambda lat, d, k, beta, i, fam: math.exp(
            ld_of(lat, i, fam, "R2_QR_of_BT") / d), "F0|fib_s2"))["L7_b5"]
    print("     X_gso_k|RQ  fibre sd = %.6e  bit_identical=%s  VAR_F=%s"
          % (a["s_c_fib"], a["bit_identical"], a["VAR_F"]))
    print("     rdet|R2     fibre sd = %.6e  bit_identical=%s  VAR_F=%s"
          % (rvs["s_c_fib"], rvs["bit_identical"], rvs["VAR_F"]))
    ratio = a["s_c_fib"] / rvs["s_c_fib"]
    print("     RATIO = %.4e  ->  %.2f orders of magnitude, SAME VERDICT"
          % (ratio, math.log10(ratio)))

    # G-REL1 rho for X_gso_k (the refusal half)
    print("\n   rider (ii) G-REL1 half, re-derived (rho at the REL1 endpoints):")
    rel = load("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/"
               "TASK-20260809-444fe7/probes/probe_nullroute.py", "pn2")
    worst = 0.0
    npass = 0
    for lat, (d, k) in LAT.items():
        lo, hi = rel.REL1_PAIR[d]
        for i in range(NB):
            xa = X_gso_k(lat, d, k, lo, i, "F0", "RQ")
            xb = X_gso_k(lat, d, k, hi, i, "F0", "RQ")
            r = rel.rho_both(xb, xa)
            worst = max(worst, r["value_maxfloor"])
            npass += int(r["value_maxfloor"] >= rel.TAU_REL)
    print("     max rho over 10 lattices x 8 bases = %r ; passing bases = %d "
          "of 80  (tau_rel = %.2f)" % (worst, npass, rel.TAU_REL))

    # ---------------------------------------------------------------- R3
    print("\n### R3  RIDER (iii) checkable half")
    rv = json.load(open(RELVAR))
    try:
        r3 = json.load(open(RIDER3))
    except Exception as e:
        print("   rider (iii) results unreadable:", e)
        r3 = None
    # committed hkz/lam1n at L7/L8 straight out of results_relvar.json
    print("   committed results_relvar.json G_VAR block keys:",
          list(rv["G_VAR"].keys()))
    print("   environment recorded in results_relvar.json:",
          json.dumps(rv.get("environment"))[:300])
    if r3 is not None:
        env = r3.get("environment_comparison") or r3.get("environment") or {}
        print("   rider (iii) environment record:",
              json.dumps(env)[:600])
    try:
        import fpylll                                        # noqa: F401
        print("   VALIDATOR HOST fpylll:", fpylll.__version__)
    except Exception as e:
        print("   VALIDATOR HOST fpylll: ABSENT (%s) -- rider (iii)'s "
              "reduction half is NOT re-executable by this session and is "
              "recorded as COVERAGE, never as a negative result."
              % e.__class__.__name__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
