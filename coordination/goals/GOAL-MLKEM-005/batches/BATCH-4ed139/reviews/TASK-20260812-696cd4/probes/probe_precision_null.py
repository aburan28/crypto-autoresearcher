#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED-TEAM PROBE 2 -- THE NULL-OBJECT CONTROL FOR THE F0 FAILURE, AND THE
PARAMETER THAT IS SUPPOSED TO DESTROY THE SIGNAL.

TASK-20260812-696cd4 / BATCH-4ed139 / GOAL-MLKEM-005.  Role: red-team.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

THIS IS A PROBE, NOT A PRE-REGISTERED MEASUREMENT.  Written after the lead's
numbers were committed.  IT RESCORES NO FROZEN VERDICT.  R2-OUT-1 = FAIL,
R2-OUT-2 = FAIL, R2-OUT-V does not fire and the branch is T-F0FAIL-PARTIAL;
those are the lead's, they are read here as inputs, and nothing below changes
them.  What is added here is a route and a precision axis that the frozen text
does not contain, evaluated on objects it does contain.

THE QUESTION.  The lead's F0 FAILURE has exactly one cause: `rdet` -- which
reads ZERO entries of A -- is ADMITTED at 38/38 cells through routes R2, R4 and
R5, because VAR-S is scale_degenerate there and VAR-F's bit-identity fallback
sees eight distinct IEEE-754 values on a fibre family whose EXACT determinants
are equal.  docs/inventor-protocol.md section 3 requires that any reported
signal be measured against a null object of the same shape, and that one name
the parameter which is supposed to destroy it.

  NULL OBJECT   `rdet` on the fibre: reads no entry of A, so its fibre
                dispersion CANNOT be information about A.
  REAL OBJECT   `X_gso_k` (rider ii's, PREREG-1 2.4) on the same fibre: reads
                the leading k Gram-Schmidt norms, so its fibre dispersion is
                A-dependence.
  THE PARAMETER Arithmetic precision.  If a fibre dispersion is rounding noise
                it must TRACK MACHINE EPSILON; if it is A-dependence it must be
                precision-invariant.

  PREDICTION, STATED BEFORE THE NUMBERS ARE READ (this probe's own, not
  pre-registered anywhere): rdet's RELATIVE fibre dispersion s/|m| scales like
  the working precision's eps -- roughly 5e8 times larger in float32 than in
  float64 -- and is EXACTLY ZERO when the determinant is not read through a
  float at all.  X_gso_k's relative fibre dispersion is unchanged (within a
  small factor) between float32 and float64.
  FALSIFIER: rdet's relative fibre dispersion does NOT move with precision, or
  X_gso_k's collapses with it.  Either outcome would mean the lead's F0 failure
  is not a float-representation effect and this probe's reading is wrong.

ALSO BUILT HERE -- THE NEARBY OBJECT THAT SHOULD NOT FAIL.  Route `R6_exact`:
log abs(det B) taken from the EXACT integer determinant through `decimal` at 60
significant digits, i.e. the same observable `rdet` with the float
representation removed and nothing else changed.  If G-VAR2 then REFUSES `rdet`
at 38/38 -- F0's declared target -- the F0 failure is localised to the float
representation of the determinant and to nothing else.

AND ONE CHEAP ENVIRONMENT FALSIFIER: the same R2/R4/R5 fibre values recomputed
with the BLAS thread count pinned to 1 and to 4, to see whether the non-bit-
identity that decides the F0 verdict is a threading artefact that a different
host might not reproduce.  (Run the script twice under different thread caps;
the cap in force is recorded in the output.)

PROVENANCE.  measure_gvar2.py (the lead, committed at 3aac83fd8) is IMPORTED.
Its main() is never called and no committed file is modified.

RE-EXECUTABLE:
    PYTHONDONTWRITEBYTECODE=1 python3 -B probe_precision_null.py \
        --out probe_precision_null_output.json
