#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM PROBE 1 -- IS 1,416 A PROPERTY OF THE CLAUSE, OR OF ONE ROUTE?

TASK-20260813-85e343 / BATCH-6b6e78 / GOAL-MLKEM-005.  Role: red-team.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

THIS IS A PROBE ON MY OWN FRAMES.  It is NOT pre-registered, it rescores NO
frozen verdict of this batch or of any prior one, and it specifies no
criterion, threshold, gate or K.  It computes three things:

  (L) THE PRECISION LADDER.  The committed VAR-F clause (imported from the
      committed measure_gvar2.py, not transcribed) is evaluated at binary32, at
      binary64, and at EXACT arithmetic, on the same 324 determinant-only
      blocks the lead scored.  At exact arithmetic every route collapses to one
      value, log|det B| = (d-k) log q, which is exactly known for these frozen
      families, so the third rung needs no route at all.  The lead reports
      1,416 verdict changes between the two float rungs, 1,396 of them on one
      route.  A quantity that is a property of THE CLAUSE should keep changing
      as the precision rung goes up; a quantity that is a property of ONE
      ROUTE'S float32 realization should collapse.  Both rungs are reported.

  (C) THE CONDITIONING OF R4, KNOWABLE BEFORE THE RUN.  R4 forms B B^T at the
      working precision.  Its entries are integers; the largest is reported per
      lattice against 2**24, the largest integer float32 represents exactly.
      If the Gram exceeds 2**24 the float32 route is wrong before slogdet is
      called, and that is arithmetic, not a measurement.

  (N) THE NEARBY OBJECT.  R4_mixed forms the SAME Gram exactly in int64,
      casts the finished matrix to float32 and calls the same slogdet.  Only
      the accumulation changes.  If the effect follows the accumulation the
      verdict changes move with it.

RE-EXECUTABLE from the repository root:
    PYTHONDONTWRITEBYTECODE=1 python3 -B <this file> --out <this dir>/probe_precision_ladder_output.json

