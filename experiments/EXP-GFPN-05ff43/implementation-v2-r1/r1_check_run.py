#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r1 / 2-a1-r1 -- the r1 COMPLETION-GATE CHECKER (addendum PS-5 checker; RC-3 (e)).

usage: python3 -B r1_check_run.py experiments/EXP-GFPN-05ff43/runs/<RUN-ID>
       python3 -B r1_check_run.py reg1 --candidate RUN_DIR [...]      (the REG-1 comparator, = r1_reg1.py)

1. Runs the frozen checks UNCHANGED in a SEPARATE PROCESS (RC-3 (e)): v2_check_run.main on a repaired v2 package
   with v2_common.PLAN_PATH -> trial-plan-v2-r1.json; a1_check_run.main on a repaired addendum package with the
   a1_common constants set as r1_entry_a1.py sets them BEFORE a1_check_run is imported (its line 30 calls
   redirect_v2 at import). This process imports neither checker, so no v2 check can be redirected by an a1 import.
2. Adds the r1 checks: protocol label, repair / amendment / addendum blocks, run card, derived_from; the three
   phase-A commits (0fa03f and 4ff597 literal, b53550 recorded); clean flags for the three implementation trees;
   resources.pari_stack (P-A): start read-backs through two fresh handles equal 67108864 / 536870912, the exit
   read-back equals them (RC-2 (b) "requested" semantics established in stage R1), configuration made before the
   first v2 / v2-a1 import, every RC-3 redirection read back equal; cypari2's version recorded;
   gate.regression_REG-1 recorded with verdict PASS and the plan's exclusion-list sha256 from G2 on; no file of the
   package carries TASK-20260923-cd932c or TASK-20260923-6c7f55; watchdogs recorded equal; the inference block.
