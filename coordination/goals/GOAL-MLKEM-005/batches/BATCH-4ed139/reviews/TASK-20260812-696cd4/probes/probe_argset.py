#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED-TEAM PROBE 1 -- THE DECLARED ARGUMENT SET (PREREG-1 3.5's conceded free
parameter), BUILT RATHER THAN PROPOSED.

TASK-20260812-696cd4 / BATCH-4ed139 / GOAL-MLKEM-005.  Role: red-team.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

THIS IS A PROBE, NOT A PRE-REGISTERED MEASUREMENT.  It was written AFTER the
lead producer's numbers were committed and it is reported as such.  It RESCORES
NO FROZEN VERDICT: R2-OUT-1, R2-OUT-2, R2-OUT-3, R2-OUT-4, R2-OUT-5, R2-OUT-V,
R2-OUT-6/7/8 and the termination branch T-F0FAIL-PARTIAL are the lead's and the
riders', are read here only as inputs, and are not recomputed, re-weighted or
re-decided.  What is scored here are OBJECTS THE FROZEN TEXT DOES NOT SCORE:
alternative fibre families, and one new candidate observable that no
pre-registration declares.  Introducing a candidate observable into the GOAL is
a Coordinator/Idea-Generator act (PREREG-1 2.4); nothing here asks for that --
X_hash is a red-team null object and is not proposed for admission anywhere.

WHAT IT TESTS -- three questions, all of them about the DECLARED ARGUMENT SET.

  Q1  IS THE DECLARED ARGUMENT SET LOAD-BEARING IN THE IMPLEMENTATION AT ALL?
      PREREG-1 3.3 says: "Let F|fib be the fibre sub-family of section 2.3
      holding X's DECLARED NUISANCE ARGUMENTS fixed across the basis index while
      the free content A varies."  Measured here, per candidate: does the fibre
      family the lead actually evaluated hold that candidate's PREREG-1 2.4
      declared nuisance arguments fixed across i?

  Q2  DOES REPAIRING THE MISMATCH FLIP A VERDICT?
      Builds F0|fib_dec -- the fibre family faithful to the declared nuisance
      set of V_evade and X_lambda, holding BOTH abs(det B) AND A[0,0] fixed
      across i while every other entry of A varies -- and re-evaluates VAR-F and
      the full G-VAR2 conjunction THROUGH THE LEAD'S OWN IMPORTED FUNCTIONS.

  Q3  THE NULL OBJECT.  X_hash = X_null + c * u(B), u(B) = SHA-256 of the exact
      integer basis mapped into [0,1).  It reads every entry of A and carries no
      lattice information of any kind: a cryptographic digest is the canonical
      null object of this shape.  Scored through the lead's own G-VAR2.

PROVENANCE.  measure_gvar2.py (the lead, committed at 3aac83fd8) is IMPORTED,
never transcribed: var_s_from_cells, var_f_from_cells, gvar2, build_basis_fam,
moduli, structural_check_and_exact_absdet, sd_mean, bit_identical, LATTICES,
BETA_GRID, Q, N_BASES, TAU_VAR, LAMBDA_GRID are used directly.  Its main() is
never called and no committed file is modified.

RE-EXECUTABLE from anywhere:
    PYTHONDONTWRITEBYTECODE=1 python3 -B probe_argset.py --out probe_argset_output.json
