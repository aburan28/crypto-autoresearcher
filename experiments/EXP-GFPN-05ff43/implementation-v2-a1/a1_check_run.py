#!/usr/bin/env python3
"""Completion-gate check for one EXP-GFPN-05ff43 v2-a1 ADDENDUM run package (addendum A1-7 (4)).

usage: python3 -B a1_check_run.py experiments/EXP-GFPN-05ff43/runs/<RUN-ID>

1. Applies v2_check_run's checks UNCHANGED (its main(), with v2_common.PLAN_PATH redirected to
   trial-plan-v2-a1.json in this process): required artifacts, run id reserved, manifest == raw-result,
   commit + clean flag, child RLIMIT_AS read back by getrlimit, msolve threads {1}, host RAM/swap, the
   inference block, certificate kind and independent re-verification, F3 undecidable, no 2^20-anchored
   field, torsion_S5_norm order 3840.
2. Adds the addendum checks:
   - manifest protocol_version "2-a1", addendum id and sha256, task id TASK-20260923-6c7f55, and no file of
     the package carries the forbidden task id (AA-5 (a));
   - both phase-A commits recorded (TASK-20260923-0fa03f, TASK-20260923-4ff597) and both clean-tree flags true;
   - watchdogs recorded equal to trial-plan-v2.json's;
   - controls_a1: all six checks (a)-(f) present with a boolean gate_pass; packages 2-9: controls_a1 passed;
   - aggregate_a1: the A1-4 label on every (16777291, ecgfp5_shaped) row, no such row in the primary section,
     the off-shape section holds exactly those rows, every v2 figure that uses one is marked; the A1-3 triple
     accounting and the AA-4 matched-triple figures RECOMPUTED from the rows equal the reported ones.
"""
import contextlib
import io
import json
import os
import sys

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

C = AC.redirect_v2()
import yaml                                              # noqa: E402

import v2_check_run as V2CHK                             # noqa: E402
import a1_reading as RD                                  # noqa: E402

CONTROLS_CHECK_PREFIXES = ("a_", "b_", "c_", "d_", "e_", "f_")


def addendum_checks(rd):
    errs = []
    rid = os.path.basename(rd.rstrip("/"))
    man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    if man.get("protocol_version") != AC.PROTOCOL_VERSION:
        errs.append("manifest protocol_version != 2-a1")
    ad = man.get("addendum") or {}
    if ad.get("id") != AC.ADDENDUM_ID or ad.get("sha256") != AC.ADDENDUM_SHA256:
        errs.append("manifest addendum id/sha256 wrong")
    if man.get("task_id") != AC.TASK_ID_RUNS:
        errs.append("manifest task_id != %s" % AC.TASK_ID_RUNS)
    for root, _dirs, files in os.walk(rd):
        for f in files:
            if f.endswith((".json", ".yaml", ".txt", ".log")):
                try:
                    if AC.FORBIDDEN_TASK_ID in open(os.path.join(root, f), errors="replace").read():
                        errs.append("forbidden task id present in %s (AA-5 (a))" % os.path.relpath(os.path.join(root, f), rd))
                except OSError:
                    pass
    code = man.get("code") or {}
    pac = code.get("phase_a_commits") or {}
    if not pac.get("TASK-20260923-0fa03f") or not pac.get("TASK-20260923-4ff597"):
        errs.append("both phase-A commits not recorded")
    if code.get("implementation_v2_clean") is not True or code.get("implementation_v2_a1_clean") is not True:
        errs.append("clean-tree flags not both true")
    if ((man.get("resources") or {}).get("watchdogs_declared") or {}).get("equal_to_trial_plan_v2") is not True:
        errs.append("watchdogs not recorded equal to trial-plan-v2.json's")
    plan = AC.load_json(AC.PLAN_A1_PATH)
    pk = next((p for p in plan["packages"] if p["run_id"] == rid), None)
    if pk is None:
        errs.append("run id not reserved in trial-plan-v2-a1.json")
        return errs
    if raw.get("kind") == "controls_a1":
        names = [c["check"] for c in raw.get("checks", [])]
        for pre in CONTROLS_CHECK_PREFIXES:
            if not any(n.startswith(pre) for n in names):
                errs.append("controls_a1 check %s missing" % pre.rstrip("_"))
        if not isinstance(raw.get("gate_pass"), bool):
            errs.append("controls_a1 gate_pass not boolean")
    if pk.get("controls_a1_gate_required"):
        cid = plan["gate"]["addendum_blocking_package"]
        rp = os.path.join(C.EXP_DIR, "runs", cid, "raw-result.json")
        r = json.load(open(rp)) if os.path.exists(rp) else {}
        if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
            errs.append("controls_a1 %s is not completed_valid with gate_pass true" % cid)
    if raw.get("aggregate_variant") == "aggregate_a1":
        errs += aggregate_checks(raw)
    return errs


