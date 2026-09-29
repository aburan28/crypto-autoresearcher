#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VAL TASK-20260812-55056b probe C -- INDEPENDENT RE-DERIVATION OF G-VAR2.

This file implements PREREG-1 sections 2 and 3 FROM THE FROZEN TEXT. It does NOT
import measure_gvar2.py and does not read results_gvar2.json. It builds its own
bases, its own six arithmetic routes, its own VAR-S, its own VAR-F, its own
conjunction, and its own graded guard, and then prints the numbers the lead's
report claims. Agreement is therefore a re-derivation, not an arithmetic recheck
of the producer's own outputs.

The ONLY objects transcribed from committed producer/fixture code are the two
fixed re-presentations U (seed [424242, d]) and H (seed [313131, d]), because
PREREG-1 2.5 names their seeds but their CONSTRUCTION lives in the committed
fixture probe_nullroute.py and is part of the frozen route definition. Both are
transcribed here and then CHECKED for exact equality against the fixture's own
objects, and that check is printed. Everything else is written from the prereg.

CLAIM TIER TOY. Observations only.

Run from the repository root:
    python3 <this file> --out rederive_gvar2.json
"""
import argparse
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import OrderedDict

import numpy as np

T0 = time.time()

# ---- PREREG-1 2.1 constants, transcribed from the frozen text
Q = 3329
LOGQ = math.log(Q)
N_BASES = 8
TAU_VAR = 1e-3

# ---- PREREG-1 2.2
LATTICES = OrderedDict([
    ("L1", (100, 30)), ("L2", (100, 70)),
    ("L4", (140, 40)), ("L5", (140, 100)),
    ("L7", (20, 6)), ("L8", (20, 14)),
    ("L9", (30, 9)), ("L10", (30, 21)),
    ("L11", (40, 12)), ("L12", (40, 28)),
])
BETA_GRID = {100: [15, 30, 35, 50, 65], 140: [20, 40, 45, 70, 95],
             20: [5, 10, 15], 30: [7, 15, 22], 40: [10, 20, 30]}

# ---- PREREG-1 6.1
LAMBDA_GRID = [0.0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1.0]

ROUTES = ["R0", "R1", "R2", "R3", "R4", "R5"]

# ---- PREREG-1 2.3 families: name -> (A seed prefix, modulus mode)
FAMILIES = OrderedDict([
    ("F0", (1, "const_q")),
    ("F1", (1, "q_plus_i")),
    ("F0|fib_s2", (2, "const_q")),
    ("F1|fib_s2", (2, "q_plus_3")),
    ("F0|fib_s3", (3, "const_q")),
    ("F1|fib_s3", (3, "q_plus_3")),
    ("F0|fib_s4", (4, "const_q")),
    ("F1|fib_s4", (4, "q_plus_3")),
])
FIBRE_OF = {"F0": ["F0|fib_s2", "F0|fib_s3", "F0|fib_s4"],
            "F1": ["F1|fib_s2", "F1|fib_s3", "F1|fib_s4"]}


def make_A(d, k, i, prefix):
    return np.random.default_rng([prefix, d, k, i]).integers(
        0, Q, size=(k, d - k), dtype=np.int64)


def moduli(d, k, i, mode):
    m = np.full(d - k, Q, dtype=np.int64)
    if mode == "q_plus_i":
        m[0] = Q + i
    elif mode == "q_plus_3":
        m[0] = Q + 3
    return m


def build(d, k, i, fam):
    prefix, mode = FAMILIES[fam]
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = make_A(d, k, i, prefix)
    B[k:, k:] = np.diag(moduli(d, k, i, mode))
    return B


# ---- the two fixed re-presentations (construction transcribed from the frozen
#      fixture probe_nullroute.py; verified against it below)
_U, _H = {}, {}


def U_of(d):
    if d not in _U:
        rng = np.random.default_rng([424242, d])
        M = np.eye(d, dtype=np.int64)
        M = M[rng.permutation(d)]
        signs = rng.integers(0, 2, size=d) * 2 - 1
        M = M * signs[:, None]
        for _ in range(d // 2):
            a, b = rng.choice(d, size=2, replace=False)
            s = int(rng.integers(0, 2)) * 2 - 1
            M[a] = M[a] + s * M[b]
        _U[d] = M
    return _U[d]


def H_of(d):
    if d not in _H:
        rng = np.random.default_rng([313131, d])
        Z = rng.standard_normal((d, d))
        Qm, Rm = np.linalg.qr(Z)
        ph = np.sign(np.diag(Rm))
        ph[ph == 0] = 1.0
        _H[d] = Qm * ph
    return _H[d]


def logdets(B, d, k, m):
    """PREREG-1 2.5, all six routes. R0 is the exact closed form of THIS
    family's determinant."""
    Bf = B.astype(np.float64)
    out = OrderedDict()
    if bool(np.all(m == Q)):
        out["R0"] = float((d - k) * LOGQ)
    else:
        out["R0"] = float(np.sum(np.log(m.astype(np.float64))))
    out["R1"] = float(np.linalg.slogdet(Bf)[1])
    out["R2"] = float(np.sum(np.log(np.abs(np.diag(np.linalg.qr(Bf.T)[1])))))
    out["R3"] = float(np.linalg.slogdet((U_of(d) @ B).astype(np.float64))[1])
    out["R4"] = float(0.5 * np.linalg.slogdet((B @ B.T).astype(np.float64))[1])
    out["R5"] = float(np.linalg.slogdet(Bf @ H_of(d))[1])
    return out