"""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_common as R                                    # noqa: E402

FROZEN_LAUNCHER = [sys.executable, "-B", os.path.abspath(__file__)]   # redirected only in development checks
# DV-1: driver commands whose code path reaches an IN-PROCESS PARI call (v2_common.curve_order_pari).
IN_PROCESS_PARI_COMMANDS = {"v2r1": {"fixture", "controls", "fixture4"}, "a1r1": set()}


def frozen_v2(rd):
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    C.PLAN_PATH = R.PLAN_V2_R1
    import v2_check_run as K
    if C.PLAN_PATH != R.PLAN_V2_R1:
        print("REFUSING: v2_common.PLAN_PATH read-back differs")
        return 2
    return K.main(rd)


def frozen_a1(rd):
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC
    AC.PLAN_A1_PATH = R.PLAN_A1_R1
    AC.V2_PLAN_PATH = R.PLAN_V2_R1
    AC.RECEIPT_V2_PHASE_B = R.RECEIPT_R1_PHASE_B
    AC.V2_GATE_PACKAGES = tuple(R.load_json(R.PLAN_V2_R1)["gate"]["blocking_packages"])
    AC.TASK_ID_RUNS = R.TASK_R2B
    AC.PROTOCOL_VERSION = R.PROTOCOL_A1_R1
    import a1_check_run as K                             # redirect_v2() at import: v2_common.PLAN_PATH -> PLAN_A1_R1
    import v2_common as C
    C.TASK_ID = R.TASK_R2B
    if C.PLAN_PATH != R.PLAN_A1_R1 or AC.PROTOCOL_VERSION != R.PROTOCOL_A1_R1 or AC.TASK_ID_RUNS != R.TASK_R2B:
        print("REFUSING: redirection read-back differs")
        return 2
    rc = K.main(rd)
    # a1_check_run's own forbidden-id scan covers TASK-20260923-cd932c; the r1 checks add TASK-20260923-6c7f55.
    return rc


def which_plan(rid):
    for key, path in (("v2r1", R.PLAN_V2_R1), ("a1r1", R.PLAN_A1_R1)):
        plan = R.load_json(path)
        if any(p["run_id"] == rid for p in plan["packages"]):
            return key, plan
    return None, None


def r1_checks(rd, which, plan):
    import json
    import yaml
    errs, notes = [], []
    rid = os.path.basename(rd.rstrip("/"))
    man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    label, task = (R.PROTOCOL_V2_R1, R.TASK_R2) if which == "v2r1" else (R.PROTOCOL_A1_R1, R.TASK_R2B)
    if man.get("protocol_version") != label:
        errs.append("manifest protocol_version != %s" % label)
    if man.get("task_id") != task or plan.get("task_id") != task:
        errs.append("manifest / plan task_id != %s" % task)
    rp = man.get("repair") or {}
    if (rp.get("id"), rp.get("sha256"), rp.get("approval_decision")) != (R.REPAIR_ID, R.REPAIR_SHA256, R.REPAIR_APPROVAL):
        errs.append("repair block id / sha256 / approval wrong")
    am = man.get("amendment") or {}
    if (am.get("id"), am.get("sha256"), am.get("approval_decision")) != (R.V2_AMENDMENT_ID, R.V2_AMENDMENT_SHA256, R.V2_APPROVAL):
        errs.append("v2 amendment block wrong")
    ad = man.get("addendum")
    if which == "a1r1" and (not ad or (ad.get("id"), ad.get("sha256"), ad.get("approval_decision")) != (R.A1_ADDENDUM_ID, R.A1_ADDENDUM_SHA256, R.A1_APPROVAL)):
        errs.append("v2-a1 addendum block wrong or missing")
    inv = {v: k for k, v in plan["id_map"].items()}
    if man.get("derived_from") != inv.get(rid):
        errs.append("derived_from %s != retired id %s" % (man.get("derived_from"), inv.get(rid)))
    code = man.get("code") or {}
    pac = code.get("phase_a_commits") or {}
    if pac.get("TASK-20260923-0fa03f") != R.PHASE_A_COMMIT_0FA03F:
        errs.append("phase_a_commits TASK-20260923-0fa03f != %s" % R.PHASE_A_COMMIT_0FA03F)
    if not pac.get(R.ARCHIVE_TASK):
        errs.append("phase_a_commits %s not recorded" % R.ARCHIVE_TASK)
    if which == "a1r1" and pac.get("TASK-20260923-4ff597") != R.PHASE_A_COMMIT_4FF597:
        errs.append("phase_a_commits TASK-20260923-4ff597 != %s" % R.PHASE_A_COMMIT_4FF597)
    if not (pac.get("sources") or {}):
        errs.append("phase_a_commits sources not recorded")
    for k in ("implementation_v2_clean", "implementation_v2_a1_clean", "implementation_v2_r1_clean"):
        if code.get(k) is not True:
            errs.append("%s not recorded true" % k)
    res = man.get("resources") or {}
    ps = res.get("pari_stack") or {}
    stack = ps.get("pari_stack") or {}
    if ps.get("status") in (None, "refused_before_any_command") or str(ps.get("status", "")).startswith("absent"):
        errs.append("pari_stack status %s" % ps.get("status"))
    for key, v in (ps.get("redirections") or {}).items():
        if v.get("equal") is not True:
            errs.append("RC-3 redirection %s not read back equal" % key)
    if not ps.get("redirections"):
        errs.append("RC-3 redirection read-back not recorded")
    st = stack.get("start_readback") or {}
    for h in ("fresh_handle_1", "fresh_handle_2"):
        r = st.get(h) or {}
        if r.get("parisize") != R.PARISIZE or r.get("parisizemax") != R.PARISIZEMAX:
            errs.append("RC-2 (a) start read-back %s %s" % (h, r))
    ex = stack.get("exit_readback") or {}
    if ex.get("parisizemax") != R.PARISIZEMAX:
        errs.append("RC-2 (b) exit parisizemax %s != %d" % (ex.get("parisizemax"), R.PARISIZEMAX))
    ok_size = ex.get("parisize") == R.PARISIZE if R.PARISIZE_EXIT_SEMANTICS == "requested" else (R.PARISIZE <= (ex.get("parisize") or 0) <= R.PARISIZEMAX)
    if not ok_size:
        errs.append("RC-2 (b) exit parisize %s (semantics %s)" % (ex.get("parisize"), R.PARISIZE_EXIT_SEMANTICS))
    if stack.get("configured_before_first_v2_or_a1_import") is not True:
        errs.append("RC-2 (c) configuration not made before the first v2 / v2-a1 import")
    if not (stack.get("versions") or {}).get("cypari2") or not ((man.get("environment") or {}).get("dependencies") or {}).get("cypari2"):
        errs.append("cypari2 version not recorded")
    if stack.get("branch") != R.PS1_BRANCH:
        errs.append("pari_stack branch %s != %s" % (stack.get("branch"), R.PS1_BRANCH))
    cmd = (man.get("code") or {}).get("command", "").split()
    sub = next((c for c in cmd if c in IN_PROCESS_PARI_COMMANDS[which] or c in ("anchor-identity", "build", "cells", "aggregate",
                                                                                  "controls-a1", "aggregate-a1")), None)
    notes.append("command %s reaches in-process PARI per DV-1: %s" % (sub, sub in IN_PROCESS_PARI_COMMANDS[which]))
    gate_ids = R.load_json(R.PLAN_V2_R1)["gate"]["blocking_packages"]
    if rid != gate_ids[0]:
        rg = (man.get("gate") or {}).get("regression_REG-1") or {}
        if rg.get("verdict") != "PASS":
            errs.append("gate.regression_REG-1 not recorded PASS: %s" % rg.get("verdict"))
        if rg.get("exclusion_list_sha256") != plan["gate"]["regression"]["exclusion_list_sha256"]:
            errs.append("gate.regression_REG-1 exclusion-list sha256 differs from the plan's")
    for root, _d, files in os.walk(rd):
        for f in files:
            b = open(os.path.join(root, f), "rb").read()
            for t in R.FORBIDDEN_TASK_IDS:
                if t.encode() in b:
                    errs.append("forbidden task id %s present in %s" % (t, os.path.relpath(os.path.join(root, f), rd)))
    if ((res.get("watchdogs_declared") or {}).get("equal_to_trial_plan_v2")) is not True:
        errs.append("watchdogs not recorded equal to trial-plan-v2.json's")
    inf = man.get("inference") or {}
    if inf.get("requested_policy") != "executor-implementation" or inf.get("resolved_model_id") is not None \
            or inf.get("fallback_used") is not False or inf.get("bedrock_used") is not False:
        errs.append("inference block not as required")
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    if man.get("status") != raw.get("run_status") and not (raw.get("run_status") == "completed_valid" and man.get("status") == "failed"):
        errs.append("manifest status disagrees with raw-result")
    return errs, notes


def main(rd):
    rd = os.path.abspath(rd)
    rid = os.path.basename(rd.rstrip("/"))
    which, plan = which_plan(rid)
    if which is None:
        print("%s: FAIL; run id not reserved in either r1 plan" % rd)
        return 1
    mode = "frozen-v2" if which == "v2r1" else "frozen-a1"
    pr = subprocess.run(FROZEN_LAUNCHER + [mode, rd], capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    print("frozen checker (%s, separate process, unchanged): %s" % ("v2_check_run" if which == "v2r1" else "a1_check_run",
                                                                     "PASS" if pr.returncode == 0 else "FAIL rc=%s" % pr.returncode))
    print(pr.stdout.rstrip())
    if pr.stderr.strip():
        print(pr.stderr.rstrip())
    errs, notes = r1_checks(rd, which, plan)
    print("%s: r1 checks %s; %s" % (rd, "PASS" if not errs else "FAIL", notes))
    for e in errs:
        print("  -", e)
    return 1 if (errs or pr.returncode) else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "reg1":
        import r1_reg1
        sys.exit(r1_reg1.main(sys.argv[2:]))
    if len(sys.argv) == 3 and sys.argv[1] == "frozen-v2":
        sys.exit(frozen_v2(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "frozen-a1":
        sys.exit(frozen_a1(sys.argv[2]))
    sys.exit(main(sys.argv[1]))