def aggregate_checks(raw):
    errs = []
    rows = raw.get("ladder_rows", [])
    for r in rows:
        off = RD.is_off_shape(r.get("p"), r.get("curve_shape"))
        if off and (r.get("reading_label") != AC.OFF_SHAPE_LABEL or r.get("read_as_primary_shape") is not False):
            errs.append("A1-4 label missing on %s %s" % (r.get("run"), r.get("arm")))
        if not off and r.get("reading_label") == AC.OFF_SHAPE_LABEL:
            errs.append("A1-4 label applied to an on-shape row %s %s" % (r.get("run"), r.get("arm")))
    offrows = [(r["run"], r["arm"]) for r in rows if RD.is_off_shape(r.get("p"), r.get("curve_shape"))]
    sec3 = [(r["run"], r["arm"]) for r in (raw.get("section_iii_off_shape_descriptive") or {}).get("rows", [])]
    if sorted(offrows) != sorted(sec3):
        errs.append("off-shape section does not hold exactly the off-shape rows")
    for s in (raw.get("section_i_primary_shape_reading") or {}).get("like_for_like_scoring", []):
        if RD.is_off_shape(s.get("p"), s.get("curve_shape")):
            errs.append("off-shape group in the primary-shape scoring")
    cellD = {}
    for r in rows:
        if r["m"] == 5 and r["target_kind"] == "random" and r["reading_label"] != AC.OFF_SHAPE_LABEL and r["D"]:
            cellD.setdefault((r["arm"], r["curve_shape"]), {})[int(r["p"])] = r["D"]
    ev = json.loads(json.dumps(RD.evaluate_all(cellD), default=str))
    rep_primary = (raw.get("section_i_primary_shape_reading") or {}).get("heur_dflat_A1_3")
    rep_ctrl = (raw.get("section_ii_control_reading") or {}).get("heur_dflat_A1_3") or {}
    if rep_primary != ev["ecgfp5_shaped"]:
        errs.append("A1-3 primary-shape triple accounting does not recompute from the rows")
    for sh in ("random_2torsion", "random_no2torsion"):
        if rep_ctrl.get(sh) != ev[sh]:
            errs.append("A1-3 %s triple accounting does not recompute from the rows" % sh)
    mt = json.loads(json.dumps(RD.matched_triples(cellD), default=str))
    if (raw.get("section_ii_control_reading") or {}).get("AA_4_matched_triple") != mt:
        errs.append("AA-4 matched-triple figures do not recompute from the rows")
    for arm_shape, e in (((raw.get("section_iv_reconciliation_with_v2_aggregate") or {}).get("figures") or {}).get("heur_dflat") or {}).items():
        fig = e.get("figure") or {}
        if arm_shape.endswith("|ecgfp5_shaped") and "16777291" in (fig.get("D_per_prime") or {}) and "mark" not in e:
            errs.append("v2 figure %s uses the off-shape rung but is not marked" % arm_shape)
    if "section_v_planned_cells_without_row" not in raw:
        errs.append("section (v) missing")
    return errs


def main(rd):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        v2_rc = V2CHK.main(rd)
    v2_out = buf.getvalue()
    errs = addendum_checks(rd)
    print("v2_check_run (unchanged, plan redirected): %s" % ("PASS" if v2_rc == 0 else "FAIL"))
    print(v2_out.rstrip())
    print("%s: addendum checks %s" % (rd, "PASS" if not errs else "FAIL"))
    for e in errs:
        print("  -", e)
    return 1 if (errs or v2_rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
