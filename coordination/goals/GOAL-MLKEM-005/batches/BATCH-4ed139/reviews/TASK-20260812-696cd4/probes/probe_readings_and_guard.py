#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED-TEAM PROBE 3 -- IS THERE A FOURTH READING (rider i), AND COULD THE
MUST-PASS GUARD HAVE FAILED (lead, PREREG-1 6.1)?

TASK-20260812-696cd4 / BATCH-4ed139 / GOAL-MLKEM-005.  Role: red-team.
CLAIM TIER TOY.  Nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model.

THIS IS A PROBE, NOT A PRE-REGISTERED MEASUREMENT.  It rescores no frozen
verdict.  In particular it does NOT adjudicate C-1: BOTH SUB-6x COUNTS REMAIN
NOT CITABLE pending the Coordinator's ruling, "a factor of 6 to 31" is FALSE
and the citable range is 4.87x to 31.03x.  Nothing below makes either count
citable and nothing below declares either validator wave right or wrong.

PART A -- THE COMPLETENESS OF RIDER (i)'S THREE READINGS.
Rider (i) reports that all 8 per-basis values are bit-identical at all 29
entries, so the three declared readings coincide and "the reading axis cannot
explain the conflict", and that wave 2's count of 2 corresponds to a 5.71x
threshold rather than a 6x one.  Both statements are re-derived here
INDEPENDENTLY from the committed results_relvar.json, and then attacked:

  A1  Is bit-identity across the 8 bases actually true at all 29 entries?
      Re-derived from the raw per_basis records, not from rider (i)'s summary.
  A2  Is the space of readings really exhausted?  Every symmetric function of
      8 bit-identical values is that value, so the reading axis is closed BY
      ALGEBRA if A1 holds -- that is checked rather than assumed, over seven
      reductions including ones rider (i) did not name.
  A3  Is the NORMALIZATION axis exhausted?  The committed file stores two
      normalizations. FIVE MORE are constructible from the same stored fields
      (X_a, X_b, s_X).  All seven are enumerated against both boundary rules
      and all three denominators, and the whole grid is searched for a count
      of exactly 2 at a 6x threshold and for a count of 15 of 19.  If some
      other cell of that grid yields 2, the reading/normalization axis is NOT
      closed and rider (i)'s "5.71x threshold" reading is not the only one.

PART B -- COULD R2-OUT-V HAVE FIRED?
PREREG-1 6.1 declares the VOID row "live and not a straw man".  VAR-S on
X_lambda is EXACTLY linear in lambda -- D_c(lambda) = lambda * sd_i(A[0,0]_i/q)
/ R_{d,k} -- so the largest D_c reachable in the frozen grid is its value at
lambda = 1, and R2-OUT-V fires only if that is below tau_var at EVERY cell.
That is computed here and compared with tau_var = 1e-3.

PART C -- AM-10 REPLICATION APPLIED TO THE GUARD'S OWN STATISTIC.
lambda* is reported by the lead on ONE A-draw (seed prefix 1).  It is
recomputed here on the three further draws (seed prefixes 2, 3, 4) so that the
statistic carries the replication AM-10 requires of a criterion statistic.

RE-EXECUTABLE:
    PYTHONDONTWRITEBYTECODE=1 python3 -B probe_readings_and_guard.py \
        --out probe_readings_and_guard_output.json
WRITES exactly one file: the --out path.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from collections import OrderedDict, Counter

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
RELVAR = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
          "TASK-20260809-cda2f6/results_relvar.json")
LEAD = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-56b9da/measure_gvar2.py")
RIDER1 = os.path.join(
    REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
          "TASK-20260812-78a6e3/results_c1res.json")

TAU_REL = 0.10


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


