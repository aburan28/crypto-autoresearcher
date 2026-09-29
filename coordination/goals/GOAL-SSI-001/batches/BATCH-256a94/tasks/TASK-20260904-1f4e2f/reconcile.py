#!/usr/bin/env python3
"""TASK-20260904-1f4e2f / BATCH-256a94 / GOAL-SSI-001 -- anchor reconciliation.

CITATION PROHIBITION (restated verbatim, not lifted by this file):

    The `P=512` crossover value and its `w=2^80` sign are **NOT
    citation-eligible**. This task does not lift that prohibition. Only a
    committed Coordinator decision on independently reviewed evidence can lift
    it.

Standalone: Python standard library only (numpy is permitted but not needed and
is not imported).  No network.  No SageMath, no g6k.  NO IMPORT FROM
experiments/ -- the frozen implementation is READ AS TEXT ONLY, never executed
and never imported.  Every committed input is opened read-only.  The single
output file is written inside this task directory.

All quantities are base-2 logarithms.  Nothing here measures anything: it is
arithmetic on already-committed literals.

Laws under comparison, all in log2 units and all with overhead_bits =
c*sqrt(log2p) added:

  L_pred  (predecessor law, as serialized in
           runs/RUN-WESOVOW-001/raw-result.json:13 "T_full / sqrt(min(w, M))"
           and as executed at cost_model.py:270 of blob 96e77f9f5 / commit
           8c5188b90):
               log2T(w) = log2T_full - 0.5*min(log2w, log2M) + overhead_bits

  L_curr  (law carried by the current committed cost_model.py:239 serialized
           text "T(w) = T_full * sqrt(M / min(w, M))" and by its executable
           expression at cost_model.py:273-275, and serialized identically in
           runs/RUN-WESOVOW-201692-001/raw-result.json:13):
               log2T(w) = log2T_full + 0.5*max(0, log2M - log2w) + overhead_bits

  L_eb0a7e (independently derived in
           coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/
           TASK-20260824-dd5b5c/corrected_charging.py, function corrected_law):
               log2T(w) = log2T_full + overhead_bits + 0.5*max(0, log2M - log2w)

L_curr and L_eb0a7e are written here as SEPARATE functions on purpose, so that
the equivalence claim in law_equivalence.md is tested numerically rather than
assumed by sharing one implementation.
"""

import argparse
import json
import math
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", "..", "..", "..", ".."))

P_RUN_PRED = "experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json"
P_RUN_SUCC = "experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/raw-result.json"
P_COST_MODEL = "experiments/EXP-WESOVOW-001/cost_model.py"
P_EB0A7E = ("coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/"
            "TASK-20260824-dd5b5c/recomputed_table.json")
OUT = "anchor_reconciliation.json"

FIELD_SIZES = (256, 384, 512, 576, 768)
MEMORY_BUDGETS = (30, 40, 50, 60, 70, 80)
OVERHEAD_C = (0.0, 0.5, 1.0, 2.0)

REPRO_TOL = 1e-9        # RG-1 / RG-2, fixed by the task card
EQ_TOL = 1e-12          # law-equality and control tolerance

PROHIBITION = (
    "The `P=512` crossover value and its `w=2^80` sign are **NOT "
    "citation-eligible**. This task does not lift that prohibition. Only a "
    "committed Coordinator decision on independently reviewed evidence can "
    "lift it."
)


def rp(rel):
    return os.path.join(REPO, rel)


def load_json(rel):
    with open(rp(rel), "r") as f:
        return json.load(f)


# ------------------------------------------------------------------ the laws
def law_pred(log2T_full, log2M, log2w, c, log2p):
    return log2T_full - 0.5 * min(log2w, log2M) + c * math.sqrt(log2p)


def law_curr(log2T_full, log2M, log2w, c, log2p):
    return log2T_full + 0.5 * max(0.0, log2M - log2w) + c * math.sqrt(log2p)


def law_eb0a7e(log2T_full, log2M, log2w, c, log2p):
    overhead_bits = c * math.sqrt(log2p)
    memory_penalty = 0.5 * max(0.0, log2M - log2w)
    return log2T_full + overhead_bits + memory_penalty


