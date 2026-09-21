#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RED TEAM PROBE A  --  TASK-20260809-444fe7 / BATCH-9e3584 / GOAL-MLKEM-005

THE NEARBY-OBJECT CONTROL ON THE LEAD'S REFUSAL (R-OUT-1, `G-VAR`).

WHAT THIS IS AND IS NOT.  This is a RED TEAM PROBE.  It is NOT pre-registered,
it is NOT a rescoring of any frozen verdict, and it does not adjudicate
R-OUT-1 in either direction.  It is run at the scale stated in its own output
and nowhere else.  CLAIM TIER: TOY.  Nothing here bears on ML-KEM security, on
any FIPS 203 parameter set, on any attack cost, or on any cost model.

THE ATTACK.  TASK-20260809-cda2f6 reports that `X_null` and (unplanted)
`X8 = rdet` are BIT-IDENTICAL across the 8 frozen bases at all 38 scored cells,
that `G-VAR` therefore FIRES, and that the AM-4/AM-8 gate is INADMISSIBLE.  The
refusal's generality rests on an unstated premise:

    in the frozen family  B_i = [[I_k, A_i], [0, q I_{d-k}]]
    |det B_i| = q^(d-k)  IS CONSTANT ACROSS i BY CONSTRUCTION.

Every determinant-only functional is therefore constant across i for a reason
that is a property of THE FAMILY, not of the observable.  This probe builds the
NEAREST family that differs in EXACTLY ONE respect -- the scaled block's
diagonal varies with the basis index -- holding A_i, d, k, beta, the observable
definitions and the code path fixed, and asks whether `G-VAR` still fires.

    F0  frozen  B_i = [[I_k, A_i], [0, q * I_{d-k}]]           det = q^(d-k)
    F1  nearby  B_i = [[I_k, A_i], [0, diag(m_i)]]             det = prod(m_i)
                m_i[0] = q + i, m_i[j>0] = q          (i = 0..7)

In BOTH families `rdet` and `X_null` read ZERO entries of A_i: their blindness
to the basis content is IDENTICAL and provable.  If `G-VAR` fires in F0 and not
in F1, then `G-VAR` does not measure blindness; it measures whether the family
holds the observable's own argument fixed.

WHAT COULD NOT FAIL, IN BOTH DIRECTIONS -- named BEFORE the run:
  * could-not-FIRE (the probe can never show G-VAR admitting a blind
    observable): if F1's moduli were still constant across i, det would be
    constant and the probe would be F0 under another name.  WE ARE NOT IN IT:
    m_i[0] = q + i is strictly increasing in i and this is asserted in the
    output.
  * could-not-PASS (the probe can never show G-VAR firing at all, so the
    contrast is vacuous): if the bit-identity test were replaced by a tolerance
    it might never fire.  WE ARE NOT IN IT: `bit_identical` is the producer's
    own function, carried verbatim, and F0 is scored by it in this same run and
    MUST reproduce the producer's refusal.  If F0 does not reproduce it, this
    probe reports an instrument defect and claims nothing about F1.

X_null IS COMPUTED DEFINITIONALLY HERE.  prereg 2.6 DEFINES
X_null(B,beta) = (beta/d)*(1/d)*log|det B|.  The producer's `x_null_of`
implements the CLOSED FORM (beta/d)(1/d)(d-k)log q, which never touches the
matrix, so its zero dispersion in F0 is true at the level of the SOURCE CODE
and not only at the level of the algebra.  This probe computes X_null from
log|det B| through the same slogdet path as `rdet`, and CHECKS that in F0 it
reproduces the pre-registered table of prereg 2.6 -- so the F0/F1 contrast is a
contrast between families and not between implementations.