WRITES exactly one file: the --out path.
"""

import argparse
import decimal
import hashlib
import importlib.util
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import OrderedDict

sys.dont_write_bytecode = True

import numpy as np

T0 = time.time()


def repo_root():
    env = os.environ.get("GVAR2_REPO_ROOT")
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    return subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()


REPO = repo_root()
LEAD = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-56b9da/measure_gvar2.py")
RIDER2 = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-4b8ede/results_falserefusal.json")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


LD = load_module(LEAD, "lead_measure_gvar2_committed")
Q = LD.Q
N_BASES = LD.N_BASES
TAU_VAR = LD.TAU_VAR
LATTICES = LD.LATTICES
BETA_GRID = LD.BETA_GRID
bit_identical = LD.bit_identical
sd_mean = LD.sd_mean
var_f_from_cells = LD.var_f_from_cells
var_s_from_cells = LD.var_s_from_cells
gvar2 = LD.gvar2


def logdet_routes_prec(B, dt):
    """R1, R2, R4, R5 in working precision `dt`.  R0 and R3 are excluded: R0
    never touches the matrix and R3's U is integral, so neither carries the
    effect under test."""
    Bf = B.astype(dt)
    out = OrderedDict()
    _, la = np.linalg.slogdet(Bf)
    out["R1_slogdet"] = float(la)
    _, Rm = np.linalg.qr(Bf.T)
    out["R2_QR_of_BT"] = float(np.sum(np.log(np.abs(np.diag(Rm)))))
    G = Bf @ Bf.T
    _, la4 = np.linalg.slogdet(G)
    out["R4_gram_half_slogdet"] = float(0.5 * la4)
    H = LD.PROBE_N.fixed_isometry(B.shape[0]).astype(dt)
    _, la5 = np.linalg.slogdet(Bf @ H)
    out["R5_slogdet_of_BH_ambient_isometry"] = float(la5)
    return out


def x_gso_k_prec(B, k, dt):
    """rider (ii)'s X_gso_k through route RQ in working precision `dt`."""
    _, Rm = np.linalg.qr(B.astype(dt).T)
    dg = np.abs(np.diag(Rm))[:k]
    return float(np.mean(np.log(dg.astype(np.float64))))