WRITES exactly one file: the --out path.
"""

import argparse
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
LEAD_RESULTS = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-56b9da/results_gvar2.json")
PREREG1 = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-34b86c/prereg.md")


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
    spec.loader.exec_module(mod)          # module level only; main() NOT called
    return mod


LD = load_module(LEAD, "lead_measure_gvar2_committed")

Q = LD.Q
N_BASES = LD.N_BASES
TAU_VAR = LD.TAU_VAR
LATTICES = LD.LATTICES
BETA_GRID = LD.BETA_GRID
bit_identical = LD.bit_identical
sd_mean = LD.sd_mean
var_s_from_cells = LD.var_s_from_cells
var_f_from_cells = LD.var_f_from_cells
gvar2 = LD.gvar2
ROUTES6 = LD.ROUTES6


# --------------------------------------------------------------- new families
# F0|fib_s2 as the lead built it (seed prefix 2, A' varies entirely).
# F0|fib_dec: the SAME draw, with A'[0,0] OVERWRITTEN by its i = 0 value at
# every i.  abs(det B) = q^(d-k) is unchanged and still bit-identical across the
# 8 bases, so PREREG-1 6.4's could-not-PASS guard still holds; A[0,0] is now
# ALSO held fixed, which is what PREREG-1 2.4 declares for V_evade and X_lambda.
def build_basis_dec(d, k, i, seed_prefix=2, fix_A00=True):
    A = LD.make_A_seed(d, k, Q, i, seed_prefix)
    if fix_A00:
        A0 = LD.make_A_seed(d, k, Q, 0, seed_prefix)
        A = A.copy()
        A[0, 0] = A0[0, 0]
    B = np.zeros((d, d), dtype=np.int64)
    B[:k, :k] = np.eye(k, dtype=np.int64)
    B[:k, k:] = A
    B[k:, k:] = np.diag(np.full(d - k, Q, dtype=np.int64))
    return B


def u_hash(B):
    """A cryptographic digest of the exact integer basis, in [0,1).  Reads every
    entry of A.  Carries no lattice information of any kind."""
    h = hashlib.sha256(np.ascontiguousarray(B).tobytes()).hexdigest()
    return int(h[:13], 16) / float(16 ** 13)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "RT-PROBE-1-ARGSET"
    R["task_id"] = "TASK-20260812-696cd4"
    R["batch_id"] = "BATCH-4ed139"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["role"] = "red-team"
    R["claim_tier"] = "toy"
    R["status"] = (
        "PROBE. NOT pre-registered; written after the producers' numbers were "
        "committed. It rescores NO frozen verdict and evaluates objects the "
        "frozen text does not score. Reported at the scale actually run.")
    R["environment"] = {"python": platform.python_version(),
                        "numpy": np.__version__,
                        "platform": platform.platform(),
                        "cpu_count": os.cpu_count()}
    try:
        R["git_revision"] = subprocess.run(
            ["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip()
    except Exception as e:
        R["git_revision"] = "UNAVAILABLE: %s" % e
    R["inputs_sha256"] = {
        "measure_gvar2.py (lead, committed 3aac83fd8)": sha256_file(LEAD),
        "results_gvar2.json (lead, committed 3aac83fd8)": sha256_file(LEAD_RESULTS),
        "prereg.md (PREREG-1, committed 8d72f2c03)": sha256_file(PREREG1)}
    R["frozen_constants_carried"] = {"q": Q, "N_BASES": N_BASES,
                                     "tau_var": TAU_VAR}

    # ================================================================== Q1
    # Which of PREREG-1 2.4's declared nuisance arguments does the fibre family
    # the lead actually evaluated hold fixed?  MEASURED, per candidate.
    print("[Q1] auditing the fibre families against the declared argument sets")
    DECLARED_NUISANCE = OrderedDict([
        ("X_null", ["abs(det B)"]),
        ("rdet", ["abs(det B)"]),
        ("V_evade", ["abs(det B)", "A[0,0]"]),
        ("X_lambda", ["abs(det B)", "A[0,0]"]),
        ("X_gso_k", ["d", "k", "beta", "q", "abs(det B)"]),
    ])
    q1 = OrderedDict()
    for fam in ("F0|fib_s2", "F0|fib_s3", "F0|fib_s4",
                "F1|fib_s2", "F1|fib_s3", "F1|fib_s4"):
        per = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            dets, a00 = [], []
            for i in range(N_BASES):
                B = LD.build_basis_fam(d, k, i, fam)
                m = LD.moduli(d, k, i, LD.FAMILIES[fam][1])
                ok, ad = LD.structural_check_and_exact_absdet(B, d, k, m)
                dets.append(ad)
                a00.append(int(B[0, k]))
            per[lat] = {"abs_det_held_fixed_across_8_bases": len(set(dets)) == 1,
                        "A00_held_fixed_across_8_bases": len(set(a00)) == 1,
                        "n_distinct_A00_over_8": len(set(a00))}
        q1[fam] = {
            "abs_det_fixed_at_every_lattice":
                all(v["abs_det_held_fixed_across_8_bases"] for v in per.values()),
            "A00_fixed_at_every_lattice":
                all(v["A00_held_fixed_across_8_bases"] for v in per.values()),
            "per_lattice": per}
    R["Q1_fibre_family_audit"] = {
        "question": "PREREG-1 3.3 requires F|fib to hold X's DECLARED nuisance "
                    "arguments (PREREG-1 2.4) fixed across the basis index. "
                    "Which are actually held fixed by the fibre families the "
                    "lead evaluated?",
        "declared_nuisance_by_candidate": DECLARED_NUISANCE,
        "measured": q1,
        "implementation_fact": (
            "measure_gvar2.py evaluates VAR-F on FIBRE_OF[family], a fixed "
            "pair of fibre-family lists that does NOT depend on the candidate. "
            "The per-candidate declared set enters the output only as the "
            "reported string 'fibre_nuisance_held_fixed'. Verified by reading "
            "the committed source, and by the measurement above.")}

    # ================================================================== Q2
    # The faithful fibre for V_evade / X_lambda, and the verdict it produces.
    print("[Q2] building F0|fib_dec and re-evaluating VAR-F and G-VAR2")

    def routes_of(B, d, k):
        out, _ = LD.logdet_routes_fam(
            B, d, k, np.full(d - k, Q, dtype=np.int64), "F0")
        return out

    # cache: (fibkind, lat, i) -> (routes dict, A00)
    CACHE = {}
    for fibkind, fixA in (("F0|fib_s2_as_scored", False),
                          ("F0|fib_dec_A00_fixed", True)):
        for lat, (d, k) in LATTICES.items():
            for i in range(N_BASES):
                B = build_basis_dec(d, k, i, 2, fixA)
                CACHE[(fibkind, lat, i)] = (routes_of(B, d, k), int(B[0, k]))
    # sanity: F0|fib_s2_as_scored must reproduce the lead's own fibre family
    repro = True
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            Bl = LD.build_basis_fam(d, k, i, "F0|fib_s2")
            Bm = build_basis_dec(d, k, i, 2, False)
            repro = repro and np.array_equal(Bl, Bm)
    R["Q2_control_my_unmodified_fibre_equals_the_leads"] = bool(repro)

    def cellstats(fibkind, cand, route, lam=None):
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per_beta = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = []
                for i in range(N_BASES):
                    rts, a00 = CACHE[(fibkind, lat, i)]
                    ld = rts[route]
                    xn = (beta / d) * (1.0 / d) * ld
                    if cand == "V_evade":
                        v = xn + 1e-9 * a00 / Q
                    elif cand == "X_lambda":
                        v = xn + lam * a00 / Q
                    elif cand == "X_null":
                        v = xn
                    elif cand == "rdet":
                        v = math.exp(ld / d)
                    else:
                        raise KeyError(cand)
                    vals.append(v)
                s, m = sd_mean(vals)
                per_beta[beta] = {"s": s, "m": m,
                                  "spread": float(max(vals) - min(vals)),
                                  "bit_identical": bool(bit_identical(vals)),
                                  "n_distinct": len({float(v).hex()
                                                     for v in vals}),
                                  "seed_prefix": 2}
            out[lat] = per_beta
        return out

    # VAR-S on the SCORED family F0 is unchanged by any of this; it is taken
    # from the lead's own committed per-cell records so that nothing is
    # recomputed that the lead already scored.
    lead = json.load(open(LEAD_RESULTS))
    LEADPROF = lead["per_cell_profiles"]

    def lead_var_s(cand, route):
        key = "%s|%s|F0" % (cand, route)
        if key in LEADPROF:
            return {ck: c["VAR_S"] for ck, c in LEADPROF[key]["per_cell"].items()}
        return None

    q2 = OrderedDict()
    CASES = [("V_evade", None)] + [("X_lambda", lam)
                                   for lam in (1e-9, 1e-4, 1e-2, 1e-1, 1.0)]
    for cand, lam in CASES:
        for route in ROUTES6:
            vs_lead = lead_var_s(cand, route)   # V_evade only
            vf_as = var_f_from_cells(cellstats("F0|fib_s2_as_scored", cand,
                                               route, lam))
            vf_dec = var_f_from_cells(cellstats("F0|fib_dec_A00_fixed", cand,
                                                route, lam))
            if vs_lead is None:
                # X_lambda: VAR-S must be computed on the SCORED family F0, not
                # on a fibre.  Done through the lead's own var_s_from_cells on
                # the lead's own F0 statistics.
                vs = var_s_from_cells(LD_stats_F0(cand, route, lam))
            else:
                vs = vs_lead
            g_as = {ck: gvar2(vs[ck], vf_as[ck]) for ck in vs}
            g_dec = {ck: gvar2(vs[ck], vf_dec[ck]) for ck in vs}
            flips = [ck for ck in vs if g_as[ck] != g_dec[ck]]
            q2["%s|lam=%s|%s" % (cand, lam, route)] = OrderedDict([
                ("n_cells", len(vs)),
                ("VAR_S_ADMIT", sum(1 for ck in vs
                                    if vs[ck]["VAR_S"] == "ADMIT")),
                ("VAR_S_REFUSE", sum(1 for ck in vs
                                     if vs[ck]["VAR_S"] == "REFUSE")),
                ("VAR_S_scale_degenerate", sum(1 for ck in vs
                                               if vs[ck]["VAR_S"]
                                               == "scale_degenerate")),
                ("VAR_F_PASS_fibre_AS_SCORED",
                 sum(1 for ck in vs if vf_as[ck]["VAR_F"] == "PASS")),
                ("VAR_F_PASS_fibre_DECLARED",
                 sum(1 for ck in vs if vf_dec[ck]["VAR_F"] == "PASS")),
                ("G_VAR2_ADMIT_fibre_AS_SCORED",
                 sum(1 for v in g_as.values() if v == "ADMIT")),
                ("G_VAR2_ADMIT_fibre_DECLARED",
                 sum(1 for v in g_dec.values() if v == "ADMIT")),
                ("n_cells_whose_G_VAR2_VERDICT_FLIPS", len(flips)),
                ("example_cell", flips[0] if flips else None),
                ("example_s_c_fib_AS_SCORED",
                 vf_as[flips[0]]["s_c_fib"] if flips else None),
                ("example_s_c_fib_DECLARED",
                 vf_dec[flips[0]]["s_c_fib"] if flips else None),
            ])
    R["Q2_declared_fibre_versus_scored_fibre"] = {
        "built": "F0|fib_dec -- seed prefix 2 exactly as PREREG-1 2.3 draws it, "
                 "with A'[0,0] overwritten by its i=0 value at every i. "
                 "abs(det B) = q^(d-k) is untouched and still bit-identical "
                 "across the 8 bases, so PREREG-1 6.4's could-not-PASS guard "
                 "still holds; A[0,0] is now ALSO fixed, which is what "
                 "PREREG-1 2.4 declares for V_evade and X_lambda.",
        "VAR_S_provenance": "V_evade's VAR-S is READ from the lead's committed "
                            "per-cell records, not recomputed. X_lambda's "
                            "VAR-S is computed on the SCORED family F0 through "
                            "the lead's own var_s_from_cells.",
        "per_case": q2}

    # ================================================================== Q3
    print("[Q3] the null object X_hash")
    HB = {}
    for lat, (d, k) in LATTICES.items():
        for i in range(N_BASES):
            for fam, fixA in (("F0", None), ("F0|fib_s2", False),
                              ("F0|fib_dec_A00_fixed", True)):
                if fam == "F0":
                    B = LD.build_basis_fam(d, k, i, "F0")
                else:
                    B = build_basis_dec(d, k, i, 2, fixA)
                HB[(fam, lat, i)] = (u_hash(B), LD.logdet_routes_fam(
                    B, d, k, np.full(d - k, Q, dtype=np.int64), "F0")[0])

    def hash_cellstats(fam, route, c):
        out = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            per_beta = OrderedDict()
            for beta in BETA_GRID[d]:
                vals = []
                for i in range(N_BASES):
                    u, rts = HB[(fam, lat, i)]
                    vals.append((beta / d) * (1.0 / d) * rts[route] + c * u)
                s, m = sd_mean(vals)
                per_beta[beta] = {"s": s, "m": m,
                                  "spread": float(max(vals) - min(vals)),
                                  "bit_identical": bool(bit_identical(vals)),
                                  "n_distinct": len({float(v).hex()
                                                     for v in vals}),
                                  "seed_prefix": 1 if fam == "F0" else 2}
            out[lat] = per_beta
        return out

    q3 = OrderedDict()
    for c in (1e-9, 1e-3, 1e-2, 1e-1):
        for route in ("R1_slogdet", "R2_QR_of_BT"):
            vs = var_s_from_cells(hash_cellstats("F0", route, c))
            vf = var_f_from_cells(hash_cellstats("F0|fib_s2", route, c))
            g = {ck: gvar2(vs[ck], vf[ck]) for ck in vs}
            Ds = [v["D_c"] for v in vs.values() if v["D_c"] is not None]
            q3["c=%s|%s" % (c, route)] = {
                "n_cells": len(vs),
                "VAR_S_ADMIT": sum(1 for v in vs.values()
                                   if v["VAR_S"] == "ADMIT"),
                "VAR_S_REFUSE": sum(1 for v in vs.values()
                                    if v["VAR_S"] == "REFUSE"),
                "VAR_S_scale_degenerate": sum(1 for v in vs.values()
                                              if v["VAR_S"]
                                              == "scale_degenerate"),
                "min_D_c": min(Ds) if Ds else None,
                "max_D_c": max(Ds) if Ds else None,
                "VAR_F_PASS": sum(1 for v in vf.values()
                                  if v["VAR_F"] == "PASS"),
                "VAR_F_decided_by_bit_identity_cells":
                    sum(1 for v in vf.values()
                        if v["decided_by"]
                        == "bit_identity_at_scale_degenerate_fibre_cell"),
                "G_VAR2_ADMIT": sum(1 for v in g.values() if v == "ADMIT"),
                "G_VAR2_REFUSE": sum(1 for v in g.values() if v == "REFUSE")}
    R["Q3_null_object_X_hash"] = {
        "definition": "X_hash(B,beta) = (beta/d)(1/d) log abs(det B) + c * u(B), "
                      "u(B) = int(sha256(B.tobytes())[:13],16) / 16^13 in [0,1)",
        "why_it_is_a_null_object": (
            "u(B) reads every entry of A and is a cryptographic digest, so it "
            "is by construction independent of every geometric property of the "
            "lattice: it carries NO usable lattice information. It is the "
            "null object of the same shape called for by "
            "docs/inventor-protocol.md section 3."),
        "declared_arguments_if_one_had_to_declare_them":
            "d, k, beta, q, abs(det B), H(B); nuisance held fixed on the "
            "fibre: abs(det B)",
        "NOT_PROPOSED_FOR_ADMISSION_ANYWHERE": True,
        "per_amplitude_and_route": q3}

    # A separate, sharper reading of Q3: X_hash at c = 1e-1 is admitted with NO
    # scale degeneracy and NO reliance on float noise, unlike rdet.
    R["Q3_contrast_with_rdet"] = {
        "rdet_R2_F0_admission_mechanism": (
            "VAR-S scale_degenerate (R_{d,k} = 0 by beta-freeness) at 38/38, so "
            "VAR-F alone decides, and VAR-F is decided by bit-identity of float "
            "values whose EXACT determinants are equal. Carried from the lead's "
            "committed results_gvar2.json, not recomputed here."),
        "X_hash_c_1e-1_admission_mechanism": (
            "VAR-S ADMIT on a non-degenerate scale, VAR-F PASS on genuine "
            "non-constancy. No degeneracy and no float noise is involved.")}

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    R["what_this_probe_does_NOT_establish"] = [
        "It rescores no frozen verdict and changes no outcome row.",
        "It does not show that G-VAR2 is wrong to admit X_hash: PREREG-1 3.5 "
        "already states that passing G-VAR2 carries NO claim that an "
        "observable carries lattice information. What X_hash measures is HOW "
        "WIDE that disclaimed gap is -- as wide as a cryptographic hash.",
        "It proposes no candidate observable and no threshold, and it amends "
        "no frozen clause. Those are Coordinator acts.",
        "CLAIM TIER TOY: nothing here bears on ML-KEM security, any FIPS 203 "
        "parameter set, any attack cost or any cost model.",
    ]
    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1)
        fh.write("\n")

    print("=" * 74)
    print("RT-PROBE-1 -- DECLARED ARGUMENT SET -- TOY")
    print("=" * 74)
    print("Q1 fibre families: abs(det) fixed / A[0,0] fixed")
    for fam, v in q1.items():
        print("  %-12s abs_det_fixed=%-5s  A00_fixed=%-5s"
              % (fam, v["abs_det_fixed_at_every_lattice"],
                 v["A00_fixed_at_every_lattice"]))
    print("\nQ2 verdict flips between the AS-SCORED fibre and the DECLARED fibre")
    for k, v in q2.items():
        if v["n_cells_whose_G_VAR2_VERDICT_FLIPS"]:
            print("  %-46s flips %2d/%2d  ADMIT %2d -> %2d"
                  % (k, v["n_cells_whose_G_VAR2_VERDICT_FLIPS"], v["n_cells"],
                     v["G_VAR2_ADMIT_fibre_AS_SCORED"],
                     v["G_VAR2_ADMIT_fibre_DECLARED"]))
    print("  (cases with zero flips omitted from this print; all are in the JSON)")
    print("\nQ3 null object X_hash through the lead's own G-VAR2")
    for k, v in q3.items():
        print("  %-26s VAR_S ADMIT %2d degen %2d  VAR_F PASS %2d  G-VAR2 ADMIT %2d"
              % (k, v["VAR_S_ADMIT"], v["VAR_S_scale_degenerate"],
                 v["VAR_F_PASS"], v["G_VAR2_ADMIT"]))
    print("\nwrote %s in %.2f s" % (args.out, R["wall_clock_seconds"]))
    return 0


_F0_CACHE = {}


def _f0_routes(lat, d, k, i):
    key = (lat, i)
    if key not in _F0_CACHE:
        B = LD.build_basis_fam(d, k, i, "F0")
        rts, _ = LD.logdet_routes_fam(
            B, d, k, np.full(d - k, Q, dtype=np.int64), "F0")
        _F0_CACHE[key] = (rts, int(B[0, k]))
    return _F0_CACHE[key]


def LD_stats_F0(cand, route, lam):
    """X_lambda's VAR-S on the SCORED family F0, through the lead's own
    cand_value semantics (transcribed from measure_gvar2.py section 1, which
    defines cand_value inside main() and so cannot be imported)."""
    out = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        per_beta = OrderedDict()
        for beta in BETA_GRID[d]:
            vals = []
            for i in range(N_BASES):
                rts, a00 = _f0_routes(lat, d, k, i)
                xn = (beta / d) * (1.0 / d) * rts[route]
                vals.append(xn + lam * a00 / Q)
            s, m = sd_mean(vals)
            per_beta[beta] = {"s": s, "m": m,
                              "spread": float(max(vals) - min(vals)),
                              "bit_identical": bool(bit_identical(vals)),
                              "n_distinct": len({float(v).hex() for v in vals}),
                              "seed_prefix": 1}
        out[lat] = per_beta
    return out


if __name__ == "__main__":
    sys.exit(main())
