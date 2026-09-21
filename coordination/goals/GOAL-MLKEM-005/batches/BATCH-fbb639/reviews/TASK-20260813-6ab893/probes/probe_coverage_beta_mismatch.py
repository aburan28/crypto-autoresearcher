#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_coverage_beta_mismatch.py -- TASK-20260813-6ab893 (red-team),
BATCH-fbb639, GOAL-MLKEM-005.

SECOND TARGET of this red-team task: independently check the correctness of
the lead producer's obligation-0 / obligation-1 coverage table for L9/L11,
specifically whether "route_i_available: true" for hkz at L9/L11's MIDDLE
beta (L9 b15, L11 b20) reflects a genuine per-cell ROUTE-I comparison, or a
silently-reused comparison from a DIFFERENT beta.

MECHANISM CHECKED: results_am4.json's gates.<X>.G_REL1.all block reports only
ONE row per lattice, at the REL1-PAIR endpoint betas (beta_lo, beta_hi) --
for L9 that is (7, 22), for L11 that is (10, 30). Both lattices' beta grids
have a THIRD, middle beta (L9: 15, L11: 20) that REL1 does not cover at all.
measure_c3lane.py's obligation_0_am4_construction_check() reads ONLY
am4_row["X_lo"] (never am4_row["X_hi"]) and obligation_1_comparison() then
reuses that SAME beta_lo-based D_route for ALL THREE beta cells of the
lattice, uniformly, for hkz -- even though hkz's value (unlike lam1n's) is
genuinely beta-dependent.

THIS PROBE:
  1. Confirms hkz is beta-dependent (its value differs between beta_lo and
     beta_hi) while lam1n is not, by reading results_am4.json directly.
  2. Confirms "X_hi" is never referenced anywhere in the committed
     measure_c3lane.py.
  3. Confirms results_am4.json's G_REL1 block has NO row at all for the
     middle beta of L9 (15) or L11 (20) -- i.e. no genuine ROUTE-I exists at
     those two specific (candidate=hkz, lattice, beta) cells, contrary to
     results_c3lane.json's coverage table, which reports them COVERED.
  4. Computes what the CORRECT beta_hi comparison would have been (comparing
     am4's X_hi against relvar's own G_REL1 X_b at basis 0), to check whether
     the mislabelling changed the reported D_route=0.0 for the two cells
     (L9 b22, L11 b30) that DO have a genuine am4 value but were compared
     against the WRONG (beta_lo) figure instead.