def raw_gso(B):
    dg = np.abs(np.diag(np.linalg.qr(B.astype(np.float64).T)[1]))
    return np.log(dg), float(np.sum(np.log(dg)))


def bit_identical(vals):
    return len({float(v).hex() for v in vals}) == 1


def sd(v):
    a = np.asarray(v, float)
    return float(a.std(ddof=1)) if a.size > 1 else 0.0


def mean(v):
    return float(np.asarray(v, float).mean())


# ------------------------------------------------------------------ the values
def collect(fam):
    """Per (lattice, basis): the six route logdets, |det| exact, A[0,0],
    raw-GSO logs. Also the entrywise block-structure guard."""
    out, guard = {}, []
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            prefix, mode = FAMILIES[fam]
            m = moduli(d, k, i, mode)
            B = build(d, k, i, fam)
            struct_ok = (np.array_equal(B[:k, :k], np.eye(k, dtype=np.int64))
                         and np.array_equal(B[k:, :k],
                                            np.zeros((d - k, k), np.int64))
                         and np.array_equal(B[k:, k:], np.diag(m)))
            ad = 1
            for v in m.tolist():
                ad *= int(v)
            gso, ld = raw_gso(B)
            out[(lat, i)] = {"ld": logdets(B, d, k, m), "absdet": ad,
                             "A00": int(B[0, k]), "gso": gso, "gso_ld": ld}
            guard.append(bool(struct_ok))
    return out, all(guard)


def cellvals(vals, fam, cand, route, lam=0.0):
    """The candidate's 8 per-basis values at every cell."""
    res = {}
    for lat, (d, k) in LATTICES.items():
        res[lat] = {}
        for beta in BETA_GRID[d]:
            v = []
            for i in range(N_BASES):
                rec = vals[(lat, i)]
                ld = rec["ld"][route]
                if cand == "X_null":
                    x = (beta / d) * (1.0 / d) * ld
                elif cand == "rdet":
                    x = math.exp(ld / d)
                elif cand == "V_evade":
                    x = (beta / d) * (1.0 / d) * ld + 1e-9 * rec["A00"] / Q
                elif cand == "X_lambda":
                    x = (beta / d) * (1.0 / d) * ld + lam * rec["A00"] / Q
                elif cand == "rawtail":
                    x = float(np.mean(rec["gso"][d - beta:]) - rec["gso_ld"] / d)
                else:
                    raise KeyError(cand)
                v.append(x)
            res[lat][beta] = v
    return res


def var_s(cv, tau=TAU_VAR):
    """PREREG-1 3.1 + 3.2, written from the frozen text."""
    out = {}
    for lat, per in cv.items():
        means = [mean(v) for v in per.values()]
        R = float(max(means) - min(means))
        for beta, v in per.items():
            s = sd(v)
            if R == 0.0:
                out[(lat, beta)] = {"s": s, "m": mean(v), "R": R, "D": None,
                                    "VAR_S": "scale_degenerate",
                                    "naive": "ADMIT" if s > 0 else "REFUSE/0-0",
                                    "bit_identical": bit_identical(v),
                                    "n_distinct": len({float(x).hex()
                                                       for x in v})}
            else:
                D = s / R
                vd = "ADMIT" if D >= tau else "REFUSE"
                out[(lat, beta)] = {"s": s, "m": mean(v), "R": R, "D": D,
                                    "VAR_S": vd, "naive": vd,
                                    "bit_identical": bit_identical(v),
                                    "n_distinct": len({float(x).hex()
                                                       for x in v})}
    return out


