#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RIDER (ii) -- THE FALSE-REFUSAL CONTROL.

TASK-20260812-4b8ede / BATCH-4ed139 / GOAL-MLKEM-005.  Role: executor.
CLAIM TIER TOY, UNCONDITIONALLY.  Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost or on any cost model.

WHAT THIS IS.  A measurement of the single candidate observable the Coordinator
introduced in PREREG-1 sections 2.4 and 8.2:

    X_gso_k(B) = (1/k) * sum_{j=1..k} log ||b*_j||   over the RAW basis,
                                                     frozen row order

    declared arguments: d, k, q, the raw GSO profile -- AND NO BETA
    routes:  RQ  QR of B^T,                      log|R_jj|, j = 1..k
             RG  Cholesky of the Gram B B^T,     log of the diagonal, j = 1..k

The definition is FROZEN and is not redefined here.  This producer implements it
as written; any objection is recorded in report_falserefusal.md and the frozen
definition is scored anyway.

THE TWO HALVES, BOTH MEASURED AND NEITHER ASSERTED.

  informativeness  the between-basis dispersion of X_gso_k over the 8 frozen
                   bases at every lattice, with |det B_i| shown bit-identical
                   across those 8 bases so the dispersion cannot come from the
                   determinant, plus a cross-family contrast at fixed
                   (d, k, q, |det B|) against the new A-draws of F0|fib.

  refusal          X_gso_k pushed through THE COMMITTED G-REL1 CODE PATH --
                   rho_both() and bit_identical() are IMPORTED from
                   BATCH-9e3584 tasks/TASK-20260809-cda2f6/measure_relvar.py,
                   not transcribed -- at both normalizations, with s_X/|X|
                   beside every entry.

  G-VAR2           scored through THE LEAD PRODUCER'S OWN COMMITTED CODE --
                   var_s_from_cells(), var_f_from_cells() and gvar2() are
                   IMPORTED from BATCH-4ed139 tasks/TASK-20260812-56b9da/
                   measure_gvar2.py, together with build_basis_fam() and the
                   family table, so this rider scores the same instrument the
                   lead scored and not a re-reading of it.

WHAT THIS ESTABLISHES AND WHAT IT DOES NOT, frozen in advance (PREREG-1 8.2).
ONE CONSTRUCTED INSTANCE, n = 1.  It narrows DEC-20260812-7c4a1e C-2(b) from
"the refusal side is untested in either direction" to "the refusal side has one
constructed instance".  IT DOES NOT MEASURE A FALSE-REFUSAL RATE and no rate is
reported, estimated or implied anywhere in this file or its outputs.

NO REDUCTION OF ANY KIND is performed, so all ten lattices are in scope and
fpylll is not required.  If fpylll is absent that is recorded as an environment
fact and nothing here depends on it.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out results_falserefusal.json

WRITES exactly one file: the --out path.  No git write, no commit.
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

import numpy as np

T0 = time.time()

TASK_ID = "TASK-20260812-4b8ede"
BATCH_ID = "BATCH-4ed139"
GOAL_ID = "GOAL-MLKEM-005"
CANDIDATE = "X_gso_k"
MEASUREMENT_CAP_SECONDS = 600.0          # task card / handoff constraint


# ------------------------------------------------------------------ plumbing
def _repo_root():
    env = os.environ.get("FALSEREFUSAL_REPO_ROOT")
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    p = here
    for _ in range(12):
        if os.path.isdir(os.path.join(p, ".git")):
            return p
        nxt = os.path.dirname(p)
        if nxt == p:
            break
        p = nxt
    return here


REPO_ROOT = _repo_root()

REL_MEASURE = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584",
    "tasks/TASK-20260809-cda2f6/measure_relvar.py")
REL_RESULTS = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584",
    "tasks/TASK-20260809-cda2f6/results_relvar.json")
GVAR2_MEASURE = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139",
    "tasks/TASK-20260812-56b9da/measure_gvar2.py")
GVAR2_RESULTS = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139",
    "tasks/TASK-20260812-56b9da/results_gvar2.json")