WRITES exactly one file: the --out path.  No git write, no commit.
"""

import argparse
import decimal
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict

sys.dont_write_bytecode = True
import numpy as np

T0 = time.time()
TASK_ID = "TASK-20260813-85e343"
BATCH_ID = "BATCH-6b6e78"
GOAL_ID = "GOAL-MLKEM-005"


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        return subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return os.path.abspath(".")


REPO = _repo_root()
G5 = "coordination/goals/GOAL-MLKEM-005"
P_MG = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-56b9da/measure_gvar2.py")
P_A1 = os.path.join(REPO, G5, "batches/BATCH-6b6e78/tasks/"
                              "TASK-20260813-2ce014/results_a1.json")


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


MG = load_module(P_MG, "committed_measure_gvar2")   # module level only
Q = MG.Q
N_BASES = MG.N_BASES
TAU_VAR = MG.TAU_VAR
LATTICES = MG.LATTICES
BETA_GRID = MG.BETA_GRID
var_f_from_cells = MG.var_f_from_cells              # THE COMMITTED CLAUSE
bit_identical = MG.bit_identical
PROBE_N = MG.PROBE_N

PIN_DET = "PIN-DET"
PIN_DET_A00 = "PIN-DET+PIN-A00"
DRAWS = [("fib_s2", 2), ("fib_s3", 3), ("fib_s4", 4)]
LAMBDAS = [0.0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1.0]
CGRID = [1e-9, 1e-3, 1e-2, 1e-1]
ROUTES6 = list(MG.ROUTES6)


def build_A(d, k, i, seed_prefix, pin):
    A = MG.make_A_seed(d, k, Q, i, seed_prefix).copy()
    if pin == PIN_DET_A00:
        A[0, 0] = MG.make_A_seed(d, k, Q, 0, seed_prefix)[0, 0]
    return A


def build_basis(d, k, i, seed_prefix, pin):
    A = build_A(d, k, i, seed_prefix, pin)
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = np.diag(MG.moduli(d, k, i, "const_q"))
    return B, A


def hash_H_int(B):
    payload = b"|".join(str(int(x)).encode() for x in B.flatten(order="C"))
    return int(hashlib.sha256(payload).hexdigest(), 16)


def routes_at(B, d, k, dt):
    """The six declared float routes at working precision dt, plus the NEARBY
    OBJECT R4_mixed (Gram accumulated exactly in int64, then cast to dt)."""
    out, err = OrderedDict(), OrderedDict()

    def _try(name, fn):
        try:
            out[name] = float(fn())
        except Exception as e:
            err[name] = "%s: %s" % (e.__class__.__name__, e)

    _try("R0_closed_form", lambda: dt(d - k) * np.log(dt(Q)))
    Bf = B.astype(dt)
    _try("R1_slogdet", lambda: np.linalg.slogdet(Bf)[1])
    _try("R2_QR_of_BT",
         lambda: np.sum(np.log(np.abs(np.diag(np.linalg.qr(Bf.T)[1])))))
    U = PROBE_N.fixed_unimodular(d)
    _try("R3_slogdet_of_UB", lambda: np.linalg.slogdet((U @ B).astype(dt))[1])
    _try("R4_gram_half_slogdet", lambda: dt(0.5) * np.linalg.slogdet(Bf @ Bf.T)[1])
    H = PROBE_N.fixed_isometry(d).astype(dt)
    _try("R5_slogdet_of_BH_ambient_isometry", lambda: np.linalg.slogdet(Bf @ H)[1])
    Gexact = (B @ B.T)                      # int64, EXACT
    _try("R4_mixed_exact_gram_then_cast",
         lambda: dt(0.5) * np.linalg.slogdet(Gexact.astype(dt))[1])
    return out, err


def candidate_value(cand, param, logdet, d, k, beta, A00, Hint):
    """PREREG-2 2.4 definitions, evaluated on a route's log|det B|."""
    xn = (beta / d) * (1.0 / d) * logdet
    if cand == "X_null":
        return xn
    if cand == "rdet":
        return float(np.exp(logdet / d))
    if cand == "X_parfree":
        return logdet / (d * k)
    if cand == "V_evade":
        return xn + 1e-9 * (A00 / Q)
    if cand == "X_lambda":
        return xn + param * (A00 / Q)
    if cand == "X_hash":
        return xn + param * (Hint / float(2 ** 256))
    raise ValueError(cand)


def candidate_value_exact(cand, param, d, k, beta, A00, Hint, ctx):
    """The SAME definitions in exact arithmetic.  log|det B| = (d-k) log q is
    exact for these families (modulus block fixed at q), taken through decimal
    at the context precision; every other operation is exact rational."""
    with decimal.localcontext(ctx):
        LD = decimal.Decimal(d - k) * decimal.Decimal(Q).ln()
        xn = (decimal.Decimal(beta) / decimal.Decimal(d)) \
            * (decimal.Decimal(1) / decimal.Decimal(d)) * LD
        if cand == "X_null":
            return xn
        if cand == "rdet":
            return (LD / decimal.Decimal(d)).exp()
        if cand == "X_parfree":
            return LD / (decimal.Decimal(d) * decimal.Decimal(k))
        if cand == "V_evade":
            return xn + decimal.Decimal("1e-9") * (decimal.Decimal(int(A00))
                                                   / decimal.Decimal(Q))
        if cand == "X_lambda":
            return xn + decimal.Decimal(repr(param)) * (
                decimal.Decimal(int(A00)) / decimal.Decimal(Q))
        if cand == "X_hash":
            return xn + decimal.Decimal(repr(param)) * (
                decimal.Decimal(int(Hint)) / decimal.Decimal(2 ** 256))
    raise ValueError(cand)


CANDS = ([("X_null", None), ("rdet", None), ("X_parfree", None),
          ("V_evade", None)]
         + [("X_lambda", lam) for lam in LAMBDAS]
         + [("X_hash", c) for c in CGRID])
