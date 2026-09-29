#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED TEAM PROBE 2 -- THE PRIMARY TARGET, BUILT: AN OBJECT A-1 CANNOT
SEPARATE FROM A REAL ONE, AND IT IS NOT A DIGEST.

TASK-20260813-85e343 / BATCH-6b6e78 / GOAL-MLKEM-005.  Role: red-team.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

THIS IS A PROBE ON THE RED TEAM'S OWN FRAMES.  Not pre-registered.  It rescores
no frozen verdict of this batch or of any prior batch.  X_lin and X_par below
are NOT candidates of PREREG-2 2.4 and are NOT added to any candidate list --
introducing a candidate is a Coordinator act.  They are objects built to test
what A-1 can and cannot separate.

WHAT IS BUILT.  Two objects on the frozen family F0 and the frozen PIN-DET
fibre, each of which

  * has an EXACT route that terminates in microseconds            -> A-1.1 holds
  * is CERTIFIED EXACTLY NON-CONSTANT on its own declared fibre  -> the class
    A-1.3 governs
  * has rho > 0 at both declared precisions and rho(f32)/rho(f64) inside the
    frozen [1/2, 2] window at every covered cell                 -> A-1.3 holds
  * is PROVABLY NOT A LATTICE INVARIANT: an explicit unimodular row operation
    leaves the lattice identical and changes the object's value exactly
  * carries no usable information about the one in-scope geometric observable,
    measured as a correlation across the fibre with replication and dispersion

  X_lin = mean(A entries) / q          -- a LINEAR functional.  Not a hash, not
                                          a digest, monotone and continuous in
                                          every entry of A.
  X_par = (#even entries of A) / (k(d-k)) -- a COUNTING functional, a ratio of
                                          small integers, exactly representable
                                          at both declared precisions.

RE-EXECUTABLE from the repository root:
    PYTHONDONTWRITEBYTECODE=1 python3 -B <this file> --out <this dir>/probe_nonconstant_null_output.json

WRITES exactly one file: the --out path.  No git write, no commit.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict
from fractions import Fraction

sys.dont_write_bytecode = True
import numpy as np

T0 = time.time()
TASK_ID = "TASK-20260813-85e343"


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
P_MF = os.path.join(REPO, G5, "batches/BATCH-4ed139/tasks/"
                              "TASK-20260812-4b8ede/measure_falserefusal.py")


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


MG = load_module(P_MG, "committed_measure_gvar2")
MF = load_module(P_MF, "committed_measure_falserefusal")
Q = MG.Q
N_BASES = MG.N_BASES
LATTICES = MG.LATTICES
BETA_GRID = MG.BETA_GRID
DRAWS = [("fib_s2", 2), ("fib_s3", 3), ("fib_s4", 4)]


def build_basis(d, k, i, seed_prefix):
    """The frozen PIN-DET fibre: modulus block fixed at q, so |det B_i| =
    q^(d-k) is bit-identical across i BY CONSTRUCTION (PREREG-2 2.3)."""
    A = MG.make_A_seed(d, k, Q, i, seed_prefix).copy()
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = np.diag(MG.moduli(d, k, i, "const_q"))
    return B, A


# ------------------------------------------------------------ the two objects
def x_lin_exact(A):
    """EXACT: a rational.  Sum of integers over q * count."""
    k, n = A.shape
    return Fraction(int(A.sum()), Q * k * n)


def x_par_exact(A):
    k, n = A.shape
    return Fraction(int((A % 2 == 0).sum()), k * n)


def x_lin_float(A, dt):
    return float(np.mean(A.astype(dt)) / dt(Q))


def x_par_float(A, dt):
    k, n = A.shape
    return float(dt((A % 2 == 0).sum()) / dt(k * n))


def x_hash_float(B, dt, c=1e-3):
    payload = b"|".join(str(int(x)).encode() for x in B.flatten(order="C"))
    h = int(hashlib.sha256(payload).hexdigest(), 16) / float(2 ** 256)
    return float(dt(c) * dt(h))


def rho(vals):
    a = np.asarray(vals, dtype=float)
    s = float(a.std(ddof=1))
    m = float(a.mean())
    return (None if m == 0.0 else s / abs(m)), s, m


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = x - x.mean()
    y = y - y.mean()
    dn = float(np.sqrt((x * x).sum() * (y * y).sum()))
    return None if dn == 0.0 else float((x * y).sum() / dn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe"] = "probe_nonconstant_null"
    R["task_id"] = TASK_ID
    R["batch_id"] = "BATCH-6b6e78"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["role"] = "red-team"
    R["claim_tier"] = "toy"
    R["status_of_this_measurement"] = (
        "A PROBE ON THE RED TEAM'S OWN FRAMES. Not pre-registered. Rescores no "
        "frozen verdict. X_lin and X_par are NOT PREREG-2 2.4 candidates and "
        "are not added to any candidate list; introducing a candidate is a "
        "Coordinator act. Nothing here bears on ML-KEM security, on any FIPS "
        "203 parameter set, on any attack cost or on any cost model.")
    R["environment"] = OrderedDict([("python", sys.version.split()[0]),
                                    ("numpy", np.__version__)])
    R["inputs_sha256"] = OrderedDict([
        ("measure_gvar2.py (committed lead, BATCH-4ed139)", sha256_file(P_MG)),
        ("measure_falserefusal.py (committed rider ii, BATCH-4ed139)",
         sha256_file(P_MF))])
    R["objects"] = OrderedDict([
        ("X_lin", OrderedDict([
            ("definition", "mean(A entries) / q"),
            ("kind", "LINEAR functional of A; not a hash, not a digest; "
                     "monotone and continuous in every entry"),
            ("declared_arguments", ["d", "k", "beta", "q", "abs(det B)",
                                    "every entry of A"]),
            ("nuisance_held_fixed_on_its_own_fibre", ["abs(det B)"]),
            ("fibre_family", "PIN-DET, the frozen PREREG-2 2.3 construction"),
            ("exact_route", "R_lin_exact: Fraction(sum(A), q*k*(d-k))")])),
        ("X_par", OrderedDict([
            ("definition", "(number of even entries of A) / (k(d-k))"),
            ("kind", "COUNTING functional; a ratio of integers below 2**24, "
                     "exactly representable at BOTH declared precisions"),
            ("declared_arguments", ["d", "k", "beta", "q", "abs(det B)",
                                    "every entry of A"]),
            ("nuisance_held_fixed_on_its_own_fibre", ["abs(det B)"]),
            ("fibre_family", "PIN-DET, the frozen PREREG-2 2.3 construction"),
            ("exact_route", "R_par_exact: Fraction(count_even(A), k*(d-k))")]))])

    # ------------------------------------------------- 1. exact certification
    print("[1] A-1.1: the exact route, and the certified class on the own fibre")
    cert = OrderedDict()
    t_exact = 0.0
    for name, fn in (("X_lin", x_lin_exact), ("X_par", x_par_exact)):
        per = OrderedDict()
        allnc = True
        for draw, sp in DRAWS:
            for lat, (d, k) in LATTICES.items():
                t = time.time()
                vals = []
                for i in range(N_BASES):
                    _B, A = build_basis(d, k, i, sp)
                    vals.append(fn(A))
                t_exact += time.time() - t
                cls = "CONSTANT" if all(v == vals[0] for v in vals) \
                    else "NON-CONSTANT"
                if cls != "NON-CONSTANT":
                    allnc = False
                per["%s|%s" % (draw, lat)] = OrderedDict([
                    ("certified_class", cls),
                    ("n_distinct_exact_values", len(set(vals))),
                    ("exact_values", [str(v) for v in vals])])
        cert[name] = OrderedDict([
            ("certified_NON_CONSTANT_everywhere", allnc),
            ("n_fibres", len(per)), ("per_fibre", per)])
        print("    %-6s certified NON-CONSTANT on every fibre: %s (%d fibres)"
              % (name, allnc, len(per)))
    R["exact_route_wall_clock_seconds_total"] = round(t_exact, 4)
    R["A_1_1_exact_certification"] = cert
    print("    exact-route wall clock, both objects, 60 fibres: %.4f s"
          % t_exact)

    # -------------------------------------------- 2. A-1.3 precision behaviour
    print("[2] A-1.3: rho at both declared precisions, and the ratio")
    inv = OrderedDict()
    for name, ffn in (("X_lin", x_lin_float), ("X_par", x_par_float)):
        rows = OrderedDict()
        worst_lo, worst_hi, n_out, n_zero, n_cells = 9e99, -9e99, 0, 0, 0
        for draw, sp in DRAWS:
            for lat, (d, k) in LATTICES.items():
                v32, v64 = [], []
                for i in range(N_BASES):
                    _B, A = build_basis(d, k, i, sp)
                    v32.append(ffn(A, np.float32))
                    v64.append(ffn(A, np.float64))
                r32, s32, m32 = rho(v32)
                r64, s64, m64 = rho(v64)
                ratio = None if (r64 in (None, 0.0)) else r32 / r64
                n_cells += 1
                if r32 == 0.0 or r64 == 0.0:
                    n_zero += 1
                if ratio is None or not (0.5 <= ratio <= 2.0):
                    n_out += 1
                if ratio is not None:
                    worst_lo = min(worst_lo, ratio)
                    worst_hi = max(worst_hi, ratio)
                rows["%s|%s" % (draw, lat)] = OrderedDict([
                    ("rho_binary32", r32), ("rho_binary64", r64),
                    ("ratio", ratio)])
        inv[name] = OrderedDict([
            ("n_fibre_cells", n_cells),
            ("n_cells_with_rho_zero_at_either_precision_FC_3b_analogue", n_zero),
            ("n_cells_outside_the_frozen_window_FC_3a_analogue", n_out),
            ("ratio_min", worst_lo), ("ratio_max", worst_hi),
            ("per_fibre", rows)])
        print("    %-6s ratio in [%.9f, %.9f]; outside [1/2,2]: %d of %d; "
              "rho == 0 anywhere: %d"
              % (name, worst_lo, worst_hi, n_out, n_cells, n_zero))
    R["A_1_3_precision_invariance"] = inv

    # ------------------------------- 3. provably not a lattice invariant
    print("[3] the unimodular row operation: SAME lattice, different value")
    uni = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        B, A = build_basis(d, k, 0, 2)
        U = np.eye(d, dtype=np.int64)
        U[0, k] = 1                       # add row k (= q e_k) to row 0
        Bp = U @ B
        Ap = Bp[:k, k:]
        detU = int(round(float(np.linalg.det(U.astype(np.float64)))))
        same_lattice = (detU == 1)
        # |det B| is the only lattice invariant this family carries, and it is
        # what PIN-DET pins.  Check it is untouched.
        absdet_ok = np.array_equal(Bp[k:, :], B[k:, :]) and \
            np.array_equal(Bp[:k, :k], B[:k, :k])
        dlin = float(x_lin_exact(Ap) - x_lin_exact(A))
        dpar = float(x_par_exact(Ap) - x_par_exact(A))
        g_before, _ = MF.x_gso_k_RQ(B, k)
        g_after, _ = MF.x_gso_k_RQ(Bp, k)
        uni[lat] = OrderedDict([
            ("det_U", detU), ("U_is_unimodular_so_the_lattice_is_identical",
                              bool(same_lattice)),
            ("row_and_identity_blocks_untouched", bool(absdet_ok)),
            ("A00_before", int(A[0, 0])), ("A00_after", int(Ap[0, 0])),
            ("delta_X_lin", dlin), ("expected_delta_X_lin", 1.0 / (k * (d - k))),
            ("delta_X_par", dpar),
            ("X_gso_k_RQ_before", g_before), ("X_gso_k_RQ_after", g_after),
            ("delta_X_gso_k_RQ", g_after - g_before)])
        print("    %-4s det U = %d  dX_lin = %+.3e  dX_par = %+.3e  "
              "dX_gso_k = %+.3e" % (lat, detU, dlin, dpar, g_after - g_before))
    R["not_a_lattice_invariant"] = uni
    R["not_a_lattice_invariant_note"] = (
        "U = I + E_{0,k} is integral with det U = 1, so B and U B generate the "
        "IDENTICAL lattice; U B differs from B only in A[0,0], which moves by "
        "+q. X_lin and X_par change on the same lattice, so neither is a "
        "lattice invariant. REPORTED AGAINST MY OWN THESIS IN THE SAME PLACE: "
        "X_gso_k moves under the same operation too, so basis-dependence does "
        "not by itself separate the built objects from the one in-scope "
        "candidate that reads the instance.")

    # --------------------------- 4. does it carry information about geometry?
    print("[4] correlation across the fibre with the in-scope geometric "
          "observable X_gso_k (RQ, binary64)")
    corr = OrderedDict()
    series = {"X_lin": [], "X_par": [], "X_hash[c=1e-3]": [],
              "X_gso_k_RG_vs_RQ_MUST_PASS_CONTROL": []}
    for draw, sp in DRAWS:
        for lat, (d, k) in LATTICES.items():
            gq, gg, xl, xp, xh = [], [], [], [], []
            for i in range(N_BASES):
                B, A = build_basis(d, k, i, sp)
                a, _ = MF.x_gso_k_RQ(B, k)
                b, _ = MF.x_gso_k_RG(B, k)
                gq.append(a)
                gg.append(b)
                xl.append(x_lin_float(A, np.float64))
                xp.append(x_par_float(A, np.float64))
                xh.append(x_hash_float(B, np.float64))
            series["X_lin"].append(pearson(xl, gq))
            series["X_par"].append(pearson(xp, gq))
            series["X_hash[c=1e-3]"].append(pearson(xh, gq))
            series["X_gso_k_RG_vs_RQ_MUST_PASS_CONTROL"].append(pearson(gg, gq))
    for nm, vals in series.items():
        v = sorted(x for x in vals if x is not None)
        n = len(v)
        med = v[n // 2]
        q1, q3 = v[n // 4], v[(3 * n) // 4]
        corr[nm] = OrderedDict([
            ("n_lattice_x_draw_pairs", n), ("median_pearson_r", med),
            ("iqr_low_q1", q1), ("iqr_high_q3", q3),
            ("min", v[0]), ("max", v[-1]),
            ("per_pair", vals)])
        print("    %-38s n=%d  median r = %+.4f  IQR [%+.4f, %+.4f]  "
              "range [%+.4f, %+.4f]" % (nm, n, med, q1, q3, v[0], v[-1]))
    R["information_about_the_geometry"] = corr
    R["information_about_the_geometry_note"] = (
        "AM-10 replication: every correlation is computed over all 8 frozen "
        "bases of a fibre and replicated over the three declared draws, giving "
        "30 lattice x draw pairs. AM-11 dispersion: the median is reported "
        "WITH its IQR and full range, never as a point estimate. The "
        "MUST-PASS control is RG against RQ -- two routes for the SAME "
        "geometric quantity -- which must come out near +1 or the correlation "
        "instrument itself is not measuring anything.")

    # ------------------------------------------------------ 5. search and cost
    R["search_and_its_cost"] = OrderedDict([
        ("constructions_tried", ["X_lin = mean(A)/q (linear functional)",
                                 "X_par = even-entry fraction (counting "
                                 "functional)"]),
        ("constructions_that_worked", 2),
        ("why_they_are_not_scaled_digests",
         "Neither applies a hash or any pseudorandom map. X_lin is linear and "
         "monotone in every entry of A; X_par is a ratio of two integers below "
         "2**24 and is exactly representable at both declared precisions, so "
         "its precision-invariance is arithmetic rather than empirical."),
        ("wall_clock_seconds_of_the_exact_routes", round(t_exact, 4))])

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1, default=str)
        fh.write("\n")
    print("\nwrote %s in %.1f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