def crossover_curr(log2T_full, log2M, log2p, c):
    """cost_model.py:288 / protocol amendment TASK-20260809-ef3e58 crossover."""
    return log2M + 2.0 * (log2T_full + c * math.sqrt(log2p) - log2p / 2.0)


# ---------------------------------------------------------------- the anchors
def parse_paper_pairs_from_source():
    """Read the PAPER_PAIRS literals as TEXT from cost_model.py:60-65.

    Deliberately a text parse and not an import: experiments/ must not be
    imported, and the literals must trace to a file:line rather than to a
    number retyped here.
    """
    with open(rp(P_COST_MODEL), "r") as f:
        lines = f.readlines()
    pairs, prov = {}, {}
    pat = re.compile(r"^\s*(\d+):\s*\(([-\d.]+),\s*([-\d.]+)\),")
    inblock = False
    for i, line in enumerate(lines, start=1):
        if line.startswith("PAPER_PAIRS"):
            inblock = True
            continue
        if inblock:
            if line.strip().startswith("}"):
                break
            m = pat.match(line)
            if m:
                p = int(m.group(1))
                pairs[p] = (float(m.group(2)), float(m.group(3)))
                prov[p] = f"{P_COST_MODEL}:{i}"
    missing = [p for p in FIELD_SIZES if p not in pairs]
    if missing:
        raise ValueError(f"PAPER_PAIRS parse failed for {missing}")
    return pairs, prov


def fitted_opt_from(raw, path):
    out, prov = {}, {}
    for p in FIELD_SIZES:
        o = raw["per_field"][f"log2p={p}"]["optimal"]
        out[p] = (float(o["log2T"]), float(o["log2M"]))
        prov[p] = f"{path}:per_field[log2p={p}].optimal.log2T,.log2M"
    return out, prov


# ------------------------------------------------------------- RG-1 and RG-2
def reproduction_gate(raw, anchor, law, law_name, run_path):
    """Recompute every committed vOW cell of a run under the law it serializes."""
    checked, mism, maxd = 0, [], 0.0
    for p in FIELD_SIZES:
        f = raw["per_field"][f"log2p={p}"]
        Tf, M = anchor[p]
        for lw in MEMORY_BUDGETS:
            row = f["van_oorschot_wiener"].get(f"w=2^{lw}")
            if row is None:
                mism.append({"log2p": p, "log2w": lw, "reason": "missing budget row"})
                continue
            for c in OVERHEAD_C:
                cell = row.get(f"c={c}")
                if cell is None or "log2T_w" not in cell:
                    mism.append({"log2p": p, "log2w": lw, "overhead_c": c,
                                 "reason": "missing cell"})
                    continue
                committed = float(cell["log2T_w"])
                recomputed = law(Tf, M, lw, c, p)
                d = abs(committed - recomputed)
                maxd = max(maxd, d)
                checked += 1
                if d > REPRO_TOL:
                    mism.append({"log2p": p, "log2w": lw, "overhead_c": c,
                                 "committed": committed, "recomputed": recomputed,
                                 "abs_diff_bits": d})
    expected = len(FIELD_SIZES) * len(MEMORY_BUDGETS) * len(OVERHEAD_C)
    status = "PASS" if (checked == expected and not mism) else "FAIL"
    return {
        "status": status,
        "run": run_path,
        "law_applied": law_name,
        "cells_expected": expected,
        "cells_checked": checked,
        "tolerance_bits": REPRO_TOL,
        "max_abs_diff_bits": maxd,
        "mismatch_count": len(mism),
        "mismatches": mism,
        "failure_condition": (
            "FAIL if any of the 120 committed van_oorschot_wiener cells is "
            "absent, or if any recomputed value differs from the committed "
            f"log2T_w by more than {REPRO_TOL} bits."),
    }


