#!/usr/bin/env python3
"""TASK-20260813-59c321 (Validator) -- probe 4 of 5.

MY OWN NULLS, BUILT WHERE A PRODUCER'S CONSTRUCTION IS LOAD-BEARING.
Everything here is pushed through the IDENTICAL code path -- it imports MY OWN
probe_rederive_a1 module (route evaluation, sd_mean, bit_identical,
var_f_from_cells) and adds only new observables.  No producer module is
imported anywhere.

Three objects, none of them named anywhere in PREREG-2:

  N1  X_dk       = log|det B| / (d + k)
      determinant-only, no beta, reads NOTHING free.  Predicted certified
      CONSTANT.  It is X_parfree's shape with a denominator PREREG-2 never
      declares, so it tests whether the certification machinery is keyed to
      the declared candidate NAMES or to the objects.

  N2  X_rowsum   = X_null + c * ((sum of every entry of A) mod q) / q
      reads the free content of A.  Predicted certified NON-CONSTANT.

  N3  X_indexnoise = X_null + c * g(i),  g a fixed pseudorandom sequence
      indexed by the BASIS INDEX ALONE.
      THIS IS THE SHARP NULL.  It is non-constant on the fibre and reads
      NOTHING WHATEVER of the instance -- not even the hash of it.  If the
      instrument certifies it NON-CONSTANT and scores it exactly like
      X_hash, then "certified NON-CONSTANT" carries no information about
      reading the instance.

Plus the DECAY CONTROL that docs/inventor-protocol.md section 3 requires:
X_hash is re-run at amplitudes of MY choosing OUTSIDE the declared grid
(1e-12, 1e-11, 1e-10, 1e-7, 1e-5).  The parameter meant to destroy the signal
is c -> 0, because X_hash -> X_null, which is exactly constant on the fibre.
The report states what rho SHOULD do (decay to 0, linearly in c at binary64)
and whether it does.  A quantity that does not decay when the parameter meant
to destroy it is turned down is the canonical artefact tell.

Writes exactly one file: its --out path.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import OrderedDict
from decimal import Decimal, localcontext

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_rederive_a1 as PR      # MY OWN module, not the producer's

Q = PR.Q
LATTICES = PR.LATTICES
BETAS = PR.BETAS
FLOAT_ROUTES = PR.FLOAT_ROUTES
N = PR.N_BASES


def g_index(i):
    """A fixed pseudorandom value per BASIS INDEX, independent of the
    instance.  Deterministic and reproducible; reads no entry of any basis."""
    h = hashlib.sha256(b"validator-59c321-indexnoise|%d" % i).hexdigest()
    return int(h, 16) / 2 ** 256


def own_value(name, L, A, d, k, beta, dt, c=None, i=None):
    xn = dt(dt(dt(beta) / dt(d)) * dt(dt(1.0) / dt(d)) * dt(L))
    if name == "X_dk":
        return dt(dt(L) / dt(dt(d) + dt(k)))
    if name == "X_rowsum":
        s = int(A.sum()) % Q
        return dt(xn + dt(dt(c) * dt(dt(s) / dt(Q))))
    if name == "X_indexnoise":
        return dt(xn + dt(dt(c) * dt(g_index(i))))
    raise ValueError(name)


def own_value_exact(name, Lx, A, d, k, beta, c=None, i=None, prec=60):
    with localcontext() as ctx:
        ctx.prec = prec
        xn = Decimal(beta) / Decimal(d) / Decimal(d) * Lx
        if name == "X_dk":
            return +(Lx / (Decimal(d) + Decimal(k)))
        if name == "X_rowsum":
            return +(xn + Decimal(repr(c)) * Decimal(int(A.sum()) % Q)
                     / Decimal(Q))
        if name == "X_indexnoise":
            hnum = int(hashlib.sha256(
                b"validator-59c321-indexnoise|%d" % i).hexdigest(), 16)
            return +(xn + Decimal(repr(c)) * Decimal(hnum)
                     / Decimal(2) ** 256)
    raise ValueError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    PR.R4_GRAM = "int"
    PR.ASSOC = "validator"

    R = OrderedDict()
    R["probe"] = "probe_own_null.py"
    R["task_id"] = "TASK-20260813-59c321"
    R["objects_named_nowhere_in_PREREG_2"] = ["X_dk", "X_rowsum",
                                              "X_indexnoise"]

    # ------------------------------------------------- build the fibre draws
    basis, A00, LEX = {}, {}, {}
    for pref in (2, 3, 4):
        fam = "F0|fib_s%d|PIN-DET" % pref
        for lat, d, k in LATTICES:
            bl = [PR.build_basis(d, k, i, pref, False) for i in range(N)]
            basis[(fam, lat)] = bl
    for lat, d, k in LATTICES:
        LEX[lat] = PR.dec_ln(Q ** (d - k), 60)

    RV = {}
    for (fam, lat), bl in basis.items():
        d, k = [(dd, kk) for l, dd, kk in LATTICES if l == lat][0]
        for pn, dt in (("binary32", np.float32), ("binary64", np.float64)):
            RV[(fam, lat, pn)] = [PR.float_routes(B, d, k, dt) for B, _ in bl]

    # ------------------------------------------- N1 / N2 / N3 certification
    OWN = [("X_dk", None), ("X_rowsum", 1e-3), ("X_indexnoise", 1e-3)]
    cert = OrderedDict()
    for name, c in OWN:
        allconst = True
        for pref in (2, 3, 4):
            fam = "F0|fib_s%d|PIN-DET" % pref
            for lat, d, k in LATTICES:
                for beta in BETAS[d]:
                    vals = [own_value_exact(name, LEX[lat],
                                            basis[(fam, lat)][i][1], d, k,
                                            beta, c=c, i=i) for i in range(N)]
                    if len(set(vals)) != 1:
                        allconst = False
        cert[name] = "CONSTANT" if allconst else "NON-CONSTANT"
    R["certified_class_of_my_own_objects"] = cert
    R["predicted_class"] = {"X_dk": "CONSTANT", "X_rowsum": "NON-CONSTANT",
                            "X_indexnoise": "NON-CONSTANT"}
    R["certification_matches_prediction"] = (
        cert == R["predicted_class"])

    # ------------------------------- score N1/N2/N3 through the same path
    scored = OrderedDict()
    for name, c in OWN:
        fc2a = fc3a = fc3b = 0
        pdeg = 0
        changed = 0
        ncells = 0
        for pref in (2, 3, 4):
            fam = "F0|fib_s%d|PIN-DET" % pref
            for rt in FLOAT_ROUTES:
                stats = {"binary32": {}, "binary64": {}}
                for lat, d, k in LATTICES:
                    for pn in ("binary32", "binary64"):
                        stats[pn].setdefault(lat, {})
                    for beta in BETAS[d]:
                        for pn, dt in (("binary32", np.float32),
                                       ("binary64", np.float64)):
                            vals = [float(own_value(
                                name, RV[(fam, lat, pn)][i][rt],
                                basis[(fam, lat)][i][1], d, k, beta, dt,
                                c=c, i=i)) for i in range(N)]
                            s, m = PR.sd_mean(vals)
                            stats[pn][lat][beta] = {
                                "s": s, "m": m,
                                "bit_identical": PR.bit_identical(vals),
                                "rho": (s / abs(m)) if m != 0 else None}
                vf = {pn: PR.var_f_from_cells(stats[pn])
                      for pn in ("binary32", "binary64")}
                for lat, d, k in LATTICES:
                    for beta in BETAS[d]:
                        ncells += 1
                        ck = "%s_b%s" % (lat, beta)
                        r32 = stats["binary32"][lat][beta]["rho"]
                        r64 = stats["binary64"][lat][beta]["rho"]
                        if vf["binary32"][ck]["VAR_F"] != \
                                vf["binary64"][ck]["VAR_F"]:
                            changed += 1
                        if cert[name] == "CONSTANT":
                            if r64 == 0.0:
                                pdeg += 1
                            elif r32 is not None and r64 is not None \
                                    and r32 <= r64:
                                fc2a += 1
                        else:
                            if r32 == 0.0 or r64 == 0.0:
                                fc3b += 1
                            if r64 not in (None, 0.0) and r32 is not None:
                                rr = r32 / r64
                                if rr < 0.5 or rr > 2.0:
                                    fc3a += 1
                            elif r64 == 0.0 and r32 not in (None, 0.0):
                                fc3a += 1
        scored[name] = {"certified": cert[name], "n_cells": ncells,
                        "FC_2a": fc2a, "FC_3a": fc3a, "FC_3b": fc3b,
                        "precision_degenerate": pdeg,
                        "VAR_F_changes_with_precision": changed}
    R["my_own_objects_scored_through_the_identical_code_path"] = scored

    # -------------------------------------- DECAY CONTROL on the X_hash family
    # amplitudes of MY choosing, outside the declared grid.
    decay = OrderedDict()
    fam = "F0|fib_s2|PIN-DET"
    lat, d, k, beta = "L1", 100, 30, 15
    HB = [PR.hash_H(B) for B, _ in basis[(fam, lat)]]
    for c in [1e-1, 1e-2, 1e-3, 1e-5, 1e-7, 1e-9, 1e-10, 1e-11, 1e-12, 0.0]:
        row = {}
        for pn, dt in (("binary32", np.float32), ("binary64", np.float64)):
            vals = [float(PR.cand_value("X_hash",
                                        RV[(fam, lat, pn)][i]["R0_closed_form"],
                                        0, d, k, beta, dt, c=c, hb=HB[i]))
                    for i in range(N)]
            s, m = PR.sd_mean(vals)
            row[pn] = {"rho": (s / abs(m)) if m != 0 else None,
                       "bit_identical": PR.bit_identical(vals)}
        r64 = row["binary64"]["rho"]
        row["rho64_over_c"] = (r64 / c) if c else None
        decay["c=%g" % c] = row
    r64s = [(c, decay["c=%g" % c]["binary64"]["rho"])
            for c in [1e-1, 1e-2, 1e-3, 1e-5, 1e-7, 1e-9, 1e-10, 1e-11,
                      1e-12, 0.0]]
    monotone = all(r64s[i][1] >= r64s[i + 1][1] for i in range(len(r64s) - 1))
    R["decay_control_X_hash_on_R0"] = OrderedDict([
        ("cell", "%s|%s|%s|R0_closed_form|beta=%d" % (fam, lat, "PIN-DET",
                                                      beta)),
        ("what_rho_SHOULD_do",
         ("decay to 0 as c -> 0, essentially linearly in c at binary64, "
          "because X_hash -> X_null which is EXACTLY constant on this fibre; "
          "and collapse to exactly 0 at binary32 once c*H(B) falls below the "
          "float32 ULP of X_null")),
        ("rho_binary64_is_monotone_nonincreasing_in_c", bool(monotone)),
        ("rho_binary64_at_c_equals_0",
         decay["c=0"]["binary64"]["rho"]),
        ("table", decay),
        ("verdict",
         ("DECAYS AS IT SHOULD -- no artefact tell" if monotone
          and decay["c=0"]["binary64"]["rho"] == 0.0
          else "DOES NOT DECAY -- artefact tell, report it")),
    ])

    # ---- and the same decay run at binary32, to locate the collapse point
    collapse = {c: decay["c=%g" % c]["binary32"]["rho"]
                for c in [1e-1, 1e-2, 1e-3, 1e-5, 1e-7, 1e-9, 1e-10, 1e-11,
                          1e-12]}
    R["binary32_collapse_point"] = OrderedDict([
        ("rho_binary32_by_amplitude", collapse),
        ("largest_c_with_rho32_exactly_zero",
         max([c for c, v in collapse.items() if v == 0.0], default=None)),
        ("reading",
         ("the amplitude at which the float32 evaluation destroys the fibre "
          "content entirely.  FC-3b's firing on X_hash[c=1e-9] is this "
          "collapse and nothing else; it is a property of the FORMAT against "
          "the amplitude, not of the object")),
    ])

    with open(a.out, "w") as f:
        json.dump(R, f, indent=1, default=str)

    p = print
    p("== MY OWN OBJECTS, NAMED NOWHERE IN PREREG-2")
    for kk, vv in cert.items():
        p("   %-14s certified %-13s predicted %s"
          % (kk, vv, R["predicted_class"][kk]))
    p("   certification matches prediction: %s"
      % R["certification_matches_prediction"])
    p("== SCORED THROUGH THE IDENTICAL CODE PATH")
    for kk, vv in scored.items():
        p("   %-14s %s" % (kk, json.dumps(vv)))
    p("== DECAY CONTROL (inventor-protocol section 3): X_hash on R0")
    p("   %-10s %-24s %-24s %-12s" % ("c", "rho(binary64)", "rho(binary32)",
                                      "rho64/c"))
    for kk, vv in decay.items():
        p("   %-10s %-24s %-24s %-12s"
          % (kk, vv["binary64"]["rho"], vv["binary32"]["rho"],
             vv["rho64_over_c"]))
    p("   monotone non-increasing in c: %s ; rho64 at c=0: %s"
      % (R["decay_control_X_hash_on_R0"]
         ["rho_binary64_is_monotone_nonincreasing_in_c"],
         R["decay_control_X_hash_on_R0"]["rho_binary64_at_c_equals_0"]))
    p("   VERDICT: %s" % R["decay_control_X_hash_on_R0"]["verdict"])
    p("== binary32 collapse: largest c with rho32 exactly 0 = %s"
      % R["binary32_collapse_point"]["largest_c_with_rho32_exactly_zero"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