PREREG = os.path.join(
    REPO_ROOT, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139",
    "tasks/TASK-20260812-34b86c/prereg.md")


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git(*args):
    try:
        return subprocess.check_output(["git"] + list(args), cwd=REPO_ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception as exc:                                # pragma: no cover
        return "GIT UNAVAILABLE: %s" % exc


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# The two committed producers, IMPORTED rather than transcribed.
MG = load_module(GVAR2_MEASURE, "_committed_measure_gvar2")
MR = load_module(REL_MEASURE, "_committed_measure_relvar")

# Frozen constants, taken from the committed producers' own module namespaces so
# this rider cannot drift from them by transcription.
Q = MG.Q
N_BASES = MG.N_BASES
TAU_VAR = MG.TAU_VAR
TAU_REL = MR.TAU_REL
S_X = MG.S_X                      # 1.0, PREREG-1 2.1
LATTICES = MG.LATTICES
BETA_GRID = MG.BETA_GRID
REL1_PAIR = MR.REL1_PAIR
FAMILIES = MG.FAMILIES
FIBRE_OF = MG.FIBRE_OF

bit_identical = MR.bit_identical
summarize = MR.summarize
rho_both = MR.rho_both

ROUTES = ["RQ_qr_of_BT", "RG_cholesky_of_gram"]
SCORED = ["F0", "F1"]
ALL_FAMILIES = ["F0", "F1",
                "F0|fib_s2", "F0|fib_s3", "F0|fib_s4",
                "F1|fib_s2", "F1|fib_s3", "F1|fib_s4"]


# --------------------------------------------- the candidate, PREREG-1 2.4/2.5
def x_gso_k_RQ(B, k):
    """RQ: QR of B^T, log|R_jj| for j = 1..k, averaged.  B^T = Q R gives
    |R[j,j]| = ||b*_j|| for the ROWS of B in their frozen order.  No reduction."""
    _, R = np.linalg.qr(B.astype(np.float64).T)
    dg = np.abs(np.diag(R))[:k]
    return float(np.mean(np.log(dg))), dg


def x_gso_k_RG(B, k):
    """RG: Cholesky of the Gram B B^T = L L^T, log of the diagonal, j = 1..k,
    averaged.  L[j,j] = ||b*_j|| for the same row order.  No reduction."""
    G = (B.astype(np.int64) @ B.astype(np.int64).T).astype(np.float64)
    L = np.linalg.cholesky(G)
    dg = np.abs(np.diag(L))[:k]
    return float(np.mean(np.log(dg))), dg


ROUTE_FN = {"RQ_qr_of_BT": x_gso_k_RQ, "RG_cholesky_of_gram": x_gso_k_RG}


def n_distinct(vals):
    return len({float(v).hex() for v in vals})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    RES = OrderedDict()
    RES["task_id"] = TASK_ID
    RES["batch_id"] = BATCH_ID
    RES["goal_id"] = GOAL_ID
    RES["rider"] = "(ii) false-refusal control, PREREG-1 8.2, outcome row R2-OUT-7"
    RES["claim_tier"] = "TOY"
    RES["candidate"] = CANDIDATE
    RES["candidate_definition"] = (
        "X_gso_k(B) = (1/k) * sum_{j=1..k} log ||b*_j|| over the RAW basis in "
        "frozen row order; declared arguments d, k, q, raw GSO profile -- NO "
        "beta. FROZEN IN PREREG-1 2.4 AND NOT REDEFINED HERE.")
    RES["n_instances"] = 1
    RES["no_rate_disclosure"] = (
        "n = 1, ONE CONSTRUCTED INSTANCE. NO FALSE-REFUSAL RATE is reported, "
        "estimated or implied. A rate needs a population and a sampling scheme "
        "and this batch has neither.")
    RES["scope"] = (
        "q = 3329; d in {20,30,40,100,140}; the frozen k and beta grids; 8 "
        "bases per lattice per family; families F0, F1 and their fibre "
        "sub-families at seed prefixes 2, 3, 4; routes RQ and RG; NO REDUCTION "
        "AT ALL. Every observation is scoped to exactly that and transports "
        "nowhere.")

    RES["provenance"] = OrderedDict([
        ("git_commit", git("rev-parse", "HEAD")),
        ("git_dirty_tree", git("status", "--porcelain")),
        ("repo_root", REPO_ROOT),
        ("imported_not_transcribed", [
            "measure_gvar2.py: build_basis_fam, structural_check_and_exact_absdet,"
            " var_s_from_cells, var_f_from_cells, gvar2, FAMILIES, FIBRE_OF,"
            " LATTICES, BETA_GRID, TAU_VAR, Q, N_BASES, S_X",
            "measure_relvar.py: rho_both, bit_identical, summarize, TAU_REL,"
            " REL1_PAIR"]),
        ("inputs_sha256", OrderedDict([
            ("prereg.md", sha256_file(PREREG)),
            ("measure_gvar2.py", sha256_file(GVAR2_MEASURE)),
            ("results_gvar2.json", sha256_file(GVAR2_RESULTS)),
            ("measure_relvar.py", sha256_file(REL_MEASURE)),
            ("results_relvar.json", sha256_file(REL_RESULTS)),
        ])),
    ])
    RES["environment"] = OrderedDict([
        ("python", sys.version.split()[0]),
        ("numpy", np.__version__),
        ("platform", platform.platform()),
        ("machine", platform.machine()),
        ("cpu_count", os.cpu_count()),
        ("fpylll_available", bool(getattr(MR, "HAVE_FPYLLL", False))),
        ("fpylll_note",
         "NOT REQUIRED BY THIS RIDER: no reduction of any kind is performed, so "
         "all ten lattices are in scope regardless. Recorded as an environment "
         "fact only."),
    ])
    RES["randomness"] = (
        "No randomness is drawn by this script. Every basis is rebuilt "
        "deterministically by the committed build_basis_fam() from "
        "np.random.default_rng([seed_prefix, d, k, i]) with seed_prefix 1 (F0, "
        "F1), 2, 3, 4 (fibre families), exactly as PREREG-1 2.3 freezes them.")

    # -------------------------------------------------------------------
    # 0.  COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE NUMBERS ARE READ
    # -------------------------------------------------------------------
    print("=" * 78)
    print("RIDER (ii) -- FALSE-REFUSAL CONTROL -- %s" % TASK_ID)
    print("CLAIM TIER TOY. n = 1, ONE CONSTRUCTED INSTANCE. NO RATE IS MEASURED.")
    print("=" * 78)
    print("\n[0] COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN")
    print("    could-not-FIRE  -- a construction that could NEVER be refused.")
    print("       Would hold if the candidate were built so that no clause of")
    print("       the gate could return a refusal at any cell. The check is")
    print("       MEASURED below, not asserted: G-REL1's rho is computed at")
    print("       every lattice at both normalizations and its per-basis pass")
    print("       count against tau_rel = %.2f is reported. A construction" % TAU_REL)
    print("       that could not fire would show rho >= tau_rel everywhere.")
    print("    could-not-PASS  -- a construction that could NEVER be informative.")
    print("       Would hold if X_gso_k were constant across the 8 bases, so")
    print("       that 'informative by construction' were vacuous. The check is")
    print("       MEASURED below: between-basis sd and the count of distinct")
    print("       IEEE-754 values over the 8 bases at every lattice, with")
    print("       |det B_i| shown BIT-IDENTICAL across those 8 bases so the")
    print("       dispersion cannot be coming from the determinant.")
    print("    Both are decided by the numbers in sections 1-5, never by this")
    print("    paragraph.")

    RES["could_not_fail_arrangements"] = OrderedDict([
        ("could_not_FIRE", OrderedDict([
            ("statement",
             "A construction that could never be refused by the gate. Would "
             "hold if the candidate satisfied every clause by construction."),
            ("how_it_is_excluded",
             "MEASURED, not asserted: G-REL1 rho at every lattice at both "
             "normalizations, with the per-basis pass count against "
             "tau_rel = 0.10 reported in section 3."),
            ("verdict", None),
        ])),
        ("could_not_PASS", OrderedDict([
            ("statement",
             "A construction that could never be informative. Would hold if "
             "X_gso_k were constant across the 8 bases, making 'informative by "
             "construction' vacuous."),
            ("how_it_is_excluded",
             "MEASURED, not asserted: between-basis sd and distinct-IEEE-754 "
             "count over the 8 bases at every lattice in section 2, with "
             "|det B_i| bit-identical across those bases."),
            ("verdict", None),
        ])),
    ])

    # -------------------------------------------------------------------
    # 1.  RAW MEASUREMENT -- both routes, every family, every lattice, 8 bases
    # -------------------------------------------------------------------
    print("\n[1] RAW MEASUREMENT -- X_gso_k through RQ and RG, 8 bases, "
          "%d families, 10 lattices" % len(ALL_FAMILIES))
    t_meas0 = time.time()
    X = {}            # (family, lattice, route) -> [8 values]
    ABSDET = {}       # (family, lattice) -> [8 exact integer |det B|]
    STRUCT_OK = True
    struct_failures = []
    for fam in ALL_FAMILIES:
        for lat, (d, k) in LATTICES.items():
            per_route = {r: [] for r in ROUTES}
            ads = []
            for i in range(N_BASES):
                B = MG.build_basis_fam(d, k, i, fam)
                m = MG.moduli(d, k, i, FAMILIES[fam][1])
                ok, ad = MG.structural_check_and_exact_absdet(B, d, k, m)
                if not ok:
                    STRUCT_OK = False
                    struct_failures.append("%s/%s/i%d" % (fam, lat, i))
                ads.append(ad)
                for r in ROUTES:
                    v, _dg = ROUTE_FN[r](B, k)
                    per_route[r].append(v)
            for r in ROUTES:
                X[(fam, lat, r)] = per_route[r]
            ABSDET[(fam, lat)] = ads
    t_meas = time.time() - t_meas0
    print("    basis rebuilds + QR + Cholesky complete in %.1f s "
          "(%d bases)" % (t_meas, len(ALL_FAMILIES) * len(LATTICES) * N_BASES))
    print("    block-structure check on every basis: %s"
          % ("OK" if STRUCT_OK else "FAILED at %s" % struct_failures))

    RES["structural_check"] = OrderedDict([
        ("all_bases_block_structure_verified", STRUCT_OK),
        ("failures", struct_failures),
        ("note",
         "|det B| is the exact integer prod(m) as a verified consequence of the "
         "verified block structure, never a float read."),
    ])

    # route agreement, AM-16(b)
    print("\n[1b] ROUTE AGREEMENT (AM-16 b) -- RQ vs RG")
    agree = OrderedDict()
    worst = 0.0
    worst_at = None
    for fam in ALL_FAMILIES:
        per_lat = OrderedDict()
        for lat in LATTICES:
            a = np.asarray(X[(fam, lat, "RQ_qr_of_BT")], dtype=float)
            b = np.asarray(X[(fam, lat, "RG_cholesky_of_gram")], dtype=float)
            dmax = float(np.max(np.abs(a - b)))
            rel = float(np.max(np.abs(a - b) / np.maximum(np.abs(a), 1e-300)))
            nbit = int(np.sum([float(u).hex() == float(v).hex()
                               for u, v in zip(a, b)]))
            per_lat[lat] = OrderedDict([
                ("max_abs_diff_RQ_minus_RG", dmax),
                ("max_rel_diff", rel),
                ("n_bit_identical_of_8", nbit),
            ])
            if dmax > worst:
                worst, worst_at = dmax, "%s/%s" % (fam, lat)
        agree[fam] = per_lat
    print("    worst absolute RQ-RG disagreement over all families, lattices "
          "and bases: %.3e at %s" % (worst, worst_at))
    RES["route_agreement_RQ_vs_RG"] = OrderedDict([
        ("per_family_per_lattice", agree),
        ("worst_abs_diff", worst),
        ("worst_at", worst_at),
        ("note",
         "Two independent float paths to the same frozen quantity. Reported as "
         "measured; no tolerance is pre-registered for it and none is invented "
         "here."),
    ])

    # -------------------------------------------------------------------
    # 2.  THE INFORMATIVENESS HALF -- DEMONSTRATED, NOT ASSERTED
    # -------------------------------------------------------------------
    print("\n[2] INFORMATIVENESS -- between-basis dispersion of X_gso_k on F0")
    print("    lattice  (d,k)      route  mean X        sd over 8      "
          "distinct/8  |det| bit-identical over 8")
    info = OrderedDict()
    all_sd_pos = True
    for lat, (d, k) in LATTICES.items():
        per_route = OrderedDict()
        det_bid = len({str(v) for v in ABSDET[("F0", lat)]}) == 1
        for r in ROUTES:
            vals = X[("F0", lat, r)]
            a = np.asarray(vals, dtype=float)
            sd = float(a.std(ddof=1))
            mn = float(a.mean())
            nd = n_distinct(vals)
            if not (sd > 0.0):
                all_sd_pos = False
            per_route[r] = OrderedDict([
                ("values_over_8_bases", [float(v) for v in vals]),
                ("mean", mn), ("sd_ddof1", sd),
                ("min", float(a.min())), ("max", float(a.max())),
                ("spread_max_minus_min", float(a.max() - a.min())),
                ("relative_sd_over_abs_mean",
                 float(sd / abs(mn)) if mn != 0 else None),
                ("n_distinct_ieee754_values_over_8_bases", nd),
                ("bit_identical_over_8_bases", bit_identical(vals)),
            ])
            print("    %-7s (%3d,%3d)  %-20s %+.9f  %.6e  %d/8  %s"
                  % (lat, d, k, r, mn, sd, nd, det_bid))
        info[lat] = OrderedDict([
            ("d", d), ("k", k),
            ("abs_det_exact_over_8_bases", [str(v) for v in ABSDET[("F0", lat)]]),
            ("abs_det_bit_identical_over_8_bases", det_bid),
            ("per_route", per_route),
        ])
    RES["informativeness_F0"] = OrderedDict([
        ("per_lattice", info),
        ("sd_strictly_positive_at_every_lattice_and_route", all_sd_pos),
        ("what_this_shows",
         "X_gso_k varies across the 8 frozen bases at every lattice while "
         "|det B_i| is bit-identical across those same 8 bases, so the "
         "variation is not a determinant effect. Within F0 the ONLY thing that "
         "varies with the basis index is A_i. Scoped to F0 and to these "
         "lattices; no claim that any observable carries lattice information "
         "is made -- PREREG-1 3.5."),
    ])

    # cross-family contrast at fixed (d, k, q, |det B|): F0 vs F0|fib_s2
    print("\n[2b] A-DEPENDENCE CONTRAST -- F0 vs F0|fib_s2 (new A draw, "
          "IDENTICAL d, k, q and |det B|)")
    contrast = OrderedDict()
    for lat, (d, k) in LATTICES.items():
        same_det = (set(str(v) for v in ABSDET[("F0", lat)])
                    == set(str(v) for v in ABSDET[("F0|fib_s2", lat)]))
        a = np.asarray(X[("F0", lat, "RQ_qr_of_BT")], dtype=float)
        b = np.asarray(X[("F0|fib_s2", lat, "RQ_qr_of_BT")], dtype=float)
        contrast[lat] = OrderedDict([
            ("abs_det_identical_across_the_two_families", bool(same_det)),
            ("mean_F0", float(a.mean())),
            ("mean_F0_fib_s2", float(b.mean())),
            ("mean_difference", float(b.mean() - a.mean())),
            ("max_per_index_abs_difference", float(np.max(np.abs(a - b)))),
        ])
        print("    %-7s |det| identical: %-5s  mean F0 %+.9f  mean fib %+.9f  "
              "max per-index |diff| %.6e"
              % (lat, same_det, a.mean(), b.mean(), np.max(np.abs(a - b))))
    RES["A_dependence_contrast_F0_vs_F0fib_s2"] = contrast

    RES["could_not_fail_arrangements"]["could_not_PASS"]["verdict"] = (
        "EXCLUDED BY MEASUREMENT: between-basis sd is strictly positive at "
        "every lattice and both routes (see informativeness_F0), with "
        "|det B_i| bit-identical across the 8 bases."
        if all_sd_pos else
        "NOT EXCLUDED: some lattice/route has zero between-basis dispersion. "
        "See informativeness_F0.")

    # -------------------------------------------------------------------
    # 3.  THE REFUSAL HALF -- THROUGH THE COMMITTED G-REL1 CODE PATH
    # -------------------------------------------------------------------
    print("\n[3] G-REL1 THROUGH THE COMMITTED CODE PATH "
          "(rho_both/bit_identical imported from measure_relvar.py)")
    print("    tau_rel = %.2f, s_X = %.1f, both normalizations, 8 bases"
          % (TAU_REL, S_X))
    rel1 = OrderedDict()
    n_forced = 0
    n_lat = 0
    any_pass = 0
    for r in ROUTES:
        per_lat = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            lo, hi = REL1_PAIR[d]
            # X_gso_k takes NO beta argument: its value at beta_lo and beta_hi
            # is the SAME NUMBER, computed once per basis. This is the frozen
            # definition applied literally, not a shortcut.
            vals = X[("F0", lat, r)]
            vals_lo = list(vals)
            vals_hi = list(vals)
            ent = [rho_both(vals_hi[i], vals_lo[i], S_X) for i in range(N_BASES)]
            diffs = [vals_hi[i] - vals_lo[i] for i in range(N_BASES)]
            forced_zero = bool(bit_identical(diffs) and abs(diffs[0]) == 0.0)
            sm_max = summarize([e["value_maxfloor"] for e in ent])
            sm_abs = summarize([e["value_absX"] for e in ent])
            npass_max = int(sum(e["value_maxfloor"] >= TAU_REL for e in ent))
            npass_abs = int(sum((e["value_absX"] or 0.0) >= TAU_REL
                                for e in ent))
            per_lat[lat] = OrderedDict([
                ("d", d), ("k", k), ("beta_lo", lo), ("beta_hi", hi),
                ("per_basis", ent),
                ("maxfloor", sm_max), ("absX", sm_abs),
                ("s_over_absX_mean", float(np.mean(
                    [e["s_over_absX"] for e in ent
                     if e["s_over_absX"] is not None]))
                 if any(e["s_over_absX"] is not None for e in ent) else None),
                ("scale_floor_binding_in_n_of_8",
                 int(sum(e["scale_floor_is_binding"] for e in ent))),
                ("n_pass_maxfloor_of_8", npass_max),
                ("n_pass_absX_of_8", npass_abs),
                ("pass_at_i0_LEGACY_READING",
                 bool(ent[0]["value_maxfloor"] >= TAU_REL)),
                ("pass_at_mean_over_8", bool(sm_max["mean"] >= TAU_REL)),
                ("FORCED_ZERO_BY_ALGEBRA", forced_zero),
                ("rho_is_exactly_zero_at_all_8_bases",
                 bool(all(e["value_maxfloor"] == 0.0 for e in ent)
                      and all((e["value_absX"] == 0.0) for e in ent))),
            ])
            n_lat += 1
            n_forced += int(forced_zero)
            any_pass += npass_max
            print("    %-4s %-7s (%3d,%3d) beta %3d->%3d  rho_maxfloor mean "
                  "%.3e  rho_absX mean %s  s_X/|X| %.4f  pass %d/8  "
                  "forced_zero %s"
                  % (r[:2], lat, d, k, lo, hi, sm_max["mean"],
                     ("%.3e" % sm_abs["mean"]) if sm_abs else "n/a",
                     per_lat[lat]["s_over_absX_mean"] or float("nan"),
                     npass_max, forced_zero))
        rel1[r] = per_lat

    # the committed aggregation, applied verbatim (measure_relvar.py section 6)
    grel1 = OrderedDict()
    for r in ROUTES:
        r1 = list(rel1[r].values())
        r1_forced = [v for v in r1 if v["FORCED_ZERO_BY_ALGEBRA"]]
        untested = bool(r1) and len(r1_forced) == len(r1)
        n_pass_mean = sum(v["pass_at_mean_over_8"] for v in r1)
        rel1_ok = bool(n_pass_mean > 0 and not untested)
        grel1[r] = OrderedDict([
            ("n_lattices_scored", len(r1)),
            ("n_forced_zero_by_algebra", len(r1_forced)),
            ("UNTESTED_BY_ALGEBRA", untested),
            ("n_pass_at_mean_over_8", n_pass_mean),
            ("n_pass_at_i0_legacy",
             sum(v["pass_at_i0_LEGACY_READING"] for v in r1)),
            ("best_mean_maxfloor",
             max([v["maxfloor"]["mean"] for v in r1], default=None)),
            ("best_mean_absX",
             max([v["absX"]["mean"] for v in r1 if v["absX"] is not None],
                 default=None)),
            ("rel1_ok_under_committed_rule", rel1_ok),
            ("committed_rule",
             "measure_relvar.py section 6: rel1_ok = (n_pass_at_mean_over_8 > 0"
             " and not UNTESTED_BY_ALGEBRA). Applied verbatim."),
        ])
    RES["G_REL1"] = OrderedDict([("per_lattice_per_route", rel1),
                                 ("aggregated", grel1)])
    RES["G_REL1_disclosure"] = (
        "The committed code labels a forced zero UNTESTED rather than a "
        "failure: its own note reads 'this candidate takes no beta argument, so "
        "REL-1 is identically 0 BY ALGEBRA. Reported as UNTESTED, NOT as a "
        "failure. This is not a test that could have failed.' Under the "
        "committed aggregation rel1_ok is nevertheless False, so the candidate "
        "does not pass G-REL. BOTH readings are reported here and neither is "
        "adjudicated by this producer.")

    rho_all_zero = all(
        v["rho_is_exactly_zero_at_all_8_bases"]
        for r in ROUTES for v in rel1[r].values())
    forced_all = all(v["FORCED_ZERO_BY_ALGEBRA"]
                     for r in ROUTES for v in rel1[r].values())
    refused_by_grel1 = bool(rho_all_zero and forced_all
                            and all(not grel1[r]["rel1_ok_under_committed_rule"]
                                    for r in ROUTES))
    print("\n    rho == 0 exactly at every lattice, every basis, both routes: %s"
          % rho_all_zero)
    print("    FORCED_ZERO_BY_ALGEBRA at every lattice, both routes: %s"
          % forced_all)
    print("    rel1_ok under the committed rule: %s"
          % {r: grel1[r]["rel1_ok_under_committed_rule"] for r in ROUTES})

    RES["could_not_fail_arrangements"]["could_not_FIRE"]["verdict"] = (
        "EXCLUDED BY MEASUREMENT: the gate does return a refusal for this "
        "candidate -- rho = 0 < tau_rel = 0.10 at every lattice and basis, so "
        "the construction is refusable and in fact refused."
        if refused_by_grel1 else
        "NOT EXCLUDED AS MEASURED: see G_REL1. The candidate was not refused "
        "at every lattice.")

    # -------------------------------------------------------------------
    # 4.  G-VAR2 THROUGH THE LEAD PRODUCER'S OWN COMMITTED CODE
    # -------------------------------------------------------------------
    print("\n[4] G-VAR2 (PREREG-1 section 3) through the LEAD'S committed "
          "var_s_from_cells / var_f_from_cells / gvar2")

    # fibre guard, PREREG-1 6.4 could-not-PASS
    print("\n    [4a] FIBRE GUARD (PREREG-1 6.4): |det B_i| bit-identical "
          "across all 8 bases in every fibre family")
    fib_guard = OrderedDict()
    guard_ok = True
    for fam in ALL_FAMILIES:
        if "|fib" not in fam:
            continue
        per_lat = OrderedDict()
        for lat, (d, k) in LATTICES.items():
            ads = ABSDET[(fam, lat)]
            ident = len({str(v) for v in ads}) == 1
            expect = (Q ** (d - k) if fam.startswith("F0")
                      else (Q + 3) * Q ** (d - k - 1))
            matches = (int(ads[0]) == int(expect))
            if not (ident and matches):
                guard_ok = False
            per_lat[lat] = OrderedDict([
                ("abs_det_exact", str(ads[0])),
                ("bit_identical_across_8_bases", ident),
                ("matches_declared_closed_form", bool(matches)),
                ("declared_closed_form",
                 "q^(d-k)" if fam.startswith("F0") else "(q+3) q^(d-k-1)"),
            ])
        fib_guard[fam] = per_lat
        print("        %-11s all 10 lattices bit-identical and matching: %s"
              % (fam, all(v["bit_identical_across_8_bases"]
                          and v["matches_declared_closed_form"]
                          for v in per_lat.values())))
    RES["fibre_guard_6_4"] = OrderedDict([
        ("per_family", fib_guard),
        ("guard_holds_everywhere", guard_ok),
        ("consequence_if_false",
         "PREREG-1 6.4: if the assertion fails anywhere the run is an "
         "instrument failure and claims nothing."),
    ])
    if not guard_ok:
        print("        *** FIBRE GUARD FAILED -- see PREREG-1 6.4 ***")

    # VAR-S and VAR-F, per route, per scored family
    gv = OrderedDict()
    for r in ROUTES:
        per_fam = OrderedDict()
        for fam in SCORED:
            # cellstats: X_gso_k is beta-free, so the SAME 8 values are used at
            # every beta of the lattice's frozen grid. That is the frozen
            # definition applied literally.
            cellstats = OrderedDict()
            for lat, (d, k) in LATTICES.items():
                vals = X[(fam, lat, r)]
                s, m = MG.sd_mean(vals)
                per_beta = OrderedDict()
                for beta in BETA_GRID[d]:
                    per_beta[beta] = {
                        "s": s, "m": m,
                        "spread": float(max(vals) - min(vals)),
                        "bit_identical": bit_identical(vals)}
                cellstats[lat] = per_beta
            var_s = MG.var_s_from_cells(cellstats)

            fib_records = OrderedDict()
            for fib in FIBRE_OF[fam]:
                fibstats = OrderedDict()
                for lat, (d, k) in LATTICES.items():
                    vals = X[(fib, lat, r)]
                    s, m = MG.sd_mean(vals)
                    per_beta = OrderedDict()
                    for beta in BETA_GRID[d]:
                        per_beta[beta] = {
                            "s": s, "m": m,
                            "bit_identical": bit_identical(vals),
                            "n_distinct": n_distinct(vals),
                            "seed_prefix": FAMILIES[fib][0]}
                    fibstats[lat] = per_beta
                fib_records[fib] = MG.var_f_from_cells(fibstats)

            primary_fib = FIBRE_OF[fam][0]
            cells = OrderedDict()
            for key, vs in var_s.items():
                vf = fib_records[primary_fib][key]
                cells[key] = OrderedDict([
                    ("VAR_S_record", vs),
                    ("VAR_F_record_primary_fibre", vf),
                    ("primary_fibre_family", primary_fib),
                    ("G_VAR2", MG.gvar2(vs, vf)),
                    ("G_VAR2_replicates", OrderedDict(
                        (fib, MG.gvar2(vs, fib_records[fib][key]))
                        for fib in FIBRE_OF[fam])),
                    ("declared_argument_set",
                     "d, k, q, raw GSO profile -- NO beta (PREREG-1 2.4)"),
                    ("route", r), ("family", fam),
                ])
            n_cells = len(cells)
            n_admit = sum(1 for v in cells.values() if v["G_VAR2"] == "ADMIT")
            n_degen = sum(1 for v in cells.values()
                          if v["VAR_S_record"]["VAR_S"] == "scale_degenerate")
            n_varf_pass = sum(1 for v in cells.values()
                              if v["VAR_F_record_primary_fibre"]["VAR_F"]
                              == "PASS")
            per_fam[fam] = OrderedDict([
                ("per_cell", cells),
                ("n_cells", n_cells),
                ("n_VAR_S_scale_degenerate", n_degen),
                ("n_VAR_S_ADMIT", sum(
                    1 for v in cells.values()
                    if v["VAR_S_record"]["VAR_S"] == "ADMIT")),
                ("n_VAR_S_REFUSE", sum(
                    1 for v in cells.values()
                    if v["VAR_S_record"]["VAR_S"] == "REFUSE")),
                ("n_VAR_F_PASS_primary_fibre", n_varf_pass),
                ("n_G_VAR2_ADMIT", n_admit),
                ("n_G_VAR2_REFUSE", n_cells - n_admit),
                ("naive_reading_verdict_counts", OrderedDict([
                    (kk, sum(1 for v in cells.values()
                             if v["VAR_S_record"]["naive_reading_VAR_S"] == kk))
                    for kk in sorted({v["VAR_S_record"]["naive_reading_VAR_S"]
                                      for v in cells.values()})])),
                ("replicate_agreement", OrderedDict(
                    (fib, sum(1 for v in cells.values()
                              if v["G_VAR2_replicates"][fib] == "ADMIT"))
                    for fib in FIBRE_OF[fam])),
            ])
            print("    route %-20s family %-3s: cells %2d  VAR-S "
                  "degenerate %2d / ADMIT %2d / REFUSE %2d  VAR-F PASS %2d  "
                  "G-VAR2 ADMIT %2d"
                  % (r, fam, n_cells, n_degen,
                     per_fam[fam]["n_VAR_S_ADMIT"],
                     per_fam[fam]["n_VAR_S_REFUSE"], n_varf_pass, n_admit))
        gv[r] = per_fam
    RES["G_VAR2"] = gv
    RES["G_VAR2_disclosure"] = (
        "PREREG-1 3.2 frozen reading is BINDING: R_{d,k} == 0 gives "
        "scale_degenerate -- not a pass and not a fail -- and the naive "
        "reading's verdict is reported beside it at every such cell. PREREG-1 "
        "3.5: passing G-VAR2 carries NO claim that an observable carries "
        "lattice information, and G-VAR2 is one clause of the AM-4/AM-8 gate "
        "and not the gate.")

    # -------------------------------------------------------------------
    # 5.  P-FR1
    # -------------------------------------------------------------------
    admitted_F0 = all(
        gv[r]["F0"]["n_G_VAR2_ADMIT"] == gv[r]["F0"]["n_cells"]
        for r in ROUTES)
    degen_F0 = all(
        gv[r]["F0"]["n_VAR_S_scale_degenerate"] == gv[r]["F0"]["n_cells"]
        for r in ROUTES)
    varf_F0 = all(
        gv[r]["F0"]["n_VAR_F_PASS_primary_fibre"] == gv[r]["F0"]["n_cells"]
        for r in ROUTES)
    p_fr1 = bool(refused_by_grel1 and admitted_F0)
    print("\n[5] P-FR1 -- 'X_gso_k is REFUSED by G-REL1 and ADMITTED by G-VAR2 "
          "(scale_degenerate on VAR-S, PASS on VAR-F)'")
    print("    refused by G-REL1 .................. %s" % refused_by_grel1)
    print("    VAR-S scale_degenerate at all F0 cells, both routes ... %s"
          % degen_F0)
    print("    VAR-F PASS at all F0 cells, both routes .............. %s"
          % varf_F0)
    print("    admitted by G-VAR2 at all F0 cells, both routes ...... %s"
          % admitted_F0)
    print("    P-FR1: %s" % ("HOLDS" if p_fr1 else "FALSIFIED"))
    if not admitted_F0:
        print("    *** G-VAR2 ALSO REFUSES X_gso_k. PREREG-1 3.2 names this in "
              "advance as an INSTRUMENT DEFECT: the degenerate-scale rule would "
              "be doing the refusing and the fibre clause would be decorative. "
              "REPORTED LOUDLY, per the completion gate. ***")

    RES["P_FR1"] = OrderedDict([
        ("statement",
         "X_gso_k is REFUSED by G-REL1 and ADMITTED by G-VAR2 "
         "(scale_degenerate on VAR-S, PASS on VAR-F)."),
        ("falsifier", "either half failing"),
        ("class", "PREDICTION (n = 1 instance), OPEN at notarization"),
        ("half_1_refused_by_G_REL1", refused_by_grel1),
        ("half_2_admitted_by_G_VAR2_F0_both_routes", admitted_F0),
        ("VAR_S_scale_degenerate_at_all_F0_cells", degen_F0),
        ("VAR_F_PASS_at_all_F0_cells", varf_F0),
        ("verdict", "HOLDS" if p_fr1 else "FALSIFIED"),
        ("instrument_defect_flag", (not admitted_F0)),
        ("instrument_defect_note",
         "PREREG-1 3.2 declares in advance that if BOTH rdet and X_gso_k are "
         "refused, the degenerate-scale rule is doing the refusing and VAR-F is "
         "decorative -- a defect in the instrument worth more than the intended "
         "result. Flag is True only if G-VAR2 refused X_gso_k here."),
        ("bound",
         "ONE CONSTRUCTED INSTANCE, n = 1. Narrows DEC-20260812-7c4a1e C-2(b) "
         "from 'the refusal side is untested in either direction' to 'the "
         "refusal side has one constructed instance'. NO RATE."),
    ])

    RES["R2_OUT_7"] = OrderedDict([
        ("row", "R2-OUT-7"),
        ("what_it_records",
         "rider (ii): P-FR1, one constructed false-refusal instance, n = 1"),
        ("P_FR1", "HOLDS" if p_fr1 else "FALSIFIED"),
        ("G_REL1_refusal", refused_by_grel1),
        ("G_VAR2_admission_F0", admitted_F0),
    ])

    elapsed = time.time() - T0
    RES["timing"] = OrderedDict([
        ("measurement_seconds", t_meas),
        ("total_script_seconds", elapsed),
        ("measurement_cap_seconds", MEASUREMENT_CAP_SECONDS),
        ("cap_exceeded", bool(t_meas > MEASUREMENT_CAP_SECONDS)),
        ("note",
         "A cap that binds is INFRASTRUCTURE SIGNAL, never a refusal and never "
         "a negative mathematical result."),
    ])
    RES["binding_carries"] = [
        "AM-10..AM-14 (DEC-20260808-05b684), AM-15, AM-16 (DEC-20260809-afe29b),"
        " AM-17 (DEC-20260812-7c4a1e) are in force.",
        "AM-3 IS NOT RETIRED; its 0.096 family-wise false-failure bound stands.",
        "BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.",
        "'a factor of 6 to 31' is FALSE; the citable range is 4.87x to 31.03x.",
        "Any use of the committed real count 29 of 48 carries the exact-null "
        "benchmark 47 of 48 in the same sentence.",
        "THE G-VAR REFUSAL IS CITED ONLY AS CONDITIONAL ON THE FROZEN FAMILY F0.",
        "CLAIM TIER STAYS TOY.",
        "AGENTS.md rule 12 is UNMET AND UNWAIVED in this goal; model_verified "
        "is false with its reason.",
    ]

    with open(args.out, "w") as fh:
        json.dump(RES, fh, indent=1, default=str)
    print("\nWROTE %s  (%.1f s total)" % (args.out, elapsed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