# ------------------------------------------------------------------- RG-3
def rg3_null_discrimination(anchors):
    """Does the procedure REPORT a difference where one exists?

    Also carries the deliberately non-discriminating synthetic object
    (log2M = 0), on which no difference exists and the procedure must report
    exactly that rather than a difference.
    """
    rows, discriminating = [], True
    for aname, values in anchors.items():
        for p in FIELD_SIZES:
            Tf, M = values[p]
            for lw in MEMORY_BUDGETS:
                for c in OVERHEAD_C:
                    a = law_pred(Tf, M, lw, c, p)
                    b = law_curr(Tf, M, lw, c, p)
                    d = b - a
                    ok = abs(d) > EQ_TOL
                    discriminating &= ok
                    rows.append({"anchor": aname, "log2p": p, "log2w": lw,
                                 "overhead_c": c,
                                 "log2T_w_predecessor_law": a,
                                 "log2T_w_current_law": b,
                                 "current_minus_predecessor_bits": d,
                                 "reported_as_different": ok})
    # KNOWN-FALSE object: log2M = 0 collapses both laws to log2T_full.
    null_obj = []
    for p in FIELD_SIZES:
        Tf, M = 100.0, 0.0
        for lw in MEMORY_BUDGETS:
            a = law_pred(Tf, M, lw, 0.0, p)
            b = law_curr(Tf, M, lw, 0.0, p)
            null_obj.append({"anchor": "SYNTHETIC_log2M_equals_0",
                             "log2p": p, "log2w": lw, "overhead_c": 0.0,
                             "log2T_w_predecessor_law": a,
                             "log2T_w_current_law": b,
                             "current_minus_predecessor_bits": b - a,
                             "reported_as_different": abs(b - a) > EQ_TOL})
    synth_all_indistinguishable = all(not r["reported_as_different"] for r in null_obj)
    return {
        "status": "PASS" if (discriminating and synth_all_indistinguishable) else "FAIL",
        "real_anchor_rows": len(rows),
        "all_real_rows_discriminate": discriminating,
        "min_abs_separation_bits": min(abs(r["current_minus_predecessor_bits"])
                                       for r in rows),
        "synthetic_log2M_0_reports_no_difference": synth_all_indistinguishable,
        "rows": rows,
        "synthetic_null_object_rows": null_obj,
        "failure_condition": (
            "FAIL if any real-anchor (p, log2w, c) cell shows |current - "
            f"predecessor| <= {EQ_TOL} bits (the procedure would then be blind "
            "to a difference that exists), OR if the synthetic log2M=0 object "
            "is reported as showing a difference (the procedure would then "
            "manufacture one that does not exist)."),
    }