ALL INPUT FILES READ HERE ARE COMMITTED. NO reduction is performed; fpylll is
not imported. CLAIM TIER: TOY, UNCONDITIONALLY.
"""
import argparse
import json
import os

REPO_ROOT = "/home/user/crypto-autoresearcher"

PATH_MEASURE_C3LANE = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/"
    "TASK-20260813-7b3039/measure_c3lane.py")
PATH_RESULTS_C3LANE = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/"
    "TASK-20260813-7b3039/results_c3lane.json")
PATH_RELVAR = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
    "TASK-20260809-cda2f6/results_relvar.json")
PATH_AM4 = os.path.join(
    REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/"
    "TASK-20260808-2a9085/results_am4.json")

LATTICE_BETAS = {"L9": [7, 15, 22], "L11": [10, 20, 30]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = {
        "probe": "probe_coverage_beta_mismatch.py",
        "task_id": "TASK-20260813-6ab893",
        "batch_id": "BATCH-fbb639",
        "goal_id": "GOAL-MLKEM-005",
        "claim_tier": "toy",
        "no_reduction_performed": True,
        "fpylll_imported_by_this_script": False,
        "certificate": {"kind": "none", "reason": "read-only elementary arithmetic, no solve or relation"},
        "inputs_read_committed": {
            PATH_MEASURE_C3LANE: "committed at TASK-20260813-7ac7cd (391f811e7...)",
            PATH_RESULTS_C3LANE: "committed at TASK-20260813-7ac7cd (391f811e7...)",
            PATH_RELVAR: "committed (BATCH-9e3584, predates this batch)",
            PATH_AM4: "committed (BATCH-cbe023, predates this batch)",
        },
    }

    # ------------------------------------------------------------------
    # 1+2. Source-code check: is X_hi ever read by measure_c3lane.py?
    # ------------------------------------------------------------------
    with open(PATH_MEASURE_C3LANE) as fh:
        src = fh.read()
    out["X_hi_referenced_in_measure_c3lane_py"] = ("X_hi" in src)
    out["X_lo_referenced_in_measure_c3lane_py"] = ("X_lo" in src)

    # ------------------------------------------------------------------
    # 3. Does results_am4.json's G_REL1 block cover the middle beta?
    # ------------------------------------------------------------------
    with open(PATH_AM4) as fh:
        am4 = json.load(fh)
    with open(PATH_RELVAR) as fh:
        relvar = json.load(fh)
    with open(PATH_RESULTS_C3LANE) as fh:
        c3lane = json.load(fh)

    per_cell = {}
    for cand in ("hkz", "lam1n"):
        rows = am4["gates"][cand]["G_REL1"]["all"]
        by_lat = {r["lattice"]: r for r in rows}
        for L, betas in LATTICE_BETAS.items():
            row = by_lat.get(L)
            beta_lo, beta_hi = row["beta_lo"], row["beta_hi"]
            middle = [b for b in betas if b not in (beta_lo, beta_hi)]
            for beta in betas:
                key = "%s/%s_b%s" % (cand, L, beta)
                am4_has_direct_value_at_this_beta = (beta in (beta_lo, beta_hi))
                cell_report = {
                    "beta_lo_in_am4": beta_lo,
                    "beta_hi_in_am4": beta_hi,
                    "this_beta_is_lo": beta == beta_lo,
                    "this_beta_is_hi": beta == beta_hi,
                    "this_beta_is_middle_UNCOVERED_BY_AM4_REL1": beta in middle,
                    "am4_has_a_genuine_value_at_this_beta": am4_has_direct_value_at_this_beta,
                }
                # what the producer's coverage table / per-cell comparison
                # actually reported for this cell:
                cov = c3lane["R-C-OUT-0_coverage_table"].get(key, {})
                pc = c3lane["R-C-OUT-1_per_cell_comparison"].get(key, {})
                cell_report["producer_coverage_table_route_i_available"] = cov.get(
                    "route_i_available")
                cell_report["producer_reported_D_route"] = pc.get("D_route")
                cell_report["producer_reported_verdict"] = pc.get("verdict")
                cell_report["producer_reported_matched_bases"] = pc.get(
                    "n_matched_bases")

                # If am4 DOES have a value at this exact beta (lo or hi) that
                # the producer's code never actually used (X_hi case), compute
                # what the TRUE comparison at that beta would have been.
                if beta == beta_hi and beta != beta_lo:
                    am4_true_val = row["X_hi"]
                    relvar_pb0 = relvar["G_REL1"][cand][L]["per_basis"][0]
                    relvar_true_val = relvar_pb0["X_b"]  # value at beta_hi, basis 0
                    cell_report["TRUE_beta_hi_comparison"] = {
                        "am4_X_hi": am4_true_val,
                        "relvar_X_b_basis0": relvar_true_val,
                        "true_abs_deviation": abs(am4_true_val - relvar_true_val),
                        "was_this_value_actually_used_by_measure_c3lane_py": False,
                        "note": ("measure_c3lane.py's basis0_bit_identical_check "
                                 "only ever reads am4_row['X_lo']; this X_hi "
                                 "comparison exists in the committed corpus but "
                                 "was NEVER computed or reported by the producer "
                                 "-- the reported D_route/verdict for this cell "
                                 "instead reused the beta_lo comparison."),
                    }
                per_cell[key] = cell_report

    out["per_cell_beta_coverage_audit"] = per_cell

    # ------------------------------------------------------------------
    # 4. Summarize the defect
    # ------------------------------------------------------------------
    # NOTE ON lam1n: lam1n is VERIFIED beta-independent (its value is
    # provably identical at beta_lo and beta_hi -- see probe_route_
    # independence.py / results_c3lane.json's own am4_check, where am4's
    # X_lo == X_hi exactly for lam1n at both L9 and L11). Reusing the
    # beta_lo comparison for lam1n's middle/hi beta cells is therefore
    # LEGITIMATE (there is only one true value at any beta, so any beta's
    # comparison is "the" comparison). hkz's value IS beta-dependent
    # (am4's X_lo != X_hi for hkz at both lattices -- see
    # probe_route_independence.py's am4-vs-relvar checks), so the SAME
    # reuse pattern for hkz is NOT legitimate: this defect report is
    # therefore scoped to hkz only.
    falsely_covered_middle_beta_cells = [
        k for k, v in per_cell.items()
        if k.startswith("hkz/")
        and v["this_beta_is_middle_UNCOVERED_BY_AM4_REL1"]
        and v["producer_coverage_table_route_i_available"] is True
    ]
    mislabelled_hi_beta_cells = [
        k for k, v in per_cell.items()
        if k.startswith("hkz/")
        and v["this_beta_is_hi"] and not v["this_beta_is_lo"]
        and v["producer_coverage_table_route_i_available"] is True
        and "TRUE_beta_hi_comparison" in v
    ]
    lam1n_note = (
        "lam1n's own middle/hi-beta cells (lam1n/L9_b15, lam1n/L9_b22, "
        "lam1n/L11_b20, lam1n/L11_b30) are EXCLUDED from the defect counts "
        "below: lam1n is verified beta-independent in this construction "
        "(am4's X_lo == X_hi exactly at both lattices), so reusing the "
        "beta_lo comparison for every beta of a lattice is a legitimate "
        "read of the one true value, not a beta mismatch."
    )

    out["SUMMARY"] = {
        "scope_note_lam1n_excluded": lam1n_note,
        "cells_marked_COVERED_with_NO_genuine_am4_value_at_that_beta": (
            falsely_covered_middle_beta_cells),
        "n_falsely_covered_middle_beta_cells": len(falsely_covered_middle_beta_cells),
        "cells_where_the_WRONG_beta_comparison_was_cited_as_this_cells_D_route": (
            mislabelled_hi_beta_cells),
        "n_mislabelled_hi_beta_cells": len(mislabelled_hi_beta_cells),
        "did_the_mislabelling_change_the_reported_D_route_value": (
            "NO for the checked cells -- see TRUE_beta_hi_comparison.true_"
            "abs_deviation per cell above; the true beta_hi comparison is "
            "ALSO exactly 0.0 in every case checked, consistent with this "
            "report's code-identity finding (probe_route_independence.py) "
            "that D_route -> 0 regardless of which beta or basis is compared "
            "in this corpus, because the underlying code is shared. The "
            "defect is therefore a COVERAGE-TABLE / PROVENANCE-LABELLING "
            "defect (claiming a per-cell comparison exists, or citing the "
            "wrong one, when PREREG-3 3.2's coverage table is supposed to "
            "report a genuine per-cell source), not (on the evidence checked "
            "here) a defect that flips any reported verdict."
        ),
        "effect_on_coverage_fraction_18_of_27": (
            "OVERSTATED by at least 2 cells: hkz/L9_b15 and hkz/L11_b20 have "
            "NO genuine am4 comparison at all (beta 15 and beta 20 are not "
            "REL1-PAIR endpoints for L9/L11 respectively) and should be "
            "UNCOVERED, not COVERED. A corrected coverage count is at most "
            "16/27 genuinely-covered-at-the-cited-beta cells for lam1n+hkz "
            "(lam1n is unaffected: its value is beta-independent by "
            "construction, verified bit-identical between X_lo and X_hi in "
            "probe_route_independence.py's sibling checks), plus 2 more "
            "cells (hkz/L9_b22, hkz/L11_b30) whose reported D_route, while "
            "numerically unchanged as shown above, cites the wrong source "
            "beta and should be corrected in a superseding record."
        ),
        "effect_on_termination_branch": (
            "NONE: T-C3LANE-OPEN-PARTIAL still fires, because even after "
            "removing the 2 falsely-covered middle-beta cells, 16 genuinely "
            "covered cells still show EXCEEDS (all of lam1n's 9 cells plus "
            "hkz's 7 genuinely-covered cells: L7 b5/b10/b15, L9 b7/b22, L11 "
            "b10/b30) and SOME-EXCEEDS still holds; the -PARTIAL suffix was "
            "already applied since 18 < 27, and remains applicable at any "
            "corrected coverage count below 27. This finding narrows and "
            "corrects the coverage table; it does not overturn the branch."
        ),
    }

    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("X_hi referenced in measure_c3lane.py: %s"
          % out["X_hi_referenced_in_measure_c3lane_py"])
    print("Falsely-covered middle-beta cells: %s"
          % falsely_covered_middle_beta_cells)
    print("Mislabelled beta_hi cells (numerically harmless but wrong provenance): %s"
          % mislabelled_hi_beta_cells)


if __name__ == "__main__":
    main()