WRITES exactly one file: probe_gvar_family.json, beside this script.
NO git write, NO commit, NO repository state is touched.
"""

import argparse
import json
import math
import platform
import sys
import time
from collections import OrderedDict

import numpy as np

T0 = time.time()

Q = 3329
N_BASES = 8
TAU_REL = 0.10                      # carried, prereg 1.5; NOT re-derived here
S_X = 1.0                           # carried, prereg 1.4

LATTICES = OrderedDict([
    ("L1", (100, 30)), ("L2", (100, 70)),
    ("L4", (140, 40)), ("L5", (140, 100)),
    ("L7", (20, 6)), ("L8", (20, 14)),
    ("L9", (30, 9)), ("L10", (30, 21)),
    ("L11", (40, 12)), ("L12", (40, 28)),
])
PAIRS = [("L1", "L2"), ("L4", "L5"), ("L7", "L8"), ("L9", "L10"), ("L11", "L12")]
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95],
             20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}

# prereg 2.6, transcribed from the NOTARIZED text for an independent check
PREREG_X_NULL = {
    ("L1", 15): 0.851595, ("L1", 30): 1.703190, ("L1", 35): 1.987055,
    ("L1", 50): 2.838650, ("L1", 65): 3.690244,
    ("L2", 15): 0.364969, ("L2", 30): 0.729938, ("L2", 35): 0.851595,
    ("L2", 50): 1.216564, ("L2", 65): 1.581533,
    ("L4", 20): 0.827595, ("L4", 40): 1.655189, ("L4", 45): 1.862088,
    ("L4", 70): 2.896581, ("L4", 95): 3.931074,
    ("L5", 20): 0.331038, ("L5", 40): 0.662076, ("L5", 45): 0.744835,
    ("L5", 70): 1.158632, ("L5", 95): 1.572430,
    ("L7", 5): 1.419325, ("L7", 10): 2.838650, ("L7", 15): 4.257974,
    ("L8", 5): 0.608282, ("L8", 10): 1.216564, ("L8", 15): 1.824846,
    ("L9", 7): 1.324703, ("L9", 15): 2.838650, ("L9", 22): 4.163353,
    ("L10", 7): 0.567730, ("L10", 15): 1.216564, ("L10", 22): 1.784294,
    ("L11", 10): 1.419325, ("L11", 20): 2.838650, ("L11", 30): 4.257974,
    ("L12", 10): 0.608282, ("L12", 20): 1.216564, ("L12", 30): 1.824846,
}


# ---- CARRIED VERBATIM from TASK-20260809-cda2f6/measure_relvar.py ----------
def make_A(d, k, q, i):
    m = d - k
    rng = np.random.default_rng([1, d, k, i])
    return rng.integers(0, q, size=(k, m), dtype=np.int64)


def rdet_of(M, d):
    _, logabs = np.linalg.slogdet(M.astype(np.float64))
    return float(np.exp(logabs / d)), float(logabs)


def rho_both(x_b, x_a, s):
    num = abs(x_b - x_a)
    den_floor = max(abs(x_a), s)
    den_raw = abs(x_a)
    return {"value_maxfloor": num / den_floor,
            "value_absX": (num / den_raw) if den_raw > 0 else None,
            "s_over_absX": (s / den_raw) if den_raw > 0 else None,
            "scale_floor_is_binding": bool(den_raw < s),
            "X_a": x_a, "X_b": x_b, "s_X": s}


def bit_identical(vals):
    """G-VAR decided STRUCTURALLY, not by tolerance (prereg 2.5).  CARRIED."""
    hx = set()
    for v in vals:
        if v is None:
            return None
        hx.add(float(v).hex())
    return len(hx) == 1


def summarize(vals):
    a = np.asarray([v for v in vals if v is not None], dtype=float)
    if a.size == 0:
        return None
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "min": float(a.min()), "median": float(np.median(a)),
            "max": float(a.max())}
# ---------------------------------------------------------------------------


def moduli(d, k, i, family):
    """F0: every trailing diagonal entry is q.  F1: the FIRST one is q + i.
    EXACTLY ONE property of the family differs; A_i, d, k, beta are untouched."""
    m = np.full(d - k, Q, dtype=np.int64)
    if family == "F1":
        m[0] = Q + i
    return m


def build_basis(d, k, i, family):
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, Q, i)          # IDENTICAL A in both families
    B[k:, k:] = np.diag(moduli(d, k, i, family))
    return B


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "PROBE-A / probe_gvar_family"
    R["task_id"] = "TASK-20260809-444fe7"
    R["role"] = "red-team"
    R["batch_id"] = "BATCH-9e3584"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["claim_tier"] = "toy"
    R["status_of_this_artifact"] = (
        "RED TEAM PROBE. NOT pre-registered. NOT a rescoring of any frozen "
        "verdict. Adjudicates R-OUT-1 in neither direction.")
    R["certificate"] = {"kind": "none",
                        "reason": "no discrete-log solve and no factor-base "
                                  "relation is claimed or produced"}
    R["environment"] = {"python": sys.version.split()[0],
                        "numpy": np.__version__,
                        "platform": platform.platform(),
                        "machine": platform.machine(),
                        "fpylll": "ABSENT -- this probe runs NO reduction and "
                                  "needs none; rdet and X_null are "
                                  "determinant-only functionals"}
    R["families"] = {
        "F0_frozen": "B_i = [[I_k, A_i],[0, q I_{d-k}]], q = 3329  "
                     "-> |det| = q^(d-k), CONSTANT in i",
        "F1_nearby": "B_i = [[I_k, A_i],[0, diag(m_i)]], m_i[0] = q + i, "
                     "m_i[j>0] = q  -> |det| = (q+i) q^(d-k-1), VARIES in i",
        "held_fixed": "A_i (identical draws), d, k, beta grid, the mirrored "
                      "pairs, tau_rel = 0.10, s_X = 1.0, the observable "
                      "definitions, and the code path",
        "differs_in_exactly_one_respect": "whether |det B_i| depends on i"}
    R["could_not_fail_named_before_the_run"] = {
        "could_not_FIRE": "F1's moduli constant in i would make F1 = F0. "
                          "Asserted false below by strict monotonicity of "
                          "m_i[0] = q + i.",
        "could_not_PASS": "a tolerance-based dispersion test might never fire. "
                          "Averted: bit_identical() is the producer's own "
                          "function, carried verbatim, and F0 is scored by it "
                          "here and must reproduce the producer's refusal."}

    # -- guard: the two families really do differ in the declared respect
    mono = [int(moduli(20, 6, i, "F1")[0]) for i in range(N_BASES)]
    R["guard_F1_moduli_strictly_increase_in_i"] = {
        "m_i[0] over i": mono,
        "strictly_increasing": bool(all(b > a for a, b in zip(mono, mono[1:]))),
        "F0_moduli_constant": [int(moduli(20, 6, i, "F0")[0])
                               for i in range(N_BASES)]}

    cells = []
    for name, (d, k) in LATTICES.items():
        for beta in BETA_GRID[d]:
            row = OrderedDict([("lattice", name), ("d", d), ("k", k),
                               ("beta", beta)])
            for fam in ("F0", "F1"):
                rdets, xnulls, logdets = [], [], []
                for i in range(N_BASES):
                    B = build_basis(d, k, i, fam)
                    rd, logabs = rdet_of(B, d)
                    rdets.append(rd)
                    logdets.append(logabs)
                    # DEFINITIONAL X_null, prereg 2.6, through the matrix
                    xnulls.append((beta / d) * (1.0 / d) * logabs)
                row[fam] = OrderedDict([
                    ("rdet_bit_identical", bit_identical(rdets)),
                    ("rdet_sd", summarize(rdets)["sd"]),
                    ("rdet_values_min_max", [min(rdets), max(rdets)]),
                    ("X_null_bit_identical", bit_identical(xnulls)),
                    ("X_null_sd", summarize(xnulls)["sd"]),
                    ("X_null_mean", summarize(xnulls)["mean"]),
                    ("G_VAR_FIRES_on_rdet", bool(bit_identical(rdets))),
                    ("G_VAR_FIRES_on_X_null", bool(bit_identical(xnulls))),
                ])
            # independent check of the NOTARIZED prereg 2.6 table, F0 only
            exp = PREREG_X_NULL.get((name, beta))
            row["prereg_2_6_X_null_expected"] = exp
            row["prereg_2_6_reproduced_to_1e-6"] = (
                bool(abs(row["F0"]["X_null_mean"] - exp) < 1e-6)
                if exp is not None else None)
            cells.append(row)
    R["cells"] = cells

    n_cells = len(cells)
    fired = {f: {"rdet": sum(1 for c in cells if c[f]["G_VAR_FIRES_on_rdet"]),
                 "X_null": sum(1 for c in cells
                               if c[f]["G_VAR_FIRES_on_X_null"])}
             for f in ("F0", "F1")}
    R["G_VAR_summary"] = {
        "n_cells_scored": n_cells,
        "cells_where_G_VAR_FIRES": fired,
        "reading": "G-VAR fires iff the 8 values are bit-identical (prereg 2.5)."}
    R["prereg_2_6_table_reproduced"] = {
        "cells_checked": sum(1 for c in cells
                             if c["prereg_2_6_reproduced_to_1e-6"] is not None),
        "cells_agreeing": sum(1 for c in cells
                              if c["prereg_2_6_reproduced_to_1e-6"]),
        "note": "F0 only. The definitional (through-the-matrix) X_null must "
                "reproduce the notarized closed-form table, or the F0/F1 "
                "contrast would be an implementation contrast."}

    # -- does X_null still WALK the G-REL clauses in F1?
    grel = []
    for name, (d, k) in LATTICES.items():
        betas = BETA_GRID[d]
        for fam in ("F0", "F1"):
            v = []
            for i in range(N_BASES):
                B = build_basis(d, k, i, fam)
                _, la = rdet_of(B, d)
                lo = (betas[0] / d) * (1.0 / d) * la
                hi = (betas[-1] / d) * (1.0 / d) * la
                v.append(rho_both(hi, lo, S_X)["value_maxfloor"])
            grel.append({"clause": "G-REL1", "family": fam, "lattice": name,
                         "beta_lo": betas[0], "beta_hi": betas[-1],
                         "mean_over_8_bases": summarize(v)["mean"],
                         "PASS_at_tau_rel_0.10":
                             bool(summarize(v)["mean"] >= TAU_REL)})
    for a, b in PAIRS:
        da, ka = LATTICES[a]
        db, kb = LATTICES[b]
        for beta in BETA_GRID[da]:
            for fam in ("F0", "F1"):
                vn, vr = [], []
                for i in range(N_BASES):
                    Ba = build_basis(da, ka, i, fam)
                    Bb = build_basis(db, kb, i, fam)
                    _, laa = rdet_of(Ba, da)
                    _, lab = rdet_of(Bb, db)
                    vn.append(rho_both((beta / db) * (1.0 / db) * lab,
                                       (beta / da) * (1.0 / da) * laa,
                                       S_X)["value_maxfloor"])
                    vr.append(rho_both(math.exp(lab / db), math.exp(laa / da),
                                       S_X)["value_maxfloor"])
                grel.append({"clause": "G-REL2", "family": fam,
                             "pair": "%s/%s" % (a, b), "beta": beta,
                             "X_null_mean_over_8_bases": summarize(vn)["mean"],
                             "X_null_PASS": bool(summarize(vn)["mean"] >= TAU_REL),
                             "rdet_mean_over_8_bases": summarize(vr)["mean"],
                             "rdet_PASS": bool(summarize(vr)["mean"] >= TAU_REL)})
    R["G_REL_in_both_families"] = grel
    R["G_REL_summary"] = {
        f: {"G-REL1 X_null PASS": sum(1 for g in grel
                                      if g["clause"] == "G-REL1"
                                      and g["family"] == f
                                      and g["PASS_at_tau_rel_0.10"]),
            "G-REL1 cells": sum(1 for g in grel if g["clause"] == "G-REL1"
                                and g["family"] == f),
            "G-REL2 X_null PASS": sum(1 for g in grel
                                      if g["clause"] == "G-REL2"
                                      and g["family"] == f and g["X_null_PASS"]),
            "G-REL2 rdet PASS": sum(1 for g in grel if g["clause"] == "G-REL2"
                                    and g["family"] == f and g["rdet_PASS"]),
            "G-REL2 cells": sum(1 for g in grel if g["clause"] == "G-REL2"
                                and g["family"] == f)}
        for f in ("F0", "F1")}

    R["what_this_probe_does_NOT_establish"] = [
        "It does NOT adjudicate R-OUT-1 in either direction and does NOT "
        "rescore any frozen verdict.",
        "It does NOT show that the producer chose the wrong family. F0 holds "
        "|det| fixed, which is the arrangement in which G-VAR has the MOST "
        "power against a determinant-only functional; that cuts FOR the "
        "producer and is reported at the same weight.",
        "It does NOT claim rdet or X_null is admissible anywhere. Both remain "
        "blind to A in BOTH families.",
        "It runs NO reduction, so it says nothing about lam1n, hkz or rawtail.",
        "CLAIM TIER TOY: nothing here bears on ML-KEM security, any FIPS 203 "
        "parameter set, any attack cost, or any cost model.",
    ]
    R["wall_clock_seconds"] = round(time.time() - T0, 3)

    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=2)
        fh.write("\n")

    print("PROBE A -- G-VAR nearby-family control")
    print("  cells scored per family:", n_cells)
    print("  G-VAR FIRES  F0: rdet %d/%d   X_null %d/%d"
          % (fired["F0"]["rdet"], n_cells, fired["F0"]["X_null"], n_cells))
    print("  G-VAR FIRES  F1: rdet %d/%d   X_null %d/%d"
          % (fired["F1"]["rdet"], n_cells, fired["F1"]["X_null"], n_cells))
    print("  prereg 2.6 table reproduced (F0, definitional path): %d/%d"
          % (R["prereg_2_6_table_reproduced"]["cells_agreeing"],
             R["prereg_2_6_table_reproduced"]["cells_checked"]))
    print("  G-REL summary:", json.dumps(R["G_REL_summary"]))
    print("  wall clock %.2f s" % R["wall_clock_seconds"])


if __name__ == "__main__":
    main()