# ------------------------------------------------------------------- RG-4
def rg4_cap_and_monotonicity(anchors):
    """Cap identity at w=M and monotonicity in w, run separately per anchor.

    DISCLOSURE, carried in the output: for L_curr the cap identity at w=M is
    ALGEBRAICALLY ENTAILED, because max(0, log2M - log2w) = 0 identically at
    log2w = log2M. Its pass is therefore a restatement of the law, not
    independent confirmation of it. The part of RG-4 that is NOT entailed is
    the predecessor-law arm: L_pred at w=M gives log2T_full - 0.5*log2M, and
    the control must and does report that as a cap VIOLATION.
    """
    per_anchor = {}
    overall = True
    for aname, values in anchors.items():
        cap_rows, mono_rows = [], []
        cap_ok, mono_ok, pred_violates = True, True, True
        for p in FIELD_SIZES:
            Tf, M = values[p]
            for c in OVERHEAD_C:
                ov = c * math.sqrt(p)
                at_M = law_curr(Tf, M, M, c, p)
                above_M = law_curr(Tf, M, M + 1.0, c, p)
                pred_at_M = law_pred(Tf, M, M, c, p)
                d_at_M = at_M - (Tf + ov)
                d_above = above_M - (Tf + ov)
                d_pred = pred_at_M - (Tf + ov)
                cap_ok &= abs(d_at_M) <= EQ_TOL and abs(d_above) <= EQ_TOL
                pred_violates &= abs(d_pred) > EQ_TOL
                cap_rows.append({
                    "anchor": aname, "log2p": p, "overhead_c": c,
                    "log2M": M, "log2T_full": Tf, "overhead_bits": ov,
                    "current_law_at_w_eq_M_minus_Tfull_overhead_bits": d_at_M,
                    "current_law_at_w_eq_M_plus_1_minus_Tfull_overhead_bits": d_above,
                    "predecessor_law_at_w_eq_M_minus_Tfull_overhead_bits": d_pred,
                    "predecessor_law_violates_cap": abs(d_pred) > EQ_TOL,
                })
                grid = list(MEMORY_BUDGETS) + [M, M + 1.0]
                vals = [law_curr(Tf, M, lw, c, p) for lw in grid]
                nonincreasing = all(vals[i + 1] <= vals[i] + EQ_TOL
                                    for i in range(len(vals) - 1))
                mono_ok &= nonincreasing
                mono_rows.append({"anchor": aname, "log2p": p, "overhead_c": c,
                                  "log2w_sequence": grid,
                                  "log2T_w_sequence": vals,
                                  "non_increasing": nonincreasing})
        status = "PASS" if (cap_ok and mono_ok and pred_violates) else "FAIL"
        overall &= status == "PASS"
        per_anchor[aname] = {
            "status": status,
            "current_law_cap_identity_holds": cap_ok,
            "current_law_non_increasing_in_w": mono_ok,
            "predecessor_law_violates_cap_everywhere": pred_violates,
            "cap_rows": cap_rows,
            "monotonicity_rows": mono_rows,
        }
    return {
        "status": "PASS" if overall else "FAIL",
        "per_anchor": per_anchor,
        "entailment_disclosure": (
            "The cap identity for the current law is ALGEBRAICALLY BUILT INTO "
            "the law under test: log2T(w) = log2T_full + 0.5*max(0, log2M - "
            "log2w) + overhead_bits is equal to log2T_full + overhead_bits at "
            "log2w = log2M by the identity max(0, 0) = 0, for every anchor and "
            "every c. Its pass is a restatement of the law, NOT independent "
            "confirmation, and is reported as such. This repeats the caveat "
            "recorded by the BATCH-eb0a7e Validator "
            "(coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/"
            "TASK-20260824-5b150a/validation_report.md:161-163) and is "
            "disclosed rather than presented as a result. The non-entailed "
            "arms of RG-4 are (a) the predecessor-law cap check, which must "
            "and does report a violation, and (b) monotonicity across the "
            "memory grid, which is a property of the whole grid rather than "
            "of the single cap point."),
        "failure_condition": (
            "FAIL if the current law departs from log2T_full + overhead_bits "
            "at log2w = log2M or log2M + 1 for any anchor/field/c; or if "
            "log2T(w) increases anywhere along the sequence log2w = 30, 40, "
            "50, 60, 70, 80, log2M, log2M+1; or if the predecessor law is NOT "
            "flagged as violating the cap at w = M."),
    }


# --------------------------------------------- proves-too-much known-false set
def proves_too_much(anchors, raw_pred, fitted):
    """Three objects whose named conclusion is KNOWN FALSE.

    The procedure must report the negative outcome on each; a pass on any of
    them would mean the procedure proves too much.
    """
    # Object 1: the predecessor law satisfies C4 at w = M -- KNOWN FALSE.
    o1 = []
    for p in FIELD_SIZES:
        Tf, M = fitted[p]
        o1.append({"log2p": p,
                   "predecessor_law_at_w_eq_M": law_pred(Tf, M, M, 0.0, p),
                   "log2T_full": Tf,
                   "deficit_bits": law_pred(Tf, M, M, 0.0, p) - Tf,
                   "satisfies_C4": abs(law_pred(Tf, M, M, 0.0, p) - Tf) <= EQ_TOL})
    o1_ok = all(not r["satisfies_C4"] for r in o1)

    # Object 2: synthetic anchor log2M = 0, on which the two laws coincide.
    o2 = []
    for lw in MEMORY_BUDGETS:
        a = law_pred(100.0, 0.0, lw, 0.0, 256)
        b = law_curr(100.0, 0.0, lw, 0.0, 256)
        o2.append({"log2w": lw, "predecessor": a, "current": b,
                   "distinguishable": abs(b - a) > EQ_TOL})
    o2_ok = all(not r["distinguishable"] for r in o2)

    # Object 3: predecessor run's committed vOW rows checked against the
    # CURRENT law -- KNOWN FALSE that they agree.
    g = reproduction_gate(raw_pred, fitted, law_curr, "L_curr", P_RUN_PRED)
    o3_ok = g["status"] == "FAIL"

    return {
        "status": "PASS" if (o1_ok and o2_ok and o3_ok) else "FAIL",
        "meaning_of_pass": (
            "PASS here means the procedure REPORTED THE NEGATIVE OUTCOME on "
            "all three known-false objects. A FAIL would mean the procedure "
            "proves too much and its agreements elsewhere carry no "
            "information."),
        "object_1_predecessor_law_satisfies_C4_at_w_eq_M": {
            "conclusion_under_test_is_known_false": True,
            "procedure_reported_cap_violation": o1_ok, "rows": o1},
        "object_2_synthetic_log2M_0_is_discriminable": {
            "conclusion_under_test_is_known_false": True,
            "procedure_reported_no_discrimination": o2_ok, "rows": o2},
        "object_3_predecessor_rows_agree_with_current_law": {
            "conclusion_under_test_is_known_false": True,
            "procedure_reported_disagreement": o3_ok,
            "max_abs_diff_bits": g["max_abs_diff_bits"],
            "mismatch_count": g["mismatch_count"]},
    }