PIN_OF = {"X_null": PIN_DET, "rdet": PIN_DET, "X_parfree": PIN_DET,
          "V_evade": PIN_DET_A00, "X_lambda": PIN_DET_A00, "X_hash": PIN_DET}


def cand_label(cand, param):
    return cand if param is None else "%s[%s=%r]" % (
        cand, "lambda" if cand == "X_lambda" else "c", param)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe"] = "probe_precision_ladder"
    R["task_id"] = TASK_ID
    R["batch_id"] = BATCH_ID
    R["goal_id"] = GOAL_ID
    R["role"] = "red-team"
    R["claim_tier"] = "toy"
    R["status_of_this_measurement"] = (
        "A PROBE ON THE RED TEAM'S OWN FRAMES. Not pre-registered. Rescores no "
        "frozen verdict of this batch or of any prior batch. Specifies no "
        "criterion, threshold, gate or K. Nothing here bears on ML-KEM "
        "security, on any FIPS 203 parameter set, on any attack cost or on any "
        "cost model.")
    R["environment"] = OrderedDict([
        ("python", sys.version.split()[0]), ("numpy", np.__version__),
        ("platform", sys.platform)])
    R["inputs_sha256"] = OrderedDict([
        ("measure_gvar2.py (committed lead, BATCH-4ed139)", sha256_file(P_MG)),
        ("results_a1.json (committed lead, BATCH-6b6e78)", sha256_file(P_A1))])
    R["imported_not_transcribed"] = (
        "var_f_from_cells, bit_identical, make_A_seed, moduli, LATTICES, "
        "BETA_GRID, TAU_VAR, ROUTES6 and probe_nullroute's fixed_unimodular / "
        "fixed_isometry come from the committed measure_gvar2.py by import.")

    # ---------------------------------------------------------------- (C)
    print("[C] R4's float32 conditioning, per lattice, before any measurement")
    cond = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        B, _ = build_basis(d, k, 0, 2, PIN_DET)
        G = B @ B.T
        mx = int(np.max(np.abs(G)))
        cond[lat] = OrderedDict([
            ("d", d), ("k", k),
            ("max_abs_entry_of_B_BT", mx),
            ("float32_exact_integer_limit_2_pow_24", 2 ** 24),
            ("exceeds_float32_exact_integer_range", bool(mx > 2 ** 24)),
            ("bits_of_the_Gram_beyond_float32_mantissa",
             max(0, int(mx).bit_length() - 24)),
            ("max_abs_entry_of_B", int(np.max(np.abs(B))))])
        print("    %-4s d=%-4d k=%-4d max|B B^T| = %-12d > 2^24 : %s  (%d bits "
              "beyond the float32 mantissa)"
              % (lat, d, k, mx, mx > 2 ** 24, max(0, mx.bit_length() - 24)))
    R["C_R4_conditioning_per_lattice"] = cond
    R["C_note"] = (
        "R4 forms B B^T AT THE WORKING PRECISION. Where max|B B^T| exceeds "
        "2**24 the float32 Gram cannot be formed exactly and the route is "
        "already wrong when slogdet is called. This is arithmetic about the "
        "declared family and is knowable with no run at all.")

    # ------------------------------------------------------------ route error
    print("[E] absolute error of each route against the exact log|det B|")
    ctx = decimal.Context(prec=60)
    err_tab = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        with decimal.localcontext(ctx):
            exact_ld = float(decimal.Decimal(d - k) * decimal.Decimal(Q).ln())
        per = OrderedDict()
        for prec, dt in (("binary32", np.float32), ("binary64", np.float64)):
            vals = OrderedDict()
            for rname in ROUTES6 + ["R4_mixed_exact_gram_then_cast"]:
                worst = 0.0
                for i in range(N_BASES):
                    B, _ = build_basis(d, k, i, 2, PIN_DET)
                    ro, _e = routes_at(B, d, k, dt)
                    if rname in ro:
                        worst = max(worst, abs(ro[rname] - exact_ld))
                vals[rname] = worst
            per[prec] = vals
        err_tab[lat] = OrderedDict([("exact_logdet", exact_ld), ("max_abs_error", per)])
        print("    %-4s exact log|det| = %.10f" % (lat, exact_ld))
        for prec in ("binary32", "binary64"):
            print("        %-9s " % prec + "  ".join(
                "%s=%.3e" % (r.split("_")[0], per[prec][r]) for r in per[prec]))
    R["E_route_absolute_error_vs_exact_logdet"] = err_tab

    # ---------------------------------------------------------------- (L)+(N)
    print("[L] the precision ladder: binary32 -> binary64 -> EXACT")
    ctx_stat = decimal.Context(prec=240)
    ROUTES_ALL = ROUTES6 + ["R4_mixed_exact_gram_then_cast"]
    # logdet[(draw,pin,lat,i,prec)][route]
    LD = {}
    A00 = {}
    HI = {}
    for draw, sp in DRAWS:
        for pin in (PIN_DET, PIN_DET_A00):
            for lat, (d, k) in LATTICES.items():
                for i in range(N_BASES):
                    B, A = build_basis(d, k, i, sp, pin)
                    A00[(draw, pin, lat, i)] = int(A[0, 0])
                    HI[(draw, pin, lat, i)] = hash_H_int(B)
                    for prec, dt in (("binary32", np.float32),
                                     ("binary64", np.float64)):
                        ro, _e = routes_at(B, d, k, dt)
                        LD[(draw, pin, lat, i, prec)] = ro
    print("    bases built and routes evaluated: %d" % len(LD))

    blocks = OrderedDict()
    changes = OrderedDict()          # (rung, route) -> count
    changes_by_cand = OrderedDict()
    n_cells = 0
    for cand, param in CANDS:
        pin = PIN_OF[cand]
        clab = cand_label(cand, param)
        for draw, sp in DRAWS:
            # exact rung first: one verdict per cell, route-free
            fib_exact = OrderedDict()
            for lat, (d, k) in LATTICES.items():
                fib_exact[lat] = OrderedDict()
                for beta in BETA_GRID[d]:
                    vals = []
                    for i in range(N_BASES):
                        vals.append(candidate_value_exact(
                            cand, param, d, k, beta,
                            A00[(draw, pin, lat, i)], HI[(draw, pin, lat, i)],
                            ctx_stat))
                    with decimal.localcontext(ctx_stat):
                        m = sum(vals) / decimal.Decimal(len(vals))
                        var = sum((v - m) ** 2 for v in vals) \
                            / decimal.Decimal(len(vals) - 1)
                        s = var.sqrt()
                    fib_exact[lat][beta] = {
                        "s": float(s), "m": float(m),
                        "bit_identical": all(v == vals[0] for v in vals),
                        "n_distinct": len(set(str(v) for v in vals)),
                        "seed_prefix": sp}
            vf_exact = var_f_from_cells(fib_exact)

            for rname in ROUTES_ALL:
                per_prec = {}
                for prec in ("binary32", "binary64"):
                    fib = OrderedDict()
                    ok = True
                    for lat, (d, k) in LATTICES.items():
                        fib[lat] = OrderedDict()
                        for beta in BETA_GRID[d]:
                            vals = []
                            for i in range(N_BASES):
                                ro = LD[(draw, pin, lat, i, prec)]
                                if rname not in ro:
                                    ok = False
                                    break
                                vals.append(candidate_value(
                                    cand, param, ro[rname], d, k, beta,
                                    A00[(draw, pin, lat, i)],
                                    HI[(draw, pin, lat, i)]))
                            if not ok:
                                break
                            a = np.asarray(vals, dtype=float)
                            fib[lat][beta] = {
                                "s": float(a.std(ddof=1)), "m": float(a.mean()),
                                "bit_identical": bit_identical(vals),
                                "n_distinct": len(set(vals)),
                                "seed_prefix": sp}
                        if not ok:
                            break
                    per_prec[prec] = var_f_from_cells(fib) if ok else None
                if per_prec["binary32"] is None or per_prec["binary64"] is None:
                    continue
                bl = "%s|%s|F0|%s|%s" % (clab, rname, draw, pin)
                c32_64 = c64_ex = c32_ex = 0
                for ck in per_prec["binary64"]:
                    n_cells += 1
                    v32 = per_prec["binary32"][ck]["VAR_F"]
                    v64 = per_prec["binary64"][ck]["VAR_F"]
                    vex = vf_exact[ck]["VAR_F"]
                    if v32 != v64:
                        c32_64 += 1
                    if v64 != vex:
                        c64_ex += 1
                    if v32 != vex:
                        c32_ex += 1
                blocks[bl] = OrderedDict([
                    ("candidate", clab), ("route", rname),
                    ("fibre_family", "F0|%s|%s" % (draw, pin)),
                    ("n_cells", len(per_prec["binary64"])),
                    ("changes_binary32_to_binary64", c32_64),
                    ("changes_binary64_to_EXACT", c64_ex),
                    ("changes_binary32_to_EXACT", c32_ex)])
                for rung, cnt in (("binary32->binary64", c32_64),
                                  ("binary64->EXACT", c64_ex),
                                  ("binary32->EXACT", c32_ex)):
                    changes[(rung, rname)] = changes.get((rung, rname), 0) + cnt
                    changes_by_cand[(rung, clab)] = \
                        changes_by_cand.get((rung, clab), 0) + cnt

    R["L_blocks"] = blocks
    lad = OrderedDict()
    for rung in ("binary32->binary64", "binary64->EXACT", "binary32->EXACT"):
        lad[rung] = OrderedDict(
            (r, changes.get((rung, r), 0)) for r in ROUTES_ALL)
        lad[rung]["TOTAL_over_the_six_declared_routes"] = sum(
            changes.get((rung, r), 0) for r in ROUTES6)
    R["L_ladder_verdict_changes_by_route"] = lad
    R["L_ladder_verdict_changes_by_candidate"] = OrderedDict(
        ("%s | %s" % (k[0], k[1]), v) for k, v in sorted(changes_by_cand.items()))
    R["L_n_cell_comparisons"] = n_cells

    print("\n[L] VAR-F verdict changes, by rung and route "
          "(the six declared routes plus the nearby object):")
    for rung in ("binary32->binary64", "binary64->EXACT", "binary32->EXACT"):
        print("    %-20s %s" % (rung, "  ".join(
            "%s=%d" % (r.split("_")[0], lad[rung][r]) for r in ROUTES_ALL)))
        print("    %-20s TOTAL over the six declared routes = %d"
              % ("", lad[rung]["TOTAL_over_the_six_declared_routes"]))

    # ---------------------------------- independent reproduction of the lead
    with open(P_A1) as fh:
        lead = json.load(fh)
    lead_total = lead["obligation_c_VAR_F_verdict_changes_with_precision"][
        "total_cells_whose_committed_VAR_F_verdict_changes"]
    mine = lad["binary32->binary64"]["TOTAL_over_the_six_declared_routes"]
    R["reproduction_of_the_lead"] = OrderedDict([
        ("lead_total_cells_whose_committed_VAR_F_verdict_changes", lead_total),
        ("this_probe_same_quantity_over_the_324_determinant_only_blocks", mine),
        ("equal", bool(lead_total == mine)),
        ("note", "The lead's 330 blocks include six X_gso_k blocks, which this "
                 "probe does not rebuild; the lead's own by-route breakdown "
                 "places every changing cell on R4 and R2, both "
                 "determinant-only routes.")])
    print("\n[R] lead reports %d changing cells; this probe measures %d on the "
          "determinant-only blocks; equal = %s"
          % (lead_total, mine, lead_total == mine))

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1, default=str)
        fh.write("\n")
    print("\nwrote %s in %.1f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
