#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 3 -- TASK-20260813-968dc8

Purely mechanical re-derivation, WITHOUT importing measure_hkz_indep.py or
any producer module:

  (a) independently computes sha256 of results_relvar.json and compares
      against the value the producer recorded and against the value cited
      in the task card;
  (b) re-derives, from the raw route_p_values/route_ii_values arrays in
      results_hkz_indep.json, D_route'' (max abs deviation) and VERDICT''
      at every cell, and compares to the producer's own recorded values;
  (c) re-derives s_c^fib and n_bases_ground_truth directly from
      results_relvar.json's own G_REL1.hkz / G_VAR.per_candidate.hkz
      blocks (never from results_hkz_indep.json), and cross-checks against
      the producer's transcription;
  (d) re-derives the R_V_OUT_3 aggregate (COVERED/ALL_SURVIVE/SOME_ARTIFACT)
      and the R_V_OUT_4 termination branch under PREREG-5 2.6's frozen
      precedence, purely from the per-cell VERDICT'' values, and compares
      to the producer's recorded branch.
"""
import hashlib
import json

REPO_ROOT = "/home/user/crypto-autoresearcher"
RESULTS_RELVAR_PATH = (REPO_ROOT + "/coordination/goals/GOAL-MLKEM-005/batches/"
                        "BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json")
RESULTS_HKZ_INDEP_PATH = (REPO_ROOT + "/coordination/goals/GOAL-MLKEM-005/batches/"
                           "BATCH-a6fab5/tasks/TASK-20260813-c0ec71/results_hkz_indep.json")

CELLS = {
    "hkz/L7_b5":   ("L7", 5),
    "hkz/L7_b15":  ("L7", 15),
    "hkz/L9_b7":   ("L9", 7),
    "hkz/L9_b22":  ("L9", 22),
    "hkz/L11_b10": ("L11", 10),
    "hkz/L11_b30": ("L11", 30),
}


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


if __name__ == "__main__":
    print("(a) results_relvar.json sha256 independently computed:")
    my_sha = sha256_file(RESULTS_RELVAR_PATH)
    print("    ", my_sha)
    print("    matches task-card-cited "
          "c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d:",
          my_sha == "c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d")

    with open(RESULTS_RELVAR_PATH) as fh:
        relvar = json.load(fh)
    with open(RESULTS_HKZ_INDEP_PATH) as fh:
        producer = json.load(fh)

    print("\n    matches producer's own recorded results_relvar_sha256:",
          my_sha == producer["results_relvar_sha256"])

    g_rel1_hkz = relvar["G_REL1"]["hkz"]
    g_var_hkz = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]

    print("\n(b)+(c) per-cell mechanical re-derivation")
    all_d_route_match = True
    all_verdict_match = True
    all_sfib_match = True
    all_relvar_source_match = True
    per_cell_verdicts = {}
    for cell, (lat, beta) in CELLS.items():
        entry = g_rel1_hkz[lat]
        field = "X_a" if beta == entry["beta_lo"] else "X_b"
        route_p_from_relvar = [row[field] for row in entry["per_basis"]]
        n_bases = len(entry["per_basis"])
        s_c_fib_mine = g_var_hkz["%s_b%d" % (lat, beta)]["float_sd"]

        pc = producer["R_V_OUT_2_per_cell"][cell]
        d_route_mine = max(abs(a - b) for a, b in
                            zip(pc["route_p_values"], pc["route_ii_values"]))
        verdict_mine = "EXCEEDS" if s_c_fib_mine > d_route_mine else "DOES NOT EXCEED"
        per_cell_verdicts[cell] = verdict_mine

        relvar_source_ok = (route_p_from_relvar == pc["route_p_values"])
        d_ok = (d_route_mine == pc["D_route_pp"])
        v_ok = (verdict_mine == pc["VERDICT_pp"])
        s_ok = (s_c_fib_mine == pc["s_c_fib"])
        all_d_route_match &= d_ok
        all_verdict_match &= v_ok
        all_sfib_match &= s_ok
        all_relvar_source_match &= relvar_source_ok

        print("  %-14s n_bases_ground_truth=%d(mine)/%d(prod)  "
              "route_p==relvar_direct_read:%s  D_route''match:%s  "
              "s_c^fib match:%s  VERDICT''match:%s"
              % (cell, n_bases, pc["n_bases_ground_truth"], relvar_source_ok,
                 d_ok, s_ok, v_ok))

    print("\nALL D_route'' recomputations match producer:", all_d_route_match)
    print("ALL VERDICT'' recomputations match producer:", all_verdict_match)
    print("ALL s_c^fib direct-from-results_relvar.json match producer's "
          "transcription:", all_sfib_match)
    print("ALL route_p_values match direct read of results_relvar.json "
          "G_REL1.hkz (never results_l7l8.json/results_am4.json):",
          all_relvar_source_match)

    print("\n(d) aggregate + termination branch, purely from per-cell VERDICT''")
    covered = list(per_cell_verdicts.keys())  # all 6 present/ok in producer's file
    exceeds = [c for c, v in per_cell_verdicts.items() if v == "EXCEEDS"]
    not_exceeds = [c for c, v in per_cell_verdicts.items() if v == "DOES NOT EXCEED"]
    all_survive = len(covered) > 0 and len(not_exceeds) == 0
    some_artifact = len(not_exceeds) > 0
    if len(covered) == 0:
        branch = "T-HKZINDEP-NODATA"
    elif some_artifact:
        branch = "T-HKZINDEP-ARTIFACT"
    else:
        branch = "T-HKZINDEP-CONFIRMED"
    partial = len(covered) < 6 and branch != "T-HKZINDEP-NODATA"
    branch_disp = branch + "-PARTIAL" if partial else branch

    print("  COVERED=%d/6  ALL_SURVIVE=%s  SOME_ARTIFACT=%s" %
          (len(covered), all_survive, some_artifact))
    print("  termination branch (mine):", branch_disp)
    print("  termination branch (producer's R_V_OUT_4_termination.branch):",
          producer["R_V_OUT_4_termination"]["branch"])
    print("  MATCH:", branch_disp == producer["R_V_OUT_4_termination"]["branch"])
    print("  no -PARTIAL warranted (all 6 covered):", not partial)