# ----------------------------------------------------------------- main table
def build_rows(anchors, anchor_prov, raw_succ, eb_rows):
    rows = []
    eb_index = {}
    for r in eb_rows:
        eb_index[(r["anchor"], r["field_size_log2p"], r["log2w"],
                  float(r["overhead_c"]))] = r
    for aname in ("fitted_opt", "PAPER_PAIRS"):
        values = anchors[aname]
        for p in FIELD_SIZES:
            Tf, M = values[p]
            for lw in MEMORY_BUDGETS:
                for c in OVERHEAD_C:
                    ov = c * math.sqrt(p)
                    v_curr = law_curr(Tf, M, lw, c, p)
                    v_eb = law_eb0a7e(Tf, M, lw, c, p)
                    v_pred = law_pred(Tf, M, lw, c, p)

                    # Comparison against the successor run, only where the
                    # grids actually overlap. The successor run's vOW cells
                    # are anchored on its OWN per_field optimal values, which
                    # are the fitted_opt anchor; PAPER_PAIRS is not an anchor
                    # of any committed run cell, so there is no overlap there.
                    run_val, run_dev, overlap = None, None, False
                    if aname == "fitted_opt":
                        cell = (raw_succ["per_field"][f"log2p={p}"]
                                ["van_oorschot_wiener"][f"w=2^{lw}"][f"c={c}"])
                        run_val = float(cell["log2T_w"])
                        run_dev = v_curr - run_val
                        overlap = True

                    eb_rec = eb_index.get((aname, p, lw, c))
                    eb_val = (float(eb_rec["log2T_w_corrected"])
                              if eb_rec is not None else None)
                    eb_dev_vs_run = (None if (eb_val is None or run_val is None)
                                     else eb_val - run_val)

                    rows.append({
                        "anchor": aname,
                        "anchor_source_time_and_memory": anchor_prov[aname][p],
                        "field_size_log2p": p,
                        "log2w": lw,
                        "overhead_c": c,
                        "overhead_bits": ov,
                        "log2T_full_anchor": Tf,
                        "log2M_anchor": M,
                        "log2T_DG": p / 2.0,
                        "log2T_w_current_law": v_curr,
                        "log2T_w_eb0a7e_law": v_eb,
                        "current_minus_eb0a7e_law_bits": v_curr - v_eb,
                        "log2T_w_predecessor_law": v_pred,
                        "eb0a7e_recomputed_table_value": eb_val,
                        "eb0a7e_table_source": (
                            P_EB0A7E + ":rows[]" if eb_val is not None else None),
                        "overlaps_RUN_WESOVOW_201692_001": overlap,
                        "RUN_WESOVOW_201692_001_log2T_w": run_val,
                        "RUN_WESOVOW_201692_001_source": (
                            f"{P_RUN_SUCC}:per_field[log2p={p}]."
                            f"van_oorschot_wiener[w=2^{lw}][c={c}].log2T_w"
                            if overlap else None),
                        "recomputed_minus_run_bits": run_dev,
                        "eb0a7e_table_minus_run_bits": eb_dev_vs_run,
                        "log2w_star_current_law": crossover_curr(Tf, M, p, c),
                        "log2speedup_vs_DG_current_law": p / 2.0 - v_curr,
                        "citation_prohibited": (p == 512),
                        "citation_prohibition_note": (
                            "NOT CITATION-ELIGIBLE. This row is at log2p = 512; "
                            "its log2w_star_current_law value and the sign of "
                            "its log2speedup_vs_DG_current_law at log2w = 80 "
                            "fall under the standing prohibition restated in "
                            "citation_prohibition_verbatim. The row is present "
                            "only because the frozen grid must be covered in "
                            "full; it may not be quoted, paraphrased, rounded, "
                            "summarised by sign, or used as an intermediate "
                            "step in any further claim."
                            if p == 512 else None),
                    })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), OUT))
    args = ap.parse_args()

    raw_pred = load_json(P_RUN_PRED)
    raw_succ = load_json(P_RUN_SUCC)
    eb = load_json(P_EB0A7E)

    # Serialized law strings, read as data from the committed artifacts.
    law_pred_serialized = raw_pred["model"]["formulas"]["T_w_vOW"]
    law_succ_serialized = raw_succ["model"]["formulas"]["T_w_vOW"]

    fitted, fitted_prov = fitted_opt_from(raw_pred, P_RUN_PRED)
    fitted_succ, _ = fitted_opt_from(raw_succ, P_RUN_SUCC)
    paper, paper_prov = parse_paper_pairs_from_source()

    anchors = {"fitted_opt": fitted, "PAPER_PAIRS": paper}
    anchor_prov = {"fitted_opt": fitted_prov, "PAPER_PAIRS": paper_prov}

    rg1 = reproduction_gate(raw_pred, fitted, law_pred, "L_pred", P_RUN_PRED)
    rg2 = reproduction_gate(raw_succ, fitted_succ, law_curr, "L_curr", P_RUN_SUCC)
    rg3 = rg3_null_discrimination(anchors)
    rg4 = rg4_cap_and_monotonicity(anchors)
    ptm = proves_too_much(anchors, raw_pred, fitted)

    rows = build_rows(anchors, anchor_prov, raw_succ, eb["rows"])

    per_anchor_summary = {}
    for aname in ("fitted_opt", "PAPER_PAIRS"):
        sub = [r for r in rows if r["anchor"] == aname]
        law_dev = max(abs(r["current_minus_eb0a7e_law_bits"]) for r in sub)
        eb_dev = [abs(r["log2T_w_current_law"] - r["eb0a7e_recomputed_table_value"])
                  for r in sub if r["eb0a7e_recomputed_table_value"] is not None]
        run_dev = [abs(r["recomputed_minus_run_bits"]) for r in sub
                   if r["recomputed_minus_run_bits"] is not None]
        per_anchor_summary[aname] = {
            "row_count": len(sub),
            "max_abs_deviation_current_law_vs_eb0a7e_law_bits": law_dev,
            "max_abs_deviation_vs_eb0a7e_recomputed_table_bits":
                (max(eb_dev) if eb_dev else None),
            "eb0a7e_table_rows_matched": len(eb_dev),
            "rows_overlapping_RUN_WESOVOW_201692_001": len(run_dev),
            "max_abs_deviation_vs_RUN_WESOVOW_201692_001_bits":
                (max(run_dev) if run_dev else None),
            "overlap_note": (
                "The successor run's committed vOW cells are anchored on its "
                "own per_field optimal values. Those are numerically identical "
                "to the predecessor run's per_field optimal values (checked "
                "below), i.e. to the fitted_opt anchor. PAPER_PAIRS is not the "
                "anchor of any committed run cell, so no committed run value "
                "exists to compare a PAPER_PAIRS row against; that is a stated "
                "ABSENCE OF OVERLAP, not agreement and not disagreement."),
        }

    optimal_identical = all(fitted[p] == fitted_succ[p] for p in FIELD_SIZES)

    # Anchor divergence, localized: same formula, different (T_full, M) inputs.
    anchor_divergence = []
    for p in FIELD_SIZES:
        tf_f, m_f = fitted[p]
        tf_p, m_p = paper[p]
        anchor_divergence.append({
            "field_size_log2p": p,
            "fitted_opt_log2T_full": tf_f, "PAPER_PAIRS_log2T_full": tf_p,
            "log2T_full_difference_bits": tf_f - tf_p,
            "fitted_opt_log2M": m_f, "PAPER_PAIRS_log2M": m_p,
            "log2M_difference_bits": m_f - m_p,
            "max_abs_log2T_w_difference_bits_over_budgets_and_c": max(
                abs(law_curr(tf_f, m_f, lw, c, p) - law_curr(tf_p, m_p, lw, c, p))
                for lw in MEMORY_BUDGETS for c in OVERHEAD_C),
        })

    out = {
        "schema": "crypto.autoresearch.anchor_reconciliation.v1",
        "task_id": "TASK-20260904-1f4e2f",
        "batch_id": "BATCH-256a94",
        "goal_id": "GOAL-SSI-001",
        "experiment_id": "EXP-WESOVOW-001",
        "citation_prohibition_verbatim": PROHIBITION,
        "claim_boundary": (
            "Arithmetic on already-committed literals and code reading. No "
            "measurement, no attack, no certificate, no security, "
            "standardized-parameter, exponent, or asymptotic-complexity claim "
            "in any direction. No hypothesis, experiment, or goal status is "
            "changed by this file."),
        "units": "all quantities are base-2 logarithms (log2)",
        "inputs": {
            "predecessor_run_raw": P_RUN_PRED,
            "successor_run_raw": P_RUN_SUCC,
            "frozen_implementation_read_as_text_only": P_COST_MODEL,
            "eb0a7e_recomputed_table": P_EB0A7E,
        },
        "serialized_laws_read_from_committed_artifacts": {
            f"{P_RUN_PRED}:13": law_pred_serialized,
            f"{P_RUN_SUCC}:13": law_succ_serialized,
            f"{P_COST_MODEL}:239": "T(w) = T_full * sqrt(M / min(w, M))",
        },
        "anchors": {
            "fitted_opt": {p: {"log2T_full": fitted[p][0], "log2M": fitted[p][1],
                               "source": fitted_prov[p]} for p in FIELD_SIZES},
            "PAPER_PAIRS": {p: {"log2T_full": paper[p][0], "log2M": paper[p][1],
                                "source": paper_prov[p]} for p in FIELD_SIZES},
        },
        "predecessor_and_successor_optimal_anchors_identical": optimal_identical,
        "grid": {"field_sizes_log2p": list(FIELD_SIZES),
                 "memory_budgets_log2w": list(MEMORY_BUDGETS),
                 "overhead_c": list(OVERHEAD_C),
                 "rows_per_anchor": len(FIELD_SIZES) * len(MEMORY_BUDGETS) * len(OVERHEAD_C)},
        "controls": {"RG-1": rg1, "RG-2": rg2, "RG-3": rg3, "RG-4": rg4,
                     "proves_too_much": ptm},
        "per_anchor_summary": per_anchor_summary,
        "anchor_divergence_localization": {
            "localized_to": ("ANCHOR INPUTS, not the formula: every row of both "
                             "anchors uses one and the same law L_curr, and the "
                             "law-level deviation between the current law and "
                             "the BATCH-eb0a7e law is reported per anchor above."),
            "per_field": anchor_divergence,
        },
        "row_count": len(rows),
        "rows": rows,
    }

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print(f"rows={len(rows)}  optimal_anchors_identical={optimal_identical}")
    for k in ("RG-1", "RG-2", "RG-3", "RG-4", "proves_too_much"):
        print(f"  {k}: {out['controls'][k]['status']}")
    for a, s in per_anchor_summary.items():
        print(f"  {a}: rows={s['row_count']} "
              f"maxdev_vs_eb0a7e_law={s['max_abs_deviation_current_law_vs_eb0a7e_law_bits']} "
              f"maxdev_vs_eb0a7e_table={s['max_abs_deviation_vs_eb0a7e_recomputed_table_bits']} "
              f"maxdev_vs_run={s['max_abs_deviation_vs_RUN_WESOVOW_201692_001_bits']} "
              f"(overlapping rows={s['rows_overlapping_RUN_WESOVOW_201692_001']})")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