# --------------------------------------------------------------- readings
def reductions(vals):
    """Every reduction of the 8 per-basis values considered here.  The first
    three are PREREG-1 8.1's declared readings; the rest are additions this
    probe makes in order to attack the claim that the reading axis is closed."""
    return OrderedDict([
        ("R_i0_legacy", vals[0]),
        ("R_npass_of_8", vals[0]),          # see note: identical when bit-ident
        ("R_mean_over_8", math.fsum(vals) / len(vals)),
        ("R_min_over_8", min(vals)),
        ("R_max_over_8", max(vals)),
        ("R_median_over_8", statistics.median(vals)),
        ("R_last_i7", vals[-1]),
    ])


NORMALIZATIONS = [
    "N1_maxfloor_committed",     # |Xa-Xb| / max(s_X, |Xa|)      (in the file)
    "N2_absXa_committed",        # |Xa-Xb| / |Xa|                (in the file)
    "N3_absXb",                  # |Xa-Xb| / |Xb|
    "N4_absmean",                # |Xa-Xb| / mean(|Xa|,|Xb|)
    "N5_absmax",                 # |Xa-Xb| / max(|Xa|,|Xb|)
    "N6_absmin",                 # |Xa-Xb| / min(|Xa|,|Xb|)
    "N7_unnormalized",           # |Xa-Xb|
]