def rdet_exact(absdet, d, prec=60):
    """Route R6_exact: rdet = abs(det B)^(1/d) from the EXACT integer
    determinant, through `decimal` at `prec` significant digits.  No float
    representation of the determinant is read anywhere."""
    with decimal.localcontext() as ctx:
        ctx.prec = prec
        v = decimal.Decimal(absdet).ln() / decimal.Decimal(d)
        return v.exp()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "RT-PROBE-2-PRECISION-NULL"
    R["task_id"] = "TASK-20260812-696cd4"
    R["batch_id"] = "BATCH-4ed139"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["role"] = "red-team"
    R["claim_tier"] = "toy"
    R["status"] = ("PROBE. NOT pre-registered; written after the producers' "
                   "numbers were committed. Rescores NO frozen verdict.")
    R["prediction_stated_before_reading_the_numbers"] = {
        "statement": "rdet's RELATIVE fibre dispersion s/|m| tracks machine "
                     "epsilon (about 5e8 x larger in float32 than in float64) "
                     "and is exactly 0 through the exact-integer route; "
                     "X_gso_k's is precision-invariant to within a small "
                     "factor.",
        "falsifier": "rdet's relative fibre dispersion does not move with "
                     "precision, or X_gso_k's collapses with it."}
    R["environment"] = {
        "python": platform.python_version(), "numpy": np.__version__,
        "platform": platform.platform(), "cpu_count": os.cpu_count(),
        "thread_caps_in_force": {v: os.environ.get(v) for v in
                                 ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                  "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                                  "VECLIB_MAXIMUM_THREADS")}}
    try:
        R["git_revision"] = subprocess.run(
            ["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip()
    except Exception as e:
        R["git_revision"] = "UNAVAILABLE: %s" % e
    R["inputs_sha256"] = {
        "measure_gvar2.py (lead, committed 3aac83fd8)": sha256_file(LEAD),
        "results_falserefusal.json (rider ii, committed d38514d22)":
            sha256_file(RIDER2)}
    R["eps"] = {"float32": float(np.finfo(np.float32).eps),
                "float64": float(np.finfo(np.float64).eps)}

    FIB = "F0|fib_s2"          # the primary fibre family, exactly as frozen

    # ------------------------------------------------ 1. the precision sweep
    print("[1] precision sweep on the fibre family %s" % FIB)
    sweep = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        rows = OrderedDict()
        per_dt = {}
        for dtname, dt in (("float32", np.float32), ("float64", np.float64)):
            vals_by_route = OrderedDict()
            gso = []
            for i in range(N_BASES):
                B = LD.build_basis_fam(d, k, i, FIB)
                rr = logdet_routes_prec(B, dt)
                for rname, v in rr.items():
                    vals_by_route.setdefault(rname, []).append(math.exp(v / d))
                gso.append(x_gso_k_prec(B, k, dt))
            per_dt[dtname] = (vals_by_route, gso)
        for rname in per_dt["float64"][0]:
            row = {}
            for dtname in ("float32", "float64"):
                vals = per_dt[dtname][0][rname]
                s, m = sd_mean(vals)
                row[dtname] = {"s_fib": s, "m_fib": m,
                               "relative_s_over_absm": (s / abs(m) if m else None),
                               "bit_identical": bool(bit_identical(vals)),
                               "n_distinct": len({float(v).hex() for v in vals})}
            r32 = row["float32"]["relative_s_over_absm"]
            r64 = row["float64"]["relative_s_over_absm"]
            row["ratio_rel32_over_rel64"] = (r32 / r64) if (r64 and r32) else None
            rows["rdet|" + rname] = row
        grow = {}
        for dtname in ("float32", "float64"):
            gso = per_dt[dtname][1]
            s, m = sd_mean(gso)
            grow[dtname] = {"s_fib": s, "m_fib": m,
                            "relative_s_over_absm": (s / abs(m) if m else None),
                            "bit_identical": bool(bit_identical(gso)),
                            "n_distinct": len({float(v).hex() for v in gso})}
        g32 = grow["float32"]["relative_s_over_absm"]
        g64 = grow["float64"]["relative_s_over_absm"]
        grow["ratio_rel32_over_rel64"] = (g32 / g64) if (g64 and g32) else None
        rows["X_gso_k|RQ"] = grow
        sweep[lat] = rows
    R["precision_sweep_on_the_fibre"] = {
        "fibre_family": FIB,
        "null_object": "rdet -- reads zero entries of A",
        "real_object": "X_gso_k (PREREG-1 2.4, rider ii) -- reads the leading "
                       "k Gram-Schmidt norms",
        "per_lattice": sweep}
    ratios_rdet = [v["ratio_rel32_over_rel64"]
                   for lat in sweep for kk, v in sweep[lat].items()
                   if kk.startswith("rdet|") and v["ratio_rel32_over_rel64"]]
    ratios_gso = [sweep[lat]["X_gso_k|RQ"]["ratio_rel32_over_rel64"]
                  for lat in sweep
                  if sweep[lat]["X_gso_k|RQ"]["ratio_rel32_over_rel64"]]
    R["precision_sweep_summary"] = {
        "rdet_ratio_rel32_over_rel64": {
            "n": len(ratios_rdet),
            "min": min(ratios_rdet) if ratios_rdet else None,
            "median": (sorted(ratios_rdet)[len(ratios_rdet) // 2]
                       if ratios_rdet else None),
            "max": max(ratios_rdet) if ratios_rdet else None},
        "X_gso_k_ratio_rel32_over_rel64": {
            "n": len(ratios_gso),
            "min": min(ratios_gso) if ratios_gso else None,
            "median": (sorted(ratios_gso)[len(ratios_gso) // 2]
                       if ratios_gso else None),
            "max": max(ratios_gso) if ratios_gso else None},
        "eps32_over_eps64": float(np.finfo(np.float32).eps
                                  / np.finfo(np.float64).eps)}

    # ------------------------ 2. the nearby object: route R6_exact for rdet
    print("[2] route R6_exact -- rdet from the exact integer determinant")
    cellstats_exact = OrderedDict()
    cellstats_f64 = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        pe, pf = OrderedDict(), OrderedDict()
        vals_e, vals_f = [], []
        for i in range(N_BASES):
            B = LD.build_basis_fam(d, k, i, FIB)
            m = LD.moduli(d, k, i, LD.FAMILIES[FIB][1])
            _, ad = LD.structural_check_and_exact_absdet(B, d, k, m)
            vals_e.append(float(rdet_exact(ad, d)))
            vals_f.append(math.exp(logdet_routes_prec(B, np.float64)
                                   ["R2_QR_of_BT"] / d))
        for beta in BETA_GRID[d]:
            for store, vals in ((pe, vals_e), (pf, vals_f)):
                s, m = sd_mean(vals)
                store[beta] = {"s": s, "m": m,
                               "spread": float(max(vals) - min(vals)),
                               "bit_identical": bool(bit_identical(vals)),
                               "n_distinct": len({float(v).hex() for v in vals}),
                               "seed_prefix": 2}
        cellstats_exact[lat] = pe
        cellstats_f64[lat] = pf
    vf_exact = var_f_from_cells(cellstats_exact)
    vf_f64 = var_f_from_cells(cellstats_f64)
    # VAR-S for rdet is scale_degenerate at every cell by beta-freeness; that is
    # the lead's measured outcome and is reproduced here on the SCORED family
    # only so the conjunction can be evaluated.
    vs_scored = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        per = OrderedDict()
        vals = []
        for i in range(N_BASES):
            B = LD.build_basis_fam(d, k, i, "F0")
            m = LD.moduli(d, k, i, LD.FAMILIES["F0"][1])
            _, ad = LD.structural_check_and_exact_absdet(B, d, k, m)
            vals.append(float(rdet_exact(ad, d)))
        for beta in BETA_GRID[d]:
            s, m = sd_mean(vals)
            per[beta] = {"s": s, "m": m, "spread": float(max(vals) - min(vals)),
                         "bit_identical": bool(bit_identical(vals)),
                         "n_distinct": len({float(v).hex() for v in vals}),
                         "seed_prefix": 1}
        vs_scored[lat] = per
    vs = var_s_from_cells(vs_scored)
    g_exact = {ck: gvar2(vs[ck], vf_exact[ck]) for ck in vs}
    g_f64 = {ck: gvar2(vs[ck], vf_f64[ck]) for ck in vs}
    R["nearby_object_route_R6_exact"] = {
        "definition": "rdet = abs(det B)^(1/d) from the EXACT integer "
                      "determinant via decimal at 60 significant digits. The "
                      "observable, the family, the fibre family, the declared "
                      "argument set, tau_var and both G-VAR2 clauses are "
                      "UNCHANGED; only the float representation of the "
                      "determinant is removed.",
        "n_cells": len(vs),
        "R6_exact": {
            "VAR_F_PASS": sum(1 for v in vf_exact.values()
                              if v["VAR_F"] == "PASS"),
            "VAR_F_FAIL": sum(1 for v in vf_exact.values()
                              if v["VAR_F"] == "FAIL"),
            "G_VAR2_ADMIT": sum(1 for v in g_exact.values() if v == "ADMIT"),
            "G_VAR2_REFUSE": sum(1 for v in g_exact.values() if v == "REFUSE"),
            "F0_declared_target_for_rdet_is_REFUSED":
                all(v == "REFUSE" for v in g_exact.values())},
        "R2_QR_of_BT_float64_same_code_path_for_contrast": {
            "VAR_F_PASS": sum(1 for v in vf_f64.values()
                              if v["VAR_F"] == "PASS"),
            "G_VAR2_ADMIT": sum(1 for v in g_f64.values() if v == "ADMIT"),
            "G_VAR2_REFUSE": sum(1 for v in g_f64.values() if v == "REFUSE")},
        "note": "The float64 R2 column is recomputed here only as an internal "
                "control that this probe reproduces the lead's mechanism; the "
                "AUTHORITATIVE R2 numbers are the lead's committed ones and "
                "are not replaced by these."}

    # --------------------- 3. would a RELATIVE-dispersion fallback separate?
    print("[3] relative-dispersion separation at scale_degenerate fibre cells")
    rel = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        entry = {}
        for rname in ("R1_slogdet", "R2_QR_of_BT", "R4_gram_half_slogdet",
                      "R5_slogdet_of_BH_ambient_isometry"):
            v = sweep[lat]["rdet|" + rname]["float64"]
            entry["rdet|" + rname] = v["relative_s_over_absm"]
        entry["X_gso_k|RQ"] = sweep[lat]["X_gso_k|RQ"]["float64"][
            "relative_s_over_absm"]
        rel[lat] = entry
    rdet_rels = [v for lat in rel for kk, v in rel[lat].items()
                 if kk.startswith("rdet|") and v]
    gso_rels = [rel[lat]["X_gso_k|RQ"] for lat in rel
                if rel[lat]["X_gso_k|RQ"]]
    R["relative_dispersion_separation"] = {
        "what_this_is": "NOT a proposed repair and NOT a threshold proposal. "
                        "It measures how far apart the null object and the "
                        "real object are on a scale-BEARING statistic, which "
                        "the frozen bit-identity fallback cannot see at all.",
        "per_lattice_relative_s_over_absm_float64": rel,
        "rdet_max_relative": max(rdet_rels) if rdet_rels else None,
        "X_gso_k_min_relative": min(gso_rels) if gso_rels else None,
        "orders_of_magnitude_between_them":
            (math.log10(min(gso_rels) / max(rdet_rels))
             if rdet_rels and gso_rels else None),
        "would_tau_var_1e-3_work_as_a_RELATIVE_threshold": {
            "rdet_cells_that_would_still_be_admitted":
                sum(1 for v in rdet_rels if v >= TAU_VAR),
            "X_gso_k_lattices_that_would_be_refused":
                sum(1 for v in gso_rels if v < TAU_VAR),
            "X_gso_k_lattices_total": len(gso_rels),
            "reading": "reported so that nobody reads this section as a free "
                       "repair: the separation is wide, and tau_var = 1e-3 is "
                       "not automatically the right place to cut it."}}

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    R["what_this_probe_does_NOT_establish"] = [
        "It rescores no frozen verdict, changes no outcome row and does not "
        "touch the termination branch.",
        "It does NOT show the lead's F0 failure is wrong. It localises its "
        "cause. Under the frozen text the failure stands exactly as reported.",
        "It proposes no repair, no route and no threshold; those are "
        "Coordinator acts.",
        "float32 is not a claim about any real deployment; it is a knob used "
        "to move machine epsilon and nothing else.",
        "CLAIM TIER TOY.",
    ]
    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1)
        fh.write("\n")

    print("=" * 74)
    print("RT-PROBE-2 -- NULL OBJECT + PRECISION -- TOY")
    print("=" * 74)
    print("eps32/eps64 = %.3e" % R["precision_sweep_summary"]["eps32_over_eps64"])
    s = R["precision_sweep_summary"]
    print("rdet    relative-dispersion ratio f32/f64: min %.3e med %.3e max %.3e"
          % (s["rdet_ratio_rel32_over_rel64"]["min"],
             s["rdet_ratio_rel32_over_rel64"]["median"],
             s["rdet_ratio_rel32_over_rel64"]["max"]))
    print("X_gso_k relative-dispersion ratio f32/f64: min %.3e med %.3e max %.3e"
          % (s["X_gso_k_ratio_rel32_over_rel64"]["min"],
             s["X_gso_k_ratio_rel32_over_rel64"]["median"],
             s["X_gso_k_ratio_rel32_over_rel64"]["max"]))
    n = R["nearby_object_route_R6_exact"]
    print("\nR6_exact on rdet: VAR-F FAIL %d/%d, G-VAR2 REFUSE %d/%d, "
          "F0 target met = %s"
          % (n["R6_exact"]["VAR_F_FAIL"], n["n_cells"],
             n["R6_exact"]["G_VAR2_REFUSE"], n["n_cells"],
             n["R6_exact"]["F0_declared_target_for_rdet_is_REFUSED"]))
    print("R2 float64 control (the lead's mechanism, reproduced): "
          "G-VAR2 ADMIT %d/%d"
          % (n["R2_QR_of_BT_float64_same_code_path_for_contrast"]
             ["G_VAR2_ADMIT"], n["n_cells"]))
    r = R["relative_dispersion_separation"]
    print("\nrelative dispersion: rdet max %.3e  X_gso_k min %.3e  -> %.1f "
          "orders apart" % (r["rdet_max_relative"], r["X_gso_k_min_relative"],
                            r["orders_of_magnitude_between_them"]))
    print("tau_var=1e-3 as a RELATIVE threshold would refuse X_gso_k at %d of "
          "%d lattices" % (r["would_tau_var_1e-3_work_as_a_RELATIVE_threshold"]
                           ["X_gso_k_lattices_that_would_be_refused"],
                           r["would_tau_var_1e-3_work_as_a_RELATIVE_threshold"]
                           ["X_gso_k_lattices_total"]))
    print("\nwrote %s in %.2f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