def var_f(cvf, tau=TAU_VAR):
    """PREREG-1 3.3, written from the frozen text."""
    out = {}
    for lat, per in cvf.items():
        means = [mean(v) for v in per.values()]
        R = float(max(means) - min(means))
        for beta, v in per.items():
            s = sd(v)
            bid = bit_identical(v)
            if R == 0.0:
                out[(lat, beta)] = {"s": s, "R": R, "D": None,
                                    "VAR_F": "PASS" if not bid else "FAIL",
                                    "by": "bit_identity", "bit_identical": bid,
                                    "n_distinct": len({float(x).hex()
                                                       for x in v})}
            else:
                D = s / R
                out[(lat, beta)] = {"s": s, "R": R, "D": D,
                                    "VAR_F": "PASS" if D >= tau else "FAIL",
                                    "by": "scaled_dispersion",
                                    "bit_identical": bid,
                                    "n_distinct": len({float(x).hex()
                                                       for x in v})}
    return out


def gvar2(vs, vf):
    """PREREG-1 3.4."""
    return "ADMIT" if (vs["VAR_S"] in ("ADMIT", "scale_degenerate")
                       and vf["VAR_F"] == "PASS") else "REFUSE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = OrderedDict()
    R["probe"] = "VAL-REDERIVE-GVAR2"
    R["task_id"] = "TASK-20260812-55056b"
    R["role"] = "validator"
    R["claim_tier"] = "toy"
    R["status"] = ("INDEPENDENT VALIDATOR RE-DERIVATION of PREREG-1 sections 2 "
                   "and 3 from the frozen text. Imports no producer module and "
                   "reads no producer result file. Observations only.")
    R["environment"] = {"python": platform.python_version(),
                        "numpy": np.__version__,
                        "platform": platform.platform()}
    try:
        R["git_revision"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            check=True).stdout.strip()
    except Exception as e:
        R["git_revision"] = "UNAVAILABLE %s" % e

    # ---- transcription check on U and H against the committed fixture
    sys.path.insert(0, os.path.join(
        "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/"
        "TASK-20260809-444fe7/probes"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pn", "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/"
              "TASK-20260809-444fe7/probes/probe_nullroute.py")
    pn = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pn)
    tc = {}
    for d in sorted({dk[0] for dk in LATTICES.values()}):
        tc["U_d%d_equal" % d] = bool(np.array_equal(U_of(d),
                                                    pn.fixed_unimodular(d)))
        tc["H_d%d_bit_equal" % d] = bool(np.array_equal(H_of(d),
                                                        pn.fixed_isometry(d)))
    R["transcription_check_U_H_vs_committed_fixture"] = tc

    VALS = {f: collect(f) for f in FAMILIES}
    R["block_structure_guard_all_families"] = {f: VALS[f][1] for f in VALS}
    V = {f: VALS[f][0] for f in VALS}

    # ---- PREREG-1 6.4 could-not-PASS guard: |det B_i| bit-identical on fibres
    fg = {}
    for f in FAMILIES:
        per = {}
        for lat in LATTICES:
            ads = {V[f][(lat, i)]["absdet"] for i in range(N_BASES)}
            per[lat] = len(ads)
        fg[f] = {"max_distinct_absdet_over_lattices": max(per.values()),
                 "all_lattices_constant": all(x == 1 for x in per.values())}
    R["fibre_determinant_guard_distinct_absdet_counts"] = fg
    R["F1_moduli_m0_over_i"] = [int(moduli(20, 6, i, "q_plus_i")[0])
                                for i in range(N_BASES)]

    # ---- F0 / F1 verdicts for X_null and rdet, all six routes
    table = OrderedDict()
    for fam in ("F0", "F1"):
        for cand in ("X_null", "rdet"):
            for rt in ROUTES:
                vs = var_s(cellvals(V[fam], fam, cand, rt))
                per_fib = {}
                for fibfam in FIBRE_OF[fam]:
                    per_fib[fibfam] = var_f(
                        cellvals(V[fibfam], fibfam, cand, rt))
                prim = FIBRE_OF[fam][0]
                verdicts = {c: gvar2(vs[c], per_fib[prim][c]) for c in vs}
                nA = sum(1 for x in verdicts.values() if x == "ADMIT")
                nR = sum(1 for x in verdicts.values() if x == "REFUSE")
                repl = {ff: sum(1 for c in vs
                                if gvar2(vs[c], per_fib[ff][c]) == "ADMIT")
                        for ff in per_fib}
                sds = [vs[c]["s"] for c in vs]
                fsds = [per_fib[prim][c]["s"] for c in vs]
                table["%s|%s|%s" % (fam, cand, rt)] = {
                    "n_cells": len(vs), "ADMIT": nA, "REFUSE": nR,
                    "n_scale_degenerate": sum(
                        1 for c in vs if vs[c]["VAR_S"] == "scale_degenerate"),
                    "n_VAR_S_ADMIT": sum(
                        1 for c in vs if vs[c]["VAR_S"] == "ADMIT"),
                    "n_VAR_F_PASS": sum(
                        1 for c in vs if per_fib[prim][c]["VAR_F"] == "PASS"),
                    "n_naive_ADMIT": sum(1 for c in vs
                                         if vs[c]["naive"] == "ADMIT"),
                    "max_s_c": max(sds), "min_s_c": min(sds),
                    "n_s_c_exactly_zero": sum(1 for x in sds if x == 0.0),
                    "max_D_c": max([vs[c]["D"] for c in vs
                                    if vs[c]["D"] is not None], default=None),
                    "fibre_sd_min": min(fsds), "fibre_sd_max": max(fsds),
                    "ADMIT_per_fibre_replicate": repl,
                }
    R["F0_F1_TABLE"] = table

    # ---- rawtail (reduction-free raw-GSO route), F0
    rt_rows = {}
    for fam in ("F0", "F1"):
        vs = var_s(cellvals(V[fam], fam, "rawtail", "R1"))
        vf = var_f(cellvals(V[FIBRE_OF[fam][0]], FIBRE_OF[fam][0],
                            "rawtail", "R1"))
        verd = {c: gvar2(vs[c], vf[c]) for c in vs}
        misses = sorted([("%s_b%s" % c, vs[c]["D"], vf[c]["D"])
                         for c in vs if verd[c] != "ADMIT"])
        rt_rows[fam] = {"ADMIT": sum(1 for x in verd.values() if x == "ADMIT"),
                        "REFUSE": sum(1 for x in verd.values()
                                      if x == "REFUSE"),
                        "misses": misses,
                        "D_c_min": min(vs[c]["D"] for c in vs),
                        "D_c_max": max(vs[c]["D"] for c in vs)}
    R["rawtail_raw_gso"] = rt_rows

    # ---- P-V1: VAR-S alone on V_evade over F0, all six routes
    pv1 = {}
    for rt in ROUTES:
        vs = var_s(cellvals(V["F0"], "F0", "V_evade", rt))
        pv1[rt] = {"REFUSE": sum(1 for c in vs if vs[c]["VAR_S"] == "REFUSE"),
                   "ADMIT": sum(1 for c in vs if vs[c]["VAR_S"] == "ADMIT"),
                   "scale_degenerate": sum(1 for c in vs
                                           if vs[c]["VAR_S"] ==
                                           "scale_degenerate"),
                   "max_D_c": max(vs[c]["D"] for c in vs
                                  if vs[c]["D"] is not None),
                   "max_s_c": max(vs[c]["s"] for c in vs)}
    R["P_V1_VAR_S_only_V_evade_F0"] = pv1

    # ---- P-G1: the graded guard, crossing amplitude per cell
    guard = {}
    for rt in ROUTES:
        cross = {}
        for lam in LAMBDA_GRID:
            vs = var_s(cellvals(V["F0"], "F0", "X_lambda", rt, lam))
            for c in vs:
                if c not in cross and vs[c]["VAR_S"] == "ADMIT":
                    cross[c] = lam
        allc = var_s(cellvals(V["F0"], "F0", "X_lambda", rt, 0.0))
        guard[rt] = {"n_cells": len(allc), "n_crossing": len(cross),
                     "lambda_star_values": sorted(set(cross.values()))}
    R["P_G1_graded_guard"] = guard

    # ---- P-R26: definitional X_null vs the notarized prereg 2.6 table
    import ast
    tree = ast.parse(open(
        "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/"
        "TASK-20260809-444fe7/probes/probe_nullroute.py").read())
    T26 = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "PREREG_2_6":
                    T26 = ast.literal_eval(node.value)
    n_ok = n_tot = 0
    worst = 0.0
    for lat, (d, k) in LATTICES.items():
        for beta in BETA_GRID[d]:
            for i in range(N_BASES):
                got = (beta / d) * (1.0 / d) * V["F0"][(lat, i)]["ld"]["R1"]
                n_tot += 1
                worst = max(worst, abs(round(got, 6) - T26[lat][beta]))
                n_ok += int(round(got, 6) == T26[lat][beta])
    R["P_R26"] = {"cells_x_bases": n_tot, "agreeing": n_ok,
                  "max_abs_dev_after_rounding": worst}

    # ---- tau_var verdict surface, six decades
    surf = {}
    for tau in [1e-16, 1e-14, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-3,
                1e-2, 1e-1, 1.0]:
        row = {}
        for fam in ("F0", "F1"):
            for cand in ("X_null", "rdet"):
                nA = 0
                for rt in ROUTES:
                    vs = var_s(cellvals(V[fam], fam, cand, rt), tau)
                    vf = var_f(cellvals(V[FIBRE_OF[fam][0]], FIBRE_OF[fam][0],
                                        cand, rt), tau)
                    nA += sum(1 for c in vs if gvar2(vs[c], vf[c]) == "ADMIT")
                row["%s|%s" % (fam, cand)] = nA
        # rawtail F0 and hkz-analogue absent; add V_evade VAR-S admissions
        nv = 0
        for rt in ROUTES:
            vs = var_s(cellvals(V["F0"], "F0", "V_evade", rt), tau)
            nv += sum(1 for c in vs if vs[c]["VAR_S"] == "ADMIT")
        row["F0|V_evade_VAR_S_ADMIT"] = nv
        vs = var_s(cellvals(V["F0"], "F0", "rawtail", "R1"), tau)
        vf = var_f(cellvals(V["F0|fib_s2"], "F0|fib_s2", "rawtail", "R1"), tau)
        row["F0|rawtail_GVAR2_ADMIT"] = sum(
            1 for c in vs if gvar2(vs[c], vf[c]) == "ADMIT")
        surf["tau=%g" % tau] = row
    R["tau_var_verdict_surface"] = surf

    R["seconds"] = round(time.time() - T0, 3)
    with open(a.out, "w") as fh:
        json.dump(R, fh, indent=1, default=str)

    # ------------------------------------------------------------- human view
    print("=" * 78)
    print("VALIDATOR INDEPENDENT RE-DERIVATION OF G-VAR2 (PREREG-1 2, 3)")
    print("=" * 78)
    print("U/H transcription vs committed fixture:",
          "ALL EQUAL" if all(tc.values()) else tc)
    print("block-structure guard:", R["block_structure_guard_all_families"])
    print("fibre |det| constant across 8 bases in every fibre family:",
          all(fg[f]["all_lattices_constant"] for f in fg if "fib" in f))
    print("F1 m_i[0] over i:", R["F1_moduli_m0_over_i"])
    print()
    print("%-24s %6s %6s %6s %8s %8s %11s %11s" %
          ("family|cand|route", "cells", "ADMIT", "REFU", "sc_deg",
           "VAR_F_P", "fib_sd_min", "fib_sd_max"))
    for k, v in table.items():
        print("%-24s %6d %6d %6d %8d %8d %11.3e %11.3e" %
              (k, v["n_cells"], v["ADMIT"], v["REFUSE"],
               v["n_scale_degenerate"], v["n_VAR_F_PASS"],
               v["fibre_sd_min"], v["fibre_sd_max"]))
    print()
    print("rawtail:", json.dumps(rt_rows, default=str)[:600])
    print()
    print("P-V1 (VAR-S alone, V_evade, F0):")
    for rt, v in pv1.items():
        print("   %-4s REFUSE=%d ADMIT=%d max_D=%.4e max_sd=%.4e" %
              (rt, v["REFUSE"], v["ADMIT"], v["max_D_c"], v["max_s_c"]))
    print()
    print("P-G1 graded guard:", json.dumps(guard))
    print("P-R26:", json.dumps(R["P_R26"]))
    print()
    print("tau_var verdict surface (count of G-VAR2 ADMIT cells over 6 routes,")
    print("38 cells each -> max 228; V_evade column is VAR-S ADMIT only):")
    cols = list(next(iter(surf.values())).keys())
    print("%-12s %s" % ("tau_var", " ".join("%22s" % c for c in cols)))
    for t, row in surf.items():
        print("%-12s %s" % (t, " ".join("%22d" % row[c] for c in cols)))
    print("\nwrote %s in %.2f s" % (a.out, R["seconds"]))


if __name__ == "__main__":
    main()