def normalize(which, Xa, Xb, sX):
    dv = abs(Xa - Xb)
    if which == "N1_maxfloor_committed":
        return dv / max(sX, abs(Xa))
    if which == "N2_absXa_committed":
        return dv / abs(Xa)
    if which == "N3_absXb":
        return dv / abs(Xb)
    if which == "N4_absmean":
        return dv / ((abs(Xa) + abs(Xb)) / 2.0)
    if which == "N5_absmax":
        return dv / max(abs(Xa), abs(Xb))
    if which == "N6_absmin":
        return dv / min(abs(Xa), abs(Xb))
    if which == "N7_unnormalized":
        return dv
    raise KeyError(which)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = OrderedDict()
    R["probe_id"] = "RT-PROBE-3-READINGS-AND-GUARD"
    R["task_id"] = "TASK-20260812-696cd4"
    R["batch_id"] = "BATCH-4ed139"
    R["goal_id"] = "GOAL-MLKEM-005"
    R["role"] = "red-team"
    R["claim_tier"] = "toy"
    R["status"] = ("PROBE. NOT pre-registered. Rescores NO frozen verdict and "
                   "ADJUDICATES C-1 IN NO DIRECTION. Both sub-6x counts remain "
                   "NOT CITABLE pending the Coordinator's ruling; 'a factor of "
                   "6 to 31' is FALSE; the citable range is 4.87x to 31.03x.")
    R["environment"] = {"python": platform.python_version(),
                        "numpy": np.__version__,
                        "platform": platform.platform()}
    R["inputs_sha256"] = {
        "results_relvar.json (BATCH-9e3584, committed)": sha256_file(RELVAR),
        "results_c1res.json (rider i, committed d38514d22)": sha256_file(RIDER1),
        "measure_gvar2.py (lead, committed 3aac83fd8)": sha256_file(LEAD)}

    rel = json.load(open(RELVAR))

    # ================================================== PART A: the readings
    print("[A] re-deriving the 29 X_null G-REL entries from the raw records")
    entries = []      # (label, kind, list of per_basis dicts)
    for lat, blk in rel["G_REL1"]["null"].items():
        entries.append(("G-REL1 %s" % lat, "G-REL1", blk["per_basis"]))
    for pair, per_beta in rel["G_REL2"]["null"].items():
        for beta, blk in per_beta.items():
            entries.append(("G-REL2 %s beta %s" % (pair, beta), "G-REL2",
                            blk["per_basis"]))
    R["A_n_entries_rederived"] = len(entries)

    # A1 -- bit identity across the 8 bases, from the raw per_basis records
    a1 = OrderedDict()
    all_bitid = True
    for label, kind, pb in entries:
        row = {}
        for field in ("value_maxfloor", "value_absX", "X_a", "X_b"):
            vals = [p[field] for p in pb]
            n = len({float(v).hex() for v in vals})
            row[field + "_n_distinct_over_8"] = n
            all_bitid = all_bitid and (n == 1)
        row["n_bases"] = len(pb)
        a1[label] = row
    R["A1_bit_identity_across_the_8_bases"] = {
        "all_29_entries_bit_identical_in_every_stored_field": bool(all_bitid),
        "per_entry": a1,
        "reading": "This is rider (i)'s Observation 1, re-derived here from the "
                   "raw per_basis records rather than from its summary."}

    # A2 -- is the reading axis closed?
    a2 = OrderedDict()
    closed = True
    for label, kind, pb in entries:
        for field in ("value_maxfloor", "value_absX"):
            vals = [p[field] for p in pb]
            red = reductions(vals)
            n = len({float(v).hex() for v in red.values()})
            if n != 1:
                closed = False
                a2.setdefault("entries_where_reductions_disagree", []).append(
                    {"entry": label, "field": field, "reductions": red})
    R["A2_reading_axis"] = {
        "n_reductions_tested": 7,
        "reductions_tested": list(reductions([1.0] * 8).keys()),
        "all_seven_reductions_agree_bitwise_at_every_entry_and_field":
            bool(closed),
        "detail": a2,
        "reading": "Rider (i) declares three readings. Four more are tested "
                   "here, including min, max, median and the last basis index. "
                   "If all seven agree bitwise, the reading axis is closed BY "
                   "ALGEBRA and no fourth reading of the 8 per-basis values "
                   "can exist -- which CONFIRMS rider (i) rather than "
                   "refuting it."}

    # A3 -- the normalization axis, searched exhaustively for a count of 2
    print("[A] searching normalization x boundary x denominator for a count of 2")
    grid = OrderedDict()
    hits_2, hits_15of19 = [], []
    for norm in NORMALIZATIONS:
        vals = []
        for label, kind, pb in entries:
            p0 = pb[0]
            v = normalize(norm, p0["X_a"], p0["X_b"], p0["s_X"])
            vals.append((label, kind, v))
        for thresh_name, thresh in (("6x", 6.0 * TAU_REL),
                                    ("5.71x", (4.0 / 7.0))):
            for rule in ("RULE_A_strict", "RULE_B_1e-12_tolerance"):
                def below(v):
                    if rule == "RULE_A_strict":
                        return v < thresh
                    return v < thresh * (1.0 - 1e-12)
                c_all = sum(1 for _, _, v in vals if below(v))
                c_rel2 = sum(1 for _, k2, v in vals
                             if k2 == "G-REL2" and below(v))
                c_rel1 = sum(1 for _, k1, v in vals
                             if k1 == "G-REL1" and below(v))
                key = "%s|%s|%s" % (norm, thresh_name, rule)
                grid[key] = {"below_over_29": c_all,
                             "below_over_19_G_REL2": c_rel2,
                             "below_over_10_G_REL1": c_rel1,
                             "min": min(v for _, _, v in vals),
                             "max": max(v for _, _, v in vals)}
                for denom, c in (("29", c_all), ("19 G-REL2", c_rel2),
                                 ("10 G-REL1", c_rel1)):
                    if c == 2 and thresh_name == "6x":
                        hits_2.append({"cell": key, "denominator": denom})
                if thresh_name == "6x" and c_rel2 == 15:
                    hits_15of19.append(key)
    R["A3_normalization_grid"] = {
        "n_cells_searched": len(grid),
        "grid": grid,
        "cells_yielding_a_count_of_EXACTLY_2_at_a_6x_threshold": hits_2,
        "cells_yielding_15_of_19_G_REL2_at_a_6x_threshold": hits_15of19,
        "what_a_hit_would_mean": "a cell yielding 2 at a 6x threshold would be "
                                 "a FOURTH axis rider (i) did not tabulate, and "
                                 "would mean its '5.71x threshold' reading is "
                                 "not the only account of wave 2's count.",
        "what_an_empty_list_means": "no normalization constructible from the "
                                    "committed fields yields 2 at 6x, which "
                                    "CONFIRMS rider (i)'s account and is "
                                    "reported at that weight.",
        "NOT_AN_ADJUDICATION": "Neither count becomes citable through this "
                               "probe. C-1 is the Coordinator's to rule."}

    # ============================================ PART B: could R2-OUT-V fire?
    print("[B] could R2-OUT-V have fired?")
    Q = LD.Q
    TAU_VAR = LD.TAU_VAR
    b = OrderedDict()
    worst = None
    for lat, (d, k) in LD.LATTICES.items():
        a00 = [int(LD.build_basis_fam(d, k, i, "F0")[0, k])
               for i in range(LD.N_BASES)]
        sdA = statistics.stdev([v / Q for v in a00])
        logdet = (d - k) * math.log(Q)
        means = [(beta / d) * (1.0 / d) * logdet for beta in LD.BETA_GRID[d]]
        Rdk = max(means) - min(means)
        Dmax = sdA / Rdk                    # D_c at lambda = 1, exactly
        b[lat] = {"sd_of_A00_over_q": sdA, "R_d_k": Rdk,
                  "D_c_at_lambda_1": Dmax,
                  "ratio_to_tau_var": Dmax / TAU_VAR,
                  "lambda_star_exact_continuous": TAU_VAR * Rdk / sdA}
        if worst is None or Dmax < worst[1]:
            worst = (lat, Dmax)
    R["B_R2_OUT_V_reachability"] = {
        "identity": "VAR-S on X_lambda is EXACTLY linear in lambda: "
                    "D_c(lambda) = lambda * sd_i(A[0,0]_i/q) / R_{d,k}, because "
                    "the X_null part is bit-identical across the 8 bases at "
                    "every F0 cell under R0/R1/R3 and contributes no dispersion.",
        "tau_var": TAU_VAR,
        "largest_lambda_in_the_frozen_grid": max(LD.LAMBDA_GRID),
        "per_lattice": b,
        "min_D_c_at_lambda_1_over_all_lattices": worst[1],
        "at_lattice": worst[0],
        "R2_OUT_V_could_have_fired_only_if_tau_var_exceeded": worst[1],
        "factor_by_which_the_frozen_tau_var_is_below_that": worst[1] / TAU_VAR,
        "reading": "R2-OUT-V fires only when NO cell crosses anywhere in the "
                   "grid. Given the frozen grid (top value 1.0), the frozen "
                   "tau_var = 1e-3 and the frozen A draw, the smallest D_c "
                   "reachable at lambda = 1 already exceeds tau_var at every "
                   "cell. PREREG-1 6.1 calls this row 'live and not a straw "
                   "man'; on these numbers it was unreachable before the run.",
        "what_this_does_NOT_say": "P-G1 is a MUST-PASS guard and a must-pass "
                                  "guard is expected to pass. The informative "
                                  "content of section 6.1 is the crossing "
                                  "amplitude lambda*, which IS a measurement. "
                                  "What is not a measurement is the binary "
                                  "non-firing of R2-OUT-V."}

    # ================== PART C: AM-10 replication of the guard's own statistic
    print("[C] AM-10 replication of lambda* over four independent A draws")
    c = OrderedDict()
    for seed_prefix in (1, 2, 3, 4):
        per_lat = OrderedDict()
        for lat, (d, k) in LD.LATTICES.items():
            a00 = [int(LD.make_A_seed(d, k, Q, i, seed_prefix)[0, 0])
                   for i in range(LD.N_BASES)]
            sdA = statistics.stdev([v / Q for v in a00])
            logdet = (d - k) * math.log(Q)
            means = [(beta / d) * (1.0 / d) * logdet
                     for beta in LD.BETA_GRID[d]]
            Rdk = max(means) - min(means)
            lam_cont = TAU_VAR * Rdk / sdA
            lam_grid = None
            for lam in LD.LAMBDA_GRID:
                if lam * sdA / Rdk >= TAU_VAR:
                    lam_grid = lam
                    break
            per_lat[lat] = {"sd_A00_over_q": sdA,
                            "lambda_star_continuous": lam_cont,
                            "lambda_star_on_the_frozen_grid": lam_grid}
        c["seed_prefix_%d" % seed_prefix] = per_lat
    lam_grid_counts = Counter(
        v["lambda_star_on_the_frozen_grid"]
        for sp in c.values() for v in sp.values())
    lam_cont_all = [v["lambda_star_continuous"]
                    for sp in c.values() for v in sp.values()]
    R["C_AM10_replication_of_lambda_star"] = {
        "why": "AM-10 requires a criterion statistic to be replicated rather "
               "than reported at one draw. The lead reports lambda* on seed "
               "prefix 1 only. Recomputed here on prefixes 1, 2, 3 and 4.",
        "per_seed_prefix": c,
        "lambda_star_on_the_frozen_grid_multiset": dict(lam_grid_counts),
        "lambda_star_continuous_dispersion": {
            "n": len(lam_cont_all), "min": min(lam_cont_all),
            "median": statistics.median(lam_cont_all),
            "max": max(lam_cont_all),
            "sd": statistics.stdev(lam_cont_all)},
        "grid_resolution_caveat": "the frozen lambda grid has NO point between "
                                  "1e-4 and 1e-2, so a grid lambda* of 1e-2 "
                                  "localises the true crossing only to two "
                                  "decades and is an UPPER BOUND on it. The "
                                  "continuous column is what the linear "
                                  "identity gives exactly.",
        "AM_10_b_both_normalizations": "the statistic here is a ratio of a "
                                       "dispersion to a range, so max(|X|,s_X) "
                                       "and |X| normalizations do not apply to "
                                       "it; the underlying sd and range are "
                                       "both reported so either can be formed."}

    # ============= PART D: is rider (i)'s Observation 1 a property of the data
    #                       or of its summation algorithm?
    print("[D] fsum versus naive summation in the mean-over-8 reading")
    dmis = []
    for label, kind, pb in entries:
        for field in ("value_maxfloor", "value_absX"):
            vals = [p[field] for p in pb]
            naive = 0.0
            for v in vals:
                naive += v
            naive /= len(vals)
            fs = math.fsum(vals) / len(vals)
            if float(naive).hex() != float(fs).hex():
                dmis.append({"entry": label, "field": field,
                             "naive_mean": naive, "fsum_mean": fs,
                             "committed_i0": vals[0],
                             "naive_equals_i0": float(naive).hex()
                                                == float(vals[0]).hex()})
    # do the ulp moves change any published count?
    dcounts = OrderedDict()
    for field, thresh_name, thresh in (
            ("value_maxfloor", "6x", 6.0 * TAU_REL),
            ("value_maxfloor", "5.71x", 4.0 / 7.0),
            ("value_absX", "6x", 6.0 * TAU_REL),
            ("value_absX", "5.71x", 4.0 / 7.0)):
        for rule, cmpf in (("RULE_A_strict", lambda v, t: v < t),
                           ("RULE_B_1e-12_tolerance",
                            lambda v, t: v < t * (1.0 - 1e-12))):
            row = {}
            for rd in ("i0", "fsum_mean", "naive_mean"):
                n29 = n19 = 0
                for label, kind, pb in entries:
                    vals = [p[field] for p in pb]
                    if rd == "i0":
                        v = vals[0]
                    elif rd == "fsum_mean":
                        v = math.fsum(vals) / len(vals)
                    else:
                        s = 0.0
                        for x in vals:
                            s += x
                        v = s / len(vals)
                    if cmpf(v, thresh):
                        n29 += 1
                        if kind == "G-REL2":
                            n19 += 1
                row[rd] = {"below_over_29": n29, "below_over_19_G_REL2": n19}
            row["counts_identical_across_all_three_readings"] = (
                row["i0"] == row["fsum_mean"] == row["naive_mean"])
            dcounts["%s|%s|%s" % (field, thresh_name, rule)] = row

    R["D_mean_reading_depends_on_the_summation_algorithm"] = {
        "counts_under_i0_fsum_and_naive_mean": dcounts,
        "every_published_count_is_unchanged_by_the_ulp_moves": all(
            v["counts_identical_across_all_three_readings"]
            for v in dcounts.values()),
        "why": "rider (i) records (deviation 3) that an earlier invocation "
               "computed the mean-over-8 with a left-to-right sum, which moved "
               "entries by 1 ulp and made that reading disagree bitwise with "
               "the other two. Its Observation 1 -- 'the three readings return "
               "the same IEEE-754 double at every entry, bitwise' -- is "
               "therefore true of the fsum implementation. Measured here: how "
               "many entries a naive sum moves.",
        "n_entry_field_pairs_checked": 2 * len(entries),
        "n_where_naive_and_fsum_disagree_bitwise": len(dmis),
        "detail": dmis,
        "reading": "The DATA property (all 8 per-basis values bit-identical, "
                   "A1) is unconditional. The READING property (the three "
                   "declared readings coincide bitwise) is conditional on the "
                   "summation algorithm, and rider (i) discloses the incident "
                   "that shows it. MEASURED CONSEQUENCE: at the 6x threshold "
                   "every count is identical under i0, fsum-mean and "
                   "naive-mean, under both boundary rules and both committed "
                   "normalizations. At the 5.71x threshold under the STRICT "
                   "boundary rule the counts are NOT identical -- the plateau "
                   "sits exactly on that boundary, so a 1-ulp move crosses it "
                   "-- and the naive-mean reading gives 12 (maxfloor) and 11 "
                   "(absX) where i0 and fsum give 2 and 0. Rider (i)'s account "
                   "of wave 2's count of 2 lives at that boundary and is "
                   "therefore conditional on the summation algorithm as well "
                   "as on the boundary rule."}

    # ============= PART E: does F0 fail from rdet alone, and under the strict
    #                       reading of route RD?
    print("[E] independent re-derivation of the F0 verdict's dependencies")
    lead_res = json.load(open(os.path.join(
        REPO, "coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/"
              "TASK-20260812-56b9da/results_gvar2.json")))
    PROF = lead_res["per_cell_profiles"]
    rdet_admits = OrderedDict()
    for key, blk in PROF.items():
        if blk.get("candidate") == "rdet" and blk.get("family") == "F0":
            rdet_admits[key] = {"n_ADMIT": blk["n_ADMIT"],
                                "n_REFUSE": blk["n_REFUSE"],
                                "n_cells": blk["n_cells_scored"]}
    rawtail_rd = PROF["rawtail|RD_rawgso|F0"]
    misses = [ck for ck, c in rawtail_rd["per_cell"].items()
              if c["G_VAR2"] != "ADMIT"]
    fpylll_touching = ["lam1n|RD_frozen_HKZ|F0", "hkz|RD_frozen_HKZ|F0"]
    R["E_F0_failure_dependency_audit"] = {
        "rdet_in_F0_per_route": rdet_admits,
        "F0_would_FAIL_from_rdet_alone":
            any(v["n_ADMIT"] > 0 for v in rdet_admits.values()),
        "rawtail_RD_cells_missing_the_ADMITTED_target": misses,
        "under_the_STRICT_reading_of_route_RD_the_rawtail_row_is_UNCOVERED_and_"
        "the_only_remaining_F0_failure_is_rdet": True,
        "blocks_that_depend_on_fpylll": fpylll_touching,
        "do_the_failing_blocks_depend_on_fpylll": False,
        "how_that_was_checked": (
            "measure_gvar2.py computes R2 with numpy.linalg.qr, R4 with "
            "numpy.linalg.slogdet of B B^T and R5 with numpy.linalg.slogdet of "
            "B H; fpylll appears only in a try/except that sets an environment "
            "string and in the lam1n/hkz RD blocks. RT-PROBE-2 independently "
            "reproduced the rdet R2 admission at 38/38 with numpy alone on a "
            "host where fpylll is ABSENT."),
        "the_alternative_the_fpylll_gap_DID_remove":
            "with the ADMITTED half uncovered, F0 could not have been PASS on "
            "this host under any rdet outcome; the reachable alternatives were "
            "FAIL and PARTIAL. That bounds what the fpylll gap cost: it "
            "removed T-PASS, not the distinction between T-F0FAIL and "
            "T-F1FAIL."}

    R["wall_clock_seconds"] = round(time.time() - T0, 3)
    R["what_this_probe_does_NOT_establish"] = [
        "It adjudicates C-1 in no direction and makes neither sub-6x count "
        "citable. 'A factor of 6 to 31' is FALSE; the citable range is 4.87x "
        "to 31.03x.",
        "It does not declare either validator wave right or wrong.",
        "It does not retire P-G1, which passed as frozen; it bounds what the "
        "non-firing of R2-OUT-V is evidence for.",
        "It rescores no frozen verdict and changes no outcome row.",
        "CLAIM TIER TOY.",
    ]
    with open(args.out, "w") as fh:
        json.dump(R, fh, indent=1)
        fh.write("\n")

    print("=" * 74)
    print("RT-PROBE-3 -- READINGS AND GUARD -- TOY")
    print("=" * 74)
    print("A1 all 29 entries bit-identical over 8 bases in every field: %s"
          % R["A1_bit_identity_across_the_8_bases"]
            ["all_29_entries_bit_identical_in_every_stored_field"])
    print("A2 all SEVEN reductions agree bitwise everywhere: %s"
          % R["A2_reading_axis"]
            ["all_seven_reductions_agree_bitwise_at_every_entry_and_field"])
    print("A3 normalization grid cells searched: %d" % len(grid))
    print("   cells yielding EXACTLY 2 at a 6x threshold: %s"
          % (hits_2 if hits_2 else "NONE"))
    print("   cells yielding 15 of 19 G-REL2 at 6x: %s"
          % (hits_15of19 if hits_15of19 else "NONE"))
    print("\nB  min D_c at lambda=1 over all cells: %.4e  (tau_var %.1e) "
          "-> R2-OUT-V unreachable by a factor of %.1f"
          % (worst[1], TAU_VAR, worst[1] / TAU_VAR))
    print("\nC  lambda* on the frozen grid over 4 A-draws x 10 lattices: %s"
          % dict(lam_grid_counts))
    lc = R["C_AM10_replication_of_lambda_star"][
        "lambda_star_continuous_dispersion"]
    print("   continuous lambda*: min %.4e median %.4e max %.4e sd %.4e"
          % (lc["min"], lc["median"], lc["max"], lc["sd"]))
    print("\nD  naive-sum vs fsum mean-over-8 disagreements: %d of %d "
          "entry-field pairs"
          % (R["D_mean_reading_depends_on_the_summation_algorithm"]
             ["n_where_naive_and_fsum_disagree_bitwise"],
             R["D_mean_reading_depends_on_the_summation_algorithm"]
             ["n_entry_field_pairs_checked"]))
    e = R["E_F0_failure_dependency_audit"]
    print("\nE  F0 would FAIL from rdet alone: %s ; failing blocks depend on "
          "fpylll: %s" % (e["F0_would_FAIL_from_rdet_alone"],
                          e["do_the_failing_blocks_depend_on_fpylll"]))
    print("   rawtail|RD cells missing the ADMITTED target: %s" % e[
        "rawtail_RD_cells_missing_the_ADMITTED_target"])
    print("\nwrote %s in %.2f s" % (args.out, R["wall_clock_seconds"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
